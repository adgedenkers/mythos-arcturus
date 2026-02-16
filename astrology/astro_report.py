#!/usr/bin/env python3
"""
astro_report.py — Family chart comparison CSV.

Usage:
    python astro_report.py [output.csv]
"""

import sys
import csv
import psycopg2

CONN_PARAMS = dict(dbname="mythos", user="postgres", host="/var/run/postgresql")

# Fixed person order
PERSON_ORDER = ["Adge", "Fitz", "Becky", "Brandi", "Riley"]

# Sign abbreviations
SIGN_ABBR = {
    "Aries": "ARI", "Taurus": "TAU", "Gemini": "GEM", "Cancer": "CAN",
    "Leo": "LEO", "Virgo": "VIR", "Libra": "LIB", "Scorpio": "SCO",
    "Sagittarius": "SAG", "Capricorn": "CAP", "Aquarius": "AQU", "Pisces": "PIS"
}

OBJECT_ORDER = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Lilith", "Mean Node", "True Node", "South Node"
]

POINT_ORDER = ["Ascendant", "Midheaven", "Descendant", "IC", "Vertex", "ARMC"]

HOUSE_ORDER = list(range(1, 13))

PART_ORDER = [
    "Part of Fortune", "Part of Spirit", "Part of Eros", "Part of Marriage",
    "Part of Death", "Part of Commerce", "Part of Courage", "Part of Fatality",
    "Part of Passion"
]


def lon_to_parts(lon):
    """Convert ecliptic longitude to (degrees, minutes, sign_abbr)."""
    sign_idx = int(lon / 30) % 12
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    sign = signs[sign_idx]
    deg_in_sign = lon % 30
    d = int(deg_in_sign)
    m = int(round((deg_in_sign - d) * 60))
    if m == 60:
        d += 1
        m = 0
    return str(d).zfill(2), str(m).zfill(2), SIGN_ABBR[sign]


def parse_degmin(degmin_str):
    """Parse '00°08'' style string into (deg, min)."""
    if not degmin_str or degmin_str == "—":
        return "", ""
    # Remove degree symbol and minute symbol
    s = degmin_str.replace("°", " ").replace("'", "").strip()
    parts = s.split()
    if len(parts) >= 2:
        return parts[0].zfill(2), parts[1].zfill(2)
    return s.zfill(2), "00"


