#!/usr/bin/env python3
"""
Mythos Chart Calculator

Calculates natal charts and stores them in PostgreSQL + Neo4j.
Provides standardized JSON output for chart data.

Usage:
    python chart_calculator.py --name "Ka'tuar'el" --date "1975-08-15" --time "14:30" \
        --location "Amsterdam, Netherlands" --lat 52.3676 --lon 4.9041
"""

import os
import sys
import json
import argparse
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal

import psycopg2
from psycopg2.extras import execute_values
import swisseph as swe

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

# Signs
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Body IDs for Swiss Ephemeris
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
    'Black Moon Lilith': swe.MEAN_APOG,
    'Chiron': swe.CHIRON,
}

ASTEROIDS = {
    'Ceres': 1,
    'Pallas': 2,
    'Juno': 3,
    'Vesta': 4,
}

# Aspect definitions
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 10},
    'Opposition': {'angle': 180, 'orb': 8},
    'Trine': {'angle': 120, 'orb': 8},
    'Square': {'angle': 90, 'orb': 7},
    'Sextile': {'angle': 60, 'orb': 6},
    'Quincunx': {'angle': 150, 'orb': 3},
    'Semi-sextile': {'angle': 30, 'orb': 2},
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
    'Sun': 'Aries',
    'Moon': 'Taurus',
    'Mercury': 'Virgo',
    'Venus': 'Pisces',
    'Mars': 'Capricorn',
    'Jupiter': 'Cancer',
    'Saturn': 'Libra',
}

DETRIMENTS = {
    'Sun': ['Aquarius'],
    'Moon': ['Capricorn'],
    'Mercury': ['Sagittarius', 'Pisces'],
    'Venus': ['Aries', 'Scorpio'],
    'Mars': ['Taurus', 'Libra'],
    'Jupiter': ['Gemini', 'Virgo'],
    'Saturn': ['Cancer', 'Leo'],
}

FALLS = {
    'Sun': 'Libra',
    'Moon': 'Scorpio',
    'Mercury': 'Pisces',
    'Venus': 'Virgo',
    'Mars': 'Cancer',
    'Jupiter': 'Capricorn',
    'Saturn': 'Aries',
}


@dataclass
class Placement:
    """A single planetary placement."""
    body: str
    longitude: float
    latitude: float
    sign: str
    degree: int
    minute: int
    second: float
    display: str
    house: int
    is_retrograde: bool
    dignity: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class HouseCusp:
    """A house cusp position."""
    house: int
    longitude: float
    sign: str
    degree: int
    minute: int
    display: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Aspect:
    """An aspect between two bodies."""
    body1: str
    body2: str
    aspect_type: str
    angle: float
    orb: float
    is_applying: bool
    
    def to_dict(self):
        return asdict(self)


@dataclass
class NatalChart:
    """Complete natal chart data."""
    chart_id: str
    entity_name: str
    entity_type: str
    
    # Birth data
    birth_datetime: str
    birth_datetime_utc: str
    timezone: str
    location_name: str
    latitude: float
    longitude: float
    
    # Calculation settings
    house_system: str
    zodiac: str
    
    # Chart data
    placements: List[Placement]
    house_cusps: List[HouseCusp]
    aspects: List[Aspect]
    
    # Summary
    sun_sign: str
    moon_sign: str
    rising_sign: str
    
    def to_dict(self):
        return {
            'chart_id': self.chart_id,
            'entity_name': self.entity_name,
            'entity_type': self.entity_type,
            'birth_datetime': self.birth_datetime,
            'birth_datetime_utc': self.birth_datetime_utc,
            'timezone': self.timezone,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'house_system': self.house_system,
            'zodiac': self.zodiac,
            'placements': [p.to_dict() for p in self.placements],
            'house_cusps': [h.to_dict() for h in self.house_cusps],
            'aspects': [a.to_dict() for a in self.aspects],
            'sun_sign': self.sun_sign,
            'moon_sign': self.moon_sign,
            'rising_sign': self.rising_sign,
        }
    
    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)


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


def calculate_aspect(long1: float, long2: float, motion1: float = 0, motion2: float = 0) -> Optional[Tuple[str, float, bool]]:
    """
    Calculate aspect between two longitudes.
    Returns (aspect_type, orb, is_applying) or None.
    """
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    
    for aspect_name, aspect_data in ASPECTS.items():
        orb = abs(diff - aspect_data['angle'])
        if orb <= aspect_data['orb']:
            # Determine if applying (bodies getting closer)
            # Simplified: compare if faster planet is approaching aspect
            is_applying = None  # Would need motion data
            return (aspect_name, orb, is_applying)
    
    return None


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day, 
                      dt.hour + dt.minute/60 + dt.second/3600)


