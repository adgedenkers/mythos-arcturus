#!/usr/bin/env python3
"""
Golden fixture validation harness for Astrology v2.

Ships in SEN-0004 (Letter A). Runs at the end of every Astrology v2
patch's apply_patch.py. A patch that fails the fixtures rolls back.

Self-contained: uses pyswisseph directly. Does not import from
ephemeris.py (which doesn't exist until Letter B). After Letter B ships,
a refactored version of this script will import from ephemeris.py and
verify consistency between the fixture set and the shared wrapper.

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/tests/check_accuracy.py
    /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/tests/check_accuracy.py --verbose
    /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/tests/check_accuracy.py --json

Exit codes:
    0 — all fixtures passed
    1 — one or more fixtures failed
    2 — script error (missing fixtures file, import error, etc.)
"""
import argparse
import json
import os
import sys
from datetime import datetime

FIXTURE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures',
    'expected_aspects.json',
)

# Use the canonical path if SE_EPHE_PATH isn't set (Letter B sets it)
DEFAULT_EPHE_PATH = os.environ.get('SE_EPHE_PATH', '/opt/mythos/astrology/ephe')

# Also check /opt/mythos/ephemeris/ as a fallback for pre-Letter-C state
FALLBACK_EPHE_PATHS = [
    '/opt/mythos/astrology/ephe',
    '/opt/mythos/ephemeris',
]


# --- Constants (duplicated from ephemeris.py, which doesn't exist yet) ---

ASPECT_ANGLES = {
    'conjunction': 0,
    'opposition': 180,
    'trine': 120,
    'square': 90,
    'sextile': 60,
    'quincunx': 150,
}


def find_ephemeris_path():
    """Find a valid ephemeris directory, preferring SE_EPHE_PATH."""
    candidates = [DEFAULT_EPHE_PATH] + [p for p in FALLBACK_EPHE_PATHS if p != DEFAULT_EPHE_PATH]
    for path in candidates:
        if os.path.isdir(path):
            # Check for at least one .se1 file
            for fname in os.listdir(path):
                if fname.endswith('.se1'):
                    return path
    return None


def date_to_jd(year, month, day, hour, minute, tz_offset_hours):
    """Convert a local date/time to Julian Day (UT)."""
    import swisseph as swe
    ut_hour = hour - tz_offset_hours + minute / 60.0
    return swe.julday(year, month, day, ut_hour)


def get_planet_longitude(jd_ut, planet_name):
    """Get ecliptic longitude of a planet at given Julian Day."""
    import swisseph as swe

    planet_map = {
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
        'Chiron': 15,  # SE_CHIRON
    }

    if planet_name not in planet_map:
        raise ValueError(f"Unknown planet: {planet_name}")

    pos = swe.calc_ut(jd_ut, planet_map[planet_name])
    return pos[0][0]  # longitude in degrees


def angular_distance(a, b):
    """Shortest angular distance between two longitudes (0-180)."""
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def calc_aspect_orb(transit_lon, natal_lon, aspect_name):
    """How far off is the actual angle from the exact aspect angle?"""
    actual_angle = angular_distance(transit_lon, natal_lon)
    target = ASPECT_ANGLES[aspect_name]
    return abs(actual_angle - target)


def load_fixtures():
    """Load the golden fixture file."""
    if not os.path.isfile(FIXTURE_FILE):
        raise FileNotFoundError(f"Fixture file not found: {FIXTURE_FILE}")
    with open(FIXTURE_FILE) as f:
        return json.load(f)


