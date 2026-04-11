#!/usr/bin/env python3
"""Natal Chart Generator (Kerykeion). pip install kerykeion"""
import argparse, json, sys
from pathlib import Path

ANGLES = {'Ascendant','Medium_Coeli','Descendant','Imum_Coeli'}

def make_subject(name, year, month, day, hour, minute, lat, lon, tz, city=None, nation=None):
    from kerykeion import AstrologicalSubjectFactory
    return AstrologicalSubjectFactory.from_birth_data(
        name, year, month, day, hour, minute,
        city=city, nation=nation,
        lng=lon, lat=lat, tz_str=tz, online=False)

def from_json(path):
    with open(path) as f: d = json.load(f)
    m = d.get('meta', {})
    bd = m.get('birth_date','').split('-')
    bt = m.get('birth_time','').split(':')
    tz_hrs = m.get('tz', 0)
    sign = '+' if tz_hrs >= 0 else '-'
    tz_s = 'Etc/GMT%s%d' % (sign, abs(tz_hrs))
    return make_subject(m.get('name','Chart'),
        int(bd[0]),int(bd[1]),int(bd[2]),
        int(bt[0]),int(bt[1]),m['lat'],m['lon'],tz_s)

def render(subject, output, theme, wheel_only, grid_only, with_angles):
    from kerykeion.chart_data_factory import ChartDataFactory
    from kerykeion.charts.chart_drawer import ChartDrawer
    cd = ChartDataFactory.create_natal_chart_data(subject)
    if not with_angles:
        cd.aspects = [a for a in cd.aspects
            if a.p1_name not in ANGLES and a.p2_name not in ANGLES]
    dr = ChartDrawer(chart_data=cd, theme=theme)
    out = Path(output).parent; out.mkdir(exist_ok=True)
    fname = Path(output).stem
    if wheel_only:
        dr.save_wheel_only_svg_file(output_path=out, filename=fname)
    elif grid_only:
        dr.save_aspect_grid_only_svg_file(output_path=out, filename=fname)
    else:
        dr.save_svg(output_path=out, filename=fname)
    print('Chart saved:', output)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Natal Chart Generator')
    p.add_argument('--json', help='Input JSON')
    p.add_argument('--name', default='Chart')
    p.add_argument('--year', type=int)
    p.add_argument('--month', type=int)
    p.add_argument('--day', type=int)
    p.add_argument('--hour', type=int, default=12)
    p.add_argument('--minute', type=int, default=0)
    p.add_argument('--lat', type=float)
    p.add_argument('--lon', type=float)
    p.add_argument('--tz', default='America/New_York')
    p.add_argument('--city', default=None)
    p.add_argument('--nation', default=None)
    p.add_argument('--output', default='chart.svg')
    p.add_argument('--theme', default='classic')
    p.add_argument('--wheel-only', action='store_true')
    p.add_argument('--grid-only', action='store_true')
    p.add_argument('--with-angles', action='store_true')
    a = p.parse_args()
    if a.json: subj = from_json(a.json)
    elif a.year: subj = make_subject(a.name,a.year,a.month,a.day,a.hour,a.minute,a.lat,a.lon,a.tz,a.city,a.nation)
    else: p.error('Provide --json or birth data')
    render(subj, a.output, a.theme, a.wheel_only, a.grid_only, a.with_angles)