def calculate_chart(
    name: str,
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    location_name: str = "",
    tz_name: str = "UTC",
    house_system: str = "Placidus",
    entity_type: str = "person"
) -> NatalChart:
    """
    Calculate a complete natal chart.
    
    Args:
        name: Entity name
        birth_dt: Birth datetime (should be in local time, will convert to UTC)
        latitude: Birth latitude (positive = North)
        longitude: Birth longitude (positive = East)
        location_name: Human-readable location
        tz_name: Timezone name
        house_system: House system to use
        entity_type: 'person', 'event', 'entity', etc.
    
    Returns:
        NatalChart object with all data
    """
    chart_id = str(uuid.uuid4())
    
    # Convert to Julian Day (assumes birth_dt is already UTC)
    jd = datetime_to_jd(birth_dt)
    
    # Calculate house cusps
    house_sys = HOUSE_SYSTEMS.get(house_system, b'P')
    cusps, ascmc = swe.houses(jd, latitude, longitude, house_sys)
    
    # ascmc contains: [ASC, MC, ARMC, Vertex, Equatorial ASC, ...]
    asc = ascmc[0]
    mc = ascmc[1]
    
    # Calculate placements
    placements = []
    placement_longs = {}  # For aspect calculation
    
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
            
            placement = Placement(
                body=body_name,
                longitude=long,
                latitude=lat,
                sign=sign,
                degree=deg,
                minute=min_,
                second=sec,
                display=format_position(long),
                house=house,
                is_retrograde=speed < 0 and body_name != 'North Node',
                dignity=dignity,
            )
            placements.append(placement)
            placement_longs[body_name] = long
            
        except Exception as e:
            log.error(f"Error calculating {body_name}: {e}")
    
    # Asteroids
    for body_name, ast_num in ASTEROIDS.items():
        try:
            result, flags = swe.calc_ut(jd, swe.AST_OFFSET + ast_num)
            long = result[0]
            lat = result[1]
            speed = result[3]
            
            sign = get_sign_from_longitude(long)
            deg, min_, sec = get_degree_parts(long)
            house = find_house(long, cusps)
            
            placement = Placement(
                body=body_name,
                longitude=long,
                latitude=lat,
                sign=sign,
                degree=deg,
                minute=min_,
                second=sec,
                display=format_position(long),
                house=house,
                is_retrograde=speed < 0,
                dignity='peregrine',
            )
            placements.append(placement)
            placement_longs[body_name] = long
            
        except Exception as e:
            log.error(f"Error calculating asteroid {body_name}: {e}")
    
    # Add South Node (opposite North Node)
    if 'North Node' in placement_longs:
        nn_long = placement_longs['North Node']
        sn_long = (nn_long + 180) % 360
        sign = get_sign_from_longitude(sn_long)
        deg, min_, sec = get_degree_parts(sn_long)
        house = find_house(sn_long, cusps)
        
        placement = Placement(
            body='South Node',
            longitude=sn_long,
            latitude=0,
            sign=sign,
            degree=deg,
            minute=min_,
            second=sec,
            display=format_position(sn_long),
            house=house,
            is_retrograde=False,
            dignity='peregrine',
        )
        placements.append(placement)
        placement_longs['South Node'] = sn_long
    
    # Add Angles
    for angle_name, angle_long in [('Ascendant', asc), ('Midheaven', mc)]:
        sign = get_sign_from_longitude(angle_long)
        deg, min_, sec = get_degree_parts(angle_long)
        
        placement = Placement(
            body=angle_name,
            longitude=angle_long,
            latitude=0,
            sign=sign,
            degree=deg,
            minute=min_,
            second=sec,
            display=format_position(angle_long),
            house=1 if angle_name == 'Ascendant' else 10,
            is_retrograde=False,
            dignity='peregrine',
        )
        placements.append(placement)
        placement_longs[angle_name] = angle_long
    
    # Calculate Descendant and IC
    dsc_long = (asc + 180) % 360
    ic_long = (mc + 180) % 360
    
    for angle_name, angle_long, house_num in [('Descendant', dsc_long, 7), ('Imum Coeli', ic_long, 4)]:
        sign = get_sign_from_longitude(angle_long)
        deg, min_, sec = get_degree_parts(angle_long)
        
        placement = Placement(
            body=angle_name,
            longitude=angle_long,
            latitude=0,
            sign=sign,
            degree=deg,
            minute=min_,
            second=sec,
            display=format_position(angle_long),
            house=house_num,
            is_retrograde=False,
            dignity='peregrine',
        )
        placements.append(placement)
        placement_longs[angle_name] = angle_long
    
    # House cusps
    house_cusp_list = []
    for i in range(12):
        long = cusps[i]
        sign = get_sign_from_longitude(long)
        deg, min_, sec = get_degree_parts(long)
        
        cusp = HouseCusp(
            house=i + 1,
            longitude=long,
            sign=sign,
            degree=deg,
            minute=min_,
            display=format_position(long),
        )
        house_cusp_list.append(cusp)
    
    # Calculate aspects
    aspects = []
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
                aspect_type, orb, is_applying = aspect_result
                aspect = Aspect(
                    body1=body1,
                    body2=body2,
                    aspect_type=aspect_type,
                    angle=ASPECTS[aspect_type]['angle'],
                    orb=round(orb, 2),
                    is_applying=is_applying,
                )
                aspects.append(aspect)
    
    # Get key signs
    sun_sign = get_sign_from_longitude(placement_longs.get('Sun', 0))
    moon_sign = get_sign_from_longitude(placement_longs.get('Moon', 0))
    rising_sign = get_sign_from_longitude(asc)
    
    # Create chart
    chart = NatalChart(
        chart_id=chart_id,
        entity_name=name,
        entity_type=entity_type,
        birth_datetime=birth_dt.isoformat(),
        birth_datetime_utc=birth_dt.isoformat(),
        timezone=tz_name,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        house_system=house_system,
        zodiac='tropical',
        placements=placements,
        house_cusps=house_cusp_list,
        aspects=aspects,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        rising_sign=rising_sign,
    )
    
    return chart


