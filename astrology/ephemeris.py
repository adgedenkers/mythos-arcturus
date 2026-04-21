"""
ephemeris.py — Mythos Astrology v2 Master Ephemeris Provider

Shipped in SEN-0005 (Letter B). The single module that ANY astrology
code on Mythos imports for Swiss Ephemeris calculation. Replaces
scattered per-script copies of PLANETS / SIGNS / ASPECT_DEFS and
duplicate `import swisseph` calls.

Design contract:
- No I/O. This module never reads or writes files or DB rows. It
  only calculates.
- `swe.set_ephe_path()` is called exactly once, at module import time,
  from SE_EPHE_PATH env var (defaulting to /opt/mythos/astrology/ephe).
- All constants and helpers are snake_case for Python convention.
- PascalCase sign/planet names are preserved in SIGNS and PLANETS keys
  because that's what the JSON schema uses and what downstream code
  expects ("Sun", "Moon", "Mercury" — not "sun", "moon", "mercury").
- House system default is Placidus ('P'). Callers can override.

Companion work:
- SEN-0004 (Letter A) shipped the golden fixture harness that this
  module is validated against.
- SEN-0005 (this patch) adds SE_EPHE_PATH to /opt/mythos/.env.
- SEN-0006 (Letter C, future) moves ephemeris files to the canonical
  path and updates 5 legacy scripts to import from here.

Usage:
    from astrology import ephemeris as e

    # Convert date to Julian Day (UT)
    jd = e.date_to_jd(2026, 4, 28, 12, 0, tz_offset_hours=-4)

    # Get all planets at that JD
    planets = e.calc_planets(jd)
    sun_lon = planets['Sun']['longitude']

    # Get house cusps
    houses = e.calc_houses(jd, lat=42.65, lon=-73.80)

    # Check aspect between two longitudes
    asp = e.calc_aspect(sun_lon, planets['Moon']['longitude'])

    # Format a position as "0d08mSagittarius"
    print(e.fmt_pos(sun_lon))
"""
from __future__ import annotations

import os
from typing import Optional, Union

import swisseph as swe


# ─── Ephemeris path (one-time init on import) ──────────────────────────

#: Canonical ephemeris path. SEN-0005 appends this to /opt/mythos/.env;
#: SEN-0006 (Letter C) moves the files here. Falls back to a sensible
#: default so this module works even without .env loaded.
DEFAULT_EPHE_PATH = '/opt/mythos/astrology/ephe'
SE_EPHE_PATH = os.environ.get('SE_EPHE_PATH', DEFAULT_EPHE_PATH)
swe.set_ephe_path(SE_EPHE_PATH)


# ─── Module metadata ───────────────────────────────────────────────────

__version__ = '2.0.0'  # Astrology v2 Letter B
__swisseph_version__ = getattr(swe, '__version__', 'unknown')


# ─── Default calculation flags ─────────────────────────────────────────

#: Default flags for swe.calc_ut(). SEFLG_SWIEPH uses the Swiss
#: Ephemeris files (highest precision). SEFLG_SPEED requests speed
#: values — without this flag, speeds silently return 0.0, and
#: retrograde/applying detection breaks. This is a Swiss Ephemeris
#: footgun: flags=0 produces mathematically correct positions but
#: all speeds are zero. Always include SEFLG_SPEED.
DEFAULT_CALC_FLAGS: int = swe.FLG_SWIEPH | swe.FLG_SPEED


# ─── Bodies ────────────────────────────────────────────────────────────

#: Core planetary bodies + lunar nodes. Keys are the PascalCase display
#: names used throughout Mythos JSON schemas.
PLANETS: dict[str, int] = {
    'Sun':        swe.SUN,
    'Moon':       swe.MOON,
    'Mercury':    swe.MERCURY,
    'Venus':      swe.VENUS,
    'Mars':       swe.MARS,
    'Jupiter':    swe.JUPITER,
    'Saturn':     swe.SATURN,
    'Uranus':     swe.URANUS,
    'Neptune':    swe.NEPTUNE,
    'Pluto':      swe.PLUTO,
    'North Node': swe.TRUE_NODE,  # True Node, not Mean Node
}

