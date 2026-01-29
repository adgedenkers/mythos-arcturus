#!/usr/bin/env python3
"""
Mythos Ephemeris Updater

Updates daily planetary positions in PostgreSQL.
Designed to run via cron daily at midnight UTC.

Usage:
    python update_ephemeris.py                  # Update today
    python update_ephemeris.py --date 2026-01-29  # Specific date
    python update_ephemeris.py --range 30       # Next 30 days
    python update_ephemeris.py --backfill 365   # Past year

Requires: pyswisseph (pip install pyswisseph)
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import execute_values

# Swiss Ephemeris
import swisseph as swe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Load environment
from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

# Database connection
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'mythos'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
}

# Swiss Ephemeris body IDs
# Maps our body names to Swiss Eph constants
BODY_MAP = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
    'North Node': swe.TRUE_NODE,  # True node
    'Black Moon Lilith': swe.MEAN_APOG,  # Mean Lilith
    'Chiron': swe.CHIRON,
}

# Asteroid bodies (require separate calculation)
ASTEROID_MAP = {
    'Ceres': 1,
    'Pallas': 2,
    'Juno': 3,
    'Vesta': 4,
}

# Signs
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Moon phases
MOON_PHASES = [
    'New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
    'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'
]


def get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude."""
    sign_num = int(longitude / 30) % 12
    return SIGNS[sign_num]


def get_sign_degree(longitude: float) -> int:
    """Get degree within sign (0-29)."""
    return int(longitude % 30)


def format_position(longitude: float) -> str:
    """Format position as '15°42'33" Aries'."""
    sign = get_sign_from_longitude(longitude)
    deg = int(longitude % 30)
    remainder = (longitude % 30) - deg
    minutes = int(remainder * 60)
    seconds = int((remainder * 60 - minutes) * 60)
    return f"{deg}°{minutes:02d}'{seconds:02d}\" {sign}"


def get_moon_phase(sun_long: float, moon_long: float) -> Tuple[str, float]:
    """Calculate moon phase from Sun and Moon positions."""
    # Calculate angle between Moon and Sun
    angle = (moon_long - sun_long) % 360
    
    # Phase percentage (0 = new, 50 = full, 100 = new again)
    if angle <= 180:
        percentage = (angle / 180) * 100
    else:
        percentage = ((360 - angle) / 180) * 100
    
    # Phase name
    phase_num = int(angle / 45) % 8
    phase_name = MOON_PHASES[phase_num]
    
    return phase_name, percentage


def calculate_positions(jd: float) -> Dict[str, Dict]:
    """
    Calculate positions for all bodies at given Julian Day.
    
    Returns dict of body_name -> {longitude, latitude, distance, is_retrograde, daily_motion}
    """
    positions = {}
    
    # Calculate main bodies
    for body_name, body_id in BODY_MAP.items():
        try:
            # Get position (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
            result, flags = swe.calc_ut(jd, body_id)
            
            longitude = result[0]
            latitude = result[1]
            distance = result[2]
            daily_motion = result[3]  # degrees per day
            
            # Retrograde if daily motion is negative (except nodes which move backward)
            is_retrograde = daily_motion < 0
            if body_name == 'North Node':
                is_retrograde = False  # Nodes always move retrograde, don't flag
            
            positions[body_name] = {
                'longitude': longitude,
                'latitude': latitude,
                'distance': distance,
                'daily_motion': daily_motion,
                'is_retrograde': is_retrograde,
            }
        except Exception as e:
            log.error(f"Error calculating {body_name}: {e}")
    
    # Calculate asteroids
    for body_name, asteroid_num in ASTEROID_MAP.items():
        try:
            result, flags = swe.calc_ut(jd, swe.AST_OFFSET + asteroid_num)
            
            positions[body_name] = {
                'longitude': result[0],
                'latitude': result[1],
                'distance': result[2],
                'daily_motion': result[3],
                'is_retrograde': result[3] < 0,
            }
        except Exception as e:
            log.error(f"Error calculating asteroid {body_name}: {e}")
    
    # Calculate South Node (opposite of North Node)
    if 'North Node' in positions:
        nn_long = positions['North Node']['longitude']
        positions['South Node'] = {
            'longitude': (nn_long + 180) % 360,
            'latitude': -positions['North Node']['latitude'],
            'distance': positions['North Node']['distance'],
            'daily_motion': positions['North Node']['daily_motion'],
            'is_retrograde': False,
        }
    
    return positions