def save_chart_to_postgres(conn, chart: NatalChart):
    """Save chart to PostgreSQL."""
    with conn.cursor() as cur:
        # Insert main chart record
        cur.execute("""
            INSERT INTO astro_charts (
                id, entity_type, entity_name, 
                event_datetime, event_datetime_utc, timezone, timezone_offset_minutes,
                location_name, latitude, longitude,
                house_system, zodiac_type
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (id) DO UPDATE SET
                entity_name = EXCLUDED.entity_name,
                updated_at = NOW()
            RETURNING id
        """, (
            chart.chart_id, chart.entity_type, chart.entity_name,
            chart.birth_datetime, chart.birth_datetime_utc, chart.timezone, 0,
            chart.location_name, chart.latitude, chart.longitude,
            chart.house_system, chart.zodiac,
        ))
        
        # Insert placements
        placement_rows = []
        for p in chart.placements:
            placement_rows.append((
                chart.chart_id, p.body,
                p.longitude, p.latitude, None,
                p.sign, p.degree, p.minute, p.second,
                p.display, p.house, None,
                p.is_retrograde, None, None, p.dignity, None
            ))
        
        execute_values(cur, """
            INSERT INTO astro_placements (
                chart_id, body_name,
                longitude, latitude, distance_au,
                sign, sign_degree, sign_minute, sign_second,
                position_display, house_number, house_position,
                is_retrograde, daily_motion, speed_ratio, dignity, calculation_method
            ) VALUES %s
            ON CONFLICT (chart_id, body_name, calculation_method) DO UPDATE SET
                longitude = EXCLUDED.longitude,
                sign = EXCLUDED.sign,
                position_display = EXCLUDED.position_display
        """, placement_rows)
        
        # Insert house cusps
        cusp_rows = []
        for c in chart.house_cusps:
            cusp_rows.append((
                chart.chart_id, c.house,
                c.longitude, c.sign, c.degree, c.minute, 0, c.display, None
            ))
        
        execute_values(cur, """
            INSERT INTO astro_house_cusps (
                chart_id, house_number,
                longitude, sign, sign_degree, sign_minute, sign_second, position_display, intercepted_sign
            ) VALUES %s
            ON CONFLICT (chart_id, house_number) DO UPDATE SET
                longitude = EXCLUDED.longitude,
                sign = EXCLUDED.sign
        """, cusp_rows)
        
        # Insert aspects
        aspect_rows = []
        for a in chart.aspects:
            aspect_rows.append((
                chart.chart_id, a.body1, a.body2,
                a.aspect_type, a.angle, a.orb, a.is_applying,
                None, True if a.aspect_type in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile'] else False
            ))
        
        execute_values(cur, """
            INSERT INTO astro_aspects (
                chart_id, body1_name, body2_name,
                aspect_type, aspect_angle, orb, is_applying,
                orb_percentage, is_major
            ) VALUES %s
            ON CONFLICT (chart_id, body1_name, body2_name, aspect_type) DO UPDATE SET
                orb = EXCLUDED.orb
        """, aspect_rows)
    
    log.info(f"Saved chart {chart.chart_id} to PostgreSQL")