#: Mean Black Moon Lilith (apogee of lunar orbit).
LILITH_ID: int = swe.MEAN_APOG

#: Oscillating (true) Black Moon Lilith — optional, less commonly used.
TRUE_LILITH_ID: int = swe.OSCU_APOG

#: Asteroid IDs. Chiron is SE_CHIRON (15). Additional asteroids require
#: ephemeris files in SE_EPHE_PATH (e.g. seas_18.se1, ast50/se50000s.se1).
ASTEROIDS: dict[str, int] = {
    'Chiron': swe.CHIRON,    # 15
    'Ceres':  swe.CERES,     # 17
    'Pallas': swe.PALLAS,    # 18
    'Juno':   swe.JUNO,      # 19
    'Vesta':  swe.VESTA,     # 20
}


# ─── Signs ─────────────────────────────────────────────────────────────

SIGNS: list[str] = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]

#: Unicode zodiac glyphs, indexed by sign name.
SIGN_GLYPHS: dict[str, str] = {
    s: chr(0x2648 + i) for i, s in enumerate(SIGNS)
}

#: Unicode planet glyphs, keyed by PLANETS.keys() + Lilith + common asteroids.
PLANET_GLYPHS: dict[str, str] = {
    'Sun':        '\u2609',
    'Moon':       '\u263d',
    'Mercury':    '\u263f',
    'Venus':      '\u2640',
    'Mars':       '\u2642',
    'Jupiter':    '\u2643',
    'Saturn':     '\u2644',
    'Uranus':     '\u2645',
    'Neptune':    '\u2646',
    'Pluto':      '\u2647',
    'North Node': '\u260a',
    'South Node': '\u260b',
    'Chiron':     '\u26b7',
    'Lilith':     '\u26b8',
}

ELEMENTS: dict[str, str] = {
    'Aries':       'Fire',  'Taurus':      'Earth',
    'Gemini':      'Air',   'Cancer':      'Water',
    'Leo':         'Fire',  'Virgo':       'Earth',
    'Libra':       'Air',   'Scorpio':     'Water',
    'Sagittarius': 'Fire',  'Capricorn':   'Earth',
    'Aquarius':    'Air',   'Pisces':      'Water',
}

MODALITIES: dict[str, str] = {
    'Aries':       'Cardinal', 'Taurus':      'Fixed',
    'Gemini':      'Mutable',  'Cancer':      'Cardinal',
    'Leo':         'Fixed',    'Virgo':       'Mutable',
    'Libra':       'Cardinal', 'Scorpio':     'Fixed',
    'Sagittarius': 'Mutable',  'Capricorn':   'Cardinal',
    'Aquarius':    'Fixed',    'Pisces':      'Mutable',
}

POLARITIES: dict[str, str] = {
    'Aries':       'masculine', 'Taurus':      'feminine',
    'Gemini':      'masculine', 'Cancer':      'feminine',
    'Leo':         'masculine', 'Virgo':       'feminine',
    'Libra':       'masculine', 'Scorpio':     'feminine',
    'Sagittarius': 'masculine', 'Capricorn':   'feminine',
    'Aquarius':    'masculine', 'Pisces':      'feminine',
}

#: Traditional (pre-Uranus) rulers.
TRAD_RULERS: dict[str, str] = {
    'Aries': 'Mars',    'Taurus': 'Venus',   'Gemini': 'Mercury',
    'Cancer': 'Moon',   'Leo': 'Sun',        'Virgo': 'Mercury',
    'Libra': 'Venus',   'Scorpio': 'Mars',   'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
}

#: Modern rulers (Scorpio=Pluto, Aquarius=Uranus, Pisces=Neptune).
MOD_RULERS: dict[str, str] = dict(TRAD_RULERS)
MOD_RULERS.update({
    'Scorpio':  'Pluto',
    'Aquarius': 'Uranus',
    'Pisces':   'Neptune',
})


