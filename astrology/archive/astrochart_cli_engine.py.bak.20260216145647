#!/usr/bin/env python3
"""
============================================================================
 ASTROCHART CLI ENGINE v2.0
 Comprehensive Geocentric Tropical Placidus Natal Chart Generator

 Author: Ka'tuar'el / Mythos System

 WHAT'S NEW vs v1:
   - compute_chart() fully implemented (was missing)
   - Eris (136199), True Node, South Node added
   - Arabic Parts: Fortune, Spirit, Eros, Marriage, Death, Commerce,
                   Courage, Fatality, Passion (with day/night sect reversal)
   - Essential Dignities: Domicile, Exaltation, Detriment, Fall, Peregrine
   - Sect: Day/Night with sect light/benefic/malefic assignments
   - Chart Ruler: Traditional + Modern, with ruler sign & house
   - Dispositor Chain: Full chain + final dispositors + mutual receptions
   - Balance: Element, Modality, Polarity tallies with dominant
   - Retrograde Summary: Structured list
   - Aspect Motion: Applying / Separating / Exact (partile)
   - Full 18-aspect orb overrides (Decile, Tridecile, Quindecile, Septile family)
   - Ephemeris path auto-detection with Moshier fallback
   - assign_house() used consistently for all bodies

 PRESERVED (drop-in compatible):
   - generate_natal_chart() return structure (all original keys + new ones)
   - generate_natal_report() signature
   - compute_aspects() with axes, alias_map, orb_overrides
   - compute_fixed_star_conjunctions()
   - run_geometry_audit() with full composition policy
   - All imports from astrochart_cli_geometry unchanged
   - CLI tool compatibility (astrochart_cli_tool.py works unchanged)

 Dependencies:
   pip install pyswisseph pytz timezonefinder geopy pandas
============================================================================
"""

import swisseph as swe
import datetime
import json
import os
import math
from itertools import combinations
from typing import Dict, List, Tuple, Optional, Any

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

try:
    import pandas as pd
except ImportError:
    pd = None

from astrochart_cli_geometry import (
    detect_geometric_patterns_with_policy,
    detect_grand_trines,
    detect_t_squares,
    detect_yods,
    detect_mystic_rectangles,
    detect_boomerangs,
    detect_cradles,
    detect_star_of_david,
    detect_kites,
)


# ============================================================================
#  CONFIGURATION
# ============================================================================

HOUSE_SYSTEM = "Placidus"
ZODIAC_TYPE = "Tropical"
EPHEMERIS = "Swiss Ephemeris"

INCLUDED_OBJECTS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Chiron", "Ceres", "Pallas", "Juno",
    "Vesta", "Eris", "Lilith", "Mean Node", "True Node",
]

AXIS_POINTS = ["Ascendant", "Midheaven", "Descendant", "IC"]

# Swiss Ephemeris body IDs (standard bodies)
OBJECT_CODES = {
    "Sun":       swe.SUN,
    "Moon":      swe.MOON,
    "Mercury":   swe.MERCURY,
    "Venus":     swe.VENUS,
    "Mars":      swe.MARS,
    "Jupiter":   swe.JUPITER,
    "Saturn":    swe.SATURN,
    "Uranus":    swe.URANUS,
    "Neptune":   swe.NEPTUNE,
    "Pluto":     swe.PLUTO,
    "Chiron":    swe.CHIRON,
    "Lilith":    swe.MEAN_APOG,       # Black Moon Lilith (mean apogee)
    "Mean Node": swe.MEAN_NODE,
    "True Node": swe.TRUE_NODE,
}

# Asteroids via SE_AST_OFFSET + catalogue number
ASTEROID_CODES = {
    "Ceres":  1,
    "Pallas": 2,
    "Juno":   3,
    "Vesta":  4,
    "Eris":   136199,
}

HOUSE_SYSTEM_CODES = {
    "Placidus":       b"P",
    "Whole Sign":     b"W",
    "Koch":           b"K",
    "Regiomontanus":  b"R",
    "Campanus":       b"C",
    "Equal":          b"E",
    # Back-compat upper-case keys from v1
    "PLACIDUS":       b"P",
    "WHOLE SIGN":     b"W",
    "KOCH":           b"K",
    "REGIOMONTANUS":  b"R",
    "CAMPANUS":       b"C",
    "EQUAL":          b"E",
}

# ---------- Zodiac Reference Data ----------

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}

MODALITIES = {
    "Aries": "Cardinal", "Taurus": "Fixed", "Gemini": "Mutable", "Cancer": "Cardinal",
    "Leo": "Fixed", "Virgo": "Mutable", "Libra": "Cardinal", "Scorpio": "Fixed",
    "Sagittarius": "Mutable", "Capricorn": "Cardinal", "Aquarius": "Fixed", "Pisces": "Mutable",
}

POLARITIES = {
    "Aries": "Positive", "Taurus": "Negative", "Gemini": "Positive", "Cancer": "Negative",
    "Leo": "Positive", "Virgo": "Negative", "Libra": "Positive", "Scorpio": "Negative",
    "Sagittarius": "Positive", "Capricorn": "Negative", "Aquarius": "Positive", "Pisces": "Negative",
}

# Traditional rulerships
RULERSHIPS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

MODERN_RULERSHIPS = {
    "Scorpio": "Pluto", "Aquarius": "Uranus", "Pisces": "Neptune",
}

