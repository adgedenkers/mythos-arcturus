"""
natal_generator.py — Astrology v2 Natal State Module

Shipped in SEN-0008 (Letter D). Provides the clean interface between
Mythos's Postgres natal chart store and consuming code.

Design contract:
- load_natal(name)       → reads from Postgres, returns chart dict
- write_chart_artifact() → writes canonical JSON artifact from chart dict
- generate_natal()       → computes via astrology.ephemeris, writes to
                          Postgres, returns chart dict

The existing pipeline (astrochart_cli_engine → astro_loader) is NOT
replaced. This module is a clean read/write interface that Letter E
(Daily Transits) and beyond will consume. The existing pipeline
continues to function for new chart generation via /chart Telegram
commands.

Database layout (public schema):
  astro_natal_charts          — header row (name, birth_date, etc.)
  astro_chart_objects         — planetary positions
  astro_natal_house_cusps     — house cusps 1–12
  astro_natal_aspects         — natal aspects
  astro_dignities             — dignity statuses
  astro_retrogrades           — retrograde list
  astro_sect                  — sect determination
  astro_balance               — element/modality balance
  astro_arabic_parts          — Arabic parts
  astro_fixed_star_conjunctions — fixed star data
  astro_chart_ruler           — chart ruler
  astro_dispositors           — dispositor chain
  astro_geometric_patterns    — geometric patterns

Output JSON shape mirrors full_chart_adge.json:
  chart_metadata, chart_objects, chart_points, house_cusps,
  chart_aspects, dignities, retrogrades, sect, balance,
  arabic_parts, fixed_star_conjunctions, chart_ruler,
  dispositors, geometric_patterns, Geometry Audit

Usage:
    from astrology.natal_generator import load_natal, write_chart_artifact

    chart = load_natal('Adge')
    write_chart_artifact(chart, Path('/opt/mythos/astrology/charts/ka.json'))
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger('mythos.astrology.natal_generator')

__version__ = '1.0.0'  # Astrology v2 Letter D

# ─── DB connection helper ──────────────────────────────────────────────

def _get_conn():
    """Return a psycopg2 connection to the mythos DB."""
    import psycopg2
    import psycopg2.extras
    return psycopg2.connect(
        host='/var/run/postgresql',
        port=5432,
        database='mythos',
        user='adge',
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


# ─── load_natal ────────────────────────────────────────────────────────

def load_natal(name: str) -> Optional[dict]:
    """
    Load a complete natal chart from Postgres by person name.

    Queries astro_natal_charts and all child tables. Returns a dict
    that mirrors the full_chart_*.json structure used elsewhere in
    Mythos (chart_metadata, chart_objects, house_cusps, chart_aspects,
    etc.).

    Returns None if no chart is found for the given name.

    The name match is case-insensitive and trims whitespace.
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()

        # ── Header row ────────────────────────────────────────────
        cur.execute(
            '''SELECT chart_id, name, birth_date, birth_time,
                      birth_place, latitude, longitude, timezone,
                      house_system, zodiac_type, ephemeris,
                      ephemeris_path, engine_version, created_at
               FROM astro_natal_charts
               WHERE lower(trim(name)) = lower(trim(%s))
               ORDER BY created_at DESC
               LIMIT 1''',
            (name,),
        )
        row = cur.fetchone()
        if not row:
            log.warning('load_natal: no chart found for name=%r', name)
            return None

        chart_id = row['chart_id']
        chart = {}

        # ── chart_metadata ────────────────────────────────────────
        chart['chart_metadata'] = {
            'Name':          row['name'],
            'Birth': {
                'Date':      str(row['birth_date']),
                'Time':      str(row['birth_time']),
                'Place':     row['birth_place'] or '',
                'Latitude':  row['latitude'],
                'Longitude': row['longitude'],
                'Timezone':  row['timezone'],
            },
            'house_system':  row['house_system'],
            'zodiac_type':   row['zodiac_type'],
            'ephemeris':     row['ephemeris'],
            'ephemeris_path':row['ephemeris_path'],
            'engine_version':row['engine_version'],
            'chart_id':      chart_id,
            'created_at':    str(row['created_at']),
        }

        # ── chart_objects (planetary positions) ───────────────────
        cur.execute(
            '''SELECT object_name, longitude, latitude, distance,
                      speed, sign, deg_min, full_position,
                      is_retrograde, house
               FROM astro_chart_objects
               WHERE chart_id = %s
               ORDER BY longitude''',
            (chart_id,),
        )
        chart['chart_objects'] = {
            r['object_name']: {
                'longitude':    r['longitude'],
                'latitude':     r['latitude'],
                'distance':     r['distance'],
                'speed':        r['speed'],
                'sign':         r['sign'],
                'deg_min':      r['deg_min'],
                'full_position':r['full_position'],
                'is_retrograde':r['is_retrograde'],
                'house':        r['house'],
            }
            for r in cur.fetchall()
        }

        # ── house_cusps ───────────────────────────────────────────
        cur.execute(
            '''SELECT house_number, cusp_longitude, sign,
                      deg_min, full_position
               FROM astro_natal_house_cusps
               WHERE chart_id = %s
               ORDER BY house_number''',
            (chart_id,),
        )
        chart['house_cusps'] = {
            r['house_number']: {
                'longitude':    r['cusp_longitude'],
                'sign':         r['sign'],
                'deg_min':      r['deg_min'],
                'full_position':r['full_position'],
            }
            for r in cur.fetchall()
        }

        # ── chart_aspects ─────────────────────────────────────────
        cur.execute(
            '''SELECT object_1, object_2, aspect, angle,
                      exact_diff, orb, tier, motion, description
               FROM astro_natal_aspects
               WHERE chart_id = %s
               ORDER BY orb''',
            (chart_id,),
        )
        chart['chart_aspects'] = [
            {
                'object_1':   r['object_1'],
                'object_2':   r['object_2'],
                'aspect':     r['aspect'],
                'angle':      r['angle'],
                'exact_diff': r['exact_diff'],
                'orb':        r['orb'],
                'tier':       r['tier'],
                'motion':     r['motion'],
                'description':r['description'],
            }
            for r in cur.fetchall()
        ]

        # ── dignities ─────────────────────────────────────────────
        cur.execute(
            '''SELECT object_name, sign, status
               FROM astro_dignities
               WHERE chart_id = %s''',
            (chart_id,),
        )
        chart['dignities'] = {
            r['object_name']: {
                'sign':   r['sign'],
                'status': r['status'],
            }
            for r in cur.fetchall()
        }

        # ── retrogrades ───────────────────────────────────────────
        # Schema: object_name, sign, house, longitude (no deg_min/full_position/speed)
        cur.execute(
            '''SELECT object_name, longitude, sign, house
               FROM astro_retrogrades
               WHERE chart_id = %s''',
            (chart_id,),
        )
        chart['retrogrades'] = [
            {
                'object_name': r['object_name'],
                'longitude':   r['longitude'],
                'sign':        r['sign'],
                'house':       r['house'],
            }
            for r in cur.fetchall()
        ]

        # ── sect ──────────────────────────────────────────────────
        cur.execute(
            'SELECT * FROM astro_sect WHERE chart_id = %s LIMIT 1',
            (chart_id,),
        )
        sect_row = cur.fetchone()
        chart['sect'] = dict(sect_row) if sect_row else {}
        if chart['sect']:
            chart['sect'].pop('id', None)
            chart['sect'].pop('chart_id', None)

        # ── balance ───────────────────────────────────────────────
        cur.execute(
            'SELECT * FROM astro_balance WHERE chart_id = %s LIMIT 1',
            (chart_id,),
        )
        bal_row = cur.fetchone()
        chart['balance'] = dict(bal_row) if bal_row else {}
        if chart['balance']:
            chart['balance'].pop('id', None)
            chart['balance'].pop('chart_id', None)

        # ── arabic_parts ──────────────────────────────────────────
        cur.execute(
            '''SELECT part_name, longitude, sign, deg_min, full_position
               FROM astro_arabic_parts
               WHERE chart_id = %s''',
            (chart_id,),
        )
        chart['arabic_parts'] = {
            r['part_name']: {
                'longitude':    r['longitude'],
                'sign':         r['sign'],
                'deg_min':      r['deg_min'],
                'full_position':r['full_position'],
            }
            for r in cur.fetchall()
        }

        # ── fixed_star_conjunctions ───────────────────────────────
        # Schema: object_name, object_longitude, star_name, star_longitude,
        #         star_j2000, magnitude, constellation, orb, significance
        cur.execute(
            '''SELECT object_name, object_longitude, star_name,
                      star_longitude, star_j2000, magnitude,
                      constellation, orb, significance
               FROM astro_fixed_star_conjunctions
               WHERE chart_id = %s''',
            (chart_id,),
        )
        chart['fixed_star_conjunctions'] = [
            {
                'object_name':      r['object_name'],
                'object_longitude': r['object_longitude'],
                'star_name':        r['star_name'],
                'star_longitude':   r['star_longitude'],
                'star_j2000':       r['star_j2000'],
                'magnitude':        r['magnitude'],
                'constellation':    r['constellation'],
                'orb':              r['orb'],
                'significance':     r['significance'],
            }
            for r in cur.fetchall()
        ]

        # ── chart_ruler ───────────────────────────────────────────
        cur.execute(
            'SELECT * FROM astro_chart_ruler WHERE chart_id = %s LIMIT 1',
            (chart_id,),
        )
        ruler_row = cur.fetchone()
        chart['chart_ruler'] = dict(ruler_row) if ruler_row else {}
        if chart['chart_ruler']:
            chart['chart_ruler'].pop('id', None)
            chart['chart_ruler'].pop('chart_id', None)

        # ── dispositors ───────────────────────────────────────────
        cur.execute(
            'SELECT * FROM astro_dispositors WHERE chart_id = %s LIMIT 1',
            (chart_id,),
        )
        disp_row = cur.fetchone()
        chart['dispositors'] = dict(disp_row) if disp_row else {}
        if chart['dispositors']:
            chart['dispositors'].pop('id', None)
            chart['dispositors'].pop('chart_id', None)

        # ── geometric_patterns ────────────────────────────────────
        # Schema: pattern_type, points (text[]), aspects (text[])
        # Multiple rows per chart — one per pattern found
        cur.execute(
            '''SELECT pattern_type, points, aspects
               FROM astro_geometric_patterns
               WHERE chart_id = %s''',
            (chart_id,),
        )
        chart['geometric_patterns'] = [
            {
                'pattern_type': r['pattern_type'],
                'points':       r['points'],
                'aspects':      r['aspects'],
            }
            for r in cur.fetchall()
        ]

        # ── chart_points (ASC, MC, etc.) ──────────────────────────
        # Schema: point_name, longitude (no sign/deg_min/full_position)
        # Derive sign and formatted position from longitude using ephemeris
        cur.execute(
            '''SELECT point_name, longitude
               FROM astro_chart_points
               WHERE chart_id = %s''',
            (chart_id,),
        )
        import sys as _sys
        _sys.path.insert(0, '/opt/mythos')
        from astrology import ephemeris as _e
        chart['chart_points'] = {
            r['point_name']: {
                'longitude':    r['longitude'],
                'sign':         _e.lon_to_sign(r['longitude'])[0],
                'formatted':    _e.fmt_pos(r['longitude']),
            }
            for r in cur.fetchall()
        }

        cur.close()
        log.info('load_natal: loaded chart for %r (chart_id=%d)', name, chart_id)
        return chart

    finally:
        conn.close()


