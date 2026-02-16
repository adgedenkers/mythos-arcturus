#!/usr/bin/env python3
"""
Mythos Astrology Calculator

Enhanced natal chart calculator with batch processing and comparison support.
Uses Swiss Ephemeris for accurate calculations.

Usage:
    # Single chart
    python calculator.py --name "Ka'tuar'el" --person-id 1
    
    # Batch from people table
    python calculator.py --batch-all
    
    # Compare two charts
    python calculator.py --compare "Ka'tuar'el" "Seraphe"
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import swisseph as swe

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

# Swiss Ephemeris path
EPHE_PATH = os.getenv('SWISSEPH_PATH', '/opt/mythos/ephemeris')

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Body IDs
BODIES = {
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
    'North Node': swe.TRUE_NODE,
    'Chiron': swe.CHIRON,
}

ASTEROIDS = {
    'Ceres': 1,
    'Pallas': 2,
    'Juno': 3,
    'Vesta': 4,
}

# Aspect definitions (angle, orb)
ASPECTS = {
    'Conjunction': (0, 10),
    'Opposition': (180, 8),
    'Trine': (120, 8),
    'Square': (90, 7),
    'Sextile': (60, 6),
    'Quincunx': (150, 3),
    'Semi-sextile': (30, 2),
}

# House systems
HOUSE_SYSTEMS = {
    'Placidus': b'P',
    'Whole Sign': b'W',
    'Equal House': b'E',
    'Koch': b'K',
    'Campanus': b'C',
    'Regiomontanus': b'R',
    'Porphyry': b'O',
}

# Dignities
RULERSHIPS = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mercury': ['Gemini', 'Virgo'],
    'Venus': ['Taurus', 'Libra'],
    'Mars': ['Aries', 'Scorpio'],
    'Jupiter': ['Sagittarius', 'Pisces'],
    'Saturn': ['Capricorn', 'Aquarius'],
    'Uranus': ['Aquarius'],
    'Neptune': ['Pisces'],
    'Pluto': ['Scorpio'],
}

EXALTATIONS = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mercury': 'Virgo',
    'Venus': 'Pisces', 'Mars': 'Capricorn', 'Jupiter': 'Cancer',
    'Saturn': 'Libra',
}

DETRIMENTS = {
    'Sun': ['Aquarius'], 'Moon': ['Capricorn'],
    'Mercury': ['Sagittarius', 'Pisces'], 'Venus': ['Aries', 'Scorpio'],
    'Mars': ['Taurus', 'Libra'], 'Jupiter': ['Gemini', 'Virgo'],
    'Saturn': ['Cancer', 'Leo'],
}

FALLS = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mercury': 'Pisces',
    'Venus': 'Virgo', 'Mars': 'Cancer', 'Jupiter': 'Capricorn',
    'Saturn': 'Aries',
}


def get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude."""
    return SIGNS[int(longitude / 30) % 12]


def get_degree_parts(longitude: float) -> Tuple[int, int, float]:
    """Get degree, minute, second from longitude."""
    in_sign = longitude % 30
    degree = int(in_sign)
    remainder = (in_sign - degree) * 60
    minute = int(remainder)
    second = (remainder - minute) * 60
    return degree, minute, second


def format_position(longitude: float) -> str:
    """Format position as '15°42'33" Aries'."""
    sign = get_sign_from_longitude(longitude)
    deg, min_, sec = get_degree_parts(longitude)
    return f"{deg}°{min_:02d}'{int(sec):02d}\" {sign}"


def get_dignity(body: str, sign: str) -> str:
    """Determine dignity of a body in a sign."""
    if body in RULERSHIPS and sign in RULERSHIPS[body]:
        return 'domicile'
    if body in EXALTATIONS and sign == EXALTATIONS[body]:
        return 'exaltation'
    if body in DETRIMENTS and sign in DETRIMENTS[body]:
        return 'detriment'
    if body in FALLS and sign == FALLS[body]:
        return 'fall'
    return 'peregrine'


def find_house(longitude: float, cusps: List[float]) -> int:
    """Find which house a longitude falls in."""
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]
        
        # Handle wrap-around at 0°
        if cusp_end < cusp_start:
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1
        else:
            if cusp_start <= longitude < cusp_end:
                return i + 1
    
    return 1  # Default to first house


