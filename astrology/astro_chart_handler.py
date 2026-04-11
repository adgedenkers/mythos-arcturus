#!/opt/mythos/.venv/bin/python3
"""
astro_chart_handler.py - Telegram /chart command for Iris.

Orchestrates the full natal chart pipeline:
  1. Parse birth data from conversational input
  2. Geocode city/state to lat/lng/timezone
  3. Write YAML to /opt/mythos/astrology/user_input/
  4. Run astrochart_cli_engine to generate full chart
  5. Load into PostgreSQL via astro_loader
  6. Return formatted summary to Telegram

Usage (Telegram):
  /chart Sarah Jones, June 15 1990, 2:30pm, Portland OR
  /chart John Smith, 1985-03-22, 14:30, Albany NY
  /chart list                    - list all charts in DB
  /chart lookup Sarah Jones      - show stored chart summary

Author: Ka'tuar'el / Mythos System
"""

import os
import sys
import re
import json
import yaml
import logging
import subprocess
from datetime import datetime
from pathlib import Path

ASTRO_DIR = Path("/opt/mythos/astrology")
sys.path.insert(0, str(ASTRO_DIR))

logger = logging.getLogger("mythos.astro_chart")

VENV_PYTHON = "/opt/mythos/.venv/bin/python3"
USER_INPUT_DIR = ASTRO_DIR / "user_input"
CHARTS_DIR = ASTRO_DIR / "charts"
CLI_TOOL = ASTRO_DIR / "astrochart_cli_tool.py"
LOADER = ASTRO_DIR / "astro_loader.py"

# ── Parsing ────────────────────────────────────────────────────────────────

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
    "oct": 10, "nov": 11, "dec": 12,
}

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}


def parse_date(date_str):
    """Parse flexible date input to YYYY-MM-DD."""
    date_str = date_str.strip().rstrip(",")

    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", date_str)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", date_str)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

    m = re.match(r"^(\w+)\s+(\d{1,2}),?\s+(\d{4})$", date_str, re.IGNORECASE)
    if m:
        month_num = MONTH_MAP.get(m.group(1).lower())
        if month_num:
            return f"{m.group(3)}-{month_num:02d}-{int(m.group(2)):02d}"

    m = re.match(r"^(\d{1,2})\s+(\w+),?\s+(\d{4})$", date_str, re.IGNORECASE)
    if m:
        month_num = MONTH_MAP.get(m.group(2).lower())
        if month_num:
            return f"{m.group(3)}-{month_num:02d}-{int(m.group(1)):02d}"

    return None


def parse_time(time_str):
    """Parse flexible time input to HH:MM (24hr)."""
    time_str = time_str.strip().lower()

    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", time_str)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return f"{h:02d}:{mi:02d}"

    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$", time_str)
    if m:
        h, mi = int(m.group(1)), int(m.group(2) or 0)
        ampm = m.group(3)
        if ampm == "pm" and h != 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return f"{h:02d}:{mi:02d}"

    return None


def parse_location(loc_str):
    """Parse location to (city, state/region)."""
    loc_str = loc_str.strip()
    m = re.match(r"^(.+?)[,\s]+([A-Za-z]{2,})$", loc_str)
    if m:
        city = m.group(1).strip().rstrip(",")
        region = m.group(2).strip()
        if region.upper() in US_STATES:
            return city, region.upper()
        return city, region
    if loc_str and not any(c.isdigit() for c in loc_str):
        return loc_str, ""
    return None


def _merge_comma_parts(raw_parts):
    """Re-merge comma-split parts that belong together."""
    merged = []
    i = 0
    while i < len(raw_parts):
        part = raw_parts[i].strip()
        if i + 1 < len(raw_parts):
            next_part = raw_parts[i + 1].strip()
            if re.match(r"^\d{4}$", next_part) and re.match(r"^\w+\s+\d{1,2}$", part, re.IGNORECASE):
                merged.append(f"{part} {next_part}")
                i += 2
                continue
            if next_part.upper() in US_STATES and not any(c.isdigit() for c in part):
                if parse_date(part) is None and parse_time(part) is None:
                    merged.append(f"{part} {next_part}")
                    i += 2
                    continue
        merged.append(part)
        i += 1
    return merged


