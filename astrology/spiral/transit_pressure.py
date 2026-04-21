"""
SEN-0006: Spiral Time Walker — Transit Pressure Engine

Computes all major transiting planet aspects to natal chart points
using Swiss Ephemeris. Tracks orb movement over time (applying vs separating).
Stores results in spiral_transit_pressure table.

Transiting planets: Sun, Moon, Mercury, Venus, Mars,
                    Jupiter, Saturn, Uranus, Neptune, Pluto
Natal points:       Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, ASC, MC

Aspect types: Conjunction (0°), Sextile (60°), Square (90°),
              Trine (120°), Opposition (180°)

Thresholds:
  watch    = orb <= 3.0°
  building = orb <= 1.5°
  exact    = orb <= 0.5°
"""

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import psycopg2
import psycopg2.extras

log = logging.getLogger("iris.transit_pressure")

# SEN-0009: natal_generator integration
# Provides a load function that uses the canonical Letter D interface.
# Falls back gracefully if natal_generator is unavailable.
def _load_natal_positions_via_generator(chart_id: int) -> dict:
    """
    Load natal positions from natal_generator.load_natal() by chart_id.
    Returns {planet_name: longitude_float} matching transit_pressure expectations.
    Falls back to {} (caller will use raw Postgres fallback) if anything fails.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='/var/run/postgresql', port=5432,
            database='mythos', user='adge',
        )
        cur = conn.cursor()
        cur.execute('SELECT name FROM astro_natal_charts WHERE chart_id = %s', (chart_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {}
        import sys as _sys
        _sys.path.insert(0, '/opt/mythos')
        from astrology.natal_generator import load_natal
        chart = load_natal(row[0])
        if not chart:
            return {}
        result = {}
        for name, data in chart.get('chart_objects', {}).items():
            result[name] = data.get('longitude', 0.0)
        for pt_name, pt_data in chart.get('chart_points', {}).items():
            result[pt_name] = pt_data.get('longitude', 0.0)
        return result
    except Exception as exc:
        log.warning('natal_generator path failed for chart_id=%d: %s', chart_id, exc)
        return {}

# ── Constants ─────────────────────────────────────────────────────────────────

ASPECTS = {
    "conjunction": 0.0,
    "sextile":     60.0,
    "square":      90.0,
    "trine":       120.0,
    "opposition":  180.0,
}

ASPECT_ORBS = {
    "conjunction": 3.0,
    "sextile":     3.0,
    "square":      3.0,
    "trine":       3.0,
    "opposition":  3.0,
}

THRESHOLDS = [
    (0.5, "exact"),
    (1.5, "building"),
    (3.0, "watch"),
]

TRANSITING_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                      "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

NATAL_POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                "Jupiter", "Saturn", "ASC", "MC"]

# Swiss Ephemeris planet codes
PLANET_CODES = {
    "Sun":     0,
    "Moon":    1,
    "Mercury": 2,
    "Venus":   3,
    "Mars":    4,
    "Jupiter": 5,
    "Saturn":  6,
    "Uranus":  7,
    "Neptune": 8,
    "Pluto":   9,
}

EPHE_PATH = os.environ.get("SE_EPHE_PATH", "/opt/mythos/astrology/ephe")


# ── DB Connection ─────────────────────────────────────────────────────────────

def _get_conn():
    db_url = os.environ.get("DATABASE_URL", "postgresql://adge@localhost/mythos")
    return psycopg2.connect(db_url)


# ── Ephemeris Helpers ─────────────────────────────────────────────────────────

def _get_transiting_positions(target_date: date) -> dict:
    """
    Compute ecliptic longitudes for all transiting planets on target_date.
    Uses noon UT as reference time.
    Returns dict: planet_name -> longitude (0-360)
    """
    try:
        import swisseph as swe
        swe.set_ephe_path(EPHE_PATH)

        # Noon UT
        jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)

        positions = {}
        for planet_name, code in PLANET_CODES.items():
            if planet_name not in TRANSITING_PLANETS:
                continue
            result, _ = swe.calc_ut(jd, code)
            positions[planet_name] = result[0]  # ecliptic longitude

        return positions

    except ImportError:
        log.error("swisseph not installed — cannot compute transits")
        return {}
    except Exception as e:
        log.error(f"transit_pressure._get_transiting_positions error: {e}")
        return {}


def _get_transiting_positions_yesterday(target_date: date) -> dict:
    """Get positions for day before target, used to determine applying/separating."""
    return _get_transiting_positions(target_date - timedelta(days=1))


# ── Natal Position Loader ─────────────────────────────────────────────────────

def _load_natal_positions(chart_id: int) -> dict:
    """
    Load natal ecliptic longitudes from astro_chart_points table.
    Returns dict: point_name -> longitude
    """
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Chart points (planets)
        cur.execute("""
            SELECT name, longitude
            FROM astro_chart_points
            WHERE chart_id = %s
        """, (chart_id,))
        points = {row["name"]: row["longitude"] for row in cur.fetchall()}

        # House cusps for ASC (house 1) and MC (house 10)
        cur.execute("""
            SELECT house_number, longitude
            FROM astro_natal_house_cusps
            WHERE chart_id = %s AND house_number IN (1, 10)
        """, (chart_id,))
        for row in cur.fetchall():
            if row["house_number"] == 1:
                points["ASC"] = row["longitude"]
            elif row["house_number"] == 10:
                points["MC"] = row["longitude"]

        cur.close()
        conn.close()

        # Filter to only the natal points we care about
        return {k: v for k, v in points.items() if k in NATAL_POINTS}

    except Exception as e:
        log.error(f"transit_pressure._load_natal_positions error: {e}")
        return {}


# ── Aspect Math ───────────────────────────────────────────────────────────────

def _normalize_lon(lon: float) -> float:
    """Normalize longitude to 0-360."""
    return lon % 360.0


def _angular_distance(a: float, b: float) -> float:
    """Shortest arc between two ecliptic longitudes."""
    diff = abs(a - b) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _find_aspects(transit_lon: float, natal_lon: float) -> list:
    """
    Check all major aspects between a transiting and natal longitude.
    Returns list of dicts for any aspects within orb.
    """
    results = []
    for aspect_name, exact_angle in ASPECTS.items():
        max_orb = ASPECT_ORBS[aspect_name]

        # Calculate the actual angular distance and how far it is from the exact aspect
        arc = _angular_distance(transit_lon, natal_lon)
        orb = abs(arc - exact_angle)

        # Handle conjunction wraparound (arc near 360 should also check 0)
        if aspect_name == "conjunction":
            orb = min(abs(arc), abs(360.0 - arc))

        if orb <= max_orb:
            results.append({
                "aspect_type":  aspect_name,
                "exact_angle":  exact_angle,
                "orb":          round(orb, 4),
            })

    return results


def _is_applying(transit_lon_today: float, transit_lon_yesterday: float,
                 natal_lon: float, exact_angle: float) -> bool:
    """
    True if the transit is applying (orb getting smaller).
    Compares orb today vs yesterday.
    """
    orb_today = abs(_angular_distance(transit_lon_today, natal_lon) - exact_angle)
    orb_yesterday = abs(_angular_distance(transit_lon_yesterday, natal_lon) - exact_angle)
    return orb_today < orb_yesterday


def _get_threshold(orb: float) -> Optional[str]:
    """Return threshold label for an orb value, or None if outside watch range."""
    for max_orb, label in THRESHOLDS:
        if orb <= max_orb:
            return label
    return None


# ── Main Computation ──────────────────────────────────────────────────────────

def compute_daily_pressure(chart_id: int, target_date: Optional[date] = None) -> list:
    """
    Compute all transit-to-natal aspects for a given date.
    Returns list of aspect dicts (not yet persisted).
    """
    if target_date is None:
        target_date = date.today()

    natal = _load_natal_positions(chart_id)
    if not natal:
        log.error(f"No natal positions found for chart_id={chart_id}")
        return []

    transit_today = _get_transiting_positions(target_date)
    transit_yesterday = _get_transiting_positions_yesterday(target_date)

    if not transit_today:
        log.error("Could not compute transiting positions")
        return []

    results = []

    for t_planet, t_lon in transit_today.items():
        t_lon_yesterday = transit_yesterday.get(t_planet)

        for n_point, n_lon in natal.items():
            aspects = _find_aspects(t_lon, n_lon)
            for asp in aspects:
                threshold = _get_threshold(asp["orb"])
                if threshold is None:
                    continue  # outside watch range

                applying = False
                if t_lon_yesterday is not None:
                    applying = _is_applying(t_lon, t_lon_yesterday, n_lon, asp["exact_angle"])

                results.append({
                    "chart_id":          chart_id,
                    "computed_date":     target_date,
                    "transiting_planet": t_planet,
                    "natal_point":       n_point,
                    "aspect_type":       asp["aspect_type"],
                    "exact_angle":       asp["exact_angle"],
                    "orb":               asp["orb"],
                    "applying":          applying,
                    "transit_lon":       round(t_lon, 4),
                    "natal_lon":         round(n_lon, 4),
                    "threshold_level":   threshold,
                })

    log.info(f"Computed {len(results)} transit aspects for chart {chart_id} on {target_date}")
    return results


def persist_pressure(aspects: list) -> int:
    """
    Upsert transit pressure records into DB.
    Returns count of records written.
    """
    if not aspects:
        return 0

    try:
        conn = _get_conn()
        cur = conn.cursor()

        for asp in aspects:
            cur.execute("""
                INSERT INTO spiral_transit_pressure
                    (chart_id, computed_date, transiting_planet, natal_point,
                     aspect_type, exact_angle, orb, applying,
                     transit_lon, natal_lon, threshold_level)
                VALUES
                    (%(chart_id)s, %(computed_date)s, %(transiting_planet)s, %(natal_point)s,
                     %(aspect_type)s, %(exact_angle)s, %(orb)s, %(applying)s,
                     %(transit_lon)s, %(natal_lon)s, %(threshold_level)s)
                ON CONFLICT (chart_id, computed_date, transiting_planet, natal_point, aspect_type)
                DO UPDATE SET
                    orb             = EXCLUDED.orb,
                    applying        = EXCLUDED.applying,
                    transit_lon     = EXCLUDED.transit_lon,
                    threshold_level = EXCLUDED.threshold_level
            """, asp)

        conn.commit()
        cur.close()
        conn.close()
        return len(aspects)

    except Exception as e:
        log.error(f"transit_pressure.persist_pressure error: {e}")
        return 0


def run_daily_pressure(chart_id: int, target_date: Optional[date] = None) -> list:
    """
    Full pipeline: compute + persist. Returns the aspect list.
    Call this once per day (from morning brief or a cron/worker).
    """
    aspects = compute_daily_pressure(chart_id, target_date)
    count = persist_pressure(aspects)
    log.info(f"Persisted {count} transit pressure records for chart {chart_id}")
    return aspects


def get_todays_pressure(chart_id: int, target_date: Optional[date] = None,
                        min_threshold: str = "watch") -> list:
    """
    Fetch today's transit pressure from DB.
    min_threshold: 'watch' | 'building' | 'exact'
    """
    if target_date is None:
        target_date = date.today()

    threshold_order = {"watch": 0, "building": 1, "exact": 2}
    min_level = threshold_order.get(min_threshold, 0)

    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT transiting_planet, natal_point, aspect_type,
                   orb, applying, threshold_level
            FROM spiral_transit_pressure
            WHERE chart_id = %s
              AND computed_date = %s
            ORDER BY
                CASE threshold_level WHEN 'exact' THEN 0 WHEN 'building' THEN 1 ELSE 2 END,
                orb ASC
        """, (chart_id, target_date))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Filter by minimum threshold
        result = []
        for row in rows:
            level = threshold_order.get(row["threshold_level"], 0)
            if level >= min_level:
                result.append(dict(row))
        return result

    except Exception as e:
        log.error(f"transit_pressure.get_todays_pressure error: {e}")
        return []


def format_pressure_brief(aspects: list, max_items: int = 6) -> str:
    """
    Format transit pressure as a compact natural-language summary
    for inclusion in Iris's morning brief.
    """
    if not aspects:
        return "No significant transits in orb today."

    exact   = [a for a in aspects if a["threshold_level"] == "exact"]
    building = [a for a in aspects if a["threshold_level"] == "building"]
    watch    = [a for a in aspects if a["threshold_level"] == "watch"]

    lines = []

    def _fmt(asp: dict) -> str:
        direction = "applying" if asp["applying"] else "separating"
        return (f"{asp['transiting_planet']} {asp['aspect_type']} natal {asp['natal_point']} "
                f"({asp['orb']:.1f}° orb, {direction})")

    if exact:
        lines.append("⚡ Exact / Peak:")
        for a in exact[:3]:
            lines.append(f"  · {_fmt(a)}")

    if building:
        lines.append("🔥 Building:")
        for a in building[:3]:
            lines.append(f"  · {_fmt(a)}")

    if watch and not exact and not building:
        lines.append("👁 In Orb:")
        for a in watch[:max_items]:
            lines.append(f"  · {_fmt(a)}")

    return "\n".join(lines)