def calculate_aspect(long1: float, long2: float) -> Optional[Tuple[str, float]]:
    """
    Calculate aspect between two longitudes.
    Returns (aspect_type, orb) or None.
    """
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    
    for aspect_name, (angle, max_orb) in ASPECTS.items():
        orb = abs(diff - angle)
        if orb <= max_orb:
            return (aspect_name, orb)
    
    return None


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day, 
                      dt.hour + dt.minute/60 + dt.second/3600)


def calculate_chart(
    conn,
    name: str,
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    location_name: str = "",
    person_id: Optional[int] = None,
    house_system: str = "Placidus",
) -> str:
    """
    Calculate a natal chart and store in database.
    
    Returns: chart_id (UUID)
    """
    log.info(f"Calculating chart for {name}")
    
    # Convert to Julian Day (assumes birth_dt is already local time)
    jd = datetime_to_jd(birth_dt)
    
    # Calculate house cusps
    house_sys = HOUSE_SYSTEMS.get(house_system, b'P')
    cusps, ascmc = swe.houses(jd, latitude, longitude, house_sys)
    
    asc = ascmc[0]
    mc = ascmc[1]
    
    # Create chart record
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO astro_charts (
                entity_type, entity_name, person_id,
                event_datetime, event_datetime_utc, timezone, timezone_offset_minutes,
                location_name, latitude, longitude,
                house_system, zodiac_type
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            RETURNING id
        """, (
            'person', name, person_id,
            birth_dt, birth_dt, 'UTC', 0,
            location_name, latitude, longitude,
            house_system, 'tropical',
        ))
        chart_id = cur.fetchone()[0]
    
    log.info(f"Created chart {chart_id}")
    
    # Calculate placements
    placement_rows = []
    placement_longs = {}
    
    # Main bodies
    for body_name, body_id in BODIES.items():
        try:
            result, flags = swe.calc_ut(jd, body_id)
            long = result[0]
            lat = result[1]
            speed = result[3]
            
            sign = get_sign_from_longitude(long)
            deg, min_, sec = get_degree_parts(long)
            house = find_house(long, cusps)
            dignity = get_dignity(body_name, sign)
            
            is_retro = speed < 0 and body_name not in ['North Node', 'Chiron']
            
            placement_rows.append((
                chart_id, body_name, 'planet',
                long, lat, None,
                sign, deg, min_, sec,
                format_position(long), house, None,
                is_retro, speed, None, dignity, 'swiss_ephemeris'
            ))
            placement_longs[body_name] = long
            
        except Exception as e:
            log.error(f"Error calculating {body_name}: {e}")
    
    # Asteroids
    for body_name, ast_num in ASTEROIDS.items():
        try:
            result, flags = swe.calc_ut(jd, swe.AST_OFFSET + ast_num)
            long = result[0]
            speed = result[3]
            
            sign = get_sign_from_longitude(long)
            deg, min_, sec = get_degree_parts(long)
            house = find_house(long, cusps)
            
            placement_rows.append((
                chart_id, body_name, 'asteroid',
                long, 0, None,
                sign, deg, min_, sec,
                format_position(long), house, None,
                speed < 0, speed, None, 'peregrine', 'swiss_ephemeris'
            ))
            placement_longs[body_name] = long
            
        except Exception as e:
            log.error(f"Error calculating asteroid {body_name}: {e}")
    
    # Add South Node
    if 'North Node' in placement_longs:
        nn_long = placement_longs['North Node']
        sn_long = (nn_long + 180) % 360
        sign = get_sign_from_longitude(sn_long)
        deg, min_, sec = get_degree_parts(sn_long)
        house = find_house(sn_long, cusps)
        
        placement_rows.append((
            chart_id, 'South Node', 'node',
            sn_long, 0, None,
            sign, deg, min_, sec,
            format_position(sn_long), house, None,
            False, 0, None, 'peregrine', 'swiss_ephemeris'
        ))
        placement_longs['South Node'] = sn_long
    
    # Add Angles
    for angle_name, angle_long, house_num in [
        ('Ascendant', asc, 1),
        ('Midheaven', mc, 10),
        ('Descendant', (asc + 180) % 360, 7),
        ('Imum Coeli', (mc + 180) % 360, 4),
    ]:
        sign = get_sign_from_longitude(angle_long)
        deg, min_, sec = get_degree_parts(angle_long)
        
        placement_rows.append((
            chart_id, angle_name, 'angle',
            angle_long, 0, None,
            sign, deg, min_, sec,
            format_position(angle_long), house_num, None,
            False, 0, None, 'peregrine', 'swiss_ephemeris'
        ))
        placement_longs[angle_name] = angle_long
    
    # Insert placements
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO astro_placements (
                chart_id, body_name, body_type,
                longitude, latitude, distance_au,
                sign, sign_degree, sign_minute, sign_second,
                position_display, house_number, house_position,
                is_retrograde, daily_motion, speed_ratio, dignity, calculation_method
            ) VALUES %s
        """, placement_rows)
    
    log.info(f"Inserted {len(placement_rows)} placements")
    
    # Insert house cusps
    cusp_rows = []
    for i in range(12):
        long = cusps[i]
        sign = get_sign_from_longitude(long)
        deg, min_, sec = get_degree_parts(long)
        
        cusp_rows.append((
            chart_id, i + 1,
            long, sign, deg, min_, sec,
            format_position(long), None
        ))
    
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO astro_house_cusps (
                chart_id, house_number,
                longitude, sign, sign_degree, sign_minute, sign_second,
                position_display, intercepted_sign
            ) VALUES %s
        """, cusp_rows)
    
    log.info(f"Inserted {len(cusp_rows)} house cusps")
    
    # Calculate aspects
    aspect_rows = []
    bodies_for_aspects = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
                          'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron', 'Ascendant', 'Midheaven']
    
    for i, body1 in enumerate(bodies_for_aspects):
        if body1 not in placement_longs:
            continue
        for body2 in bodies_for_aspects[i+1:]:
            if body2 not in placement_longs:
                continue
            
            aspect_result = calculate_aspect(placement_longs[body1], placement_longs[body2])
            if aspect_result:
                aspect_type, orb = aspect_result
                is_major = aspect_type in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
                
                aspect_rows.append((
                    chart_id, body1, body2,
                    aspect_type, ASPECTS[aspect_type][0], orb,
                    None, None, is_major, None
                ))
    
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO astro_aspects (
                chart_id, body1_name, body2_name,
                aspect_type, aspect_angle, orb,
                orb_percentage, is_partile, is_major, strength_score
            ) VALUES %s
        """, aspect_rows)
    
    log.info(f"Inserted {len(aspect_rows)} aspects")
    
    conn.commit()
    log.info(f"Chart {chart_id} complete")
    
    return str(chart_id)