def parse_chart_request(text):
    """Parse a /chart command into structured data dict or None."""
    text = re.sub(r"^/chart\s+", "", text, flags=re.IGNORECASE).strip()

    if "|" in text:
        parts = [p.strip() for p in text.split("|")]
    else:
        raw_parts = [p.strip() for p in text.split(",")]
        parts = _merge_comma_parts(raw_parts)

    if len(parts) < 3:
        return None

    name = parts[0].strip()
    if not name:
        return None

    date_str = None
    time_str = None
    loc_str = None

    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        if date_str is None and parse_date(part) is not None:
            date_str = parse_date(part)
        elif time_str is None and parse_time(part) is not None:
            time_str = parse_time(part)
        elif loc_str is None:
            loc_str = part

    if not date_str:
        return None

    if not time_str:
        time_str = "12:00"

    location = parse_location(loc_str) if loc_str else None
    city = location[0] if location else "Unknown"
    region = location[1] if location else ""

    return {
        "name": name,
        "date": date_str,
        "time": time_str,
        "city": city,
        "region": region,
    }


# ── Geocoding ──────────────────────────────────────────────────────────────

def geocode_location(city, region, country="USA"):
    """Geocode city/region to lat, lng, timezone dict. Returns None on failure."""
    try:
        from geopy.geocoders import Nominatim
        from timezonefinder import TimezoneFinder

        geocoder = Nominatim(user_agent="mythos_astrology")
        queries = [
            f"{city}, {region}, {country}" if region else f"{city}, {country}",
            f"{city}, {region}" if region else city,
        ]

        location = None
        for q in queries:
            location = geocoder.geocode(q)
            if location:
                break

        if not location:
            return None

        lat, lng = location.latitude, location.longitude
        tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lng) or "UTC"

        return {
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "timezone": tz_name,
            "display": location.address,
        }
    except Exception as e:
        logger.error(f"Geocode failed for {city}, {region}: {e}")
        return None


# ── YAML Generation ────────────────────────────────────────────────────────

def generate_yaml(parsed, geo):
    """Build YAML-ready dict from parsed input + geocode results."""
    return {
        "name": parsed["name"],
        "birth": {
            "date": parsed["date"],
            "time": parsed["time"],
            "city": parsed["city"],
            "region": parsed["region"],
            "country": "USA",
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
        },
    }


def save_yaml(data, output_dir=None):
    """Write YAML file, return path."""
    if output_dir is None:
        output_dir = USER_INPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", data["name"].lower()).strip("_")
    path = output_dir / f"{safe_name}.yaml"
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    return path


# ── Engine Execution ───────────────────────────────────────────────────────

def run_chart_engine(yaml_path, output_prefix=None):
    """Run the astrochart CLI engine. Returns (success, output_or_error)."""
    if output_prefix is None:
        stem = Path(yaml_path).stem
        output_prefix = str(CHARTS_DIR / stem)

    cmd = [
        VENV_PYTHON,
        str(CLI_TOOL),
        "-f", str(yaml_path),
        "--prefix", output_prefix,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ASTRO_DIR),
            env={**os.environ, "PYTHONPATH": str(ASTRO_DIR)},
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Engine error (rc={result.returncode}):\n{result.stderr}\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return False, "Chart engine timed out (120s)"
    except Exception as e:
        return False, f"Failed to run engine: {e}"


def run_db_loader(chart_dir):
    """Load chart data into PostgreSQL via astro_loader.py."""
    report_path = os.path.join(chart_dir, "natal_report.json")
    if not os.path.exists(report_path):
        full_path = os.path.join(chart_dir, "full_chart.txt")
        if os.path.exists(full_path):
            report_path = full_path
        else:
            return False, f"No natal_report.json or full_chart.txt in {chart_dir}"

    cmd = [VENV_PYTHON, str(LOADER), report_path]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=str(ASTRO_DIR),
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Loader error:\n{result.stderr}\n{result.stdout}"
    except Exception as e:
        return False, f"Failed to run loader: {e}"