def save_chart_to_neo4j(chart: NatalChart):
    """Save chart relationships to Neo4j."""
    from neo4j import GraphDatabase
    
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', '')
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Create Chart node
        session.run("""
            MERGE (c:Chart {chart_id: $chart_id})
            SET c.entity_name = $entity_name,
                c.entity_type = $entity_type,
                c.birth_datetime = $birth_datetime,
                c.sun_sign = $sun_sign,
                c.moon_sign = $moon_sign,
                c.rising_sign = $rising_sign,
                c.location = $location
        """, 
            chart_id=chart.chart_id,
            entity_name=chart.entity_name,
            entity_type=chart.entity_type,
            birth_datetime=chart.birth_datetime,
            sun_sign=chart.sun_sign,
            moon_sign=chart.moon_sign,
            rising_sign=chart.rising_sign,
            location=chart.location_name,
        )
        
        # Create placements and relationships
        for p in chart.placements:
            session.run("""
                MATCH (c:Chart {chart_id: $chart_id})
                MATCH (s:Sign {name: $sign})
                MATCH (h:House {number: $house})
                MERGE (p:Placement {chart_id: $chart_id, body: $body})
                SET p.longitude = $longitude,
                    p.display = $display,
                    p.is_retrograde = $is_retrograde,
                    p.dignity = $dignity
                MERGE (c)-[:HAS_PLACEMENT]->(p)
                MERGE (p)-[:IN_SIGN]->(s)
                MERGE (p)-[:IN_HOUSE]->(h)
            """,
                chart_id=chart.chart_id,
                body=p.body,
                sign=p.sign,
                house=p.house,
                longitude=p.longitude,
                display=p.display,
                is_retrograde=p.is_retrograde,
                dignity=p.dignity,
            )
        
        # Create aspect relationships
        for a in chart.aspects:
            session.run("""
                MATCH (p1:Placement {chart_id: $chart_id, body: $body1})
                MATCH (p2:Placement {chart_id: $chart_id, body: $body2})
                MERGE (p1)-[r:ASPECTS {type: $aspect_type}]->(p2)
                SET r.orb = $orb,
                    r.is_applying = $is_applying
            """,
                chart_id=chart.chart_id,
                body1=a.body1,
                body2=a.body2,
                aspect_type=a.aspect_type,
                orb=a.orb,
                is_applying=a.is_applying,
            )
    
    driver.close()
    log.info(f"Saved chart {chart.chart_id} to Neo4j")


def main():
    parser = argparse.ArgumentParser(description='Calculate natal chart')
    parser.add_argument('--name', required=True, help='Entity name')
    parser.add_argument('--date', required=True, help='Birth date (YYYY-MM-DD)')
    parser.add_argument('--time', required=True, help='Birth time (HH:MM)')
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--location', default='', help='Location name')
    parser.add_argument('--tz', default='UTC', help='Timezone')
    parser.add_argument('--house-system', default='Placidus', help='House system')
    parser.add_argument('--entity-type', default='person', help='Entity type')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--save-db', action='store_true', help='Save to databases')
    
    args = parser.parse_args()
    
    # Initialize Swiss Ephemeris
    swe.set_ephe_path(os.getenv('SWISSEPH_PATH', '/usr/share/ephe'))
    
    # Parse datetime
    date_parts = args.date.split('-')
    time_parts = args.time.split(':')
    birth_dt = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
        int(time_parts[0]), int(time_parts[1]), 0
    )
    
    # Calculate chart
    chart = calculate_chart(
        name=args.name,
        birth_dt=birth_dt,
        latitude=args.lat,
        longitude=args.lon,
        location_name=args.location,
        tz_name=args.tz,
        house_system=args.house_system,
        entity_type=args.entity_type,
    )
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(chart.to_json())
        log.info(f"Saved chart to {args.output}")
    else:
        print(chart.to_json())
    
    # Save to databases
    if args.save_db:
        conn = psycopg2.connect(**DB_CONFIG)
        try:
            save_chart_to_postgres(conn, chart)
            conn.commit()
        finally:
            conn.close()
        
        try:
            save_chart_to_neo4j(chart)
        except Exception as e:
            log.warning(f"Could not save to Neo4j: {e}")
    
    swe.close()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"NATAL CHART: {chart.entity_name}")
    print(f"{'='*50}")
    print(f"Sun: {chart.sun_sign}")
    print(f"Moon: {chart.moon_sign}")
    print(f"Rising: {chart.rising_sign}")
    print(f"Chart ID: {chart.chart_id}")


if __name__ == '__main__':
    main()
