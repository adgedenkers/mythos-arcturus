#!/usr/bin/env python3
"""
Seraphe Lunar Transit Calculator
=================================
Calculates when the transiting Moon hits any of Seraphe's natal points
for a given month/year. Uses Swiss Ephemeris for precision.

Usage:
    python3 seraphe_lunar_transits.py 03/2026
    python3 seraphe_lunar_transits.py 03/2026 --json
    python3 seraphe_lunar_transits.py 03/2026 --json --output transits_march2026.json

Birth: August 19, 1978 · 2:02 PM EDT · Norwich, NY
"""

import sys
import os
import json
import math
import argparse
from datetime import datetime, timedelta, timezone

# Add ephemeris engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swisseph as swe

# ─── SERAPHE'S BIRTH DATA ───────────────────────────────────────────────────
BIRTH = {
    'year': 1978, 'month': 8, 'day': 19,
    'hour': 14, 'minute': 2,
    'tz_offset': -4,  # EDT
    'lat': 42.5326, 'lon': -75.5235,  # Norwich, NY
    'name': 'Seraphe'
}

# ─── ASPECT DEFINITIONS ─────────────────────────────────────────────────────
ASPECTS = {
    'conjunction':    {'angle': 0,   'orb': 2.0, 'symbol': '☌', 'weight': 5},
    'opposition':     {'angle': 180, 'orb': 2.0, 'symbol': '☍', 'weight': 4},
    'square':         {'angle': 90,  'orb': 2.0, 'symbol': '□', 'weight': 4},
    'trine':          {'angle': 120, 'orb': 2.0, 'symbol': '△', 'weight': 2},
    'sextile':        {'angle': 60,  'orb': 1.5, 'symbol': '⚹', 'weight': 1},
    'quincunx':       {'angle': 150, 'orb': 1.5, 'symbol': '⚻', 'weight': 3},
}

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_GLYPHS = {s: chr(0x2648 + i) for i, s in enumerate(SIGNS)}

ELEMENT_MAP = {
    'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water',
    'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water',
    'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'
}

ELEMENT_QUALITY = {
    'Water': 'Amplifies permeability — psychic channel wide open',
    'Earth': 'Temporary grounding — some relief from the flood',
    'Fire': 'Can feel agitating — restless, hot, scattered',
    'Air': 'Scatters emotionally — thoughts race, feelings diffuse',
}


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def lon_to_sign(lon):
    idx = int(lon / 30) % 12
    return SIGNS[idx], lon % 30

def fmt_degree(lon):
    """Format longitude as 14°44' Pisces"""
    sign, deg_in_sign = lon_to_sign(lon)
    d = int(deg_in_sign)
    m = int((deg_in_sign - d) * 60)
    return f"{d}°{m:02d}' {sign}"

def ang_dist(a, b):
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d

def get_moon_lon(jd):
    """Get Moon longitude at a given Julian Day."""
    swe.set_ephe_path(None)
    pos = swe.calc_ut(jd, swe.MOON)
    return pos[0][0]

def get_moon_speed(jd):
    """Get Moon speed in degrees/day."""
    swe.set_ephe_path(None)
    pos = swe.calc_ut(jd, swe.MOON)
    return pos[0][3]

def jd_to_datetime(jd, tz_offset=-4):
    """Convert Julian Day to datetime in given timezone."""
    # Get UTC components
    ut = swe.revjul(jd)
    year, month, day = int(ut[0]), int(ut[1]), int(ut[2])
    hour_frac = ut[3]
    hour = int(hour_frac)
    minute = int((hour_frac - hour) * 60)
    second = int(((hour_frac - hour) * 60 - minute) * 60)

    dt_utc = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    dt_local = dt_utc + timedelta(hours=tz_offset)
    return dt_local

def datetime_to_jd(year, month, day, hour=0, minute=0, tz_offset=0):
    """Convert date/time to Julian Day (UT)."""
    ut_hour = hour + minute / 60.0 - tz_offset
    return swe.julday(year, month, day, ut_hour)