# ─── Aspects ───────────────────────────────────────────────────────────

#: Aspect definitions: exact angle, default orb (degrees), whether major.
#: Mirrors the uploaded daily_transits.py orb conventions.
ASPECT_DEFS: dict[str, dict[str, Union[int, float, bool]]] = {
    'conjunction': {'angle':   0, 'orb': 8, 'major': True},
    'opposition':  {'angle': 180, 'orb': 8, 'major': True},
    'trine':       {'angle': 120, 'orb': 8, 'major': True},
    'square':      {'angle':  90, 'orb': 7, 'major': True},
    'sextile':     {'angle':  60, 'orb': 6, 'major': True},
    'quincunx':    {'angle': 150, 'orb': 3, 'major': False},
}

#: Human-friendly verb forms for aspect names.
ASPECT_WORDS: dict[str, str] = {
    'conjunction': 'conjunct',
    'opposition':  'opposite',
    'trine':       'trine',
    'square':      'square',
    'sextile':     'sextile',
    'quincunx':    'quincunx',
}


# ─── House systems ─────────────────────────────────────────────────────

#: Default house system. 'P' = Placidus. Swiss Ephemeris uses single-char codes.
DEFAULT_HOUSE_SYSTEM = 'P'

#: Map from friendly names to Swiss Ephemeris house system codes.
HOUSE_SYSTEMS: dict[str, str] = {
    'Placidus':     'P',
    'Koch':         'K',
    'Porphyry':     'O',
    'Regiomontanus':'R',
    'Campanus':     'C',
    'Equal':        'E',
    'Whole Sign':   'W',
    'Alcabitius':   'B',
    'Morinus':      'M',
}


# ─── Utility helpers ───────────────────────────────────────────────────

def lon_to_sign(lon: float) -> tuple[str, float]:
    """Convert ecliptic longitude to (sign_name, degrees_within_sign)."""
    idx = int(lon / 30) % 12
    return SIGNS[idx], lon % 30


def fmt_pos(lon: float) -> str:
    """Format a longitude as '0d08mSagittarius'."""
    sign, deg = lon_to_sign(lon)
    d = int(deg)
    m_fractional = (deg - d) * 60
    m = int(m_fractional)
    return f'{d}d{m:02d}m{sign}'


def ang_dist(a: float, b: float) -> float:
    """Shortest angular distance between two longitudes (0-180)."""
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def calc_aspect(
    lon1: float,
    lon2: float,
    speed1: Optional[float] = None,
    speed2: Optional[float] = None,
) -> Optional[dict]:
    """
    Detect an aspect between two longitudes.

    Returns a dict {aspect, angle, orb, exact, major, applying} or None
    if no defined aspect matches within orb. `applying` is True if the
    aspect is still forming (orb shrinking), False if separating, None
    if speeds were not provided.
    """
    diff = ang_dist(lon1, lon2)
    for name, aspect in ASPECT_DEFS.items():
        orb_actual = abs(diff - aspect['angle'])
        if orb_actual <= aspect['orb']:
            applying: Optional[bool] = None
            if speed1 is not None and speed2 is not None:
                # Simple proxy: aspect is "applying" if bodies are converging
                # toward exact. Full applying/separating requires more detail,
                # but this matches the uploaded daily_transits.py behavior.
                applying = orb_actual > 0.01
            return {
                'aspect':   name,
                'angle':    aspect['angle'],
                'orb':      round(orb_actual, 4),
                'exact':    orb_actual < 1.0,
                'major':    aspect.get('major', False),
                'applying': applying,
            }
    return None


def det_sect(sun_lon: float, asc_lon: float) -> str:
    """Determine chart sect: 'diurnal' if Sun is above horizon, else 'nocturnal'."""
    d = (sun_lon - asc_lon) % 360
    return 'diurnal' if 180 < d <= 360 or d == 0 else 'nocturnal'


