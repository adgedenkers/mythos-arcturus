#!/usr/bin/env python3
"""
SEN-0004: Planetary Geometry Engine
Computes geocentric planetary positions, aspects, alignments, and gravitational
forcing vectors using Swiss Ephemeris (pyswisseph).

Runs hourly to build a continuous time series of planetary geometry.
"""

import json
import logging
import math
import os
import signal
import sys
import time
from datetime import datetime, timezone, timedelta

import psycopg2
import psycopg2.extras

# Swiss Ephemeris
try:
    import swisseph as swe
except ImportError:
    print("ERROR: pyswisseph not installed. Run: pip install pyswisseph --break-system-packages")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_NAME = os.getenv("MYTHOS_DB", "mythos")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "/var/run/postgresql")
DB_PORT = os.getenv("MYTHOS_DB_PORT", "5432")

EPHE_PATH = "/opt/mythos/ephemeris"

# Computation interval
COMPUTE_INTERVAL = 3600  # 1 hour

LOG_DIR = "/opt/mythos/logs"
LOG_FILE = os.path.join(LOG_DIR, "planetary_geometry.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("planetary_geometry")

# ---------------------------------------------------------------------------
# Planet definitions
# ---------------------------------------------------------------------------

# Swiss Ephemeris planet codes
PLANETS = {
    'Sun':     swe.SUN,
    'Moon':    swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus':   swe.VENUS,
    'Mars':    swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn':  swe.SATURN,
    'Uranus':  swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto':   swe.PLUTO,
}

# Planet masses (kg) for gravitational calculation
PLANET_MASSES = {
    'Sun':     1.989e30,
    'Moon':    7.342e22,
    'Mercury': 3.301e23,
    'Venus':   4.867e24,
    'Mars':    6.417e23,
    'Jupiter': 1.898e27,
    'Saturn':  5.683e26,
    'Uranus':  8.681e25,
    'Neptune': 1.024e26,
    'Pluto':   1.309e22,
}

G = 6.674e-11  # gravitational constant
AU_TO_M = 1.496e11  # meters per AU

# Zodiac signs
ZODIAC = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Aspect definitions: name, target_angle, orb, sigma for gaussian
ASPECTS = [
    ('conjunction', 0,   8, 4.0),
    ('opposition',  180, 8, 4.0),
    ('trine',       120, 6, 3.0),
    ('square',      90,  6, 3.0),
    ('sextile',     60,  4, 2.0),
]


# ---------------------------------------------------------------------------
# Swiss Ephemeris helpers
# ---------------------------------------------------------------------------

def init_ephe():
    """Initialize Swiss Ephemeris with data path."""
    swe.set_ephe_path(EPHE_PATH)


def datetime_to_jd(dt):
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def get_planet_position(planet_code, jd):
    """Get geocentric ecliptic position for a planet."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result, ret_flags = swe.calc_ut(jd, planet_code, flags)
    
    ecl_lon = result[0]     # ecliptic longitude
    ecl_lat = result[1]     # ecliptic latitude
    distance = result[2]    # distance in AU
    speed = result[3]       # speed in deg/day

    sign_idx = int(ecl_lon / 30)
    sign_degree = ecl_lon % 30

    return {
        'ecliptic_lon': ecl_lon,
        'ecliptic_lat': ecl_lat,
        'distance_au': distance,
        'speed_deg_day': speed,
        'is_retrograde': speed < 0,
        'zodiac_sign': ZODIAC[sign_idx],
        'zodiac_degree': sign_degree,
    }


# ---------------------------------------------------------------------------
# Computation
# ---------------------------------------------------------------------------

def compute_positions(dt):
    """Compute all planet positions for a given datetime."""
    jd = datetime_to_jd(dt)
    positions = {}
    for name, code in PLANETS.items():
        try:
            pos = get_planet_position(code, jd)
            pos['planet'] = name
            pos['timestamp'] = dt
            positions[name] = pos
        except Exception as e:
            log.error(f"Failed to compute {name}: {e}")
    return positions


def compute_aspects(positions, dt):
    """Compute all planetary aspects with continuous strength."""
    aspects = []
    planet_names = list(positions.keys())

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]
            lon1 = positions[p1]['ecliptic_lon']
            lon2 = positions[p2]['ecliptic_lon']

            # Angular separation (0-180)
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for asp_name, target, orb_max, sigma in ASPECTS:
                orb = abs(diff - target)
                if orb <= orb_max:
                    # Gaussian strength
                    strength = math.exp(-(orb ** 2) / (2 * sigma ** 2))

                    # Determine if applying (getting tighter)
                    speed1 = positions[p1]['speed_deg_day']
                    speed2 = positions[p2]['speed_deg_day']
                    is_applying = None
                    if speed1 is not None and speed2 is not None:
                        # Simplified: if relative speed is reducing the orb
                        is_applying = abs(speed1 - speed2) > 0

                    aspects.append({
                        'timestamp': dt,
                        'planet_a': p1,
                        'planet_b': p2,
                        'aspect_type': asp_name,
                        'exact_angle': target,
                        'actual_angle': diff,
                        'orb': orb,
                        'strength': strength,
                        'is_applying': is_applying,
                    })

    return aspects


def compute_forcing_vectors(positions, dt):
    """Compute gravitational forcing vector for each planet relative to Earth."""
    planet_vectors = {}
    net_fx = 0.0
    net_fy = 0.0

    for name, pos in positions.items():
        if name == 'Earth':
            continue

        mass = PLANET_MASSES.get(name, 0)
        dist_m = pos['distance_au'] * AU_TO_M
        if dist_m <= 0:
            continue

        # Gravitational force magnitude
        force = G * mass / (dist_m ** 2)

        # Direction from ecliptic longitude (radians)
        theta = math.radians(pos['ecliptic_lon'])
        fx = force * math.cos(theta)
        fy = force * math.sin(theta)

        planet_vectors[name] = {
            'fx': fx,
            'fy': fy,
            'magnitude': force,
            'direction_deg': pos['ecliptic_lon'],
            'distance_au': pos['distance_au'],
        }

        net_fx += fx
        net_fy += fy

    net_magnitude = math.sqrt(net_fx ** 2 + net_fy ** 2)
    net_direction = math.degrees(math.atan2(net_fy, net_fx)) % 360

    # Reinforcement metric: how aligned are all vectors?
    # 1.0 = all pulling same direction, 0.0 = perfectly canceling
    total_individual = sum(v['magnitude'] for v in planet_vectors.values())
    reinforcement = net_magnitude / total_individual if total_individual > 0 else 0

    # Compression: span of all planets
    lons = [pos['ecliptic_lon'] for pos in positions.values()]
    if lons:
        # Handle wrap-around at 0/360
        lons_sorted = sorted(lons)
        max_gap = 0
        for i in range(len(lons_sorted)):
            gap = (lons_sorted[(i + 1) % len(lons_sorted)] - lons_sorted[i]) % 360
            max_gap = max(max_gap, gap)
        compression_span = 360 - max_gap
    else:
        compression_span = 360

    return {
        'timestamp': dt,
        'planet_vectors': json.dumps(planet_vectors),
        'net_fx': net_fx,
        'net_fy': net_fy,
        'net_magnitude': net_magnitude,
        'net_direction_deg': net_direction,
        'total_reinforcement': reinforcement,
        'compression_span': compression_span,
    }


def detect_alignments(positions, aspects, dt):
    """Detect major planetary alignment patterns."""
    alignments = []

    # Stellium: 3+ planets within 10 degrees
    lons = [(name, pos['ecliptic_lon']) for name, pos in positions.items()]
    lons.sort(key=lambda x: x[1])

    for i in range(len(lons)):
        group = [lons[i]]
        for j in range(i + 1, len(lons)):
            diff = (lons[j][1] - lons[i][1]) % 360
            if diff <= 15:
                group.append(lons[j])
            else:
                break
        if len(group) >= 3:
            planets = [g[0] for g in group]
            center = sum(g[1] for g in group) / len(group)
            span = max(g[1] for g in group) - min(g[1] for g in group)
            alignments.append({
                'timestamp': dt,
                'alignment_type': 'stellium',
                'planets': planets,
                'description': f"{len(planets)}-planet stellium: {', '.join(planets)}",
                'strength': len(planets) / len(PLANETS),
                'ecliptic_center': center,
                'span_degrees': span,
            })

    # Grand trine: three mutual trines (strength > 0.5)
    strong_trines = [a for a in aspects if a['aspect_type'] == 'trine' and a['strength'] > 0.5]
    trine_planets = set()
    for t in strong_trines:
        trine_planets.add(t['planet_a'])
        trine_planets.add(t['planet_b'])

    if len(trine_planets) >= 3:
        # Check if any 3 planets are all in mutual trine
        from itertools import combinations
        for combo in combinations(trine_planets, 3):
            mutual = True
            for pair in combinations(combo, 2):
                found = any(
                    (a['planet_a'] in pair and a['planet_b'] in pair)
                    for a in strong_trines
                )
                if not found:
                    mutual = False
                    break
            if mutual:
                alignments.append({
                    'timestamp': dt,
                    'alignment_type': 'grand_trine',
                    'planets': list(combo),
                    'description': f"Grand trine: {', '.join(combo)}",
                    'strength': 0.9,
                    'ecliptic_center': None,
                    'span_degrees': None,
                })

    # Compression: all planets within 90 degrees
    all_lons = [pos['ecliptic_lon'] for pos in positions.values()]
    if all_lons:
        all_sorted = sorted(all_lons)
        max_gap = 0
        for i in range(len(all_sorted)):
            gap = (all_sorted[(i + 1) % len(all_sorted)] - all_sorted[i]) % 360
            max_gap = max(max_gap, gap)
        span = 360 - max_gap
        if span < 90:
            alignments.append({
                'timestamp': dt,
                'alignment_type': 'compression',
                'planets': list(positions.keys()),
                'description': f"Planetary compression: {span:.1f}° span",
                'strength': 1.0 - (span / 90.0),
                'ecliptic_center': None,
                'span_degrees': span,
            })

    return alignments


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
    )


def store_positions(conn, positions):
    sql = """
        INSERT INTO planetary_positions 
            (timestamp, planet, ecliptic_lon, ecliptic_lat, distance_au,
             speed_deg_day, is_retrograde, zodiac_sign, zodiac_degree)
        VALUES (%(timestamp)s, %(planet)s, %(ecliptic_lon)s, %(ecliptic_lat)s,
                %(distance_au)s, %(speed_deg_day)s, %(is_retrograde)s,
                %(zodiac_sign)s, %(zodiac_degree)s)
        ON CONFLICT (timestamp, planet) DO UPDATE SET
            ecliptic_lon = EXCLUDED.ecliptic_lon,
            distance_au = EXCLUDED.distance_au,
            speed_deg_day = EXCLUDED.speed_deg_day,
            is_retrograde = EXCLUDED.is_retrograde
    """
    rows = list(positions.values())
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows)
    conn.commit()


def store_aspects(conn, aspects):
    if not aspects:
        return
    sql = """
        INSERT INTO planetary_aspects 
            (timestamp, planet_a, planet_b, aspect_type, exact_angle,
             actual_angle, orb, strength, is_applying)
        VALUES (%(timestamp)s, %(planet_a)s, %(planet_b)s, %(aspect_type)s,
                %(exact_angle)s, %(actual_angle)s, %(orb)s, %(strength)s,
                %(is_applying)s)
        ON CONFLICT (timestamp, planet_a, planet_b, aspect_type) DO UPDATE SET
            actual_angle = EXCLUDED.actual_angle,
            orb = EXCLUDED.orb,
            strength = EXCLUDED.strength
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, aspects)
    conn.commit()


