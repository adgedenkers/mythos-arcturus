#!/usr/bin/env python3
"""
weekly_report.py — Astrological transit report using kerykeion 5.10+

Usage:
    python3 weekly_report.py                              # this week, full roster
    python3 weekly_report.py --core                       # this week, core roster
    python3 weekly_report.py 2026-04-12 2026-04-18        # custom range, full
    python3 weekly_report.py 2026-04-12 2026-04-18 --core
    python3 weekly_report.py --people adge,seraphe
"""

import json, sys
from datetime import date, datetime, timedelta
from pathlib import Path

from kerykeion import (
    AstrologicalSubject,
    AstrologicalSubjectFactory,
    EphemerisDataFactory,
    TransitsTimeRangeFactory,
    NatalAspects,
)

PEOPLE_FILE = Path('/opt/mythos/astrology/people.json')

# Points as kerykeion expects them (capitalized for API, lowercased for attribute access)
CORE_POINTS = [
    'Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto',
    'Chiron','Mean_Lilith',
    'True_North_Lunar_Node','True_South_Lunar_Node',
    'Ascendant','Medium_Coeli','Descendant','Imum_Coeli',
]

FULL_POINTS = CORE_POINTS + [
    'Pholus','Ceres','Pallas','Juno','Vesta',
    'Eris','Sedna','Haumea','Makemake','Ixion','Orcus','Quaoar',
    'Pars_Fortunae','Pars_Spiritus','Pars_Amoris','Pars_Fidei',
    'Vertex','Anti_Vertex','Regulus','Spica',
    'Mean_North_Lunar_Node','Mean_South_Lunar_Node','True_Lilith',
]

ASPECTS_LIST = [
    {'name': 'conjunction',    'orb': 8},
    {'name': 'opposition',     'orb': 8},
    {'name': 'trine',          'orb': 7},
    {'name': 'square',         'orb': 6},
    {'name': 'sextile',        'orb': 5},
    {'name': 'quincunx',       'orb': 3},
    {'name': 'semi-sextile',   'orb': 2},
    {'name': 'semi-square',    'orb': 2},
    {'name': 'sesquiquadrate', 'orb': 2},
    {'name': 'quintile',       'orb': 2},
    {'name': 'biquintile',     'orb': 2},
]

AEON5_START = date(2026, 3, 20)
def nine_day_sun(d):
    days = (d - AEON5_START).days
    if days < 0: return "pre-5"
    cycle = days // 9
    day_of_cycle = (days % 9) + 1
    season = cycle // 3 + 1
    month = cycle // 9 + 1
    return f"5.{month}.{season}.{day_of_cycle}"

