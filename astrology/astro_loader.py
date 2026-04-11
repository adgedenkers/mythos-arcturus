#!/usr/bin/env python3
"""
astro_loader.py — Load consolidated astrology chart JSON into PostgreSQL (mythos db).

Usage:
    /opt/mythos/.venv/bin/python3 astro_loader.py <consolidated_chart.txt>

Input format — either:
  A) Concatenated JSON files with === filename.json === delimiters
  B) A single natal_report.json (which contains all sections)

Idempotent: re-running for the same chart (name+date+time) replaces old data.
"""

import sys
import json
import re
import psycopg2
from psycopg2.extras import Json


# ------------------------------------------------------------------
# 1. Parse the consolidated text file into individual JSON objects
# ------------------------------------------------------------------

def parse_consolidated(filepath: str) -> dict[str, any]:
    """Parse a file with === name.json === delimiters into {name: parsed_json}."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    sections = {}
    parts = re.split(r'^===\s*(.+?\.json)\s*===$', raw, flags=re.MULTILINE)

    if len(parts) < 3:
        # Maybe it's a single natal_report.json
        try:
            data = json.loads(raw.strip())
            if "Chart Metadata" in data:
                return unpack_natal_report(data)
            else:
                print("ERROR: Single JSON file but not a natal_report format.")
                sys.exit(1)
        except json.JSONDecodeError:
            print("ERROR: Could not parse file as JSON or consolidated format.")
            sys.exit(1)

    for i in range(1, len(parts), 2):
        filename = parts[i].strip()
        content = parts[i + 1].strip()
        if not content:
            continue
        try:
            sections[filename] = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"WARNING: Could not parse {filename}: {e}")

    return sections


def unpack_natal_report(report: dict) -> dict[str, any]:
    """Unpack a natal_report.json into individual section dicts."""
    mapping = {
        "chart_metadata.json": report.get("Chart Metadata"),
        "chart_objects.json": report.get("Planetary Positions"),
        "chart_points.json": report.get("Chart Points (Angles)"),
        "chart_aspects.json": report.get("Aspects"),
        "house_cusps.json": report.get("House Cusps"),
        "arabic_parts.json": report.get("Arabic Parts"),
        "balance.json": report.get("Balance"),
        "chart_ruler.json": report.get("Chart Ruler"),
        "dignities.json": report.get("Essential Dignities"),
        "dispositors.json": report.get("Dispositor Chain"),
        "fixed_star_conjunctions.json": report.get("Fixed Star Conjunctions"),
        "geometric_patterns.json": report.get("Geometric Patterns"),
        "Geometry Audit.json": report.get("Geometry Audit"),
        "retrogrades.json": report.get("Retrograde Bodies"),
        "sect.json": report.get("Sect"),
    }
    return {k: v for k, v in mapping.items() if v is not None}


# ------------------------------------------------------------------
# 2. Insert functions — one per table
# ------------------------------------------------------------------

def upsert_chart(cur, meta: dict) -> int:
    """Insert or replace the chart record. Returns chart_id."""
    birth = meta["Birth"]
    name = meta["Name"]
    bdate = birth["Date"]
    btime = birth["Time"]

    # Delete existing chart with same identity (cascade deletes children)
    cur.execute(
        "DELETE FROM astro_natal_charts WHERE name = %s AND birth_date = %s AND birth_time = %s",
        (name, bdate, btime)
    )

    cur.execute("""
        INSERT INTO astro_natal_charts
            (name, birth_date, birth_time, birth_place, latitude, longitude,
             timezone, house_system, zodiac_type, ephemeris, ephemeris_path, engine_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING chart_id
    """, (
        name, bdate, btime, birth["Place"],
        birth["Latitude"], birth["Longitude"], birth["Timezone"],
        meta.get("House System", "Placidus"),
        meta.get("Zodiac Type", "Tropical"),
        meta.get("Ephemeris"),
        meta.get("Ephemeris Path"),
        meta.get("Engine Version"),
    ))
    return cur.fetchone()[0]


def insert_objects(cur, chart_id: int, objects: dict):
    for name, obj in objects.items():
        cur.execute("""
            INSERT INTO astro_chart_objects
                (chart_id, object_name, longitude, latitude, distance, speed,
                 sign, deg_min, full_position, is_retrograde, house)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            chart_id, name,
            obj["Longitude"], obj.get("Latitude"), obj.get("Distance"), obj.get("Speed"),
            obj["Sign"], obj.get("DegMin"), obj.get("Full"),
            obj.get("Retrograde", False), obj.get("House"),
        ))