def store_forcing(conn, forcing):
    sql = """
        INSERT INTO planetary_forcing 
            (timestamp, planet_vectors, net_fx, net_fy, net_magnitude,
             net_direction_deg, total_reinforcement, compression_span)
        VALUES (%(timestamp)s, %(planet_vectors)s, %(net_fx)s, %(net_fy)s,
                %(net_magnitude)s, %(net_direction_deg)s, %(total_reinforcement)s,
                %(compression_span)s)
        ON CONFLICT (timestamp) DO UPDATE SET
            net_magnitude = EXCLUDED.net_magnitude,
            net_direction_deg = EXCLUDED.net_direction_deg,
            total_reinforcement = EXCLUDED.total_reinforcement,
            compression_span = EXCLUDED.compression_span
    """
    with conn.cursor() as cur:
        cur.execute(sql, forcing)
    conn.commit()


def store_alignments(conn, alignments):
    if not alignments:
        return
    sql = """
        INSERT INTO planetary_alignments 
            (timestamp, alignment_type, planets, description, strength,
             ecliptic_center, span_degrees)
        VALUES (%(timestamp)s, %(alignment_type)s, %(planets)s, %(description)s,
                %(strength)s, %(ecliptic_center)s, %(span_degrees)s)
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, alignments)
    conn.commit()


# ---------------------------------------------------------------------------
# Telegram Summary
# ---------------------------------------------------------------------------

def get_geometry_summary(conn):
    """Formatted summary of current planetary geometry."""
    lines = []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Latest positions
            cur.execute("""
                SELECT planet, zodiac_sign, zodiac_degree, is_retrograde, distance_au
                FROM planetary_positions
                WHERE timestamp = (SELECT MAX(timestamp) FROM planetary_positions)
                ORDER BY ecliptic_lon
            """)
            positions = cur.fetchall()

            if positions:
                lines.append("🪐 **Planetary Positions**")
                for p in positions:
                    retro = " ℞" if p['is_retrograde'] else ""
                    lines.append(
                        f"  {p['planet']}: {p['zodiac_degree']:.1f}° {p['zodiac_sign']}{retro}"
                    )
                lines.append("")

            # Strong aspects (strength > 0.7)
            cur.execute("""
                SELECT planet_a, planet_b, aspect_type, orb, strength
                FROM planetary_aspects
                WHERE timestamp = (SELECT MAX(timestamp) FROM planetary_aspects)
                  AND strength > 0.7
                ORDER BY strength DESC LIMIT 10
            """)
            aspects = cur.fetchall()

            if aspects:
                lines.append("✨ **Active Aspects**")
                asp_symbols = {
                    'conjunction': '☌', 'opposition': '☍', 'trine': '△',
                    'square': '□', 'sextile': '⚹'
                }
                for a in aspects:
                    sym = asp_symbols.get(a['aspect_type'], '?')
                    lines.append(
                        f"  {a['planet_a']} {sym} {a['planet_b']} "
                        f"(orb {a['orb']:.1f}°, str {a['strength']:.0%})"
                    )
                lines.append("")

            # Latest forcing vector
            cur.execute("""
                SELECT net_magnitude, net_direction_deg, total_reinforcement, 
                       compression_span, timestamp
                FROM planetary_forcing
                ORDER BY timestamp DESC LIMIT 1
            """)
            fv = cur.fetchone()

            if fv:
                # Direction arrow
                d = fv['net_direction_deg']
                arrows = ['→', '↗', '↑', '↖', '←', '↙', '↓', '↘']
                arrow = arrows[int(((d + 22.5) % 360) / 45)]

                sign_idx = int(d / 30)
                sign = ZODIAC[sign_idx] if sign_idx < 12 else '?'

                lines.append("🧭 **Gravitational Vector**")
                lines.append(f"  Direction: {d:.1f}° ({sign}) {arrow}")
                lines.append(f"  Reinforcement: {fv['total_reinforcement']:.0%}")
                lines.append(f"  Compression: {fv['compression_span']:.0f}° span")

            # Recent alignments
            cur.execute("""
                SELECT alignment_type, planets, description, strength
                FROM planetary_alignments
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                ORDER BY strength DESC LIMIT 5
            """)
            aligns = cur.fetchall()
            if aligns:
                lines.append("")
                lines.append("🔮 **Active Patterns**")
                for a in aligns:
                    lines.append(f"  {a['description']}")

    except Exception as e:
        log.error(f"Geometry summary failed: {e}")
        lines.append("Error reading geometry data")

    return "\n".join(lines) if lines else "No planetary data available yet."


# ---------------------------------------------------------------------------
# Backfill
# ---------------------------------------------------------------------------

def backfill_hours(conn, hours=168):
    """Backfill the last N hours of planetary data (default 7 days)."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    count = 0

    for h in range(hours, -1, -1):
        dt = now - timedelta(hours=h)

        # Check if already computed
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM planetary_positions WHERE timestamp = %s LIMIT 1",
                (dt,)
            )
            if cur.fetchone():
                continue

        positions = compute_positions(dt)
        if not positions:
            continue

        aspects = compute_aspects(positions, dt)
        forcing = compute_forcing_vectors(positions, dt)
        alignments = detect_alignments(positions, aspects, dt)

        store_positions(conn, positions)
        store_aspects(conn, aspects)
        store_forcing(conn, forcing)
        if alignments:
            store_alignments(conn, alignments)

        count += 1

    log.info(f"Backfilled {count} hours of planetary data")
    return count


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