def date_to_julian(d: date) -> float:
    """Convert date to Julian Day (at midnight UTC)."""
    return swe.julday(d.year, d.month, d.day, 0.0)


def update_ephemeris_for_date(conn, target_date: date) -> int:
    """
    Update ephemeris for a single date.
    Returns number of rows inserted/updated.
    """
    jd = date_to_julian(target_date)
    positions = calculate_positions(jd)
    
    if not positions:
        log.warning(f"No positions calculated for {target_date}")
        return 0
    
    # Get Sun and Moon for moon phase
    sun_long = positions.get('Sun', {}).get('longitude', 0)
    moon_long = positions.get('Moon', {}).get('longitude', 0)
    moon_phase, moon_phase_pct = get_moon_phase(sun_long, moon_long)
    
    # Prepare rows for insert
    rows = []
    for body_name, data in positions.items():
        longitude = data['longitude']
        
        row = (
            target_date,
            body_name,
            longitude,
            data.get('latitude'),
            data.get('distance'),
            get_sign_from_longitude(longitude),
            get_sign_degree(longitude),
            format_position(longitude),
            data.get('is_retrograde', False),
            data.get('daily_motion'),
            moon_phase if body_name == 'Moon' else None,
            moon_phase_pct if body_name == 'Moon' else None,
            False,  # is_void_of_course - would need more calculation
            None,   # void_of_course_until
        )
        rows.append(row)
    
    # Insert with ON CONFLICT UPDATE
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO astro_ephemeris (
                date, body_name, longitude, latitude, distance_au,
                sign, sign_degree, position_display,
                is_retrograde, daily_motion,
                moon_phase, moon_phase_percentage,
                is_void_of_course, void_of_course_until
            ) VALUES %s
            ON CONFLICT (date, body_name) DO UPDATE SET
                longitude = EXCLUDED.longitude,
                latitude = EXCLUDED.latitude,
                distance_au = EXCLUDED.distance_au,
                sign = EXCLUDED.sign,
                sign_degree = EXCLUDED.sign_degree,
                position_display = EXCLUDED.position_display,
                is_retrograde = EXCLUDED.is_retrograde,
                daily_motion = EXCLUDED.daily_motion,
                moon_phase = EXCLUDED.moon_phase,
                moon_phase_percentage = EXCLUDED.moon_phase_percentage
            """,
            rows
        )
    
    return len(rows)


def detect_ingresses(conn, start_date: date, end_date: date):
    """Detect and record sign ingresses in date range."""
    with conn.cursor() as cur:
        # Find where sign changes between consecutive days
        cur.execute("""
            WITH daily AS (
                SELECT 
                    date,
                    body_name,
                    sign,
                    LAG(sign) OVER (PARTITION BY body_name ORDER BY date) as prev_sign,
                    is_retrograde
                FROM astro_ephemeris
                WHERE date BETWEEN %s AND %s
            )
            SELECT date, body_name, prev_sign, sign, is_retrograde
            FROM daily
            WHERE sign != prev_sign AND prev_sign IS NOT NULL
        """, (start_date, end_date))
        
        ingresses = cur.fetchall()
        
        for ing_date, body, leaving, entering, is_retro in ingresses:
            cur.execute("""
                INSERT INTO astro_ingresses (
                    body_name, entering_sign, leaving_sign, 
                    ingress_datetime_utc, is_retrograde_ingress
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (body, entering, leaving, datetime.combine(ing_date, datetime.min.time()), is_retro))
        
        log.info(f"Recorded {len(ingresses)} ingresses")


