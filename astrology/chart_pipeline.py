"""
Astro Chart Pipeline — Birth Time Sourcing + Auto Chart Generation

When the person intelligence pipeline encounters someone with a DOB but
no birth time, this module:
  1. Checks astrotheme.com for a known birth time
  2. If found, updates the people table with the time
  3. Generates a full natal chart via the existing astro_chart_handler pipeline
  4. Stores SVG/PNG in /opt/mythos/astrology/charts/{safe_name}/

Can also be called standalone to generate charts for anyone in the
people table who has sufficient data (DOB + time + city).

Cross-stream: SEN owns this file. Writes to SYS-owned people table
(birth time updates only). Reads from NEU person_researcher records.
"""

import json
import logging
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple

log = logging.getLogger("iris.chart_pipeline")

ASTRO_DIR = Path("/opt/mythos/astrology")
CHARTS_DIR = ASTRO_DIR / "charts"

# Astrotheme URL pattern
ASTROTHEME_URL = "https://www.astrotheme.com/astrology/{name}"
REQUEST_TIMEOUT = 15


# ═══════════════════════════════════════════════════
# BIRTH TIME SOURCING
# ═══════════════════════════════════════════════════

def search_astrotheme(first_name: str, last_name: str) -> Optional[Dict]:
    """
    Search astrotheme.com for a person's birth time and location.

    Returns dict with any found data:
        {"birth_time": "19:24", "birth_city": "Kesswil", "birth_country": "Switzerland",
         "rodden_rating": "AA", "source": "astrotheme"}
    Or None if not found.
    """
    # Build the URL — astrotheme uses First_Last format
    name_slug = f"{first_name}_{last_name}".replace(" ", "_")
    url = ASTROTHEME_URL.format(name=name_slug)

    log.info(f"Checking astrotheme for birth time: {first_name} {last_name} ({url})")

    html = _fetch_page(url)
    if not html:
        # Try with full name variations
        for slug in _name_variations(first_name, last_name):
            html = _fetch_page(ASTROTHEME_URL.format(name=slug))
            if html:
                break

    if not html:
        log.info(f"No astrotheme page found for {first_name} {last_name}")
        return None

    result = _parse_astrotheme(html)
    if result:
        log.info(f"Astrotheme birth time found: {first_name} {last_name} -> {result}")
    return result