def days_in_month(year, month):
    if month == 12:
        return (datetime(year + 1, 1, 1) - datetime(year, 12, 1)).days
    return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days


# ─── COMPUTE SERAPHE'S NATAL POINTS ──────────────────────────────────────────

def compute_natal_points():
    """Calculate all of Seraphe's natal points from Swiss Ephemeris."""
    b = BIRTH
    ut_hour = b['hour'] + b['minute'] / 60.0 - b['tz_offset']
    jd = swe.julday(b['year'], b['month'], b['day'], ut_hour)
    swe.set_ephe_path(None)

    points = {}

    # Planets
    planet_ids = {
        'Moon': swe.MOON,
        'Sun': swe.SUN,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO,
        'North Node': swe.TRUE_NODE,
    }

    for name, pid in planet_ids.items():
        pos = swe.calc_ut(jd, pid)
        lon = pos[0][0]
        sign, deg = lon_to_sign(lon)
        points[name] = {
            'longitude': lon,
            'formatted': fmt_degree(lon),
            'sign': sign,
            'weight': get_point_weight(name),
            'category': get_point_category(name),
        }

    # South Node
    nn_lon = points['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    points['South Node'] = {
        'longitude': sn_lon,
        'formatted': fmt_degree(sn_lon),
        'sign': lon_to_sign(sn_lon)[0],
        'weight': get_point_weight('South Node'),
        'category': get_point_category('South Node'),
    }

    # Lilith (Mean Black Moon)
    pos = swe.calc_ut(jd, swe.MEAN_APOG)
    lon = pos[0][0]
    points['Lilith'] = {
        'longitude': lon,
        'formatted': fmt_degree(lon),
        'sign': lon_to_sign(lon)[0],
        'weight': get_point_weight('Lilith'),
        'category': get_point_category('Lilith'),
    }

    # House cusps / angles (Placidus)
    cusps, ascmc = swe.houses(jd, b['lat'], b['lon'], b'P')
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    dsc_lon = (asc_lon + 180) % 360
    ic_lon = (mc_lon + 180) % 360

    for name, lon in [('Ascendant', asc_lon), ('MC', mc_lon),
                      ('Descendant', dsc_lon), ('IC', ic_lon)]:
        points[name] = {
            'longitude': lon,
            'formatted': fmt_degree(lon),
            'sign': lon_to_sign(lon)[0],
            'weight': get_point_weight(name),
            'category': get_point_category(name),
        }

    return points


def get_point_weight(name):
    weights = {
        'Moon': 5, 'IC': 5, 'Neptune': 5, 'Pluto': 4,
        'Sun': 3, 'Mercury': 2, 'Venus': 3, 'Mars': 3,
        'Jupiter': 3, 'Saturn': 3, 'Uranus': 3,
        'Ascendant': 3, 'MC': 3, 'Descendant': 2,
        'Lilith': 3, 'North Node': 2, 'South Node': 3,
    }
    return weights.get(name, 2)

def get_point_category(name):
    categories = {
        'Moon': 'LUNAR CORE', 'IC': 'LUNAR CORE', 'South Node': 'LUNAR CORE',
        'Neptune': 'PSYCHIC AXIS', 'Pluto': 'PSYCHIC AXIS',
        'Ascendant': 'ANGLES', 'MC': 'ANGLES', 'Descendant': 'ANGLES',
        'Sun': 'THE LIGHTS', 'Mercury': 'THE LIGHTS',
        'Venus': 'HEART & DRIVE', 'Mars': 'HEART & DRIVE',
        'Jupiter': 'HEAVYWEIGHTS', 'Saturn': 'HEAVYWEIGHTS', 'Uranus': 'HEAVYWEIGHTS',
        'Lilith': 'SHADOW', 'North Node': 'SHADOW',
    }
    return categories.get(name, 'OTHER')


# ─── TRANSIT SCANNING ENGINE ─────────────────────────────────────────────────