_running = True

def _shutdown(signum, frame):
    global _running
    log.info("Shutdown signal received")
    _running = False

signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)


def run():
    global _running
    log.info("Planetary Geometry Engine starting")

    init_ephe()

    conn = get_db()
    try:
        # Initial backfill (7 days)
        log.info("Running initial backfill (7 days)...")
        backfill_hours(conn, 168)
    except Exception as e:
        log.error(f"Backfill failed: {e}")
    finally:
        conn.close()

    last_compute = 0

    while _running:
        now = time.time()
        conn = None

        try:
            if now - last_compute >= COMPUTE_INTERVAL:
                conn = get_db()

                dt = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

                log.info(f"Computing planetary geometry for {dt.isoformat()}")

                positions = compute_positions(dt)
                if positions:
                    aspects = compute_aspects(positions, dt)
                    forcing = compute_forcing_vectors(positions, dt)
                    alignments = detect_alignments(positions, aspects, dt)

                    store_positions(conn, positions)
                    store_aspects(conn, aspects)
                    store_forcing(conn, forcing)
                    if alignments:
                        store_alignments(conn, alignments)

                    log.info(
                        f"Stored: {len(positions)} positions, {len(aspects)} aspects, "
                        f"{len(alignments)} alignments"
                    )

                last_compute = now

        except Exception as e:
            log.error(f"Main loop error: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        for _ in range(30):
            if not _running:
                break
            time.sleep(1)

    log.info("Planetary geometry engine stopped")


if __name__ == "__main__":
    run()