def main():
    outpath = sys.argv[1] if len(sys.argv) > 1 else "/opt/mythos/astrology/reports/family_chart_comparison.csv"

    conn = psycopg2.connect(**CONN_PARAMS)
    cur = conn.cursor()

    # Get charts - map names to match our order
    cur.execute("SELECT chart_id, name FROM astro_natal_charts ORDER BY name")
    charts = {name: cid for cid, name in cur.fetchall()}
    
    print(f"Charts in DB: {list(charts.keys())}")
    
    # Map DB names to our display names (handle Rebecca/Becky etc)
    name_map = {}
    for display_name in PERSON_ORDER:
        # Try exact match first
        if display_name in charts:
            name_map[display_name] = charts[display_name]
        else:
            # Try partial/alternate matches
            for db_name, cid in charts.items():
                if db_name.lower().startswith(display_name.lower()[:3]):
                    name_map[display_name] = cid
                    break
                # Rebecca -> Becky
                if display_name == "Becky" and db_name.lower() in ("rebecca", "seraphe", "becky"):
                    name_map[display_name] = cid
                    break

    found = [n for n in PERSON_ORDER if n in name_map]
    missing = [n for n in PERSON_ORDER if n not in name_map]
    if missing:
        print(f"WARNING: No chart found for: {', '.join(missing)}")
    print(f"Using: {found}")

    chart_ids = [name_map[n] for n in found]

    # Build header
    header = ["Class", "Object"]
    for n in found:
        header.extend([f"{n}_Deg", f"{n}_Min", f"{n}_Sign"])

    rows = []

    def blank_row():
        rows.append([""] * len(header))

    def add_row(cls, obj, data_by_name):
        """data_by_name = {name: (deg, min, sign)} """
        row = [cls, obj]
        for n in found:
            d = data_by_name.get(n, ("", "", ""))
            row.extend([d[0], d[1], d[2]])
        rows.append(row)

    # =========================================================
    # PLANETS
    # =========================================================
    cur.execute("""
        SELECT c.name, o.object_name, o.longitude, o.sign, o.deg_min, o.is_retrograde
        FROM astro_chart_objects o
        JOIN astro_natal_charts c ON c.chart_id = o.chart_id
        WHERE o.chart_id = ANY(%s)
    """, (chart_ids,))

    obj_data = {}
    for db_name, obj, lon, sign, degmin, retro in cur.fetchall():
        # Reverse map db_name to display name
        for display, cid in name_map.items():
            if charts.get(db_name) == cid or any(charts[k] == cid for k in charts if k == db_name):
                if display not in obj_data:
                    obj_data[display] = {}
                d, m = parse_degmin(degmin)
                s = SIGN_ABBR.get(sign, sign or "")
                if retro:
                    s += " R"
                obj_data[display][obj] = (d, m, s)
                break

    for obj in OBJECT_ORDER:
        vals = {}
        for n in found:
            vals[n] = obj_data.get(n, {}).get(obj, ("", "", ""))
        add_row("Planet", obj, vals)

    blank_row()

    # =========================================================
    # ANGLES
    # =========================================================
    cur.execute("""
        SELECT c.name, p.point_name, p.longitude
        FROM astro_chart_points p
        JOIN astro_natal_charts c ON c.chart_id = p.chart_id
        WHERE p.chart_id = ANY(%s)
    """, (chart_ids,))

    pt_data = {}
    for db_name, point, lon in cur.fetchall():
        for display, cid in name_map.items():
            if charts.get(db_name) == cid or any(charts[k] == cid for k in charts if k == db_name):
                if display not in pt_data:
                    pt_data[display] = {}
                d, m, s = lon_to_parts(lon)
                pt_data[display][point] = (d, m, s)
                break

    for pt in POINT_ORDER:
        vals = {}
        for n in found:
            vals[n] = pt_data.get(n, {}).get(pt, ("", "", ""))
        add_row("Angle", pt, vals)

    blank_row()

    # =========================================================
    # HOUSE CUSPS
    # =========================================================
    cur.execute("""
        SELECT c.name, h.house_number, h.cusp_longitude, h.sign, h.deg_min
        FROM astro_natal_house_cusps h
        JOIN astro_natal_charts c ON c.chart_id = h.chart_id
        WHERE h.chart_id = ANY(%s)
    """, (chart_ids,))

    house_data = {}
    for db_name, hnum, lon, sign, degmin in cur.fetchall():
        for display, cid in name_map.items():
            if charts.get(db_name) == cid or any(charts[k] == cid for k in charts if k == db_name):
                if display not in house_data:
                    house_data[display] = {}
                d, m = parse_degmin(degmin)
                s = SIGN_ABBR.get(sign, sign or "")
                house_data[display][hnum] = (d, m, s)
                break

    for h in HOUSE_ORDER:
        vals = {}
        for n in found:
            vals[n] = house_data.get(n, {}).get(h, ("", "", ""))
        add_row("House", f"House {h}", vals)

    blank_row()

    # =========================================================
    # ARABIC PARTS
    # =========================================================
    cur.execute("""
        SELECT c.name, a.part_name, a.longitude, a.sign, a.deg_min
        FROM astro_arabic_parts a
        JOIN astro_natal_charts c ON c.chart_id = a.chart_id
        WHERE a.chart_id = ANY(%s)
    """, (chart_ids,))

    ap_data = {}
    all_parts = set()
    for db_name, part, lon, sign, degmin in cur.fetchall():
        for display, cid in name_map.items():
            if charts.get(db_name) == cid or any(charts[k] == cid for k in charts if k == db_name):
                if display not in ap_data:
                    ap_data[display] = {}
                d, m = parse_degmin(degmin)
                s = SIGN_ABBR.get(sign, sign or "")
                ap_data[display][part] = (d, m, s)
                all_parts.add(part)
                break

    for part in PART_ORDER:
        if part in all_parts:
            vals = {}
            for n in found:
                vals[n] = ap_data.get(n, {}).get(part, ("", "", ""))
            add_row("Arabic Part", part, vals)
    # Any extra parts not in our order
    for part in sorted(all_parts - set(PART_ORDER)):
        vals = {}
        for n in found:
            vals[n] = ap_data.get(n, {}).get(part, ("", "", ""))
        add_row("Arabic Part", part, vals)

    # =========================================================
    # WRITE CSV
    # =========================================================
    import os
    os.makedirs(os.path.dirname(outpath) if os.path.dirname(outpath) else ".", exist_ok=True)

    with open(outpath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            while len(row) < len(header):
                row.append("")
            writer.writerow(row)

    print(f"\n✓ CSV written to {outpath}")
    print(f"  {len(rows)} rows, {len(found)} people, {len(header)} columns")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
