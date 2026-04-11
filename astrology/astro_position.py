#!/opt/mythos/.venv/bin/python3
"""
astro_position.py — Precise astrological position calculator for the Mythos system.
Part of: /opt/mythos/astrology/

Supports city/state geolocation for exact birth chart coordinates.
Uses Swiss Ephemeris (pyswisseph) — installed in Mythos venv.

Usage:
    # Current sky
    python3 astro_position.py --now --planet all

    # Date only (midnight UTC)
    python3 astro_position.py --date "1977-11-22" --planet all

    # Date + time + timezone
    python3 astro_position.py --date "1977-11-22 14:30" --tz "America/New_York" --planet all

    # Date + time + city/state (auto-resolves lat/lon + timezone)
    python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --planet all

    # Full birth chart data (all planets + house cusps + angles)
    python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart

    # JSON output (loader-compatible)
    python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart --output json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    import swisseph as swe
except ImportError:
    print("ERROR: pyswisseph not installed. Run: /opt/mythos/.venv/bin/pip install pyswisseph")
    sys.exit(1)

# ── Ephemeris path ─────────────────────────────────────────────────────────────
import os as _os
_EPHE_CANDIDATES = [
    _os.environ.get("SWISSEPH_PATH", ""),
    "/opt/mythos/astrology/ephe",
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ephe"),
    "/dev/astrology/swisseph/ephe",
    "/home/adge/dev/astrology/swisseph/ephe",
    "/opt/swisseph/ephe",
    "/usr/share/swisseph/ephe",
    "/usr/share/ephe",
]
_EPHE_PATH_SET = None
for _p in _EPHE_CANDIDATES:
    if _p and _os.path.isdir(_p):
        swe.set_ephe_path(_p)
        _EPHE_PATH_SET = _p
        break

# ── Constants ──────────────────────────────────────────────────────────────────

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_SYMBOLS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

PLANETS: dict[str, tuple[str, int | None]] = {
    "sun":       ("Sun",        swe.SUN),
    "moon":      ("Moon",       swe.MOON),
    "mercury":   ("Mercury",    swe.MERCURY),
    "venus":     ("Venus",      swe.VENUS),
    "mars":      ("Mars",       swe.MARS),
    "jupiter":   ("Jupiter",    swe.JUPITER),
    "saturn":    ("Saturn",     swe.SATURN),
    "uranus":    ("Uranus",     swe.URANUS),
    "neptune":   ("Neptune",    swe.NEPTUNE),
    "pluto":     ("Pluto",      swe.PLUTO),
    "chiron":    ("Chiron",     swe.CHIRON),
    "ceres":     ("Ceres",      swe.CERES),
    "pallas":    ("Pallas",     swe.PALLAS),
    "juno":      ("Juno",       swe.JUNO),
    "vesta":     ("Vesta",      swe.VESTA),
    "eris":      ("Eris",       swe.AST_OFFSET + 136199),
    "sedna":     ("Sedna",      swe.AST_OFFSET + 90377),
    "lilith":    ("Lilith",     swe.MEAN_APOG),
    "meannode":  ("Mean Node",  swe.MEAN_NODE),
    "truenode":  ("True Node",  swe.TRUE_NODE),
    "northnode": ("True Node",  swe.TRUE_NODE),
    "southnode": ("South Node", None),
}

ALIASES: dict[str, str] = {
    "north node": "northnode",
    "south node": "southnode",
    "mean node":  "meannode",
    "true node":  "truenode",
    "black moon": "lilith",
    "bml":        "lilith",
    "nn":         "northnode",
    "sn":         "southnode",
}

ALL_ORDER = [
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
    "uranus", "neptune", "pluto", "chiron", "ceres", "pallas", "juno",
    "vesta", "eris", "lilith", "meannode", "truenode", "southnode",
]

SYMBOLS: dict[str, str] = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇",
    "chiron": "⚷", "ceres": "⚳", "pallas": "⚴", "juno": "⚵", "vesta": "⚶",
    "eris": "⯝", "sedna": "⊕", "lilith": "⚸",
    "meannode": "☊", "truenode": "☊", "northnode": "☊", "southnode": "☋",
}

HOUSE_NAMES = ["", "I", "II", "III", "IV", "V", "VI",
               "VII", "VIII", "IX", "X", "XI", "XII"]

# ── Geolocation ────────────────────────────────────────────────────────────────

def resolve_location(city: str, state: str) -> tuple[float, float, str, str]:
    """Resolve city/state to (lat, lon, timezone, display_name)."""
    try:
        from geopy.geocoders import Nominatim
        from timezonefinder import TimezoneFinder
    except ImportError:
        print("ERROR: geolocation requires geopy and timezonefinder.")
        print("  Run: /opt/mythos/.venv/bin/pip install geopy timezonefinder")
        sys.exit(1)

    geocoder = Nominatim(user_agent="mythos_astrology")
    location = geocoder.geocode(f"{city}, {state}, USA") or geocoder.geocode(f"{city}, {state}")
    if not location:
        print(f"ERROR: Could not geocode '{city}, {state}'")
        sys.exit(1)

    lat, lon = location.latitude, location.longitude
    tz_name  = TimezoneFinder().timezone_at(lat=lat, lng=lon) or "UTC"

    return lat, lon, tz_name, location.address


# ── Core Calculations ──────────────────────────────────────────────────────────

def datetime_to_jd(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc = dt.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60.0 + utc.second / 3600.0)


def lon_to_sign_pos(lon: float) -> dict:
    lon       = lon % 360.0
    sign_idx  = int(lon // 30)
    pos       = lon % 30
    deg       = int(pos)
    min_      = int((pos - deg) * 60)
    sec       = round(((pos - deg) * 60 - min_) * 60, 1)
    if sec >= 60:  sec -= 60; min_ += 1
    if min_ >= 60: min_ -= 60; deg  += 1
    sign = SIGNS[sign_idx % 12]
    return {
        "longitude":   round(lon, 6),
        "sign":        sign,
        "sign_symbol": SIGN_SYMBOLS[sign_idx % 12],
        "sign_index":  sign_idx % 12,
        "degree":      deg,
        "minute":      min_,
        "second":      sec,
        "DegMin":      f"{deg:02d}°{min_:02d}'",
        "Full":        f"{deg}°{min_:02d}'{sec:04.1f}\" {sign}",
    }


def get_position(planet_key: str, jd: float) -> dict:
    key = planet_key.lower().replace(" ", "")
    key = ALIASES.get(key, key)
    if key not in PLANETS:
        raise ValueError(f"Unknown planet: '{planet_key}'")
    display_name, body_id = PLANETS[key]

    if key == "southnode":
        nn  = get_position("truenode", jd)
        pos = lon_to_sign_pos(nn["longitude"] + 180.0)
        return {**pos, "planet": key, "Name": display_name, "Symbol": SYMBOLS.get(key, ""),
                "Retrograde": False, "Speed": nn["Speed"], "Latitude": 0.0, "Distance": None}

    flags    = swe.FLG_SWIEPH | swe.FLG_SPEED
    xx, _    = swe.calc_ut(jd, body_id, flags)
    lon, lat, dist, speed = xx[0], xx[1], xx[2], xx[3]
    pos = lon_to_sign_pos(lon)
    return {**pos, "planet": key, "Name": display_name, "Symbol": SYMBOLS.get(key, ""),
            "Retrograde": speed < 0, "Speed": round(speed, 6),
            "Latitude": round(lat, 6), "Distance": round(dist, 8)}


def compute_all_positions(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: int = 0,
    planet_keys: list[str] | None = None,
    tz_str: str = "UTC",
) -> dict:
    """
    Compute positions for multiple planets in one call.

    Uses the same get_position() and Swiss Ephemeris calculations
    as individual lookups — identical precision, just batched.

    Args:
        year, month, day: Date components
        hour, minute, second: Time components (defaults to noon UTC)
        planet_keys: List of planet keys to compute. None = ALL_ORDER
        tz_str: Timezone string for the input time (default UTC)

    Returns:
        dict keyed by planet key, each value is the full get_position() result.
        Example: {"sun": {"sign": "Libra", "degree": 14, ...}, "moon": {...}}
    """
    # Build datetime in the specified timezone, convert to UTC for JD
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = timezone.utc
    dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    jd = datetime_to_jd(dt)

    keys = planet_keys or ALL_ORDER
    results = {}
    for key in keys:
        try:
            results[key] = get_position(key, jd)
        except Exception as e:
            results[key] = {"error": str(e), "planet": key}

    return results


def compute_noon_chart(
    year: int, month: int, day: int,
    planet_keys: list[str] | None = None,
) -> dict:
    """
    Convenience: compute a noon UTC chart for a date.
    Used when birth time is unknown — standard practice.

    Returns same format as compute_all_positions().
    """
    return compute_all_positions(
        year, month, day,
        hour=12, minute=0, second=0,
        planet_keys=planet_keys,
        tz_str="UTC",
    )


def get_houses(jd: float, lat: float, lon: float, system: str = "P") -> dict:
    """Calculate house cusps + angles. Returns {cusps, angles}."""
    cusps, ascmc = swe.houses(jd, lat, lon, system.encode())
    angles = {
        "Ascendant": ascmc[0],
        "Midheaven": ascmc[1],
        "Descendant": (ascmc[0] + 180.0) % 360.0,
        "IC":         (ascmc[1] + 180.0) % 360.0,
        "Vertex":     ascmc[3],
        "ARMC":       ascmc[2],
    }
    house_data = {}
    for i in range(1, 13):
        cusp_lon = cusps[i]
        pos = lon_to_sign_pos(cusp_lon)
        house_data[str(i)] = {"Cusp": round(cusp_lon, 6), "Sign": pos["sign"],
                               "DegMin": pos["DegMin"], "Full": pos["Full"]}
    angle_data = {}
    for name, a_lon in angles.items():
        pos = lon_to_sign_pos(a_lon)
        angle_data[name] = {"Longitude": round(a_lon, 6), "Sign": pos["sign"],
                             "DegMin": pos["DegMin"], "Full": pos["Full"]}
    return {"cusps": house_data, "angles": angle_data}


def assign_houses(planet_results: list[dict], house_cusps: dict) -> list[dict]:
    """Tag each planet with its house number."""
    cusp_lons = [float(house_cusps[str(i)]["Cusp"]) for i in range(1, 13)]
    for r in planet_results:
        plon  = r["longitude"]
        house = 12
        for i in range(12):
            start = cusp_lons[i]
            end   = cusp_lons[(i + 1) % 12]
            if start <= end:
                if start <= plon < end:
                    house = i + 1; break
            else:
                if plon >= start or plon < end:
                    house = i + 1; break
        r["House"] = house
    return planet_results


# ── Output Formatters ──────────────────────────────────────────────────────────

def to_chart_objects_json(results: list[dict]) -> dict:
    return {
        r["Name"]: {
            "Longitude":  r["longitude"],
            "Latitude":   r.get("Latitude"),
            "Distance":   r.get("Distance"),
            "Speed":      r["Speed"],
            "Sign":       r["sign"],
            "DegMin":     r["DegMin"],
            "Full":       r["Full"],
            "Retrograde": r["Retrograde"],
            "House":      r.get("House"),
        }
        for r in results
    }


def print_table(results, dt, tz_label, location_str=None, houses=None):
    BOX     = 64
    dt_line = f"{dt.strftime('%Y-%m-%d  %H:%M')}  {tz_label}"
    print(f"\n  ╔{'═' * BOX}╗")
    print(f"  ║  {'Astrological Positions':<{BOX-2}}║")
    print(f"  ║  {dt_line:<{BOX-2}}║")
    if location_str:
        print(f"  ║  {location_str[:BOX-2]:<{BOX-2}}║")
    print(f"  ╚{'═' * BOX}╝\n")

    has_houses = any(r.get("House") for r in results)
    h_col = "  H" if has_houses else ""
    print(f"  {'Planet':<22} {'Pos':<16} {'Sign':<15}{h_col}  {'Lon':>9}  {'Spd':>9}")
    print(f"  {'─'*22} {'─'*16} {'─'*15}{'─'*len(h_col)}  {'─'*9}  {'─'*9}")

    for r in results:
        label    = f"{r['Symbol']} {r['Name']}"
        retro    = "℞" if r["Retrograde"] else " "
        pos_str  = f"{r['degree']:2d}°{r['minute']:02d}'{r['second']:04.1f}\""
        sign_str = f"{r['sign_symbol']} {r['sign']}"
        hnum     = f"  {r['House']:>2}" if has_houses and r.get("House") else ("   " if has_houses else "")
        print(f"  {label:<22} {pos_str:<16}{retro} {sign_str:<15}{hnum}  {r['longitude']:>9.4f}°  {r['Speed']:>+9.4f}")

    if houses:
        print(f"\n  {'─'*64}")
        print(f"  HOUSE CUSPS\n  {'─'*64}")
        for i in range(1, 13):
            c = houses["cusps"][str(i)]
            print(f"  House {HOUSE_NAMES[i]:<5}  {c['Full']}")
        print(f"\n  ANGLES\n  {'─'*40}")
        for name, a in houses["angles"].items():
            print(f"  {name:<14}  {a['Full']}")
    print()


def print_csv(results, dt):
    print("datetime,planet,sign,degree,minute,second,longitude,retrograde,speed,latitude,house")
    dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    for r in results:
        print(f"{dt_str},{r['Name']},{r['sign']},{r['degree']},{r['minute']},"
              f"{r['second']},{r['longitude']},{'Y' if r['Retrograde'] else 'N'},"
              f"{r['Speed']},{r.get('Latitude','')},{r.get('House','')}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_dt(date_str: str, tz_str: str) -> datetime:
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y"]:
        try:
            dt = datetime.strptime(date_str, fmt)
            try:
                tz = ZoneInfo(tz_str) if tz_str else timezone.utc
            except ZoneInfoNotFoundError:
                print(f"ERROR: Unknown timezone '{tz_str}'"); sys.exit(1)
            return dt.replace(tzinfo=tz)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: '{date_str}'")


def resolve_planets(planet_arg: str) -> list[str]:
    p = planet_arg.lower().strip()
    if p == "all": return ALL_ORDER
    if "," in p:   return [x.strip() for x in p.split(",")]
    return [ALIASES.get(p.replace(" ", ""), p.replace(" ", ""))]


def main():
    parser = argparse.ArgumentParser(
        description="Precise astrological positions — Mythos System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 astro_position.py --now --planet all
  python3 astro_position.py --date "1977-11-22" --planet sun
  python3 astro_position.py --date "1977-11-22 14:30" --tz "America/New_York" --planet all
  python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --planet all
  python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart
  python3 astro_position.py --date "1977-11-22 14:30" --city "Albany" --state "NY" --chart --output json
  python3 astro_position.py --date "1244-03-16" --planet all
        """
    )
    parser.add_argument("--date")
    parser.add_argument("--now",     action="store_true")
    parser.add_argument("--tz",      default=None, help="Timezone e.g. 'America/New_York'")
    parser.add_argument("--city",    help="City for geolocation e.g. 'Albany'")
    parser.add_argument("--state",   help="State e.g. 'NY' or 'New York'")
    parser.add_argument("--lat",     type=float, help="Latitude (manual override)")
    parser.add_argument("--lon",     type=float, help="Longitude (manual override)")
    parser.add_argument("--planet",  default="all")
    parser.add_argument("--chart",   action="store_true",
                        help="Full chart: all planets + houses + angles (requires location)")
    parser.add_argument("--houses",  default="P",
                        help="House system: P=Placidus(default) K=Koch E=Equal W=Whole C=Campanus R=Regiomontanus")
    parser.add_argument("--output",  default="table", choices=["table", "json", "csv"])
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # ── Resolve location ───────────────────────────────────────────────────────
    lat = lon = None
    tz_name  = args.tz
    location_display = None

    if args.city and args.state:
        lat, lon, resolved_tz, location_display = resolve_location(args.city, args.state)
        if not tz_name:
            tz_name = resolved_tz
        if args.output == "table":
            print(f"\n  📍 {location_display}")
            print(f"     Lat: {lat:.4f}°  Lon: {lon:.4f}°  TZ: {tz_name}")
    elif args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
        if not tz_name:
            try:
                from timezonefinder import TimezoneFinder
                tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon) or "UTC"
            except ImportError:
                tz_name = "UTC"

    if not tz_name:
        tz_name = "UTC"

    # ── Resolve datetime ───────────────────────────────────────────────────────
    if args.now:
        dt = datetime.now(tz=timezone.utc)
    elif args.date:
        try:
            dt = parse_dt(args.date, tz_name)
        except ValueError as e:
            print(f"ERROR: {e}"); sys.exit(1)
    else:
        parser.print_help(); sys.exit(1)

    jd = datetime_to_jd(dt)

    # ── Planets ────────────────────────────────────────────────────────────────
    planet_keys = ALL_ORDER if args.chart else resolve_planets(args.planet)

    results = []
    errors  = []
    for key in planet_keys:
        try:
            results.append(get_position(key, jd))
        except Exception as e:
            errors.append(f"  {key}: {e}")

    # ── Houses ─────────────────────────────────────────────────────────────────
    houses = None
    if lat is not None and lon is not None:
        try:
            houses  = get_houses(jd, lat, lon, args.houses)
            results = assign_houses(results, houses["cusps"])
        except Exception as e:
            errors.append(f"  houses: {e}")
    elif args.chart:
        print("ERROR: --chart requires --city/--state or --lat/--lon"); sys.exit(1)

    # ── Output ─────────────────────────────────────────────────────────────────
    if args.output == "json":
        out = {
            "datetime":    dt.isoformat(),
            "timezone":    tz_name,
            "latitude":    lat,
            "longitude":   lon,
            "location":    location_display,
            "house_system": args.houses,
            "planets":     to_chart_objects_json(results),
        }
        if houses:
            out["house_cusps"]          = houses["cusps"]
            out["chart_points"]         = {k: v["Longitude"] for k, v in houses["angles"].items()}
            out["chart_points_detail"]  = houses["angles"]
        print(json.dumps(out, indent=2))

    elif args.output == "csv":
        print_csv(results, dt)

    else:
        loc_str = f"{lat:.4f}°, {lon:.4f}°  ·  {tz_name}" if lat is not None else None
        print_table(results, dt, tz_name, loc_str, houses)
        if errors:
            print("  Errors:")
            for e in errors: print(e)
            print()

    if errors and args.output != "table":
        for e in errors: print(e, file=sys.stderr)


if __name__ == "__main__":
    main()