# Exaltations: planet -> (sign, exact_degree)
EXALTATIONS = {
    "Sun": ("Aries", 19), "Moon": ("Taurus", 3), "Mercury": ("Virgo", 15),
    "Venus": ("Pisces", 27), "Mars": ("Capricorn", 28), "Jupiter": ("Cancer", 15),
    "Saturn": ("Libra", 21),
}

# Detriment: planet -> list of signs
DETRIMENTS = {
    "Sun": ["Aquarius"], "Moon": ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"], "Venus": ["Aries", "Scorpio"],
    "Mars": ["Taurus", "Libra"], "Jupiter": ["Gemini", "Virgo"],
    "Saturn": ["Cancer", "Leo"],
}

# Fall: planet -> sign
FALLS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mercury": "Pisces",
    "Venus": "Virgo", "Mars": "Cancer", "Jupiter": "Capricorn",
    "Saturn": "Aries",
}


# ============================================================================
#  SWISS EPHEMERIS INITIALIZATION
# ============================================================================

_EPHE_CANDIDATES = [
    os.environ.get("SWISSEPH_PATH", ""),
    "/dev/astrology/swisseph/ephe",          # Adge laptop
    "/opt/swisseph/ephe",                    # AWS server
    "/home/adge/dev/astrology/swisseph/ephe",# Alt laptop path
    "/usr/share/swisseph/ephe",              # Linux package
    "/usr/share/ephe",                       # Alt Linux
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ephe"),
]

SE_EPHE_PATH = "(Moshier built-in)"
for _p in _EPHE_CANDIDATES:
    if _p and os.path.isdir(_p):
        swe.set_ephe_path(_p)
        SE_EPHE_PATH = _p
        break
else:
    # Moshier fallback (built-in, less accurate for minor asteroids)
    swe.set_ephe_path(None)


# ============================================================================
#  UTILITY FUNCTIONS
# ============================================================================