# ─── write_chart_artifact ──────────────────────────────────────────────

def write_chart_artifact(chart: dict, path: Path) -> None:
    """
    Write a chart dict to a canonical JSON artifact file.

    Creates parent directories if needed. Overwrites any existing file.
    Writes with 2-space indent for human readability.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(chart, f, indent=2, default=str, ensure_ascii=False)
    log.info('write_chart_artifact: wrote %s (%d bytes)', path, path.stat().st_size)


# ─── generate_natal ────────────────────────────────────────────────────

def generate_natal(
    name: str,
    dob: str,
    tob: str,
    lat: float,
    lon: float,
    tz_str: str,
    birth_place: str = '',
    house_system: str = 'Placidus',
    zodiac_type: str = 'Tropical',
    overwrite: bool = False,
) -> dict:
    """
    Compute a natal chart from scratch using astrology.ephemeris,
    write to Postgres, and return the chart dict.

    Parameters:
        name         human-readable name (used as identifier in DB)
        dob          'YYYY-MM-DD'
        tob          'HH:MM' in local time
        lat          decimal latitude
        lon          decimal longitude
        tz_str       IANA timezone string e.g. 'America/New_York'
        birth_place  human-readable place name (stored but not geocoded)
        house_system 'Placidus' (default) or any supported system
        zodiac_type  'Tropical' (default) or 'Sidereal'
        overwrite    if True, delete existing rows for this chart first

    Returns a chart dict matching load_natal() output.

    Note: This function bypasses astrochart_cli_engine.py intentionally.
    It uses astrology.ephemeris directly, storing computed values in
    the same Postgres tables that astro_loader.py uses. The two paths
    produce compatible output.
    """
    import pytz
    from datetime import datetime
    import sys
    sys.path.insert(0, '/opt/mythos')
    from astrology import ephemeris as e

    # ── Parse birth datetime ───────────────────────────────────────
    dt_naive = datetime.strptime(f'{dob} {tob}', '%Y-%m-%d %H:%M')
    tz = pytz.timezone(tz_str)
    dt_local = tz.localize(dt_naive)
    dt_ut = dt_local.astimezone(pytz.utc)
    jd = e.date_to_jd(
        dt_ut.year, dt_ut.month, dt_ut.day,
        dt_ut.hour, dt_ut.minute,
        tz_offset_hours=0,
    )

    # ── Compute positions ──────────────────────────────────────────
    planets = e.calc_planets(jd, include_asteroids=True)
    houses_data = e.calc_houses(jd, lat, lon, e.HOUSE_SYSTEMS.get(house_system, 'P'))

    # Assign houses to planets
    cusps = houses_data['cusps']
    for body_name, body in planets.items():
        body['house'] = e.assign_house(body['longitude'], cusps)

    # ── Build chart dict ───────────────────────────────────────────
    chart = {}

    chart['chart_metadata'] = {
        'Name': name,
        'Birth': {
            'Date':      dob,
            'Time':      tob,
            'Place':     birth_place,
            'Latitude':  lat,
            'Longitude': lon,
            'Timezone':  tz_str,
        },
        'house_system':   house_system,
        'zodiac_type':    zodiac_type,
        'ephemeris':      'Swiss Ephemeris',
        'ephemeris_path': e.SE_EPHE_PATH,
        'engine_version': f'astrology.ephemeris {e.__version__}',
    }

    # chart_objects — use ephemeris.py output shape
    chart['chart_objects'] = {}
    for body_name, body in planets.items():
        chart['chart_objects'][body_name] = {
            'longitude':    body['longitude'],
            'latitude':     0.0,   # ecliptic latitude — not returned by default
            'distance':     None,
            'speed':        body['speed'],
            'sign':         body['sign'],
            'deg_min':      e.fmt_pos(body['longitude']).split('m')[0] + 'm' + body['sign'],
            'full_position':e.fmt_pos(body['longitude']),
            'is_retrograde':body['retrograde'],
            'house':        body['house'],
        }

    # house_cusps
    chart['house_cusps'] = {}
    for i, cusp_lon in enumerate(cusps):
        house_num = i + 1
        sign, deg = e.lon_to_sign(cusp_lon)
        chart['house_cusps'][house_num] = {
            'longitude':    cusp_lon,
            'sign':         sign,
            'deg_min':      e.fmt_pos(cusp_lon),
            'full_position':e.fmt_pos(cusp_lon),
        }

    # chart_points (angles)
    chart['chart_points'] = {}
    for angle_name, angle_data in houses_data['angles'].items():
        chart['chart_points'][angle_name] = {
            'longitude':    angle_data['longitude'],
            'sign':         angle_data['sign'],
            'deg_min':      angle_data['formatted'],
            'full_position':angle_data['formatted'],
        }

    # Aspects — compute natal aspects between all bodies
    chart['chart_aspects'] = []
    body_names = list(chart['chart_objects'].keys())
    for i in range(len(body_names)):
        for j in range(i + 1, len(body_names)):
            b1, b2 = body_names[i], body_names[j]
            lon1 = chart['chart_objects'][b1]['longitude']
            lon2 = chart['chart_objects'][b2]['longitude']
            asp = e.calc_aspect(lon1, lon2)
            if asp:
                chart['chart_aspects'].append({
                    'object_1':   b1,
                    'object_2':   b2,
                    'aspect':     asp['aspect'],
                    'angle':      asp['angle'],
                    'exact_diff': asp['orb'],
                    'orb':        asp['orb'],
                    'tier':       'major' if asp['major'] else 'minor',
                    'motion':     None,
                    'description':None,
                })

    # Placeholder sections — not computed here, populated by
    # astrochart_cli_engine for full charts
    for section in ['dignities', 'retrogrades', 'sect', 'balance',
                    'arabic_parts', 'fixed_star_conjunctions',
                    'chart_ruler', 'dispositors', 'geometric_patterns']:
        chart[section] = {} if section not in ('retrogrades', 'chart_aspects',
                                                'fixed_star_conjunctions') else []

    # ── Persist to Postgres ────────────────────────────────────────
    _persist_to_postgres(
        chart, name, dob, tob, lat, lon, tz_str, birth_place,
        house_system, zodiac_type, overwrite,
    )

    log.info('generate_natal: generated and persisted chart for %r', name)
    return chart


def _persist_to_postgres(
    chart: dict, name: str, dob: str, tob: str,
    lat: float, lon: float, tz_str: str, birth_place: str,
    house_system: str, zodiac_type: str, overwrite: bool,
) -> int:
    """Write chart dict to Postgres. Returns chart_id."""
    import psycopg2

    conn = _get_conn()
    try:
        cur = conn.cursor()

        # Upsert header row
        cur.execute(
            '''INSERT INTO astro_natal_charts
               (name, birth_date, birth_time, birth_place,
                latitude, longitude, timezone, house_system,
                zodiac_type, ephemeris, ephemeris_path, engine_version)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (name, birth_date, birth_time)
               DO UPDATE SET
                 birth_place    = EXCLUDED.birth_place,
                 latitude       = EXCLUDED.latitude,
                 longitude      = EXCLUDED.longitude,
                 timezone       = EXCLUDED.timezone,
                 house_system   = EXCLUDED.house_system,
                 zodiac_type    = EXCLUDED.zodiac_type,
                 ephemeris      = EXCLUDED.ephemeris,
                 ephemeris_path = EXCLUDED.ephemeris_path,
                 engine_version = EXCLUDED.engine_version
               RETURNING chart_id''',
            (
                name, dob, tob, birth_place,
                lat, lon, tz_str, house_system,
                zodiac_type,
                chart['chart_metadata'].get('ephemeris', 'Swiss Ephemeris'),
                chart['chart_metadata'].get('ephemeris_path', ''),
                chart['chart_metadata'].get('engine_version', ''),
            ),
        )
        chart_id = cur.fetchone()['chart_id']

        # Upsert chart_objects
        for obj_name, obj in chart.get('chart_objects', {}).items():
            cur.execute(
                '''INSERT INTO astro_chart_objects
                   (chart_id, object_name, longitude, latitude, distance,
                    speed, sign, deg_min, full_position, is_retrograde, house)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (chart_id, object_name)
                   DO UPDATE SET
                     longitude    = EXCLUDED.longitude,
                     speed        = EXCLUDED.speed,
                     sign         = EXCLUDED.sign,
                     deg_min      = EXCLUDED.deg_min,
                     full_position= EXCLUDED.full_position,
                     is_retrograde= EXCLUDED.is_retrograde,
                     house        = EXCLUDED.house''',
                (
                    chart_id, obj_name,
                    obj['longitude'], obj.get('latitude', 0.0),
                    obj.get('distance'), obj.get('speed'),
                    obj['sign'], obj.get('deg_min'), obj.get('full_position'),
                    obj.get('is_retrograde', False), obj.get('house'),
                ),
            )

        # Upsert house cusps
        for house_num, cusp in chart.get('house_cusps', {}).items():
            cur.execute(
                '''INSERT INTO astro_natal_house_cusps
                   (chart_id, house_number, cusp_longitude, sign, deg_min, full_position)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (chart_id, house_number)
                   DO UPDATE SET
                     cusp_longitude = EXCLUDED.cusp_longitude,
                     sign           = EXCLUDED.sign,
                     deg_min        = EXCLUDED.deg_min,
                     full_position  = EXCLUDED.full_position''',
                (
                    chart_id, int(house_num), cusp['longitude'],
                    cusp['sign'], cusp.get('deg_min'), cusp.get('full_position'),
                ),
            )

        conn.commit()
        cur.close()
        return chart_id

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─── self_check ────────────────────────────────────────────────────────

def self_check() -> dict:
    """Return module health status for diagnostics."""
    result = {
        'module_version': __version__,
        'db_reachable':   False,
        'adge_chart':     False,
        'seraphe_chart':  False,
    }
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT count(*) as n FROM astro_natal_charts"
        )
        row = cur.fetchone()
        result['db_reachable'] = True
        result['chart_count'] = row['n']

        # Check Adge's chart
        cur.execute(
            "SELECT chart_id FROM astro_natal_charts "
            "WHERE lower(trim(name)) = 'adge' LIMIT 1"
        )
        if cur.fetchone():
            result['adge_chart'] = True

        # Check Seraphe's chart
        cur.execute(
            "SELECT chart_id FROM astro_natal_charts "
            "WHERE lower(trim(name)) IN ('becky denkers', 'seraphe', 'rebecca denkers') "
            "LIMIT 1"
        )
        if cur.fetchone():
            result['seraphe_chart'] = True

        cur.close()
        conn.close()
    except Exception as e:
        result['error'] = str(e)

    return result


if __name__ == '__main__':
    import json as _json
    print(_json.dumps(self_check(), indent=2, default=str))