def _fetch_page(url: str) -> Optional[str]:
    """Fetch a page, return HTML or None."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
            if r.status == 200:
                return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        log.debug(f"Astrotheme HTTP error {e.code}: {url}")
    except Exception as e:
        log.debug(f"Astrotheme fetch failed: {e}")
    return None


def _name_variations(first: str, last: str) -> list:
    """Generate URL slug variations for name lookup."""
    variations = []
    # Full first name + last name
    variations.append(f"{first}_{last}")
    # First initial + last name (for people known by short names)
    if len(first) > 1:
        variations.append(f"{first[0]}_{last}")
    # Handle multi-part last names
    if " " in last:
        # "da Vinci" -> "Leonardo_da_Vinci"
        variations.append(f"{first}_{'_'.join(last.split())}")
    # Handle "von", "de", "van" prefixes
    for prefix in ["von_", "de_", "van_", "di_"]:
        if prefix.replace("_", " ") in last.lower():
            clean = last.lower().replace(prefix.replace("_", " "), "").strip()
            variations.append(f"{first}_{clean}")
    return variations


def _parse_astrotheme(html: str) -> Optional[Dict]:
    """
    Extract birth data from an astrotheme page.
    Looks for patterns like:
        "Born: July 26, 1875, 7:24 PM"
        "In: Kesswil (Switzerland)"
    """
    result = {}

    # Extract birth time — look for time pattern near "Born" or in the birth data section
    # Pattern: "Month DD, YYYY, H:MM AM/PM"
    time_match = re.search(
        r'(\w+ \d{1,2},?\s+\d{4}),?\s+(\d{1,2}:\d{2}\s*(?:AM|PM))',
        html, re.IGNORECASE
    )
    if time_match:
        date_str = time_match.group(1)
        time_str = time_match.group(2).strip()
        result["birth_time_raw"] = time_str
        result["birth_time"] = _convert_to_24h(time_str)

    if not result.get("birth_time"):
        # Try another pattern — just H:MM AM/PM near birth-related context
        # Look within 500 chars of "born" keyword
        born_idx = html.lower().find("born")
        if born_idx > 0:
            snippet = html[born_idx:born_idx + 500]
            time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', snippet, re.IGNORECASE)
            if time_match:
                result["birth_time_raw"] = time_match.group(1).strip()
                result["birth_time"] = _convert_to_24h(time_match.group(1).strip())

    # Extract birth location — "in: City (Country)" or "In City, Country"
    loc_match = re.search(
        r'(?:in|In)\s*:?\s*([A-Z][\w\s-]+?)(?:\s*\(([^)]+)\)|\s*,\s*([A-Z][\w\s]+))',
        html
    )
    if loc_match:
        city = loc_match.group(1).strip() if loc_match.group(1) else None
        country = loc_match.group(2) or loc_match.group(3)
        if city:
            result["birth_city"] = city
        if country:
            result["birth_country"] = country.strip()

    # Check for Rodden rating
    rodden_match = re.search(r'Rodden[:\s]+([A-Z]{1,2})', html, re.IGNORECASE)
    if rodden_match:
        result["rodden_rating"] = rodden_match.group(1).upper()

    if result.get("birth_time"):
        result["source"] = "astrotheme"
        return result

    return None


def _convert_to_24h(time_str: str) -> str:
    """Convert '7:24 PM' to '19:24'."""
    time_str = time_str.strip().upper()
    match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
    if not match:
        return time_str

    hour = int(match.group(1))
    minute = int(match.group(2))
    ampm = match.group(3)

    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


# ═══════════════════════════════════════════════════
# DATABASE UPDATES
# ═══════════════════════════════════════════════════

def update_birth_time(db_config: dict, person_id: int, birth_time: str,
                      birth_city: str = None, birth_country: str = None,
                      source: str = "astrotheme"):
    """Update a person's birth time (and optionally city/country) in the people table."""
    import psycopg2

    host = db_config.get("host", "localhost")
    conn_kwargs = {
        "host": "/var/run/postgresql" if host in ("localhost", "127.0.0.1", "") else host,
        "port": db_config.get("port", 5432),
        "database": db_config.get("database", "mythos"),
        "user": db_config.get("user", "adge"),
    }
    if host not in ("localhost", "127.0.0.1", ""):
        conn_kwargs["password"] = db_config.get("password", "")

    conn = psycopg2.connect(**conn_kwargs)
    try:
        cur = conn.cursor()
        updates = ["time_of_birth = %s"]
        values = [birth_time]

        if birth_city:
            updates.append("birth_city = COALESCE(birth_city, %s)")
            values.append(birth_city)
        if birth_country:
            updates.append("birth_country = COALESCE(birth_country, %s)")
            values.append(birth_country)

        values.append(person_id)
        cur.execute(
            f"UPDATE people SET {', '.join(updates)} WHERE id = %s AND time_of_birth IS NULL",
            values,
        )
        updated = cur.rowcount
        conn.commit()
        cur.close()

        if updated:
            log.info(f"Updated birth time for person_id={person_id}: {birth_time} (source: {source})")
        return updated > 0
    finally:
        conn.close()


# ═══════════════════════════════════════════════════
# CHART GENERATION
# ═══════════════════════════════════════════════════