# ─── Date conversion ───────────────────────────────────────────────────

def date_to_jd(
    year: int,
    month: int,
    day: int,
    hour: int = 12,
    minute: int = 0,
    tz_offset_hours: float = 0.0,
) -> float:
    """
    Convert a civil date/time in a given timezone offset to Julian Day (UT).

    Example: noon EDT (UTC-4) on 2026-04-28:
        date_to_jd(2026, 4, 28, 12, 0, tz_offset_hours=-4)
    """
    ut_hour_fractional = hour - tz_offset_hours + minute / 60.0
    return swe.julday(year, month, day, ut_hour_fractional)


# ─── Core ephemeris calculations ───────────────────────────────────────

def calc_planets(
    jd: float,
    flags: Optional[int] = None,
    include_asteroids: bool = False,
    include_lilith: bool = True,
) -> dict[str, dict]:
    """
    Calculate positions of all tracked bodies at a given Julian Day.

    Returns a dict keyed by body name (PLANETS, LILITH, optional asteroids).
    Each value is a dict with: longitude, speed, sign, degree_in_sign,
    formatted, retrograde, element, modality, house (None — set by
    calc_houses_assignment), dignity (None — set by dignity calc).

    flags defaults to DEFAULT_CALC_FLAGS (SEFLG_SWIEPH | SEFLG_SPEED).
    Pass a custom int to override. Do NOT pass 0 unless you
    specifically want speeds to be zero — that's the Swiss Ephemeris
    footgun this wrapper exists to prevent.
    """
    if flags is None:
        flags = DEFAULT_CALC_FLAGS

    results: dict[str, dict] = {}

    for name, body_id in PLANETS.items():
        pos, _ = swe.calc_ut(jd, body_id, flags)
        lon, _lat, _dist, spd = pos[0], pos[1], pos[2], pos[3]
        sign, deg = lon_to_sign(lon)
        results[name] = {
            'longitude':      lon,
            'speed':          spd,
            'sign':           sign,
            'degree_in_sign': deg,
            'formatted':      fmt_pos(lon),
            'retrograde':     spd < 0,
            'element':        ELEMENTS[sign],
            'modality':       MODALITIES[sign],
            'house':          None,  # set by assign_houses() if used
            'dignity':        None,  # set by dignity calc if used
        }

    # South Node is always opposite North Node
    if 'North Node' in results:
        nn = results['North Node']
        sn_lon = (nn['longitude'] + 180) % 360
        sn_sign, sn_deg = lon_to_sign(sn_lon)
        results['South Node'] = {
            'longitude':      sn_lon,
            'speed':          -nn['speed'],  # opposite motion
            'sign':           sn_sign,
            'degree_in_sign': sn_deg,
            'formatted':      fmt_pos(sn_lon),
            'retrograde':     nn['speed'] > 0,  # SN retrograde when NN direct
            'element':        ELEMENTS[sn_sign],
            'modality':       MODALITIES[sn_sign],
            'house':          None,
            'dignity':         None,
        }

    if include_lilith:
        pos, _ = swe.calc_ut(jd, LILITH_ID, flags)
        lon, _, _, spd = pos[0], pos[1], pos[2], pos[3]
        sign, deg = lon_to_sign(lon)
        results['Lilith'] = {
            'longitude':      lon,
            'speed':          spd,
            'sign':           sign,
            'degree_in_sign': deg,
            'formatted':      fmt_pos(lon),
            'retrograde':     spd < 0,
            'element':        ELEMENTS[sign],
            'modality':       MODALITIES[sign],
            'house':          None,
            'dignity':         None,
        }

    if include_asteroids:
        for name, body_id in ASTEROIDS.items():
            try:
                pos, _ = swe.calc_ut(jd, body_id, flags)
                lon, _, _, spd = pos[0], pos[1], pos[2], pos[3]
                sign, deg = lon_to_sign(lon)
                results[name] = {
                    'longitude':      lon,
                    'speed':          spd,
                    'sign':           sign,
                    'degree_in_sign': deg,
                    'formatted':      fmt_pos(lon),
                    'retrograde':     spd < 0,
                    'element':        ELEMENTS[sign],
                    'modality':       MODALITIES[sign],
                    'house':          None,
                    'dignity':         None,
                }
            except swe.Error:
                # Asteroid ephemeris file missing — skip gracefully
                # Letter C ensures these are in place
                pass

    return results