def insert_points(cur, chart_id: int, points: dict):
    for name, lon in points.items():
        cur.execute("""
            INSERT INTO astro_chart_points (chart_id, point_name, longitude)
            VALUES (%s, %s, %s)
        """, (chart_id, name, lon))


def insert_house_cusps(cur, chart_id: int, cusps: dict):
    for num_str, cusp in cusps.items():
        cur.execute("""
            INSERT INTO astro_natal_house_cusps
                (chart_id, house_number, cusp_longitude, sign, deg_min, full_position)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            chart_id, int(num_str),
            cusp["Cusp"], cusp["Sign"], cusp.get("DegMin"), cusp.get("Full"),
        ))


def insert_aspects(cur, chart_id: int, aspects: list):
    for a in aspects:
        cur.execute("""
            INSERT INTO astro_natal_aspects
                (chart_id, object_1, object_2, aspect, angle,
                 exact_diff, orb, tier, motion, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            chart_id, a["Object 1"], a["Object 2"], a["Aspect"],
            a["Angle"], a["Exact Difference"], a["Orb"],
            a["Tier"], a.get("Motion"), a.get("Description"),
        ))


def insert_arabic_parts(cur, chart_id: int, parts: dict):
    for name, p in parts.items():
        cur.execute("""
            INSERT INTO astro_arabic_parts
                (chart_id, part_name, longitude, sign, deg_min, full_position, house, formula)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            chart_id, name,
            p["Longitude"], p["Sign"], p.get("DegMin"), p.get("Full"),
            p.get("House"), p.get("Formula"),
        ))


def insert_dignities(cur, chart_id: int, dignities: dict):
    for name, d in dignities.items():
        cur.execute("""
            INSERT INTO astro_dignities (chart_id, object_name, sign, status)
            VALUES (%s, %s, %s, %s)
        """, (chart_id, name, d["Sign"], d["Status"]))


def insert_retrogrades(cur, chart_id: int, retros: list):
    for r in retros:
        cur.execute("""
            INSERT INTO astro_retrogrades (chart_id, object_name, sign, house, longitude)
            VALUES (%s, %s, %s, %s, %s)
        """, (chart_id, r["Object"], r["Sign"], r.get("House"), r["Longitude"]))


def insert_fixed_stars(cur, chart_id: int, stars: list):
    for s in stars:
        cur.execute("""
            INSERT INTO astro_fixed_star_conjunctions
                (chart_id, object_name, object_longitude, star_name, star_longitude,
                 star_j2000, magnitude, constellation, orb, significance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            chart_id, s["Object"], s["Object_Longitude"],
            s["Star"], s["Star_Longitude"], s.get("Star_J2000"),
            s.get("Magnitude"), s.get("Constellation"),
            s["Orb"], s.get("Significance"),
        ))


def insert_patterns(cur, chart_id: int, patterns: list):
    for p in patterns:
        cur.execute("""
            INSERT INTO astro_geometric_patterns (chart_id, pattern_type, points, aspects)
            VALUES (%s, %s, %s, %s)
        """, (chart_id, p["Type"], p["Points"], p.get("Aspects", [])))


def insert_geometry_audit(cur, chart_id: int, audit: dict):
    for ptype, a in audit.items():
        cur.execute("""
            INSERT INTO astro_geometry_audit
                (chart_id, pattern_type, expected_count, detected_count, status, missing, extra)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            chart_id, ptype,
            a["expected_count"], a["detected_count"], a["status"],
            Json(a.get("missing", [])), Json(a.get("extra", [])),
        ))


def insert_balance(cur, chart_id: int, bal: dict):
    e = bal.get("Elements", {})
    m = bal.get("Modalities", {})
    p = bal.get("Polarities", {})
    cur.execute("""
        INSERT INTO astro_balance
            (chart_id, fire, earth, air, water, dominant_element,
             cardinal, fixed, mutable, dominant_modality,
             positive, negative, dominant_polarity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        chart_id,
        e.get("Fire", 0), e.get("Earth", 0), e.get("Air", 0), e.get("Water", 0),
        bal.get("Dominant Element"),
        m.get("Cardinal", 0), m.get("Fixed", 0), m.get("Mutable", 0),
        bal.get("Dominant Modality"),
        p.get("Positive", 0), p.get("Negative", 0),
        bal.get("Dominant Polarity"),
    ))