def detect_retrogrades(conn, start_date: date, end_date: date):
    """Detect and record retrograde stations in date range."""
    with conn.cursor() as cur:
        # Find where retrograde status changes
        cur.execute("""
            WITH daily AS (
                SELECT 
                    date,
                    body_name,
                    longitude,
                    sign,
                    is_retrograde,
                    LAG(is_retrograde) OVER (PARTITION BY body_name ORDER BY date) as was_retrograde
                FROM astro_ephemeris
                WHERE date BETWEEN %s AND %s
                AND body_name IN ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto')
            )
            SELECT date, body_name, longitude, sign, is_retrograde, was_retrograde
            FROM daily
            WHERE is_retrograde != was_retrograde AND was_retrograde IS NOT NULL
        """, (start_date, end_date))
        
        stations = cur.fetchall()
        
        for station_date, body, longitude, sign, is_retro, was_retro in stations:
            station_type = 'retrograde' if is_retro else 'direct'
            
            if is_retro:
                # Station retrograde - insert new record
                cur.execute("""
                    INSERT INTO astro_retrogrades (
                        body_name, station_retrograde_datetime_utc,
                        station_retrograde_degree, station_retrograde_sign
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (body, datetime.combine(station_date, datetime.min.time()), longitude, sign))
            else:
                # Station direct - update existing record
                cur.execute("""
                    UPDATE astro_retrogrades
                    SET station_direct_datetime_utc = %s,
                        station_direct_degree = %s,
                        station_direct_sign = %s
                    WHERE body_name = %s
                    AND station_direct_datetime_utc IS NULL
                    ORDER BY station_retrograde_datetime_utc DESC
                    LIMIT 1
                """, (datetime.combine(station_date, datetime.min.time()), longitude, sign, body))
            
            log.info(f"{body} station {station_type} on {station_date} at {format_position(longitude)}")


def main():
    parser = argparse.ArgumentParser(description='Update Mythos ephemeris data')
    parser.add_argument('--date', type=str, help='Specific date (YYYY-MM-DD)')
    parser.add_argument('--range', type=int, help='Number of days forward from today')
    parser.add_argument('--backfill', type=int, help='Number of days backward from today')
    parser.add_argument('--detect-events', action='store_true', help='Detect ingresses and retrogrades')
    
    args = parser.parse_args()
    
    # Initialize Swiss Ephemeris
    # Use default ephemeris path or set custom
    swe.set_ephe_path(os.getenv('SWISSEPH_PATH', '/usr/share/ephe'))
    
    # Determine date range
    if args.date:
        start_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        end_date = start_date
    elif args.range:
        start_date = date.today()
        end_date = start_date + timedelta(days=args.range)
    elif args.backfill:
        end_date = date.today()
        start_date = end_date - timedelta(days=args.backfill)
    else:
        # Default: today only
        start_date = date.today()
        end_date = start_date
    
    log.info(f"Updating ephemeris from {start_date} to {end_date}")
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    
    try:
        total_rows = 0
        current_date = start_date
        
        while current_date <= end_date:
            rows = update_ephemeris_for_date(conn, current_date)
            total_rows += rows
            
            if current_date.day == 1 or current_date == start_date:
                log.info(f"Processing {current_date}...")
            
            current_date += timedelta(days=1)
        
        conn.commit()
        log.info(f"Updated {total_rows} ephemeris rows")
        
        # Detect events if requested
        if args.detect_events:
            log.info("Detecting astronomical events...")
            detect_ingresses(conn, start_date, end_date)
            detect_retrogrades(conn, start_date, end_date)
            conn.commit()
        
    except Exception as e:
        conn.rollback()
        log.error(f"Error: {e}")
        raise
    finally:
        conn.close()
        swe.close()
    
    log.info("Ephemeris update complete")


if __name__ == '__main__':
    main()