def get_sign(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude."""
    return ZODIAC_SIGNS[int(longitude % 360 // 30)]


def deg_min(longitude: float) -> str:
    """Format longitude as degrees and arc-minutes within sign."""
    in_sign = longitude % 30
    d = int(in_sign)
    m = int((in_sign - d) * 60)
    return f"{d:02d}\u00b0{m:02d}'"


def deg_min_sec(longitude: float) -> str:
    """Format longitude as degrees, minutes, seconds within sign."""
    in_sign = longitude % 30
    d = int(in_sign)
    rem = (in_sign - d) * 60
    m = int(rem)
    s = int((rem - m) * 60)
    return f"{d:02d}\u00b0{m:02d}'{s:02d}\""


def format_full_position(longitude: float) -> str:
    """Format as 'DD\u00b0MM' Sign'."""
    return f"{deg_min(longitude)} {get_sign(longitude)}"


def normalize_degrees(deg: float) -> float:
    """Normalize to 0\u2013360."""
    return deg % 360.0


def angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes."""
    diff = abs(normalize_degrees(lon1) - normalize_degrees(lon2))
    return min(diff, 360.0 - diff)


def parse_orb_to_decimal_safe(value, default=1.0):
    try:
        return float(value)
    except Exception:
        return default


def assign_house(longitude: float, cusps: list) -> int:
    """
    Determine which Placidus house a longitude falls in.
    cusps: list of 12 cusp longitudes (index 0 = House 1).
    """
    lon = normalize_degrees(longitude)
    for i in range(12):
        cusp_start = normalize_degrees(cusps[i])
        cusp_end = normalize_degrees(cusps[(i + 1) % 12])
        if cusp_start < cusp_end:
            if cusp_start <= lon < cusp_end:
                return i + 1
        else:
            # Wraps across 0\u00b0 Aries
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 1  # fallback


# ============================================================================
#  LOCATION & TIMEZONE
# ============================================================================

def get_timezone_and_coords(city: str, region: str, country: str, date_str: str):
    """
    Geocode a place and determine timezone.
    Returns: (lat, lon, offset_hours, timezone_str)
    """
    geolocator = Nominatim(user_agent="mythos_astro_chart")
    tf = TimezoneFinder()
    query = f"{city}, {region}, {country}" if region else f"{city}, {country}"
    location = geolocator.geocode(query)
    if not location:
        raise ValueError(f"Location not found: {query}")
    lat, lon = location.latitude, location.longitude
    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    if not timezone_str:
        raise ValueError(f"Could not determine timezone for {lat}, {lon}")
    tz = pytz.timezone(timezone_str)
    local_dt = tz.localize(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M"))
    offset_hours = local_dt.utcoffset().total_seconds() / 3600
    return lat, lon, offset_hours, timezone_str


def resolve_location_and_time(city, region, country, date_str, latitude=None, longitude=None):
    """
    Unified location/time resolver. Uses provided lat/lon or geocodes.
    Returns (lat, lon, tz_obj, localized_datetime).
    """
    if latitude is not None and longitude is not None:
        lat, lon = float(latitude), float(longitude)
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        if not tz_str:
            tz_str = "America/New_York" if (country or "").upper() in ("USA", "US") else "UTC"
        tz = pytz.timezone(tz_str)
        dt_naive = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        dt_local = tz.localize(dt_naive)
        return lat, lon, tz, dt_local
    else:
        lat, lon, _, tz_str = get_timezone_and_coords(city, region, country, date_str)
        tz = pytz.timezone(tz_str)
        dt_naive = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        dt_local = tz.localize(dt_naive)
        return lat, lon, tz, dt_local


# ============================================================================
#  CORE CHART COMPUTATION  (was missing in v1)
# ============================================================================

def compute_chart(lat: float, lon: float, dt_local, house_system: str = "Placidus"):
    """
    Compute planetary positions, house cusps, and angles via Swiss Ephemeris.

    Args:
        lat: Geographic latitude
        lon: Geographic longitude
        dt_local: Timezone-aware datetime
        house_system: House system name (default: Placidus)

    Returns:
        (positions, houses, axes)
        positions : dict  {name: {Longitude, Latitude, Distance, Speed, Sign, Retrograde, House, ...}}
        houses    : dict  {1: {Cusp, Sign, DegMin, Full}, 2: {...}, ...}
        axes      : dict  {Ascendant: lon, Midheaven: lon, Descendant: lon, IC: lon, Vertex: lon, ARMC: lon}
    """
    # --- UTC conversion ---
    dt_utc = dt_local.astimezone(pytz.utc)
    decimal_hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, decimal_hour, swe.GREG_CAL)

    # --- House cusps ---
    hsys = HOUSE_SYSTEM_CODES.get(house_system, b"P")
    cusps_raw, ascmc = swe.houses(jd, lat, lon, hsys)

    cusp_list = [float(cusps_raw[i]) for i in range(12)]

    houses = {}
    for i in range(12):
        c = cusp_list[i]
        houses[i + 1] = {
            "Cusp": round(c, 6),
            "Sign": get_sign(c),
            "DegMin": deg_min(c),
            "Full": format_full_position(c),
        }

    axes = {
        "Ascendant":  round(float(ascmc[0]), 6),
        "Midheaven":  round(float(ascmc[1]), 6),
        "Descendant": round(normalize_degrees(float(ascmc[0]) + 180), 6),
        "IC":         round(normalize_degrees(float(ascmc[1]) + 180), 6),
        "Vertex":     round(float(ascmc[3]), 6),
        "ARMC":       round(float(ascmc[2]), 6),
    }

    # --- Planetary/point positions ---
    positions = {}
    calc_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    # Standard bodies
    for obj_name, planet_id in OBJECT_CODES.items():
        try:
            pos, _ = swe.calc_ut(jd, planet_id, calc_flags)
            lon_ = float(pos[0])
            lat_ = float(pos[1])
            dist = float(pos[2])
            speed = float(pos[3])

            positions[obj_name] = {
                "Longitude": round(lon_, 6),
                "Latitude": round(lat_, 6),
                "Distance": round(dist, 8),
                "Speed": round(speed, 6),
                "Sign": get_sign(lon_),
                "DegMin": deg_min(lon_),
                "Full": format_full_position(lon_),
                "Retrograde": speed < 0.0,
                "House": assign_house(lon_, cusp_list),
            }
        except Exception as e:
            print(f"  WARNING: Could not calculate {obj_name}: {e}")

    # Asteroids (Ceres, Pallas, Juno, Vesta, Eris)
    for obj_name, ast_num in ASTEROID_CODES.items():
        try:
            ast_id = swe.AST_OFFSET + ast_num
            pos, _ = swe.calc_ut(jd, ast_id, calc_flags)
            lon_ = float(pos[0])
            lat_ = float(pos[1])
            dist = float(pos[2])
            speed = float(pos[3])

            positions[obj_name] = {
                "Longitude": round(lon_, 6),
                "Latitude": round(lat_, 6),
                "Distance": round(dist, 8),
                "Speed": round(speed, 6),
                "Sign": get_sign(lon_),
                "DegMin": deg_min(lon_),
                "Full": format_full_position(lon_),
                "Retrograde": speed < 0.0,
                "House": assign_house(lon_, cusp_list),
            }
        except Exception as e:
            print(f"  WARNING: Could not calculate asteroid {obj_name} ({ast_num}): {e}")

    # --- South Node (derived: opposite Mean Node) ---
    if "Mean Node" in positions:
        nn_lon = positions["Mean Node"]["Longitude"]
        sn_lon = normalize_degrees(nn_lon + 180)
        positions["South Node"] = {
            "Longitude": round(sn_lon, 6),
            "Latitude": round(-positions["Mean Node"]["Latitude"], 6),
            "Distance": positions["Mean Node"]["Distance"],
            "Speed": positions["Mean Node"]["Speed"],
            "Sign": get_sign(sn_lon),
            "DegMin": deg_min(sn_lon),
            "Full": format_full_position(sn_lon),
            "Retrograde": positions["Mean Node"]["Retrograde"],
            "House": assign_house(sn_lon, cusp_list),
        }

    return positions, houses, axes


# ============================================================================
#  ESSENTIAL DIGNITIES
# ============================================================================

def compute_dignities(positions: dict) -> dict:
    """
    Essential dignities for the seven traditional planets.
    Returns {planet: {"Status": [...], "Sign": str}}.
    """
    dignities = {}
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        if name not in positions:
            continue
        sign = positions[name]["Sign"]
        statuses = []

        # Domicile
        if sign in [s for s, r in RULERSHIPS.items() if r == name]:
            statuses.append("Domicile")

        # Exaltation
        if name in EXALTATIONS and sign == EXALTATIONS[name][0]:
            statuses.append("Exaltation")

        # Detriment
        if name in DETRIMENTS and sign in DETRIMENTS[name]:
            statuses.append("Detriment")

        # Fall
        if name in FALLS and sign == FALLS[name]:
            statuses.append("Fall")

        if not statuses:
            statuses.append("Peregrine")

        dignities[name] = {"Status": statuses, "Sign": sign}

    return dignities


# ============================================================================
#  SECT (DAY / NIGHT)
# ============================================================================

def compute_sect(positions: dict, axes: dict) -> dict:
    """Day/Night chart with sect assignments."""
    if "Sun" not in positions:
        return {"Sect": "Unknown"}

    is_day = 7 <= positions["Sun"]["House"] <= 12

    if is_day:
        return {
            "Sect": "Day",
            "Sect Light": "Sun", "Sect Benefic": "Jupiter", "Sect Malefic": "Saturn",
            "Contra Light": "Moon", "Contra Benefic": "Venus", "Contra Malefic": "Mars",
        }
    else:
        return {
            "Sect": "Night",
            "Sect Light": "Moon", "Sect Benefic": "Venus", "Sect Malefic": "Mars",
            "Contra Light": "Sun", "Contra Benefic": "Jupiter", "Contra Malefic": "Saturn",
        }


# ============================================================================
#  CHART RULER & DISPOSITOR CHAIN
# ============================================================================

def compute_chart_ruler(positions: dict, axes: dict) -> dict:
    """Chart ruler from ASC sign (traditional + modern)."""
    asc_lon = axes.get("Ascendant", 0)
    asc_sign = get_sign(asc_lon)
    trad = RULERSHIPS.get(asc_sign, "Unknown")
    modern = MODERN_RULERSHIPS.get(asc_sign, None)

    result = {"Ascendant Sign": asc_sign, "Traditional Ruler": trad}
    if trad in positions:
        result["Traditional Ruler Sign"] = positions[trad]["Sign"]
        result["Traditional Ruler House"] = positions[trad]["House"]
    if modern:
        result["Modern Ruler"] = modern
        if modern in positions:
            result["Modern Ruler Sign"] = positions[modern]["Sign"]
            result["Modern Ruler House"] = positions[modern]["House"]
    return result


def compute_dispositor_chain(positions: dict) -> dict:
    """Dispositor chain, final dispositors, mutual receptions."""
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars",
               "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    chain = {}
    for p in planets:
        if p in positions:
            chain[p] = RULERSHIPS.get(positions[p]["Sign"], p)

    final = [p for p, r in chain.items() if p == r]

    mutual = []
    done = set()
    for p1 in chain:
        for p2 in chain:
            if p1 < p2 and chain.get(p1) == p2 and chain.get(p2) == p1:
                key = tuple(sorted([p1, p2]))
                if key not in done:
                    mutual.append(list(key))
                    done.add(key)

    return {"Chain": chain, "Final Dispositors": final, "Mutual Receptions": mutual}


# ============================================================================
#  BALANCE (Element / Modality / Polarity)
# ============================================================================

def compute_balance(positions: dict, axes: dict) -> dict:
    """Tally element, modality, polarity across planets + ASC + MC."""
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    polarities = {"Positive": 0, "Negative": 0}

    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars",
                 "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
        if name in positions:
            s = positions[name]["Sign"]
            elements[ELEMENTS[s]] += 1
            modalities[MODALITIES[s]] += 1
            polarities[POLARITIES[s]] += 1

    for angle in ("Ascendant", "Midheaven"):
        if angle in axes:
            s = get_sign(axes[angle])
            elements[ELEMENTS[s]] += 1
            modalities[MODALITIES[s]] += 1
            polarities[POLARITIES[s]] += 1

    return {
        "Elements": elements,     "Dominant Element": max(elements, key=elements.get),
        "Modalities": modalities, "Dominant Modality": max(modalities, key=modalities.get),
        "Polarities": polarities, "Dominant Polarity": max(polarities, key=polarities.get),
    }


# ============================================================================
#  ARABIC PARTS (LOTS)
# ============================================================================

def compute_arabic_parts(positions: dict, axes: dict, houses: dict, sect: dict) -> dict:
    """
    Hellenistic Arabic Parts with proper day/night reversal.

    Part of Fortune  = ASC + Moon - Sun  (day) / ASC + Sun - Moon  (night)
    Part of Spirit   = ASC + Sun - Moon  (day) / ASC + Moon - Sun  (night)
    Part of Eros     = ASC + Venus - Spirit
    Part of Marriage  = ASC + DSC - Venus
    Part of Death     = ASC + 8th cusp - Moon
    Part of Commerce  = ASC + Mercury - Sun
    Part of Courage   = ASC + Mars - Fortune
    Part of Fatality  = ASC + Saturn - Sun
    Part of Passion   = ASC + Mars - Sun
    """
    parts = {}
    asc = axes.get("Ascendant", 0)
    dsc = axes.get("Descendant", 0)
    sun = positions.get("Sun", {}).get("Longitude", 0)
    moon = positions.get("Moon", {}).get("Longitude", 0)
    venus = positions.get("Venus", {}).get("Longitude", 0)
    mars = positions.get("Mars", {}).get("Longitude", 0)
    mercury = positions.get("Mercury", {}).get("Longitude", 0)
    saturn = positions.get("Saturn", {}).get("Longitude", 0)
    h8 = houses.get(8, {})
    h8_cusp = h8.get("Cusp", 0) if isinstance(h8, dict) else float(h8) if h8 else 0

    is_day = sect.get("Sect", "Day") == "Day"
    cusp_list = [houses.get(i, {}).get("Cusp", 0) if isinstance(houses.get(i), dict) else 0
                 for i in range(1, 13)]

    def _store(name, lon_raw, formula):
        lon = normalize_degrees(lon_raw)
        parts[name] = {
            "Longitude": round(lon, 6),
            "Sign": get_sign(lon),
            "DegMin": deg_min(lon),
            "Full": format_full_position(lon),
            "House": assign_house(lon, cusp_list),
            "Formula": formula,
        }
        return lon

    # Fortune & Spirit (sect-reversed pair)
    if is_day:
        pof = _store("Part of Fortune", asc + moon - sun, "ASC + Moon - Sun (day)")
        pos = _store("Part of Spirit",  asc + sun - moon, "ASC + Sun - Moon (day)")
    else:
        pof = _store("Part of Fortune", asc + sun - moon, "ASC + Sun - Moon (night)")
        pos = _store("Part of Spirit",  asc + moon - sun, "ASC + Moon - Sun (night)")

    _store("Part of Eros",     asc + venus - pos,    "ASC + Venus - Part of Spirit")
    _store("Part of Marriage",  asc + dsc - venus,    "ASC + DSC - Venus")
    _store("Part of Death",     asc + h8_cusp - moon, "ASC + 8th cusp - Moon")
    _store("Part of Commerce",  asc + mercury - sun,  "ASC + Mercury - Sun")
    _store("Part of Courage",   asc + mars - pof,     "ASC + Mars - Part of Fortune")
    _store("Part of Fatality",  asc + saturn - sun,   "ASC + Saturn - Sun")
    _store("Part of Passion",   asc + mars - sun,     "ASC + Mars - Sun")

    return parts


# ============================================================================
#  RETROGRADE SUMMARY
# ============================================================================

def compute_retrograde_summary(positions: dict) -> list:
    return [
        {"Object": n, "Sign": d["Sign"], "House": d["House"], "Longitude": d["Longitude"]}
        for n, d in positions.items() if d.get("Retrograde")
    ]


# ============================================================================
#  ASPECT CALCULATION
# ============================================================================

def compute_aspects(
    positions,
    aspect_definitions,
    default_orb=6,
    axes=None,
    include_axes=False,
    alias_map=None,
    orb_overrides=None,
):
    """
    All pairwise aspects between chart objects (and optionally angles).
    Now includes Applying/Separating/Exact motion detection.
    """
    augmented = {k: dict(v) for k, v in positions.items()}

    if include_axes and axes:
        for key in ("Ascendant", "Midheaven", "Descendant", "IC"):
            if key in axes:
                lon = float(axes[key])
                augmented[key] = {
                    "Longitude": lon, "Latitude": 0.0,
                    "Sign": get_sign(lon), "Retrograde": False,
                    "House": None, "Speed": 0.0,
                }

    names = list(augmented.keys())

    def _get_angle(name):
        spec = aspect_definitions.get(name)
        if spec is None:
            return None
        return float(spec.get("Angle", spec)) if isinstance(spec, dict) else float(spec)

    def _get_desc(name):
        spec = aspect_definitions.get(name, {})
        return spec.get("Description", "") if isinstance(spec, dict) else ""

    def _get_orb(name):
        if orb_overrides and name in orb_overrides:
            return float(orb_overrides[name])
        spec = aspect_definitions.get(name, {})
        if isinstance(spec, dict) and "Orb" in spec:
            return float(spec["Orb"])
        return float(default_orb)

    aspects = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            lon1 = float(augmented[a]["Longitude"])
            lon2 = float(augmented[b]["Longitude"])

            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff

            for asp_name in aspect_definitions:
                angle = _get_angle(asp_name)
                if angle is None:
                    continue
                orb_allow = _get_orb(asp_name)
                delta = abs(diff - angle)
                if delta <= orb_allow + 1e-9:
                    out_a = alias_map.get(a, a) if alias_map else a
                    out_b = alias_map.get(b, b) if alias_map else b

                    # Motion detection
                    speed_a = augmented[a].get("Speed", 0) or 0
                    speed_b = augmented[b].get("Speed", 0) or 0
                    if delta < 0.5:
                        motion = "Exact (partile)"
                    elif abs(speed_a) > abs(speed_b):
                        motion = "Applying"
                    else:
                        motion = "Separating"

                    aspects.append({
                        "Object 1": out_a,
                        "Object 2": out_b,
                        "Aspect": asp_name,
                        "Angle": angle,
                        "Exact Difference": round(diff, 4),
                        "Orb": round(delta, 4),
                        "Motion": motion,
                        "Description": _get_desc(asp_name),
                    })

    aspects.sort(key=lambda x: x["Orb"])
    return aspects


# ============================================================================
#  FIXED STAR CONJUNCTIONS
# ============================================================================

def _load_star_friendly_map():
    return {
        "alpha Leo": "Regulus", "alpha CrB": "Alphecca",
        "eta Oph": "Sabik", "epsilon Ori": "Alnilam",
        "zeta Ori": "Alnitak", "delta Crv": "Algorab",
        "alpha Vir": "Spica", "alpha Sco": "Antares",
        "alpha Tau": "Aldebaran", "alpha Gem": "Pollux",
        "beta Gem": "Castor", "alpha CMa": "Sirius",
        "alpha Aql": "Altair", "alpha Lyr": "Vega",
        "alpha Ori": "Betelgeuse", "alpha CMi": "Procyon",
        "alpha Boo": "Arcturus", "alpha UMi": "Polaris",
    }


def compute_fixed_star_conjunctions(positions, star_csv, orb=1.0, include_axes=False, axes=None):
    """Find fixed-star conjunctions within orb degrees."""
    if pd is None:
        print("  WARNING: pandas not available, skipping fixed star conjunctions")
        return []
    if not os.path.exists(star_csv):
        print(f"  WARNING: Fixed star CSV not found: {star_csv}")
        return []

    df = pd.read_csv(star_csv)
    df.columns = [c.strip().lower() for c in df.columns]

    lon_col = next((c for c in ("decimal long", "longitude", "long") if c in df.columns), None)
    if lon_col is None:
        print("  WARNING: No longitude column in fixed star CSV")
        return []

    friendly_map = _load_star_friendly_map()

    def _star_id(row):
        for c in ("star", "name", "id", "designation"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        return "Unknown"

    def _star_friendly(row, fallback):
        for c in ("proper", "proper name", "traditional", "friendly", "popular",
                   "common", "english", "name_clean"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        return friendly_map.get(fallback, fallback)

    def _constellation(row):
        for c in ("constellation", "const", "abbr"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        return None

    test_points = {obj: float(d["Longitude"]) for obj, d in positions.items()}
    if include_axes and axes:
        for k in ("Ascendant", "Midheaven", "Descendant", "IC"):
            if k in axes:
                test_points[k] = float(axes[k])

    out = []
    for obj, obj_lon in test_points.items():
        for _, row in df.iterrows():
            star_lon = row[lon_col]
            if pd.isna(star_lon):
                continue
            try:
                star_lon = float(star_lon)
            except Exception:
                continue
            d = abs(obj_lon - star_lon)
            if d > 180:
                d = 360 - d
            if d <= float(orb):
                sid = _star_id(row)
                item = {
                    "Object": obj, "Longitude": obj_lon,
                    "Star": sid, "Star_Friendly": _star_friendly(row, sid),
                    "Star_Longitude": star_lon, "Orb": round(d, 4),
                }
                const = _constellation(row)
                if const:
                    item["Constellation"] = const
                if "significance" in df.columns and pd.notna(row["significance"]):
                    item["Significance"] = str(row["significance"]).strip()
                out.append(item)
    return out


# ============================================================================
#  GEOMETRY AUDIT
# ============================================================================

def run_geometry_audit(
    chart_data,
    aspect_defs=None,
    print_report=True,
    include_modern=True,
    include_minor=True,
    min_core=2,
    max_minor=1,
    include_axes=False,
    include_nodes=False,
):
    """Compare detector outputs vs canonical enumeration from the aspect list."""
    aspects_raw = chart_data.get("chart_aspects", [])

    CORE = {"Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"}
    ANGLES = {"Ascendant","Descendant","Midheaven","IC"}
    NODES = {"Mean Node","True Node","North Node","South Node","Node"}
    MINOR = {"Ceres","Pallas","Juno","Vesta","Lilith","Part of Fortune","Vertex","Anti-Vertex"}
    NORM = {"True Node":"Mean Node","North Node":"Mean Node","Node":"Mean Node"}

    def _n(x): return NORM.get(x, x)

    a_angles = include_modern or include_axes
    a_nodes  = include_modern or include_nodes

    ALLOWED = set(CORE)
    if include_minor: ALLOWED |= MINOR
    if a_angles:      ALLOWED |= ANGLES
    if a_nodes:       ALLOWED |= NODES; ALLOWED.add("Mean Node")
    if include_modern: ALLOWED.add("Chiron")

    def _comp_ok(pts):
        return sum(1 for p in pts if p in CORE) >= min_core and \
               sum(1 for p in pts if p in MINOR) <= max_minor

    def _filter(aspects_):
        out = []
        for a in aspects_:
            x, y = _n(a["Object 1"]), _n(a["Object 2"])
            if x in ALLOWED and y in ALLOWED:
                aa = dict(a); aa["Object 1"] = x; aa["Object 2"] = y; out.append(aa)
        return out

    aspects = _filter(aspects_raw)

    def _np(a, b): return tuple(sorted([a, b]))
    def _idx(asp):
        m = {}
        for a in asp:
            m.setdefault(_np(a["Object 1"], a["Object 2"]), set()).add(a["Aspect"])
        return m
    def _h(m, p, t): return t in m.get(_np(*p), ())
    def _ab(m):
        s = set()
        for x, y in m: s.add(x); s.add(y)
        return s

    # Enumerators
    def _gt(B, m):
        o = set()
        for a,b,c in combinations(sorted(B),3):
            if _h(m,(a,b),"Trine") and _h(m,(b,c),"Trine") and _h(m,(a,c),"Trine"):
                o.add((a,b,c))
        return o

    def _ts(B, m):
        o = set()
        for a,b,c in combinations(sorted(B),3):
            for ap in (a,b,c):
                bs = sorted({a,b,c}-{ap})
                if _h(m,tuple(bs),"Opposition") and _h(m,(ap,bs[0]),"Square") and _h(m,(ap,bs[1]),"Square"):
                    o.add(tuple(sorted([a,b,c]))); break
        return o

    def _yd(B, m):
        o = set()
        for a,b,c in combinations(sorted(B),3):
            for ap in (a,b,c):
                bs = sorted({a,b,c}-{ap})
                if _h(m,tuple(bs),"Sextile") and _h(m,(ap,bs[0]),"Quincunx") and _h(m,(ap,bs[1]),"Quincunx"):
                    o.add(tuple(sorted([a,b,c]))); break
        return o

    def _kt(B, m):
        o = set()
        for tri in _gt(B, m):
            a,b,c = tri
            for d in _ab(m)-{a,b,c}:
                for v in (a,b,c):
                    ot = list({a,b,c}-{v})
                    if _h(m,(d,v),"Opposition") and _h(m,(d,ot[0]),"Sextile") and _h(m,(d,ot[1]),"Sextile"):
                        o.add(tuple(sorted([a,b,c,d])))
        return o

    def _mr(B, m):
        o = set()
        for a,b,c,d in combinations(sorted(B),4):
            if not (_h(m,(a,c),"Opposition") and _h(m,(b,d),"Opposition")): continue
            s1=[("Sextile",(a,b)),("Trine",(b,c)),("Sextile",(c,d)),("Trine",(d,a))]
            s2=[("Trine",(a,b)),("Sextile",(b,c)),("Trine",(c,d)),("Sextile",(d,a))]
            ok=lambda ss: all(_h(m,p,t) for t,p in ss)
            if ok(s1) or ok(s2): o.add(tuple(sorted([a,b,c,d])))
        return o

    def _bm(B, m):
        o = set()
        for yod in _yd(B, m):
            for cand in yod:
                ot = sorted(set(yod)-{cand})
                if _h(m,(cand,ot[0]),"Quincunx") and _h(m,(cand,ot[1]),"Quincunx") and _h(m,tuple(ot),"Sextile"):
                    for d in _ab(m)-set(yod):
                        if _h(m,(cand,d),"Opposition") and _h(m,(d,ot[0]),"Sextile") and _h(m,(d,ot[1]),"Sextile"):
                            o.add(tuple(sorted(list(yod)+[d])))
                    break
        return o

    def _cr(B, m):
        o = set()
        for a,b,c,d in combinations(sorted(B),4):
            if _h(m,(a,c),"Opposition") or _h(m,(b,d),"Opposition"): continue
            s1=[("Sextile",(a,b)),("Trine",(b,c)),("Sextile",(c,d)),("Trine",(d,a))]
            s2=[("Trine",(a,b)),("Sextile",(b,c)),("Trine",(c,d)),("Sextile",(d,a))]
            ok=lambda ss: all(_h(m,p,t) for t,p in ss)
            if ok(s1) or ok(s2): o.add(tuple(sorted([a,b,c,d])))
        return o

    def _sd(B, m):
        o = set()
        tris = list(_gt(B, m))
        for i in range(len(tris)):
            for j in range(i+1, len(tris)):
                T1,T2=set(tris[i]),set(tris[j])
                if T1&T2: continue
                U=tuple(sorted(T1|T2))
                if all(sum(1 for y in U if x!=y and _h(m,(x,y),"Sextile"))==2 for x in U):
                    o.add(U)
        return o

    def _policy(s): return {t for t in s if _comp_ok(t)}

    # Detectors
    def _det(asp):
        D={"Grand Trine":detect_grand_trines,"T-Square":detect_t_squares,"Yod":detect_yods,
           "Kite":lambda a:detect_kites(a,detect_grand_trines(a)),
           "Mystic Rectangle":detect_mystic_rectangles,
           "Boomerang":lambda a:detect_boomerangs(a,detect_yods(a)),
           "Cradle":detect_cradles,
           "Star of David":lambda a:detect_star_of_david(detect_grand_trines(a))}
        out={}
        for nm,fn in D.items():
            s=set()
            for it in fn(asp):
                pts=it.get("Points") or it.get("points") or []
                pn=tuple(sorted(_n(p) for p in pts))
                if _comp_ok(pn): s.add(pn)
            out[nm]=s
        return out

    def _enum(asp):
        m=_idx(asp); B=_ab(m)
        e={"Grand Trine":_gt(B,m),"T-Square":_ts(B,m),"Yod":_yd(B,m),"Kite":_kt(B,m),
           "Mystic Rectangle":_mr(B,m),"Boomerang":_bm(B,m),"Cradle":_cr(B,m),
           "Star of David":_sd(B,m)}
        for k in e: e[k]=_policy(e[k])
        return e

    got=_det(aspects); exp=_enum(aspects)

    report={}
    for typ in exp:
        ex,de=exp[typ],got.get(typ,set())
        mi,xt=ex-de,de-ex
        report[typ]={
            "expected_count":len(ex),"detected_count":len(de),
            "status":"OK" if not mi and not xt else ("MISMATCH" if mi else "EXTRA"),
            "missing":[list(p) for p in sorted(mi)],
            "extra":[list(p) for p in sorted(xt)],
        }

    if print_report:
        print("\n=== Geometric Pattern Audit ===")
        for typ,cell in report.items():
            ic="\u2705" if cell["status"]=="OK" else ("\u274c" if cell["status"]=="MISMATCH" else "\u26a0\ufe0f")
            print(f"\n{typ}: {ic} {cell['status']}")
            print(f"  expected: {cell['expected_count']}   detected: {cell['detected_count']}")
            for p in cell["missing"]: print("   - "+", ".join(p))
            for p in cell["extra"]:   print("   + "+", ".join(p))
        print()

    chart_data["Geometry Audit"]=report
    return report


# ============================================================================
#  MAIN GENERATOR
# ============================================================================

def generate_natal_chart(
    name, dob, tob, city, region, country,
    latitude=None, longitude=None,
    house_system="Placidus",
    aspects_file="aspects.json",
    star_csv="astrochart_cli_fixed_stars.csv",
):
    """
    Generate a complete natal chart.
    Returns dict with all original keys from v1 PLUS new analytical sections.
    """
    dt_str = f"{dob} {tob}"
    lat, lon, tz, dt_local = resolve_location_and_time(
        city, region, country, dt_str, latitude, longitude
    )

    # Core: positions, houses, angles
    positions, houses, axes = compute_chart(lat, lon, dt_local, house_system=house_system)

    # Analytical layers
    sect       = compute_sect(positions, axes)
    dignities  = compute_dignities(positions)
    ruler      = compute_chart_ruler(positions, axes)
    dispositors= compute_dispositor_chain(positions)
    balance    = compute_balance(positions, axes)
    parts      = compute_arabic_parts(positions, axes, houses, sect)
    retrogrades= compute_retrograde_summary(positions)

    # Aspects
    aspect_defs = {}
    if os.path.exists(aspects_file):
        with open(aspects_file) as f:
            aspect_defs = json.load(f)
    else:
        print(f"  WARNING: {aspects_file} not found, using minimal defaults")
        aspect_defs = {
            "Conjunction":{"Angle":0,"Orb":8},"Opposition":{"Angle":180,"Orb":7},
            "Trine":{"Angle":120,"Orb":7},"Square":{"Angle":90,"Orb":6},
            "Sextile":{"Angle":60,"Orb":6.5},"Quincunx":{"Angle":150,"Orb":3},
        }

    orb_overrides = {
        "Conjunction":6.0,"Opposition":6.0,"Trine":7.0,"Square":6.0,
        "Sextile":6.5,"Semi-sextile":3.0,"Semi-square":3.0,
        "Sesquiquadrate":3.5,"Quintile":3.0,"Biquintile":2.0,
        "Decile":1.5,"Tridecile":1.5,"Quindecile":1.5,
        "Septile":1.2,"Biseptile":1.2,"Triseptile":1.2,
    }

    alias_map = {"Midheaven": "MC", "Mean Node": "North Node"}

    aspects = compute_aspects(
        positions, aspect_defs, default_orb=6,
        axes=axes, include_axes=True,
        alias_map=alias_map, orb_overrides=orb_overrides,
    )

    # Geometric patterns
    patterns = detect_geometric_patterns_with_policy(
        aspects, include_modern=True, include_minor=True, min_core=2, max_minor=1,
    )

    # Fixed stars
    stars = compute_fixed_star_conjunctions(
        positions, star_csv, orb=1.0, axes=axes, include_axes=True,
    )

    return {
        # ---- Original v1 keys (preserved for CLI tool compat) ----
        "chart_metadata": {
            "Name": name,
            "Birth": {
                "Date": dob, "Time": tob,
                "Place": f"{city}, {region}, {country}",
                "Latitude": lat, "Longitude": lon,
                "Timezone": str(tz),
            },
            "House System": house_system,
            "Zodiac Type": ZODIAC_TYPE,
            "Ephemeris": EPHEMERIS,
            "Ephemeris Path": SE_EPHE_PATH,
            "Included Objects": list(positions.keys()),
            "Engine Version": "2.0",
        },
        "chart_objects": positions,
        "house_cusps": houses,
        "chart_points": axes,
        "chart_aspects": aspects,
        "geometric_patterns": patterns,
        "fixed_star_conjunctions": stars,
        # ---- New v2 analytical sections ----
        "arabic_parts": parts,
        "dignities": dignities,
        "sect": sect,
        "chart_ruler": ruler,
        "dispositors": dispositors,
        "balance": balance,
        "retrogrades": retrogrades,
    }


def generate_natal_report(chart_data, filename="natal_report.json", geometry_audit=None):
    """Generate final JSON report."""
    report = {
        "Chart Metadata":       chart_data.get("chart_metadata", {}),
        "Planetary Positions":  chart_data.get("chart_objects", {}),
        "House Cusps":          chart_data.get("house_cusps", {}),
        "Chart Points (Angles)":chart_data.get("chart_points", {}),
        "Aspects":              chart_data.get("chart_aspects", []),
        "Geometric Patterns":   chart_data.get("geometric_patterns", []),
        "Fixed Star Conjunctions": chart_data.get("fixed_star_conjunctions", []),
        # v2 sections
        "Arabic Parts":         chart_data.get("arabic_parts", {}),
        "Essential Dignities":  chart_data.get("dignities", {}),
        "Sect":                 chart_data.get("sect", {}),
        "Chart Ruler":          chart_data.get("chart_ruler", {}),
        "Dispositor Chain":     chart_data.get("dispositors", {}),
        "Balance":              chart_data.get("balance", {}),
        "Retrograde Bodies":    chart_data.get("retrogrades", []),
    }
    if geometry_audit is not None:
        report["Geometry Audit"] = geometry_audit

    with open(filename, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Report saved: {filename}")
    return report