# ── Summary Formatting ─────────────────────────────────────────────────────

def format_chart_summary(chart_dir):
    """Build a concise Telegram-friendly chart summary from the output JSONs."""
    lines = []

    meta_path = os.path.join(chart_dir, "chart_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        name = meta.get("Name", "Unknown")
        birth = meta.get("Birth", {})
        lines.append(f"✦ {name.upper()} — NATAL CHART")
        lines.append(f"  Born: {birth.get('Date', '?')} at {birth.get('Time', '?')}")
        lines.append(f"  Place: {birth.get('Place', '?')}")
        lines.append(f"  System: {meta.get('House System', '?')} / {meta.get('Zodiac Type', '?')}")
        lines.append("")

    ruler_path = os.path.join(chart_dir, "chart_ruler.json")
    if os.path.exists(ruler_path):
        with open(ruler_path) as f:
            ruler = json.load(f)
        lines.append(f"☉ ASC: {ruler.get('Ascendant Sign', '?')} — Ruler: {ruler.get('Traditional Ruler', '?')} in {ruler.get('Traditional Ruler Sign', '?')} (H{ruler.get('Traditional Ruler House', '?')})")

    objects_path = os.path.join(chart_dir, "chart_objects.json")
    if os.path.exists(objects_path):
        with open(objects_path) as f:
            objects = json.load(f)
        lines.append("")
        lines.append("PLANETS:")
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            p = objects.get(planet, {})
            if p:
                retro = " ℞" if p.get("Retrograde") else ""
                house = f"H{p.get('House', '?')}"
                lines.append(f"  {planet:<9} {p.get('Full', '?'):<26} {house}{retro}")

        outers = ["Uranus", "Neptune", "Pluto", "Chiron"]
        outer_parts = []
        for planet in outers:
            p = objects.get(planet, {})
            if p:
                retro = "℞" if p.get("Retrograde") else ""
                outer_parts.append(f"{planet[:3]}: {p.get('Sign', '?')} H{p.get('House', '?')}{retro}")
        if outer_parts:
            lines.append(f"  {' | '.join(outer_parts)}")

    sect_path = os.path.join(chart_dir, "sect.json")
    if os.path.exists(sect_path):
        with open(sect_path) as f:
            sect = json.load(f)
        lines.append(f"\n☽ Sect: {sect.get('Sect', '?')} — Light: {sect.get('Sect Light', '?')}, Benefic: {sect.get('Sect Benefic', '?')}")

    balance_path = os.path.join(chart_dir, "balance.json")
    if os.path.exists(balance_path):
        with open(balance_path) as f:
            bal = json.load(f)
        elems = bal.get("Elements", {})
        mods = bal.get("Modalities", {})
        lines.append(f"  Elements: 🔥{elems.get('Fire', 0)} 🌍{elems.get('Earth', 0)} 💨{elems.get('Air', 0)} 💧{elems.get('Water', 0)} → {bal.get('Dominant Element', '?')}")
        lines.append(f"  Modality: Card {mods.get('Cardinal', 0)} | Fix {mods.get('Fixed', 0)} | Mut {mods.get('Mutable', 0)} → {bal.get('Dominant Modality', '?')}")

    patterns_path = os.path.join(chart_dir, "geometric_patterns.json")
    if os.path.exists(patterns_path):
        with open(patterns_path) as f:
            patterns = json.load(f)
        if patterns:
            lines.append(f"\n⬡ Geometric Patterns: {len(patterns)} found")
            for p in patterns[:5]:
                pts = ", ".join(p.get("Points", []))
                lines.append(f"  {p.get('Type', '?')}: {pts}")
            if len(patterns) > 5:
                lines.append(f"  ...and {len(patterns) - 5} more")

    stars_path = os.path.join(chart_dir, "fixed_star_conjunctions.json")
    if os.path.exists(stars_path):
        with open(stars_path) as f:
            stars = json.load(f)
        if stars:
            lines.append(f"\n★ Fixed Stars: {len(stars)} conjunction(s)")
            for s in stars[:3]:
                lines.append(f"  {s.get('Object', '?')} ☌ {s.get('Star', '?')} (orb {s.get('Orb', '?')}°)")

    if not lines:
        return "Chart generated but no summary data available."

    return "\n".join(lines)



# ── Chart Wheel Generation (Kerykeion + CairoSVG) ─────────────────────────

def generate_chart_wheel(chart_dir):
    """
    Generate a natal chart wheel PNG from chart metadata.
    Uses kerykeion for SVG generation, cairosvg for PNG conversion.
    Returns path to PNG or None on failure.
    """
    import yaml as _yaml

    meta_path = os.path.join(chart_dir, "chart_metadata.json")
    if not os.path.exists(meta_path):
        logger.warning(f"No chart_metadata.json in {chart_dir}")
        return None

    with open(meta_path) as f:
        meta = json.load(f)

    birth = meta.get("Birth", {})
    name = meta.get("Name", "Unknown")
    date_str = birth.get("Date", "")
    time_str = birth.get("Time", "")
    lat = birth.get("Latitude")
    lng = birth.get("Longitude")
    tz = birth.get("Timezone", "UTC")
    place = birth.get("Place", "Unknown")

    if not date_str or lat is None:
        logger.warning(f"Incomplete birth data for wheel generation: {name}")
        return None

    try:
        from kerykeion import AstrologicalSubject, KerykeionChartSVG
        import cairosvg

        # Parse date/time
        parts = date_str.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        time_parts = time_str.split(":")
        hour = int(time_parts[0]) if time_parts else 12
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        # City from place string
        city = place.split(",")[0].strip() if place else "Unknown"

        subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            nation="",
            lat=float(lat),
            lng=float(lng),
            tz_str=tz,
        )

        # Generate SVG
        chart_svg = KerykeionChartSVG(subject)
        chart_svg.makeSVG()

        # Find the generated SVG (kerykeion saves to cwd or home)
        svg_path = None
        search_dirs = [os.getcwd(), os.path.expanduser("~"), "/root", "/tmp"]
        for search_dir in search_dirs:
            if not os.path.isdir(search_dir):
                continue
            for f in os.listdir(search_dir):
                if f.endswith(".svg") and name.replace(" ", "_") in f:
                    svg_path = os.path.join(search_dir, f)
                    break
                if f.endswith(".svg") and name in f:
                    svg_path = os.path.join(search_dir, f)
                    break
            if svg_path:
                break

        if not svg_path:
            # Try matching any recently created SVG
            import glob
            import time
            for search_dir in search_dirs:
                for svg in glob.glob(os.path.join(search_dir, "*.svg")):
                    if time.time() - os.path.getmtime(svg) < 30:
                        svg_path = svg
                        break
                if svg_path:
                    break

        if not svg_path:
            logger.warning(f"Could not find generated SVG for {name}")
            return None

        # Move SVG to chart dir
        dest_svg = os.path.join(chart_dir, "natal_wheel.svg")
        os.rename(svg_path, dest_svg)

        # Convert to PNG
        dest_png = os.path.join(chart_dir, "natal_wheel.png")
        cairosvg.svg2png(url=dest_svg, write_to=dest_png, output_width=1200, output_height=1200, background_color="white")

        logger.info(f"Chart wheel generated: {dest_png}")
        return dest_png

    except ImportError as e:
        logger.error(f"Missing dependency for wheel generation: {e}")
        return None
    except Exception as e:
        logger.error(f"Chart wheel generation failed for {name}: {e}", exc_info=True)
        return None