def insert_sect(cur, chart_id: int, sect: dict):
    cur.execute("""
        INSERT INTO astro_sect
            (chart_id, sect, sect_light, sect_benefic, sect_malefic,
             contra_light, contra_benefic, contra_malefic)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        chart_id, sect["Sect"], sect["Sect Light"],
        sect["Sect Benefic"], sect["Sect Malefic"],
        sect["Contra Light"], sect["Contra Benefic"], sect["Contra Malefic"],
    ))


def insert_chart_ruler(cur, chart_id: int, ruler: dict):
    cur.execute("""
        INSERT INTO astro_chart_ruler
            (chart_id, ascendant_sign, traditional_ruler, ruler_sign, ruler_house)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        chart_id, ruler["Ascendant Sign"],
        ruler["Traditional Ruler"], ruler["Traditional Ruler Sign"],
        ruler["Traditional Ruler House"],
    ))


def insert_dispositors(cur, chart_id: int, disp: dict):
    cur.execute("""
        INSERT INTO astro_dispositors
            (chart_id, chain, final_dispositors, mutual_receptions,
             circular_loops, classical_mutual_receptions, modern_mutual_receptions)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        chart_id,
        Json(disp.get("Chain", {})),
        Json(disp.get("Final Dispositors", [])),
        Json(disp.get("Mutual Receptions", [])),
        Json(disp.get("Circular Loops", [])),
        Json(disp.get("Classical Mutual Receptions", [])),
        Json(disp.get("Modern Mutual Receptions", [])),
    ))


# ------------------------------------------------------------------
# 3. Main
# ------------------------------------------------------------------

TABLE_LIST = [
    'astro_natal_charts', 'astro_chart_objects', 'astro_chart_points',
    'astro_natal_house_cusps', 'astro_natal_aspects', 'astro_arabic_parts',
    'astro_dignities', 'astro_retrogrades', 'astro_fixed_star_conjunctions',
    'astro_geometric_patterns', 'astro_geometry_audit', 'astro_balance',
    'astro_sect', 'astro_chart_ruler', 'astro_dispositors',
]

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <consolidated_chart.txt>")
        print(f"       {sys.argv[0]} <natal_report.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Parsing {filepath}...")
    sections = parse_consolidated(filepath)

    print(f"  Found sections: {', '.join(sorted(sections.keys()))}")

    meta = sections.get("chart_metadata.json")
    if not meta:
        print("ERROR: No chart_metadata.json found in input.")
        sys.exit(1)

    conn = psycopg2.connect(dbname="mythos", user="postgres", host="/var/run/postgresql")
    conn.autocommit = False
    cur = conn.cursor()

    try:
        chart_id = upsert_chart(cur, meta)
        print(f"  Chart inserted: id={chart_id}, name={meta['Name']}")

        loaders = {
            "chart_objects.json":            lambda d: insert_objects(cur, chart_id, d),
            "chart_points.json":             lambda d: insert_points(cur, chart_id, d),
            "house_cusps.json":              lambda d: insert_house_cusps(cur, chart_id, d),
            "chart_aspects.json":            lambda d: insert_aspects(cur, chart_id, d),
            "arabic_parts.json":             lambda d: insert_arabic_parts(cur, chart_id, d),
            "dignities.json":                lambda d: insert_dignities(cur, chart_id, d),
            "retrogrades.json":              lambda d: insert_retrogrades(cur, chart_id, d),
            "fixed_star_conjunctions.json":  lambda d: insert_fixed_stars(cur, chart_id, d),
            "geometric_patterns.json":       lambda d: insert_patterns(cur, chart_id, d),
            "Geometry Audit.json":           lambda d: insert_geometry_audit(cur, chart_id, d),
            "balance.json":                  lambda d: insert_balance(cur, chart_id, d),
            "sect.json":                     lambda d: insert_sect(cur, chart_id, d),
            "chart_ruler.json":              lambda d: insert_chart_ruler(cur, chart_id, d),
            "dispositors.json":              lambda d: insert_dispositors(cur, chart_id, d),
        }

        loaded = []
        skipped = []
        for filename, loader_fn in loaders.items():
            data = sections.get(filename)
            if data is not None:
                loader_fn(data)
                loaded.append(filename)
            else:
                skipped.append(filename)

        conn.commit()

        print(f"\n  === Load Summary for '{meta['Name']}' (chart_id={chart_id}) ===")
        print(f"  Loaded: {len(loaded)} sections")
        for f in loaded:
            print(f"    ✓ {f}")
        if skipped:
            print(f"  Skipped (not in input): {len(skipped)} sections")
            for f in skipped:
                print(f"    — {f}")

        print(f"\n  === Row Counts ===")
        for table in TABLE_LIST:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE chart_id = %s", (chart_id,))
            cnt = cur.fetchone()[0]
            print(f"    {table:40s} {cnt} rows")

        print("\n  ✓ Done.")

    except Exception as e:
        conn.rollback()
        print(f"\n  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