def run_fixture(fixture, people, tolerance):
    """
    Run a single fixture.

    Returns dict with: id, person, pass, expected_orb, actual_orb,
    delta, error (if any).
    """
    fid = fixture['id']
    person_key = fixture['person']
    person = people[person_key]

    result = {
        'id': fid,
        'person': person_key,
        'transit_planet': fixture['transit_planet'],
        'aspect': fixture['aspect'],
        'natal_target': fixture['natal_target'],
        'expected_orb': fixture['expected_orb_degrees'],
        'pass': False,
        'actual_orb': None,
        'delta': None,
        'error': None,
    }

    try:
        # Natal position
        bd = person['birth_date'].split('-')
        bt = person['birth_time'].split(':')
        natal_jd = date_to_jd(
            int(bd[0]), int(bd[1]), int(bd[2]),
            int(bt[0]), int(bt[1]),
            person['tz_offset_hours'],
        )
        natal_lon = get_planet_longitude(natal_jd, fixture['natal_target'])

        # Transit position — use the provided UT time
        td = fixture['transit_date'].split('-')
        tt = fixture['transit_time_ut'].split(':')
        transit_jd = date_to_jd(
            int(td[0]), int(td[1]), int(td[2]),
            int(tt[0]), int(tt[1]),
            0,  # already UT
        )
        transit_lon = get_planet_longitude(transit_jd, fixture['transit_planet'])

        # Calculate orb
        actual_orb = calc_aspect_orb(transit_lon, natal_lon, fixture['aspect'])
        delta = abs(actual_orb - fixture['expected_orb_degrees'])

        result['actual_orb'] = round(actual_orb, 4)
        result['delta'] = round(delta, 4)
        result['pass'] = delta <= tolerance

    except Exception as e:
        result['error'] = f"{type(e).__name__}: {e}"

    return result


def format_text_report(results, ephe_path, tolerance):
    """Produce a human-readable pass/fail report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ASTROLOGY v2 — Golden Fixture Check")
    lines.append("=" * 70)
    lines.append(f"Ephemeris path: {ephe_path}")
    lines.append(f"Tolerance: ±{tolerance}°")
    lines.append(f"Fixtures loaded: {len(results)}")
    lines.append("")

    for r in results:
        status = "✓ PASS" if r['pass'] else ("✗ FAIL" if r['error'] is None else "⚠ ERROR")
        lines.append(f"{status}  {r['id']}")
        lines.append(f"       Transit: {r['transit_planet']} {r['aspect']} natal {r['natal_target']}")
        if r['error']:
            lines.append(f"       ERROR: {r['error']}")
        else:
            lines.append(f"       Expected orb: {r['expected_orb']}°")
            lines.append(f"       Actual orb:   {r['actual_orb']}°")
            lines.append(f"       Delta:        {r['delta']}°")
        lines.append("")

    passed = sum(1 for r in results if r['pass'])
    failed = sum(1 for r in results if not r['pass'] and r['error'] is None)
    errored = sum(1 for r in results if r['error'] is not None)

    lines.append("-" * 70)
    lines.append(f"Total: {len(results)}  Passed: {passed}  Failed: {failed}  Errored: {errored}")
    lines.append("=" * 70)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Astrology v2 golden fixture check")
    parser.add_argument('--verbose', '-v', action='store_true', help='Extra output')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of text')
    parser.add_argument('--tolerance', type=float, default=None,
                        help='Override orb tolerance in degrees (default: from fixture file)')
    args = parser.parse_args()

    # Check pyswisseph
    try:
        import swisseph as swe
    except ImportError:
        print("ERROR: pyswisseph not available in this Python environment.", file=sys.stderr)
        sys.exit(2)

    # Find ephemeris path and configure
    ephe_path = find_ephemeris_path()
    if ephe_path is None:
        print(f"ERROR: No valid ephemeris directory found. Tried: {FALLBACK_EPHE_PATHS}", file=sys.stderr)
        sys.exit(2)
    swe.set_ephe_path(ephe_path)

    # Load fixtures
    try:
        data = load_fixtures()
    except Exception as e:
        print(f"ERROR: Could not load fixtures: {e}", file=sys.stderr)
        sys.exit(2)

    tolerance = args.tolerance if args.tolerance is not None else data.get('_tolerance_degrees', 0.1)

    # Run fixtures
    results = []
    for fixture in data['fixtures']:
        r = run_fixture(fixture, data['people'], tolerance)
        results.append(r)

    # Report
    if args.json:
        payload = {
            'timestamp': datetime.now().isoformat(),
            'ephemeris_path': ephe_path,
            'tolerance': tolerance,
            'results': results,
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r['pass']),
                'failed': sum(1 for r in results if not r['pass'] and r['error'] is None),
                'errored': sum(1 for r in results if r['error'] is not None),
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_text_report(results, ephe_path, tolerance))

    # Exit code
    all_passed = all(r['pass'] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