def signed_aspect_error(moon_lon, natal_lon, target_angle):
    """
    Compute a SIGNED error for aspect detection.
    For conjunction (target=0): positive when Moon is approaching, negative after passing.
    For other aspects: sign flips as Moon crosses exact.
    """
    # Raw difference (signed, 0-360)
    raw = (moon_lon - natal_lon) % 360

    if target_angle == 0:
        # Conjunction: raw wraps around 0/360
        # Map to -180..+180
        if raw > 180:
            return raw - 360
        return raw
    elif target_angle == 180:
        # Opposition: exact at raw=180
        return raw - 180
    else:
        # For other aspects, there are TWO positions where ang_dist = target
        # Use the nearest one
        d = ang_dist(moon_lon, natal_lon)
        return d - target_angle


def scan_month(year, month, natal_points, tz_offset=-4, step_hours=2):
    """
    Scan the entire month for Moon aspects to natal points.
    Uses 2-hour steps to detect when aspects become exact,
    then binary search for precise timing.
    """
    n_days = days_in_month(year, month)
    jd_start = datetime_to_jd(year, month, 1, 0, 0, 0)  # UTC midnight
    jd_end = datetime_to_jd(year, month, n_days, 23, 59, 0)

    step = step_hours / 24.0  # step in days
    events = []

    for pname, pdata in natal_points.items():
        natal_lon = pdata['longitude']

        for asp_name, asp_def in ASPECTS.items():
            target_angle = asp_def['angle']
            orb_limit = asp_def['orb']

            # Scan through the month
            jd = jd_start
            prev_err = None

            while jd <= jd_end:
                moon_lon = get_moon_lon(jd)

                if target_angle in (0, 180):
                    # Use signed error for conjunction/opposition
                    err = signed_aspect_error(moon_lon, natal_lon, target_angle)
                else:
                    # For other aspects, ang_dist works but we need sign changes
                    diff = ang_dist(moon_lon, natal_lon)
                    err = diff - target_angle

                # Detect zero-crossing (aspect becoming exact)
                if prev_err is not None and abs(err) <= orb_limit + 5:
                    if prev_err * err < 0:  # sign change = crossed exact
                        # Binary search for exact time
                        jd_a, jd_b = jd - step, jd
                        for _ in range(50):
                            jd_mid = (jd_a + jd_b) / 2
                            mid_moon = get_moon_lon(jd_mid)
                            if target_angle in (0, 180):
                                mid_err = signed_aspect_error(mid_moon, natal_lon, target_angle)
                            else:
                                mid_err = ang_dist(mid_moon, natal_lon) - target_angle

                            if abs(mid_err) < 0.001:
                                break

                            # Same sign as prev_err → crossing is after mid
                            err_a_moon = get_moon_lon(jd_a)
                            if target_angle in (0, 180):
                                err_a = signed_aspect_error(err_a_moon, natal_lon, target_angle)
                            else:
                                err_a = ang_dist(err_a_moon, natal_lon) - target_angle

                            if err_a * mid_err > 0:
                                jd_a = jd_mid
                            else:
                                jd_b = jd_mid

                        exact_jd = (jd_a + jd_b) / 2
                        exact_moon = get_moon_lon(exact_jd)
                        exact_diff = ang_dist(exact_moon, natal_lon)
                        exact_orb = abs(exact_diff - target_angle)

                        # Only keep if within actual orb
                        if exact_orb <= orb_limit:
                            dt_local = jd_to_datetime(exact_jd, tz_offset)
                            moon_sign, moon_deg = lon_to_sign(exact_moon)

                            intensity = asp_def['weight'] * pdata['weight']

                            events.append({
                                'datetime': dt_local,
                                'datetime_str': dt_local.strftime('%Y-%m-%d %I:%M %p'),
                                'date_str': dt_local.strftime('%a %b %d'),
                                'time_str': dt_local.strftime('%I:%M %p'),
                                'natal_point': pname,
                                'natal_lon': natal_lon,
                                'natal_formatted': pdata['formatted'],
                                'natal_category': pdata['category'],
                                'aspect': asp_name,
                                'aspect_symbol': asp_def['symbol'],
                                'orb': round(exact_orb, 4),
                                'moon_lon': exact_moon,
                                'moon_sign': moon_sign,
                                'moon_deg': round(moon_deg, 2),
                                'moon_formatted': fmt_degree(exact_moon),
                                'intensity': intensity,
                                'point_weight': pdata['weight'],
                                'aspect_weight': asp_def['weight'],
                                'jd': exact_jd,
                            })

                prev_err = err
                jd += step

    # Deduplicate (same point + same aspect within 4 hours = same event)
    events.sort(key=lambda e: e['jd'])
    deduped = []
    for ev in events:
        is_dup = False
        for existing in deduped:
            if (existing['natal_point'] == ev['natal_point'] and
                existing['aspect'] == ev['aspect'] and
                abs(existing['jd'] - ev['jd']) < 4 / 24.0):
                # Keep the one with tighter orb
                if ev['orb'] < existing['orb']:
                    deduped.remove(existing)
                    deduped.append(ev)
                is_dup = True
                break
        if not is_dup:
            deduped.append(ev)

    deduped.sort(key=lambda e: e['jd'])
    return deduped