def batch_calculate_from_people(conn):
    """Calculate charts for all people with birth data."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                id, first_name, middle_name, last_name, known_as,
                date_of_birth, time_of_birth,
                birth_city, birth_state, birth_country
            FROM people
            WHERE date_of_birth IS NOT NULL
              AND time_of_birth IS NOT NULL
        """)
        people = cur.fetchall()
    
    log.info(f"Found {len(people)} people with birth data")
    
    # Geocode locations (simplified - would need actual geocoding)
    location_coords = {
        'Albany, NY, USA': (42.6526, -73.7562),
        'Norwich, NY, USA': (42.5320, -75.5235),
        'Schenectady, NY, USA': (42.8142, -73.9396),
    }
    
    chart_ids = []
    for person in people:
        name = person['known_as'] or person['first_name']
        
        # Build location string
        loc_parts = [person['birth_city'], person['birth_state'], person['birth_country']]
        location = ', '.join([p for p in loc_parts if p])
        
        # Get coordinates
        coords = location_coords.get(location)
        if not coords:
            log.warning(f"No coordinates for {location}, skipping {name}")
            continue
        
        # Build datetime
        birth_dt = datetime.combine(person['date_of_birth'], person['time_of_birth'])
        
        # Calculate
        try:
            chart_id = calculate_chart(
                conn,
                name=name,
                birth_dt=birth_dt,
                latitude=coords[0],
                longitude=coords[1],
                location_name=location,
                person_id=person['id'],
            )
            chart_ids.append(chart_id)
        except Exception as e:
            log.error(f"Error calculating chart for {name}: {e}")
    
    log.info(f"Created {len(chart_ids)} charts")
    return chart_ids