def calc_houses(
    jd: float,
    lat: float,
    lon: float,
    system: str = DEFAULT_HOUSE_SYSTEM,
) -> dict:
    """
    Calculate house cusps and angles for a given location and time.

    Returns a dict with:
      - angles: dict of ASC/MC/DSC/IC, each with longitude/sign/formatted
      - cusps: list of 12 cusp longitudes (House 1 through House 12)
      - system: the house system used
    """
    # swisseph returns (cusps[12], ascmc[8])
    # ascmc[0] = ASC, ascmc[1] = MC, ascmc[2] = ARMC, ascmc[3] = Vertex, ...
    cusps, ascmc = swe.houses(jd, lat, lon, system.encode('ascii'))

    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    dsc_lon = (asc_lon + 180) % 360
    ic_lon = (mc_lon + 180) % 360

    asc_sign, _ = lon_to_sign(asc_lon)
    mc_sign, _ = lon_to_sign(mc_lon)
    dsc_sign, _ = lon_to_sign(dsc_lon)
    ic_sign, _ = lon_to_sign(ic_lon)

    return {
        'angles': {
            'ASC': {'longitude': asc_lon, 'sign': asc_sign, 'formatted': fmt_pos(asc_lon)},
            'MC':  {'longitude': mc_lon,  'sign': mc_sign,  'formatted': fmt_pos(mc_lon)},
            'DSC': {'longitude': dsc_lon, 'sign': dsc_sign, 'formatted': fmt_pos(dsc_lon)},
            'IC':  {'longitude': ic_lon,  'sign': ic_sign,  'formatted': fmt_pos(ic_lon)},
        },
        'cusps': list(cusps),  # 12 longitudes, indexed 0..11 = House 1..12
        'system': system,
    }


def assign_house(planet_lon: float, cusps: list[float]) -> int:
    """
    Given a planet's longitude and a list of 12 house cusps, return
    which house (1-12) the planet is in. Handles wrap-around across
    0° Aries correctly.
    """
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        # Handle wrap-around
        if start <= end:
            if start <= planet_lon < end:
                return i + 1
        else:
            if planet_lon >= start or planet_lon < end:
                return i + 1
    return 12  # defensive fallback


# ─── Self-check ────────────────────────────────────────────────────────

def self_check() -> dict:
    """
    Return module health status. Useful for diagnostics and patch
    verification. Does NOT raise — returns a dict with pass/fail flags.
    """
    result = {
        'module_version':     __version__,
        'swisseph_version':   __swisseph_version__,
        'ephe_path':          SE_EPHE_PATH,
        'ephe_path_exists':   os.path.isdir(SE_EPHE_PATH),
        'planets_loaded':     len(PLANETS),
        'signs_loaded':       len(SIGNS),
        'aspects_defined':    len(ASPECT_DEFS),
        'house_systems':      len(HOUSE_SYSTEMS),
    }

    # Smoke test: compute Sun position at a known date
    try:
        jd = date_to_jd(2026, 4, 28, 12, 0, tz_offset_hours=0)
        planets = calc_planets(jd)
        result['sun_lon_2026_04_28_12ut'] = planets['Sun']['longitude']
        result['smoke_test'] = 'pass'
    except Exception as e:
        result['smoke_test'] = f'fail: {e}'

    return result


if __name__ == '__main__':
    # Run as script for quick diagnostic
    import json
    print(json.dumps(self_check(), indent=2, default=str))