# ─── SPECIAL WINDOWS ─────────────────────────────────────────────────────────

def find_special_windows(events, natal_points):
    """Identify the critical monthly windows from the document."""
    windows = []

    # Find IC crossing to Moon conjunction window (11°-16° Pisces)
    ic_conj = [e for e in events if e['natal_point'] == 'IC' and e['aspect'] == 'conjunction']
    moon_conj = [e for e in events if e['natal_point'] == 'Moon' and e['aspect'] == 'conjunction']

    if ic_conj and moon_conj:
        windows.append({
            'name': 'EMOTIONAL RESET WINDOW (IC → Natal Moon)',
            'description': 'Moon transits 11°-16° Pisces. Maximum permeability. Magdalene channel widest. NOT a day for armor or the outside world.',
            'start': ic_conj[0]['datetime_str'],
            'end': moon_conj[0]['datetime_str'],
            'severity': 'CRITICAL',
        })

    # Find Neptune conjunction window (psychic flooding)
    neptune_conj = [e for e in events if e['natal_point'] == 'Neptune' and e['aspect'] == 'conjunction']
    if neptune_conj:
        windows.append({
            'name': 'PSYCHIC FLOODING (Moon ☌ Neptune)',
            'description': 'Moon conjuncts natal Neptune at 15° Sagittarius. Activates Moon-Neptune square. Boundary dissolution. Psychic antenna on full blast.',
            'start': neptune_conj[0]['datetime_str'],
            'end': neptune_conj[0]['datetime_str'],
            'severity': 'HIGH',
        })

    # Venus conjunction (sweet spot)
    venus_conj = [e for e in events if e['natal_point'] == 'Venus' and e['aspect'] == 'conjunction']
    if venus_conj:
        windows.append({
            'name': 'HEART OPENING (Moon ☌ Venus)',
            'description': 'Sweetest transit of the month. Love, connection, beauty, tenderness. Heart leads. Good for partnership and creativity.',
            'start': venus_conj[0]['datetime_str'],
            'end': venus_conj[0]['datetime_str'],
            'severity': 'SUPPORTIVE',
        })

    # Lunar Return
    if moon_conj:
        windows.append({
            'name': 'LUNAR RETURN',
            'description': 'Transiting Moon conjuncts natal Moon. Monthly emotional reset. Everything resets. Maximum permeability. Day for receiving and transmitting.',
            'start': moon_conj[0]['datetime_str'],
            'end': moon_conj[0]['datetime_str'],
            'severity': 'CRITICAL',
        })

    return windows


# ─── OUTPUT FORMATTING ────────────────────────────────────────────────────────