def print_chart_summary(conn, chart_id: str):
    """Print a text summary of a chart."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Chart info
        cur.execute("SELECT * FROM astro_charts WHERE id = %s", (chart_id,))
        chart = cur.fetchone()
        
        # Placements
        cur.execute("""
            SELECT body_name, position_display, house_number, is_retrograde, dignity
            FROM astro_placements
            WHERE chart_id = %s
            ORDER BY 
                CASE body_name
                    WHEN 'Sun' THEN 1
                    WHEN 'Moon' THEN 2
                    WHEN 'Mercury' THEN 3
                    WHEN 'Venus' THEN 4
                    WHEN 'Mars' THEN 5
                    WHEN 'Jupiter' THEN 6
                    WHEN 'Saturn' THEN 7
                    WHEN 'Uranus' THEN 8
                    WHEN 'Neptune' THEN 9
                    WHEN 'Pluto' THEN 10
                    WHEN 'Ascendant' THEN 98
                    WHEN 'Midheaven' THEN 99
                    ELSE 50
                END
        """, (chart_id,))
        placements = cur.fetchall()
        
        # Aspects
        cur.execute("""
            SELECT body1_name, body2_name, aspect_type, orb
            FROM astro_aspects
            WHERE chart_id = %s
              AND is_major = TRUE
            ORDER BY orb
        """, (chart_id,))
        aspects = cur.fetchall()
    
    print(f"\n{'='*60}")
    print(f"NATAL CHART: {chart['entity_name']}")
    print(f"{'='*60}")
    print(f"Born: {chart['event_datetime']}")
    print(f"Location: {chart['location_name']}")
    print(f"House System: {chart['house_system']}")
    print(f"\nPLACEMENTS:")
    print(f"{'-'*60}")
    
    for p in placements:
        retro = " (R)" if p['is_retrograde'] else ""
        dignity = f" [{p['dignity']}]" if p['dignity'] != 'peregrine' else ""
        print(f"{p['body_name']:15} {p['position_display']:20} House {p['house_number']:2}{retro}{dignity}")
    
    print(f"\nMAJOR ASPECTS:")
    print(f"{'-'*60}")
    for a in aspects:
        print(f"{a['body1_name']:12} {a['aspect_type']:15} {a['body2_name']:12} (orb: {a['orb']:.2f}°)")


def main():
    parser = argparse.ArgumentParser(description='Mythos Astrology Calculator')
    parser.add_argument('--name', help='Entity name')
    parser.add_argument('--person-id', type=int, help='Person ID from people table')
    parser.add_argument('--batch-all', action='store_true', help='Calculate for all people')
    parser.add_argument('--show', help='Show chart by ID')
    
    args = parser.parse_args()
    
    # Initialize Swiss Ephemeris
    if not os.path.exists(EPHE_PATH):
        log.error(f"Ephemeris path not found: {EPHE_PATH}")
        log.error("Run install.sh to download ephemeris files")
        sys.exit(1)
    
    swe.set_ephe_path(EPHE_PATH)
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        if args.batch_all:
            chart_ids = batch_calculate_from_people(conn)
            print(f"\nCreated {len(chart_ids)} charts")
            
        elif args.show:
            print_chart_summary(conn, args.show)
            
        elif args.person_id:
            # Get person data
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id, first_name, middle_name, last_name, known_as,
                        date_of_birth, time_of_birth,
                        birth_city, birth_state, birth_country
                    FROM people
                    WHERE id = %s
                """, (args.person_id,))
                person = cur.fetchone()
            
            if not person:
                log.error(f"Person {args.person_id} not found")
                sys.exit(1)
            
            # Simplified geocoding
            location_coords = {
                'Albany, NY, USA': (42.6526, -73.7562),
                'Norwich, NY, USA': (42.5320, -75.5235),
                'Schenectady, NY, USA': (42.8142, -73.9396),
            }
            
            loc_parts = [person['birth_city'], person['birth_state'], person['birth_country']]
            location = ', '.join([p for p in loc_parts if p])
            
            coords = location_coords.get(location)
            if not coords:
                log.error(f"No coordinates for {location}")
                sys.exit(1)
            
            name = args.name or person['known_as'] or person['first_name']
            birth_dt = datetime.combine(person['date_of_birth'], person['time_of_birth'])
            
            chart_id = calculate_chart(
                conn,
                name=name,
                birth_dt=birth_dt,
                latitude=coords[0],
                longitude=coords[1],
                location_name=location,
                person_id=person['id'],
            )
            
            print(f"\nChart created: {chart_id}")
            print_chart_summary(conn, chart_id)
        
        else:
            parser.print_help()
    
    finally:
        conn.close()
        swe.close()


if __name__ == '__main__':
    main()