def generate_chart_for_person(db_config: dict, person_id: int) -> Optional[str]:
    """
    Generate a natal chart for a person in the people table.
    Uses the existing astro_chart_handler pipeline.

    Returns path to the chart directory, or None if insufficient data.
    """
    import psycopg2
    import psycopg2.extras

    host = db_config.get("host", "localhost")
    conn_kwargs = {
        "host": "/var/run/postgresql" if host in ("localhost", "127.0.0.1", "") else host,
        "port": db_config.get("port", 5432),
        "database": db_config.get("database", "mythos"),
        "user": db_config.get("user", "adge"),
        "cursor_factory": psycopg2.extras.RealDictCursor,
    }
    if host not in ("localhost", "127.0.0.1", ""):
        conn_kwargs["password"] = db_config.get("password", "")

    conn = psycopg2.connect(**conn_kwargs)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM people WHERE id = %s", (person_id,))
        row = cur.fetchone()
        cur.close()

        if not row:
            log.warning(f"Person {person_id} not found")
            return None

        dob = row.get("date_of_birth")
        tob = row.get("time_of_birth")
        city = row.get("birth_city")
        state = row.get("birth_state")
        country = row.get("birth_country")
        first = row["first_name"]
        middle = row.get("middle_name", "")
        last = row["last_name"]
        full_name = " ".join(p for p in [first, middle, last] if p).strip()

        if not dob:
            log.info(f"No DOB for {full_name} — cannot generate chart")
            return None

        if not tob:
            log.info(f"No birth time for {full_name} — will use noon chart")
            hour, minute = 12, 0
            is_noon = True
        else:
            tob_str = str(tob)
            parts = tob_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            is_noon = False

        if not city:
            log.info(f"No birth city for {full_name} — cannot geocode, skipping chart")
            return None

        # Build safe directory name
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', full_name.lower().replace(" ", "_"))
        chart_dir = str(CHARTS_DIR / safe_name)
        os.makedirs(chart_dir, exist_ok=True)

        # Geocode
        sys.path.insert(0, str(ASTRO_DIR))
        try:
            from astro_chart_handler import geocode_location
            geo = geocode_location(city, state or "", country or "USA")
            if not geo:
                log.warning(f"Geocoding failed for {city}, {state}")
                return None
            lat = geo["latitude"]
            lon = geo["longitude"]
            tz = geo["timezone"]
            place = geo.get("display", f"{city}, {state or country}")
        except Exception as e:
            log.error(f"Geocoding error: {e}")
            return None

        # Write chart_metadata.json (used by generate_chart_wheel)
        meta = {
            "Name": full_name,
            "Birth": {
                "Date": str(dob),
                "Time": f"{hour:02d}:{minute:02d}",
                "Place": place,
                "Latitude": lat,
                "Longitude": lon,
                "Timezone": tz,
            },
            "noon_chart": is_noon,
            "person_id": person_id,
        }
        meta_path = os.path.join(chart_dir, "chart_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2, default=str)

        # Generate SVG wheel via Kerykeion
        try:
            from astro_chart_handler import generate_chart_wheel
            png_path = generate_chart_wheel(chart_dir)
            if png_path:
                log.info(f"Chart generated: {png_path}")
            else:
                log.warning(f"Chart wheel generation returned None for {full_name}")
        except Exception as e:
            log.error(f"Chart generation failed for {full_name}: {e}")
            png_path = None

        # Also run the full engine for detailed JSON output if we have exact time
        if not is_noon:
            try:
                from astro_chart_handler import save_yaml, run_chart_engine, run_db_loader
                yaml_data = {
                    "name": full_name,
                    "birth_date": str(dob),
                    "birth_time": f"{hour:02d}:{minute:02d}",
                    "city": city,
                    "region": state or "",
                    "country": country or "USA",
                    "latitude": lat,
                    "longitude": lon,
                    "timezone": tz,
                }
                yaml_path = save_yaml(yaml_data)
                ok, output = run_chart_engine(yaml_path, chart_dir)
                if ok:
                    run_db_loader(chart_dir)
                    log.info(f"Full chart engine + DB load complete for {full_name}")
                else:
                    log.warning(f"Chart engine failed for {full_name}: {output[:200]}")
            except Exception as e:
                log.warning(f"Full engine pipeline failed (non-fatal): {e}")

        return chart_dir
    finally:
        conn.close()


# ═══════════════════════════════════════════════════
# INTEGRATION WITH DEEP RESEARCH
# ═══════════════════════════════════════════════════

def source_birth_time_and_chart(db_config: dict, person_id: int,
                                 first_name: str, last_name: str) -> Optional[str]:
    """
    Full pipeline for deep research integration:
    1. If person has no birth time, check astrotheme
    2. If birth time found or already known, generate chart
    3. Return chart directory path or None

    Called from person_researcher.run_deep_research()
    """
    import psycopg2
    import psycopg2.extras

    # Check current state
    host = db_config.get("host", "localhost")
    conn_kwargs = {
        "host": "/var/run/postgresql" if host in ("localhost", "127.0.0.1", "") else host,
        "port": db_config.get("port", 5432),
        "database": db_config.get("database", "mythos"),
        "user": db_config.get("user", "adge"),
        "cursor_factory": psycopg2.extras.RealDictCursor,
    }
    if host not in ("localhost", "127.0.0.1", ""):
        conn_kwargs["password"] = db_config.get("password", "")

    conn = psycopg2.connect(**conn_kwargs)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT date_of_birth, time_of_birth, birth_city FROM people WHERE id = %s",
            (person_id,),
        )
        row = cur.fetchone()
        cur.close()

        if not row or not row["date_of_birth"]:
            return None

        # Step 1: Source birth time if missing
        if not row["time_of_birth"]:
            astro_data = search_astrotheme(first_name, last_name)
            if astro_data and astro_data.get("birth_time"):
                update_birth_time(
                    db_config, person_id,
                    astro_data["birth_time"],
                    birth_city=astro_data.get("birth_city"),
                    birth_country=astro_data.get("birth_country"),
                    source="astrotheme",
                )
                log.info(
                    f"Sourced birth time for {first_name} {last_name}: "
                    f"{astro_data['birth_time']} (Rodden: {astro_data.get('rodden_rating', '?')})"
                )

        # Step 2: Generate chart (works with or without birth time — noon chart fallback)
        if row["birth_city"]:
            chart_dir = generate_chart_for_person(db_config, person_id)
            return chart_dir

        return None
    finally:
        conn.close()