def format_text_report(year, month, events, natal_points, windows):
    """Generate the full text report."""
    month_name = datetime(year, month, 1).strftime('%B %Y')
    lines = []

    lines.append('=' * 78)
    lines.append(f"  SERAPHE — LUNAR TRANSIT MAP — {month_name.upper()}")
    lines.append(f"  Transiting Moon aspects to all natal points")
    lines.append(f"  Birth: August 19, 1978 · 2:02 PM EDT · Norwich, NY")
    lines.append(f"  Times shown in EDT (UTC-4)")
    lines.append('=' * 78)
    lines.append('')

    # ─── SPECIAL WINDOWS ─────────────────────────────────────────────
    if windows:
        lines.append('─' * 78)
        lines.append('  ⚡ KEY WINDOWS THIS MONTH')
        lines.append('─' * 78)
        for w in windows:
            severity_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'SUPPORTIVE': '💚'}.get(w['severity'], '⚪')
            lines.append(f"  {severity_icon} {w['name']}")
            lines.append(f"     {w['start']}")
            lines.append(f"     {w['description']}")
            lines.append('')

    # ─── DAY BY DAY ──────────────────────────────────────────────────
    lines.append('─' * 78)
    lines.append('  📅 DAY-BY-DAY TRANSIT LOG')
    lines.append('─' * 78)
    lines.append('')

    # Group by date
    by_date = {}
    for ev in events:
        date_key = ev['date_str']
        by_date.setdefault(date_key, []).append(ev)

    n_days = days_in_month(year, month)
    for day in range(1, n_days + 1):
        dt = datetime(year, month, day)
        date_key = dt.strftime('%a %b %d')

        # Get Moon sign at noon
        jd_noon = datetime_to_jd(year, month, day, 12, 0, -4)
        noon_moon = get_moon_lon(jd_noon)
        noon_sign, noon_deg = lon_to_sign(noon_moon)
        element = ELEMENT_MAP[noon_sign]
        elem_note = ELEMENT_QUALITY[element]

        day_events = by_date.get(date_key, [])

        if day_events:
            # Compute day intensity
            max_intensity = max(e['intensity'] for e in day_events)
            intensity_bar = '█' * min(max_intensity, 25)

            lines.append(f"  {date_key}  ·  Moon in {SIGN_GLYPHS[noon_sign]} {noon_sign} ({element})")
            lines.append(f"  {elem_note}")
            lines.append(f"  Intensity: {intensity_bar} ({max_intensity})")
            lines.append('')

            for ev in sorted(day_events, key=lambda e: e['jd']):
                lines.append(
                    f"    {ev['time_str']:>8}  "
                    f"{ev['aspect_symbol']} Moon {ev['aspect']:12s} "
                    f"{ev['natal_point']:14s} "
                    f"({ev['natal_formatted']})  "
                    f"orb {ev['orb']:.2f}°  "
                    f"[{ev['natal_category']}]"
                )

            lines.append('')
        else:
            lines.append(f"  {date_key}  ·  Moon in {SIGN_GLYPHS[noon_sign]} {noon_sign} ({element})")
            lines.append(f"  {elem_note}")
            lines.append(f"  — No exact aspects this day —")
            lines.append('')

    # ─── NATAL POINTS REFERENCE ──────────────────────────────────────
    lines.append('─' * 78)
    lines.append('  📍 NATAL POINTS REFERENCE')
    lines.append('─' * 78)
    lines.append('')
    for cat in ['LUNAR CORE', 'PSYCHIC AXIS', 'ANGLES', 'THE LIGHTS',
                'HEART & DRIVE', 'HEAVYWEIGHTS', 'SHADOW']:
        cat_points = {k: v for k, v in natal_points.items() if v['category'] == cat}
        if cat_points:
            lines.append(f"  {cat}")
            for pname, pdata in cat_points.items():
                stars = '★' * pdata['weight'] + '☆' * (5 - pdata['weight'])
                lines.append(f"    {pname:14s}  {pdata['formatted']:20s}  {stars}")
            lines.append('')

    # ─── STATS ────────────────────────────────────────────────────────
    lines.append('─' * 78)
    lines.append('  📊 MONTH SUMMARY')
    lines.append('─' * 78)
    lines.append(f"  Total exact aspects: {len(events)}")

    asp_counts = {}
    for ev in events:
        asp_counts[ev['aspect']] = asp_counts.get(ev['aspect'], 0) + 1
    for asp_name in ASPECTS:
        if asp_name in asp_counts:
            lines.append(f"    {ASPECTS[asp_name]['symbol']} {asp_name:14s}: {asp_counts[asp_name]}")

    # Highest intensity days
    day_intensity = {}
    for ev in events:
        dk = ev['date_str']
        day_intensity[dk] = day_intensity.get(dk, 0) + ev['intensity']
    if day_intensity:
        top_days = sorted(day_intensity.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append('')
        lines.append('  Highest intensity days:')
        for dk, intensity in top_days:
            lines.append(f"    {dk}: {intensity} total intensity")

    lines.append('')
    lines.append('=' * 78)

    return '\n'.join(lines)


def build_json_output(year, month, events, natal_points, windows):
    """Build structured JSON output."""
    month_name = datetime(year, month, 1).strftime('%B %Y')

    # Clean events for JSON (remove non-serializable datetime objects)
    clean_events = []
    for ev in events:
        clean = {k: v for k, v in ev.items() if k != 'datetime'}
        clean_events.append(clean)

    return {
        'meta': {
            'subject': 'Seraphe (Rebecca Lydia Denkers)',
            'birth': 'August 19, 1978 · 2:02 PM EDT · Norwich, NY',
            'month': month_name,
            'year': year,
            'month_num': month,
            'timezone': 'EDT (UTC-4)',
            'total_events': len(events),
            'generated': datetime.now().isoformat(),
        },
        'natal_points': natal_points,
        'special_windows': windows,
        'events': clean_events,
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Seraphe's Monthly Lunar Transit Calculator"
    )
    parser.add_argument(
        'month_year',
        help='Month/Year to calculate, e.g. 03/2026'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Also output JSON format'
    )
    parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output filename base (without extension)'
    )
    parser.add_argument(
        '--tz', type=float, default=-4,
        help='Timezone offset from UTC (default: -4 for EDT)'
    )

    args = parser.parse_args()

    # Parse month/year
    parts = args.month_year.split('/')
    if len(parts) != 2:
        print("Error: Use MM/YYYY format, e.g. 03/2026", file=sys.stderr)
        sys.exit(1)

    month = int(parts[0])
    year = int(parts[1])

    if month < 1 or month > 12:
        print("Error: Month must be 1-12", file=sys.stderr)
        sys.exit(1)

    month_name = datetime(year, month, 1).strftime('%B %Y')
    print(f"Calculating Seraphe's lunar transits for {month_name}...", file=sys.stderr)

    # Step 1: Compute natal points
    print("  Computing natal chart...", file=sys.stderr)
    natal_points = compute_natal_points()

    # Step 2: Scan the month
    print(f"  Scanning {days_in_month(year, month)} days at 2-hour resolution...", file=sys.stderr)
    events = scan_month(year, month, natal_points, tz_offset=args.tz)
    print(f"  Found {len(events)} exact aspects.", file=sys.stderr)

    # Step 3: Identify special windows
    windows = find_special_windows(events, natal_points)

    # Step 4: Generate output
    report = format_text_report(year, month, events, natal_points, windows)

    # Determine output
    if args.output:
        base = args.output
    else:
        base = f"seraphe_lunar_{year}_{month:02d}"

    # Always write text report
    txt_path = f"{base}.txt"
    with open(txt_path, 'w') as f:
        f.write(report)
    print(f"  ✓ Text report: {txt_path}", file=sys.stderr)

    # Print to stdout too
    print(report)

    # JSON if requested
    if args.json:
        json_data = build_json_output(year, month, events, natal_points, windows)
        json_path = f"{base}.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        print(f"  ✓ JSON output: {json_path}", file=sys.stderr)

    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