SIGNS = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']
def fmt_lon(lon):
    si = int(lon // 30)
    deg = lon - si*30
    d = int(deg); m = int((deg-d)*60)
    return f"{d:2d}°{m:02d}' {SIGNS[si]}"

def load_people():
    return json.loads(PEOPLE_FILE.read_text())

def build_subject(pdata, active_points=None):
    """Build AstrologicalSubjectModel from people.json record with full active_points."""
    return AstrologicalSubjectFactory.from_birth_data(
        name=pdata['name'],
        year=pdata['year'], month=pdata['month'], day=pdata['day'],
        hour=pdata.get('hour') or 12,
        minute=pdata.get('minute') or 0,
        city=pdata.get('city'),
        nation=pdata.get('nation','US'),
        lng=pdata.get('lng'),
        lat=pdata.get('lat'),
        tz_str=pdata.get('tz_str','America/New_York'),
        online=False,
        active_points=active_points,
    )

def subject_for_date(d, active_points):
    """Build a transit subject at noon local ET for the given date, Oxford NY."""
    return AstrologicalSubjectFactory.from_birth_data(
        name='Transit', year=d.year, month=d.month, day=d.day,
        hour=12, minute=0,
        city='Oxford', nation='US',
        lng=-75.5977, lat=42.4423,
        tz_str='America/New_York', online=False,
        active_points=active_points,
    )

def extract_positions(subject, active_points):
    """Pull every active point as (name, dict) from subject.model_dump()."""
    d = subject.model_dump()
    out = {}
    for pname in active_points:
        key = pname.lower()
        obj = d.get(key)
        if isinstance(obj, dict) and 'abs_pos' in obj and obj.get('abs_pos') is not None:
            out[pname] = obj
    return out

def parse_args():
    args = sys.argv[1:]
    mode = 'full'; people_filter = None; dates = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--core': mode = 'core'
        elif a == '--full': mode = 'full'
        elif a == '--people':
            i += 1; people_filter = args[i].split(',')
        elif a.startswith('20') and '-' in a:
            dates.append(date.fromisoformat(a))
        i += 1
    if len(dates) == 2:
        start, end = dates
    elif len(dates) == 1:
        start = dates[0]; end = start + timedelta(days=6)
    else:
        today = date.today()
        days_until_sat = (5 - today.weekday()) % 7 or 7
        start = today; end = today + timedelta(days=days_until_sat)
    return start, end, mode, people_filter

def main():
    start, end, mode, people_filter = parse_args()
    active_points = FULL_POINTS if mode == 'full' else CORE_POINTS

    out = []
    def p(s=''): out.append(s)

    p("="*78)
    p(f"ASTROLOGICAL REPORT — {mode.upper()} roster ({len(active_points)} points requested)")
    p(f"Range: {start.isoformat()} → {end.isoformat()}")
    p(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    p("="*78)

    people_all = load_people()
    if people_filter:
        people_all = {k: v for k, v in people_all.items() if k in people_filter}

    subjects = {}
    p("\n--- NATAL CHARTS ---")
    for key, pdata in people_all.items():
        try:
            subj = build_subject(pdata)
            subjects[key] = subj
            sun_sign = subj.sun.sign if hasattr(subj.sun, 'sign') else subj.sun['sign']
            moon_sign = subj.moon.sign if hasattr(subj.moon, 'sign') else subj.moon['sign']
            asc_sign = subj.first_house.sign if hasattr(subj.first_house, 'sign') else subj.first_house['sign']
            p(f"  ✓ {pdata['name']:12s} {sun_sign} Sun, {moon_sign} Moon, {asc_sign} Rising")
        except Exception as e:
            p(f"  ✗ {key}: {e}")

    # Daily positions — build one transit subject per day, extract all active points
    p("\n" + "="*78)
    p("DAILY TRANSIT POSITIONS (noon ET, Oxford NY)")
    p("="*78)
    daily_transit_subjects = []
    for i in range((end - start).days + 1):
        dd = start + timedelta(days=i)
        ts = subject_for_date(dd, active_points)
        daily_transit_subjects.append((dd, ts))
        positions = extract_positions(ts, active_points)

        p(f"\n### {dd.isoformat()} ({dd.strftime('%A')}) — Nine Day Sun {nine_day_sun(dd)}")
        aries = []
        for pname in active_points:
            if pname not in positions: continue
            obj = positions[pname]
            lon = obj['abs_pos']
            retro = ' R' if obj.get('retrograde') else '  '
            p(f"  {pname:24s} {fmt_lon(lon)}{retro}")
            if obj.get('sign') == 'Ari':
                aries.append((pname, lon - int(lon//30)*30))
        if aries:
            aries.sort(key=lambda x: x[1])
            p(f"  ARIES STELLIUM ({len(aries)}): " + ', '.join(f"{n}@{d:.1f}°" for n,d in aries))

    # Per-person transit aspects
    for key, subj in subjects.items():
        p("\n" + "="*78)
        p(f"TRANSIT ASPECTS — {subj.name.upper()}")
        p("="*78)
        try:
            factory = TransitsTimeRangeFactory(
                natal_chart=subj,
                ephemeris_data_points=[ts for _, ts in daily_transit_subjects],
                active_points=[pt for pt in active_points if pt in CORE_POINTS],
                active_aspects=ASPECTS_LIST,
            )
            result = factory.get_transit_moments()
            for i, moment in enumerate(result.transits):
                dd = start + timedelta(days=i)
                p(f"\n--- {dd.isoformat()} ({dd.strftime('%A')}) ---")
                asp_list = getattr(moment, 'aspects', None) or []
                if not asp_list:
                    p("  (no aspects in orb)")
                    continue
                asp_sorted = sorted(asp_list, key=lambda x: x.orbit)
                for a in asp_sorted:
                    p(f"  T:{a.p1_name:22s} {a.aspect:14s} N:{a.p2_name:22s}  orb {a.orbit:5.2f}°")
        except Exception as e:
            import traceback
            p(f"  ERROR: {e}")
            p(traceback.format_exc())

    p("\n" + "="*78)
    p("NATAL CHART REMINDERS (tight aspects <2°)")
    p("="*78)
    for key, subj in subjects.items():
        p(f"\n--- {subj.name} ---")
        try:
            na = NatalAspects(subj, active_points=[pt for pt in active_points if pt in CORE_POINTS],
                              active_aspects=ASPECTS_LIST)
            tight = sorted([a for a in na.all_aspects if a.orbit < 2.0], key=lambda x: x.orbit)
            for a in tight[:20]:
                p(f"  {a.p1_name:22s} {a.aspect:14s} {a.p2_name:22s}  orb {a.orbit:5.2f}°")
        except Exception as e:
            p(f"  ERROR: {e}")

    p("\n" + "="*78)
    p("END OF REPORT")
    p("="*78)
    print("\n".join(out))

if __name__ == '__main__':
    main()