def get_chart_wheel_path(chart_dir):
    """Return path to existing wheel PNG, or generate one."""
    png_path = os.path.join(chart_dir, "natal_wheel.png")
    if os.path.exists(png_path):
        return png_path
    return generate_chart_wheel(chart_dir)


# ── Interactive Chart List ─────────────────────────────────────────────────

def get_chart_list_data():
    """Get chart list from database. Returns list of (chart_id, name, birth_date, birth_time, birth_place)."""
    try:
        import psycopg2
        conn = psycopg2.connect(dbname="mythos", user="postgres", host="/var/run/postgresql")
        cur = conn.cursor()
        cur.execute("""
            SELECT chart_id, name, birth_date, birth_time, birth_place
            FROM astro_natal_charts ORDER BY name
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error listing charts: {e}")
        return []


def format_chart_list():
    """Format chart list as styled text (fallback for CLI)."""
    rows = get_chart_list_data()
    if not rows:
        return "No charts in database."

    SIGN_GLYPHS = {
        "Aries": "\u2648", "Taurus": "\u2649", "Gemini": "\u264a", "Cancer": "\u264b",
        "Leo": "\u264c", "Virgo": "\u264d", "Libra": "\u264e", "Scorpio": "\u264f",
        "Sagittarius": "\u2650", "Capricorn": "\u2651", "Aquarius": "\u2652", "Pisces": "\u2653",
    }

    lines = ["\u2726 *NATAL CHARTS* (" + str(len(rows)) + ")", ""]
    for cid, name, bdate, btime, place in rows:
        # Try to get ASC sign from chart_ruler.json
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower()).strip("_")
        ruler_path = os.path.join(str(CHARTS_DIR), safe_name, "chart_ruler.json")
        asc_info = ""
        if os.path.exists(ruler_path):
            try:
                with open(ruler_path) as f:
                    ruler = json.load(f)
                asc_sign = ruler.get("Ascendant Sign", "")
                asc_info = " " + SIGN_GLYPHS.get(asc_sign, "") if asc_sign else ""
            except Exception:
                pass
        lines.append(asc_info + " *" + name + "*")
        lines.append("  " + str(bdate) + " \u00b7 " + str(btime)[:5] + " \u00b7 " + str(place))
        lines.append("")
    return "\n".join(lines)


def resolve_chart_dir(name):
    """Find chart directory for a name. Tries exact match, then fuzzy."""
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower()).strip("_")
    chart_dir = str(CHARTS_DIR / safe_name)
    if os.path.isdir(chart_dir):
        return chart_dir

    # Try partial match on directory names
    if CHARTS_DIR.exists():
        for d in CHARTS_DIR.iterdir():
            if d.is_dir() and safe_name in d.name.lower():
                return str(d)

    # Try DB lookup for the actual name, then derive dir
    try:
        import psycopg2
        conn = psycopg2.connect(dbname="mythos", user="postgres", host="/var/run/postgresql")
        cur = conn.cursor()
        cur.execute("""
            SELECT name FROM astro_natal_charts
            WHERE LOWER(name) LIKE %s ORDER BY name LIMIT 1
        """, ("%" + name.lower() + "%",))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            db_safe = re.sub(r"[^a-zA-Z0-9_]", "_", row[0].lower()).strip("_")
            db_dir = str(CHARTS_DIR / db_safe)
            if os.path.isdir(db_dir):
                return db_dir
    except Exception:
        pass

    return None


def format_chart_lookup(name):
    """Look up a stored chart by name. Returns text summary."""
    chart_dir = resolve_chart_dir(name)
    if chart_dir:
        return format_chart_summary(chart_dir)
    return "No chart found for '" + name + "'."


# ── Main Pipeline ──────────────────────────────────────────────────────────

def run_full_pipeline(text):
    """Full pipeline: parse > geocode > YAML > engine > loader > summary.
    Returns (text_result, chart_dir_or_none)."""
    stripped = re.sub(r"^/chart\s*", "", text, flags=re.IGNORECASE).strip()

    if stripped.lower() == "list":
        return format_chart_list(), None

    if stripped.lower().startswith("lookup "):
        name = stripped[7:].strip()
        chart_dir = resolve_chart_dir(name)
        if chart_dir:
            return format_chart_summary(chart_dir), chart_dir
        return "No chart found for '" + name + "'.", None

    if stripped.lower() == "help":
        return (
            "\u2726 */chart* \u2014 Natal Chart Generator\n\n"
            "*Usage:*\n"
            "  /chart Name, Date, Time, City State\n\n"
            "*Examples:*\n"
            "  /chart Sarah Jones, June 15 1990, 2:30pm, Portland OR\n"
            "  /chart John Smith, 1985-03-22, 14:30, Albany NY\n\n"
            "*Other:*\n"
            "  /chart list \u2014 all charts (interactive)\n"
            "  /chart lookup <name> \u2014 show stored chart\n"
        ), None

    parsed = parse_chart_request(text)
    if not parsed:
        return (
            "\u26a0\ufe0f Couldn't parse that. Format:\n"
            "  /chart Name, Date, Time, City State\n\n"
            "Examples:\n"
            "  /chart Sarah Jones, June 15 1990, 2:30pm, Portland OR\n"
            "  /chart John Smith, 1985-03-22, 14:30, Albany NY"
        ), None

    geo = geocode_location(parsed["city"], parsed["region"])
    if not geo:
        return "\u26a0\ufe0f Couldn't geocode: " + parsed["city"] + ", " + parsed["region"] + "\nCheck city/state and try again.", None

    yaml_data = generate_yaml(parsed, geo)
    yaml_path = save_yaml(yaml_data)

    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", parsed["name"].lower()).strip("_")
    chart_dir = str(CHARTS_DIR / safe_name)

    status_lines = [
        "\u23f3 Generating chart for " + parsed["name"] + "...",
        "  \U0001f4c5 " + parsed["date"] + " at " + parsed["time"],
        "  \U0001f4cd " + geo["display"],
        "  \U0001f310 " + f"{geo['latitude']:.4f}" + "\u00b0, " + f"{geo['longitude']:.4f}" + "\u00b0 (" + geo["timezone"] + ")",
    ]

    ok, output = run_chart_engine(yaml_path, chart_dir)
    if not ok:
        status_lines.append("\n\u274c Engine failed:\n" + output[:500])
        return "\n".join(status_lines), None

    status_lines.append("  \u2705 Chart engine complete")

    ok_db, db_output = run_db_loader(chart_dir)
    if ok_db:
        status_lines.append("  \u2705 Loaded into PostgreSQL")
    else:
        status_lines.append("  \u26a0\ufe0f DB load: " + db_output[:200])

    summary = format_chart_summary(chart_dir)
    status_lines.append("")
    status_lines.append(summary)

    return "\n".join(status_lines), chart_dir


# ── Telegram Bot Integration ───────────────────────────────────────────────

async def handle_chart_command(update, context):
    """Telegram handler for /chart command."""
    text = update.message.text
    chat_id = update.effective_chat.id
    stripped = re.sub(r"^/chart\s*", "", text, flags=re.IGNORECASE).strip()

    # ── /chart list: interactive with buttons ──
    if stripped.lower() == "list":
        rows = get_chart_list_data()
        if not rows:
            await update.message.reply_text("No charts in database.")
            return

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        SIGN_GLYPHS = {
            "Aries": "\u2648", "Taurus": "\u2649", "Gemini": "\u264a", "Cancer": "\u264b",
            "Leo": "\u264c", "Virgo": "\u264d", "Libra": "\u264e", "Scorpio": "\u264f",
            "Sagittarius": "\u2650", "Capricorn": "\u2651", "Aquarius": "\u2652", "Pisces": "\u2653",
        }

        lines = ["\u2726 *NATAL CHARTS* (" + str(len(rows)) + ")"]
        lines.append("")
        buttons = []
        for cid, name, bdate, btime, place in rows:
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower()).strip("_")
            ruler_path = os.path.join(str(CHARTS_DIR), safe_name, "chart_ruler.json")
            asc_glyph = ""
            if os.path.exists(ruler_path):
                try:
                    with open(ruler_path) as f:
                        ruler = json.load(f)
                    asc_sign = ruler.get("Ascendant Sign", "")
                    asc_glyph = SIGN_GLYPHS.get(asc_sign, "")
                except Exception:
                    pass
            lines.append(asc_glyph + " *" + name + "* \u00b7 " + str(bdate) + " \u00b7 " + str(place))
            btn_label = asc_glyph + " " + name
            buttons.append([InlineKeyboardButton(btn_label, callback_data="chart:" + safe_name)])

        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return

    # ── All other /chart subcommands ──
    progress_msg = await context.bot.send_message(
        chat_id=chat_id, text="\u23f3 Processing chart request..."
    )

    try:
        result, chart_dir = run_full_pipeline(text)

        # Send text result
        if len(result) > 4000:
            chunks = [result[i:i + 4000] for i in range(0, len(result), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await progress_msg.edit_text(chunk, parse_mode="Markdown")
                else:
                    await context.bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown")
        else:
            await progress_msg.edit_text(result, parse_mode="Markdown")

        # Send chart wheel image if available
        if chart_dir:
            wheel_path = get_chart_wheel_path(chart_dir)
            if wheel_path and os.path.exists(wheel_path):
                with open(wheel_path, "rb") as img:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=img,
                        caption="\U0001fa90 Natal Chart Wheel",
                    )

    except Exception as e:
        logger.error(f"Chart command error: {e}", exc_info=True)
        await progress_msg.edit_text("\u274c Error: " + str(e))


async def handle_chart_callback(update, context):
    """Handle inline button clicks from /chart list."""
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    data = query.data  # "chart:safe_name"

    if not data.startswith("chart:"):
        return

    safe_name = data[6:]
    chart_dir = str(CHARTS_DIR / safe_name)

    if not os.path.isdir(chart_dir):
        await query.message.reply_text("Chart directory not found: " + safe_name)
        return

    progress_msg = await context.bot.send_message(
        chat_id=chat_id, text="\u23f3 Loading chart..."
    )

    try:
        summary = format_chart_summary(chart_dir)

        if len(summary) > 4000:
            chunks = [summary[i:i + 4000] for i in range(0, len(summary), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await progress_msg.edit_text(chunk, parse_mode="Markdown")
                else:
                    await context.bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown")
        else:
            await progress_msg.edit_text(summary, parse_mode="Markdown")

        # Send wheel image
        wheel_path = get_chart_wheel_path(chart_dir)
        if wheel_path and os.path.exists(wheel_path):
            with open(wheel_path, "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption="\U0001fa90 Natal Chart Wheel",
                )

    except Exception as e:
        logger.error(f"Chart callback error: {e}", exc_info=True)
        await progress_msg.edit_text("\u274c Error: " + str(e))


def register_handlers(app):
    """Register /chart command and callback handlers with the Telegram bot Application."""
    from telegram.ext import CommandHandler, CallbackQueryHandler
    app.add_handler(CommandHandler("chart", handle_chart_command))
    app.add_handler(CallbackQueryHandler(handle_chart_callback, pattern="^chart:"))
    logger.info("Registered /chart command + callback handlers")


# ── Standalone CLI ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: astro_chart_handler.py '<chart command text>'")
        print("  e.g.: astro_chart_handler.py '/chart Sarah Jones, June 15 1990, 2:30pm, Portland OR'")
        print("  e.g.: astro_chart_handler.py '/chart list'")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    if not text.startswith("/chart"):
        text = "/chart " + text

    result, chart_dir = run_full_pipeline(text)
    print(result)
    if chart_dir:
        wheel = get_chart_wheel_path(chart_dir)
        if wheel:
            print("\nWheel: " + wheel)
