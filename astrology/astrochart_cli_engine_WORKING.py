import swisseph as swe
import datetime
import json
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import os
import pandas as pd

from astrochart_cli_geometry import (
    detect_geometric_patterns_with_policy,
    detect_grand_trines,
    detect_t_squares,
    detect_yods,
    detect_mystic_rectangles,
    detect_boomerangs,
    detect_cradles,
    detect_star_of_david,
    detect_kites,
)


HOUSE_SYSTEM = "Placidus"
ZODIAC_TYPE = "Tropical"
EPHEMERIS = "Swiss Ephemeris"
INCLUDED_OBJECTS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Chiron", "Ceres", "Pallas", "Juno",
    "Vesta", "Lilith", "Mean Node"
]

AXIS_POINTS = ["Ascendant", "Midheaven", "Descendant", "IC"]

# --------------------------------------------------
# Swiss Ephemeris Path
# --------------------------------------------------

# Tell Swiss Ephemeris where your data files live
#SE_EPHE_PATH = "/opt/swisseph/ephe"           # ubuntu server on aws
SE_EPHE_PATH = "/dev/astrology/swisseph/ephe"  # atlas ubuntu laptop
# SE_EPHE_PATH = "/usr/share/ephe"        # common on Linux

if os.path.exists(SE_EPHE_PATH):
    swe.set_ephe_path(SE_EPHE_PATH)
else:
    raise FileNotFoundError(f"Swiss Ephemeris path not found: {SE_EPHE_PATH}")

HOUSE_SYSTEM_CODES = {
    "PLACIDUS": b"P",
    "WHOLE SIGN": b"W",
    "KOCH": b"K",
    "REGIOMONTANUS": b"R",
    "CAMPANUS": b"C",
    "EQUAL": b"E",
}


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def deg_min(decimal_degrees):
    deg = int(decimal_degrees)
    minutes = (decimal_degrees - deg) * 60
    return f"{deg}° {minutes:.2f}'"

def get_sign(longitude):
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    idx = int(longitude // 30)
    return signs[idx]

def parse_orb_to_decimal_safe(value, default=1.0):
    try:
        return float(value)
    except Exception:
        return default

def _load_star_friendly_map():
    """
    Minimal built-in Bayer/constellation → proper name map.
    Key should match your CSV's identifier format (e.g., 'α Leo', 'η Oph').
    Extend as needed or replace with a CSV-backed map.
    """
    return {
        "α Leo": "Regulus",
        "α CrB": "Alphecca",      # aka Gemma
        "η Oph": "Sabik",
        "ε Ori": "Alnilam",
        "ζ Ori": "Alnitak",
        "δ Crv": "Algorab",
        # Add more as you like…
    }


# --------------------------------------------------
# Location and Time
# --------------------------------------------------

def get_timezone_and_coords(city, region, country, date_str):
    geolocator = Nominatim(user_agent="astro_chart_generator")
    tf = TimezoneFinder()
    location = geolocator.geocode(f"{city}, {region}, {country}")
    if not location:
        raise ValueError("Location not found")
    lat, lon = location.latitude, location.longitude
    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    timezone = pytz.timezone(timezone_str)
    local_dt = timezone.localize(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M"))
    offset_hours = local_dt.utcoffset().total_seconds() / 3600
    return lat, lon, offset_hours, timezone_str

def get_sign(lon):
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[int(lon // 30)]

def deg_min(lon):
    return f"{int(lon % 30)}°{int((lon % 1) * 60):02d}'"

def generate_chart(input_data, sweph_path="/usr/share/ephe"):
    swe.set_ephe_path(sweph_path)
    name = input_data["Name"]
    dob = input_data["Date of Birth"]
    tob = input_data["Time of Birth"]
    place = input_data["Place of Birth"]
    date_str = f"{dob} {tob}"
    lat, lon, tz_offset, tz_name = get_timezone_and_coords(place["City"], place["Region"], place["Country"], date_str)
    dt_utc = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60, swe.GREG_CAL)

    object_codes = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS,
        "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
        "Chiron": swe.CHIRON, "Ceres": 10001, "Pallas": 10002, "Juno": 10003, "Vesta": 10004,
        "Lilith": swe.MEAN_APOG, "Mean Node": swe.MEAN_NODE
    }

    # 4) Planetary/Object positions
    positions = {}
    cusp_list = [float(cusps[i]) for i in range(12)]  # House 1..12
    for obj in INCLUDED_OBJECTS:
        # Map friendly names to Swiss Ephemeris IDs
        try:
            if obj == "Lilith":
                planet_id = swe.MEAN_APOG          # Black Moon Lilith (mean apogee)
            elif obj == "Mean Node":
                planet_id = swe.MEAN_NODE
            else:
                planet_id = getattr(swe, obj.upper().replace(" ", "_"))
        except AttributeError:
            continue  # Skip objects not available in this build

        pos, _ = swe.calc_ut(jd, planet_id)  # Ecliptic longitude/latitude
        lon_, lat_, dist = float(pos[0]), float(pos[1]), float(pos[2])
        speed = float(pos[3])

        house_num = assign_house(lon_, cusp_list)

        positions[obj] = {
            "Longitude": lon_,
            "Latitude": lat_,
            "Sign": get_sign(lon_),
            "Retrograde": speed < 0.0,
            "House": house_num,
        }

    return positions, houses, axes


# --------------------------------------------------
# Aspect Calculation
# --------------------------------------------------

def compute_aspects(
    positions,
    aspect_definitions,
    default_orb=6,
    axes=None,
    include_axes=False,
    alias_map=None,
    orb_overrides=None,
):
    """
    Build all pairwise aspects between chart objects (and optionally angles).
    - positions: dict of {name: {"Longitude": float, ...}}
    - aspect_definitions: dict like {"Trine": {"Angle":120,"Orb":6,"Description":"..."}, ...}
    - axes: dict like {"Ascendant": lon, "Midheaven": lon, "Descendant": lon, "IC": lon}
    - include_axes: if True, include axes as aspectable points
    - alias_map: optional renames in output (e.g., {"Midheaven":"MC","Mean Node":"North Node"})
    - orb_overrides: per-aspect orb override dict (e.g., {"Sextile":6.5, "Septile":1.2})
    """

    # --- assemble working set of points ---
    augmented = {k: dict(v) for k, v in positions.items()}

    if include_axes and axes:
        # Keep internal keys as the canonical engine names; we'll alias only at OUTPUT.
        for key in ("Ascendant", "Midheaven", "Descendant", "IC"):
            if key in axes:
                lon = float(axes[key])
                augmented[key] = {
                    "Longitude": lon,
                    "Latitude": 0.0,
                    "Sign": get_sign(lon),
                    "Retrograde": False,
                    "House": None,
                }

    names = list(augmented.keys())

    def _get_angle(name):
        spec = aspect_definitions.get(name)
        if spec is None:
            return None
        return float(spec.get("Angle", spec)) if isinstance(spec, dict) else float(spec)

    def _get_desc(name):
        spec = aspect_definitions.get(name, {})
        return spec.get("Description", "") if isinstance(spec, dict) else ""

    def _get_orb(name):
        if orb_overrides and name in orb_overrides:
            return float(orb_overrides[name])
        spec = aspect_definitions.get(name, {})
        if isinstance(spec, dict) and "Orb" in spec:
            return float(spec["Orb"])
        return float(default_orb)

    aspects = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            lon1 = float(augmented[a]["Longitude"])
            lon2 = float(augmented[b]["Longitude"])

            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff

            for asp_name in aspect_definitions.keys():
                angle = _get_angle(asp_name)
                if angle is None:
                    continue
                orb_allow = _get_orb(asp_name)
                delta = abs(diff - angle)
                if delta <= orb_allow + 1e-9:
                    out_a = alias_map.get(a, a) if alias_map else a
                    out_b = alias_map.get(b, b) if alias_map else b
                    aspects.append({
                        "Object 1": out_a,
                        "Object 2": out_b,
                        "Aspect": asp_name,
                        "Angle": angle,
                        "Exact Difference": round(diff, 2),
                        "Orb": round(delta, 2),
                        "Description": _get_desc(asp_name),
                    })
    return aspects


# def compute_aspects(positions, aspect_definitions, default_orb=6):
#     aspects = []
#     objs = list(positions.keys())
#     for i, obj1 in enumerate(objs):
#         for obj2 in objs[i+1:]:
#             lon1 = positions[obj1]["Longitude"]
#             lon2 = positions[obj2]["Longitude"]
#             diff = abs(lon1 - lon2)
#             if diff > 180:
#                 diff = 360 - diff

#             for aspect, data in aspect_definitions.items():
#                 if isinstance(data, dict):
#                     angle = data.get("Angle")
#                     orb_allowed = data.get("Orb", default_orb)
#                 else:
#                     # fallback in case someone uses flat format
#                     angle = data
#                     orb_allowed = default_orb

#                 if angle is None:
#                     continue

#                 if abs(diff - angle) <= orb_allowed:
#                     aspects.append({
#                         "Object 1": obj1,
#                         "Object 2": obj2,
#                         "Aspect": aspect,
#                         "Angle": angle,
#                         "Exact Difference": round(diff, 2),
#                         "Orb": round(abs(diff - angle), 2),
#                         "Description": data.get("Description", "") if isinstance(data, dict) else ""
#                     })
#     return aspects


# --------------------------------------------------
# Fixed Star Conjunctions
# --------------------------------------------------

def compute_fixed_star_conjunctions(positions, star_csv, orb=1.0, include_axes=False, axes=None):
    """
    Find fixed-star conjunctions to planets (and optionally chart axes) within `orb` degrees.
    Adds 'Star_Friendly' from CSV if available; otherwise falls back to a built-in map.
    """
    import pandas as pd

    df = pd.read_csv(star_csv)
    df.columns = [c.strip().lower() for c in df.columns]

    # pick longitude column
    lon_col = next((c for c in ("decimal long", "longitude", "long") if c in df.columns), None)
    if lon_col is None:
        raise KeyError("No longitude-like column found in fixed star CSV (looked for 'decimal long', 'longitude', 'long').")

    # built-in fallback friendly names
    friendly_map = _load_star_friendly_map()

    # helpers
    def get_star_id(row):
        for c in ("star", "name", "id", "designation"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        return "Unknown"

    def get_star_friendly(row, fallback_id):
        # Try CSV columns first
        for c in ("proper", "proper name", "traditional", "friendly", "popular", "common", "english", "name_clean"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        # Fallback to our map
        return friendly_map.get(fallback_id, fallback_id)

    def get_constellation(row):
        for c in ("constellation", "const", "abbr"):
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                return str(row[c]).strip()
        return None

    # build points to test: planets + (optional) axes
    test_points = {obj: float(data["Longitude"]) for obj, data in positions.items()}
    if include_axes and axes:
        for k, v in axes.items():
            test_points[k] = float(v)

    out = []
    for obj, lon in test_points.items():
        for _, row in df.iterrows():
            star_lon = row[lon_col]
            if pd.isna(star_lon):
                continue
            try:
                star_lon = float(star_lon)
            except Exception:
                continue

            # circular distance
            diff = abs(lon - star_lon)
            if diff > 180:
                diff = 360 - diff

            if diff <= float(orb):
                star_id = get_star_id(row)
                friendly = get_star_friendly(row, star_id)
                item = {
                    "Object": obj,
                    "Longitude": lon,
                    "Star": star_id,
                    "Star_Friendly": friendly,
                    "Star_Longitude": star_lon,
                    "Orb": round(diff, 2),
                }
                const = get_constellation(row)
                if const:
                    item["Constellation"] = const
                if "significance" in df.columns and pd.notna(row["significance"]):
                    item["Significance"] = str(row["significance"]).strip()
                out.append(item)

    return out



def run_geometry_audit(
    chart_data,
    aspect_defs=None,
    print_report=True,
    # --- NEW policy flags (preferred) ---
    include_modern=True,   # Angles (ASC/MC/DSC/IC) + Nodes + Chiron
    include_minor=True,    # Ceres, Pallas, Juno, Vesta, Lilith, POF, Vertex/Anti-Vertex
    min_core=2,            # require ≥2 core planets in any detected pattern
    max_minor=1,           # allow ≤1 minor body per pattern
    # --- Back-compat flags (deprecated) ---
    include_axes=False,    # if True, force-include Angles even if include_modern=False
    include_nodes=False,   # if True, force-include Nodes even if include_modern=False
):
    """
    Compare detector outputs vs canonical enumeration from the aspect list,
    using a unified participation policy for ALL geometric shapes.

    Participation policy (defaults):
      - Core bodies (always allowed): Sun, Moon, Mercury, Venus, Mars,
        Jupiter, Saturn, Uranus, Neptune, Pluto.
      - Modern add-ons (include_modern=True by default):
          Angles (Ascendant, Descendant, Midheaven, IC),
          Lunar Node (we normalize North/True -> Mean Node; South Node allowed if present),
          Chiron.
      - Minor/optional bodies (include_minor=True by default):
          Ceres, Pallas, Juno, Vesta, Lilith, Part of Fortune, Vertex, Anti-Vertex.
      - Composition constraints per pattern (defaults):
          ≥ 2 Core bodies, ≤ 1 Minor body.

    Back-compat:
      - include_axes/include_nodes can be used to force-include Angles/Nodes
        even if include_modern=False.

    Writes a structured report to chart_data["Geometry Audit"] and returns it.
    """
    aspects_raw = chart_data.get("chart_aspects", [])

    # -------- Policy sets & helpers --------
    CORE_BODIES = {
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    }

    ANGLES = {"Ascendant", "Descendant", "Midheaven", "IC"}

    NODE_ALIASES = {"Mean Node", "True Node", "North Node", "South Node", "Node"}
    NODE_NORMALIZE = {"True Node": "Mean Node", "North Node": "Mean Node", "Node": "Mean Node"}
    # South Node keeps its own name if present in aspects
    def _norm_name(x: str) -> str:
        return NODE_NORMALIZE.get(x, x)

    MODERN_POINTS = {"Chiron"} | ANGLES | NODE_ALIASES

    MINOR_POINTS = {
        "Ceres", "Pallas", "Juno", "Vesta",
        "Lilith",
        "Part of Fortune",
        "Vertex", "Anti-Vertex",
    }

    # Resolve effective allowances from flags
    allow_angles = include_modern or include_axes
    allow_nodes  = include_modern or include_nodes
    allow_chiron = include_modern

    ALLOWED = set(CORE_BODIES)
    if include_minor:
        ALLOWED |= MINOR_POINTS
    if allow_angles:
        ALLOWED |= ANGLES
    if allow_nodes:
        # include all aliases so we can normalize consistently
        ALLOWED |= NODE_ALIASES
        # make sure "Mean Node" is always recognized if any alias is allowed
        ALLOWED.add("Mean Node")
    if allow_chiron:
        ALLOWED.add("Chiron")

    def _is_core(p: str) -> bool:
        return p in CORE_BODIES

    def _is_minor(p: str) -> bool:
        return p in MINOR_POINTS

    def _passes_composition_policy(points, min_core=min_core, max_minor=max_minor):
        cores = sum(1 for p in points if _is_core(p))
        minors = sum(1 for p in points if _is_minor(p))
        return (cores >= min_core) and (minors <= max_minor)

    # ---- aspect filtering & normalization (policy-aligned) ----
    def _filter_aspects_for_geometry(aspects_):
        out = []
        for a in aspects_:
            x = _norm_name(a["Object 1"])
            y = _norm_name(a["Object 2"])
            if x in ALLOWED and y in ALLOWED:
                aa = dict(a)
                aa["Object 1"] = x
                aa["Object 2"] = y
                out.append(aa)
        return out

    aspects = _filter_aspects_for_geometry(aspects_raw)

    # ---- utilities for enumeration ----
    from itertools import combinations

    def _norm_pair(a, b):
        return tuple(sorted([a, b]))

    def _index_aspects(aspects_):
        by_type = {}
        by_pair_types = {}
        for a in aspects_:
            t = a["Aspect"]
            x = a["Object 1"]
            y = a["Object 2"]
            by_type.setdefault(t, []).append(_norm_pair(x, y))
            by_pair_types.setdefault(_norm_pair(x, y), set()).add(t)
        return by_type, by_pair_types

    def _has(aspect_map, p, t):
        return t in aspect_map.get(_norm_pair(*p), ())

    def _all_bodies(aspect_map):
        s = set()
        for (x, y) in aspect_map.keys():
            s.add(x); s.add(y)
        return s

    def _tri_all(pairs, t, aspect_map):
        (a, b, c) = pairs
        return (_has(aspect_map, (a, b), t) and
                _has(aspect_map, (b, c), t) and
                _has(aspect_map, (a, c), t))

    # ---- enumerators (purely from aspect map) ----
    def _enumerate_grand_trines(bodies, aspect_map):
        out = set()
        for (a, b, c) in combinations(sorted(bodies), 3):
            if _tri_all((a, b, c), "Trine", aspect_map):
                out.add(tuple(sorted([a, b, c])))
        return out

    def _enumerate_t_squares(bodies, aspect_map):
        out = set()
        for (a, b, c) in combinations(sorted(bodies), 3):
            for apex in (a, b, c):
                base = sorted(set([a, b, c]) - {apex})
                if (_has(aspect_map, tuple(base), "Opposition") and
                    _has(aspect_map, (apex, base[0]), "Square") and
                    _has(aspect_map, (apex, base[1]), "Square")):
                    out.add(tuple(sorted([a, b, c])))
                    break
        return out

    def _enumerate_yods(bodies, aspect_map):
        out = set()
        for (a, b, c) in combinations(sorted(bodies), 3):
            for apex in (a, b, c):
                base = sorted(set([a, b, c]) - {apex})
                if (_has(aspect_map, tuple(base), "Sextile") and
                    _has(aspect_map, (apex, base[0]), "Quincunx") and
                    _has(aspect_map, (apex, base[1]), "Quincunx")):
                    out.add(tuple(sorted([a, b, c])))
                    break
        return out

    def _kite_from_trine(tri, aspect_map):
        a, b, c = tri
        tri_set = {a, b, c}
        out = set()
        for d in _all_bodies(aspect_map) - tri_set:
            for v in (a, b, c):
                others = list(tri_set - {v})
                if (_has(aspect_map, (d, v), "Opposition") and
                    _has(aspect_map, (d, others[0]), "Sextile") and
                    _has(aspect_map, (d, others[1]), "Sextile")):
                    out.add(tuple(sorted([a, b, c, d])))
        return out

    def _enumerate_kites(bodies, aspect_map):
        out = set()
        tris = _enumerate_grand_trines(bodies, aspect_map)
        for tri in tris:
            for quad in _kite_from_trine(tri, aspect_map):
                out.add(quad)
        return out

    def _enumerate_mystic_rectangles(bodies, aspect_map):
        out = set()
        for (a, b, c, d) in combinations(sorted(bodies), 4):
            if not (_has(aspect_map, (a, c), "Opposition") and _has(aspect_map, (b, d), "Opposition")):
                continue
            sides1 = [("Sextile", (a, b)), ("Trine", (b, c)), ("Sextile", (c, d)), ("Trine", (d, a))]
            sides2 = [("Trine", (a, b)), ("Sextile", (b, c)), ("Trine", (c, d)), ("Sextile", (d, a))]
            def ok(sides): return all(_has(aspect_map, p, t) for (t, p) in sides)
            if ok(sides1) or ok(sides2):
                out.add(tuple(sorted([a, b, c, d])))
        return out

    def _enumerate_boomerangs(bodies, aspect_map):
        out = set()
        for (a, b, c) in _enumerate_yods(bodies, aspect_map):
            apex = None; base = None
            for candidate in (a, b, c):
                others = sorted({a, b, c} - {candidate})
                if (_has(aspect_map, (candidate, others[0]), "Quincunx") and
                    _has(aspect_map, (candidate, others[1]), "Quincunx") and
                    _has(aspect_map, tuple(others), "Sextile")):
                        apex = candidate; base = others; break
            if apex is None: continue
            for d in _all_bodies(aspect_map) - {a, b, c}:
                if (_has(aspect_map, (apex, d), "Opposition") and
                    _has(aspect_map, (d, base[0]), "Sextile") and
                    _has(aspect_map, (d, base[1]), "Sextile")):
                    out.add(tuple(sorted([a, b, c, d])))
        return out

    def _enumerate_cradles(bodies, aspect_map):
        out = set()
        for (a, b, c, d) in combinations(sorted(bodies), 4):
            if _has(aspect_map, (a, c), "Opposition") or _has(aspect_map, (b, d), "Opposition"):
                continue
            sides1 = [("Sextile", (a, b)), ("Trine", (b, c)), ("Sextile", (c, d)), ("Trine", (d, a))]
            sides2 = [("Trine", (a, b)), ("Sextile", (b, c)), ("Trine", (c, d)), ("Sextile", (d, a))]
            def ok(sides): return all(_has(aspect_map, p, t) for (t, p) in sides)
            if ok(sides1) or ok(sides2):
                out.add(tuple(sorted([a, b, c, d])))
        return out

    def _enumerate_star_of_david(bodies, aspect_map):
        out = set()
        tris = list(_enumerate_grand_trines(bodies, aspect_map))
        for i in range(len(tris)):
            for j in range(i + 1, len(tris)):
                T1 = set(tris[i]); T2 = set(tris[j])
                if T1 & T2: continue
                U = tuple(sorted(T1 | T2))
                good = True
                for x in U:
                    deg = 0
                    for y in U:
                        if x == y: continue
                        if _has(aspect_map, (x, y), "Sextile"):
                            deg += 1
                    if deg != 2:
                        good = False; break
                if good:
                    out.add(U)
        return out

    def _normalize_points(points):
        return tuple(sorted(points))

    def _apply_composition_policy_to_sets(pattern_set):
        return {
            tup for tup in pattern_set
            if _passes_composition_policy(tup, min_core=min_core, max_minor=max_minor)
        }

    # --- detectors (import) ---
    from astrochart_cli_geometry import (
        detect_grand_trines, detect_t_squares, detect_yods, detect_mystic_rectangles,
        detect_boomerangs, detect_cradles, detect_star_of_david, detect_kites
    )

    # --- run detectors on filtered aspects, then apply composition policy ---
    def _patterns_from_detectors(aspects_):
        detectors = {
            "Grand Trine": detect_grand_trines,
            "T-Square": detect_t_squares,
            "Yod": detect_yods,
            "Kite": lambda asp: detect_kites(asp, detect_grand_trines(asp)),
            "Mystic Rectangle": detect_mystic_rectangles,
            "Boomerang": lambda asp: detect_boomerangs(asp, detect_yods(asp)),
            "Cradle": detect_cradles,
            "Star of David": lambda asp: detect_star_of_david(detect_grand_trines(asp)),
        }
        out = {}
        for name, fn in detectors.items():
            found = fn(aspects_)
            s = set()
            for item in found:
                pts = item.get("Points") or item.get("points") or []
                pts_norm = _normalize_points(tuple(_norm_name(p) for p in pts))
                if _passes_composition_policy(pts_norm, min_core=min_core, max_minor=max_minor):
                    s.add(pts_norm)
            out[name] = s
        return out

    # --- canonical enumeration from aspect map, then apply composition policy ---
    def _patterns_from_enumeration(aspects_):
        _, by_pair_types = _index_aspects(aspects_)
        bodies = _all_bodies(by_pair_types)

        enum = {
            "Grand Trine": _enumerate_grand_trines(bodies, by_pair_types),
            "T-Square": _enumerate_t_squares(bodies, by_pair_types),
            "Yod": _enumerate_yods(bodies, by_pair_types),
            "Kite": _enumerate_kites(bodies, by_pair_types),
            "Mystic Rectangle": _enumerate_mystic_rectangles(bodies, by_pair_types),
            "Boomerang": _enumerate_boomerangs(bodies, by_pair_types),
            "Cradle": _enumerate_cradles(bodies, by_pair_types),
            "Star of David": _enumerate_star_of_david(bodies, by_pair_types),
        }
        # apply composition policy
        for k in list(enum.keys()):
            enum[k] = _apply_composition_policy_to_sets(enum[k])
        return enum

    got = _patterns_from_detectors(aspects)
    exp = _patterns_from_enumeration(aspects)

    # --- compare ---
    report = {}
    for typ in exp.keys():
        expected = exp[typ]
        detected = got.get(typ, set())
        missing = expected - detected
        extra = detected - expected
        report[typ] = {
            "expected_count": len(expected),
            "detected_count": len(detected),
            "status": "OK" if (not missing and not extra) else ("MISMATCH" if missing else "EXTRA"),
            "missing": [list(p) for p in sorted(missing)],
            "extra": [list(p) for p in sorted(extra)],
        }

    if print_report:
        print("\n=== Geometric Pattern Audit ===")
        for typ, cell in report.items():
            status_icon = "✅" if cell["status"] == "OK" else ("❌" if cell["status"] == "MISMATCH" else "⚠️")
            print(f"\n{typ}: {status_icon} {cell['status']}")
            print(f"  expected: {cell['expected_count']}   detected: {cell['detected_count']}")
            if cell["missing"]:
                print("  MISSING:")
                for pts in cell["missing"]:
                    print("   - " + ", ".join(pts))
            if cell["extra"]:
                print("  EXTRA:")
                for pts in cell["extra"]:
                    print("   + " + ", ".join(pts))
        print()

    chart_data["Geometry Audit"] = report
    return report



# def run_geometry_audit(chart_data, aspect_defs=None, print_report=True,
#                        include_axes=False, include_nodes=False):
#     """
#     Compare detector outputs vs. canonical enumeration from the aspect list.
#     Set include_axes / include_nodes to True if you want to count MC/IC/ASC/DSC
#     and/or the Node in geometric shapes. Defaults (False/False) match detectors.
#     """
#     aspects = chart_data.get("chart_aspects", [])

#     AXES = {"Ascendant", "Descendant", "Midheaven", "IC"}
#     NODE_ALIASES = {"Mean Node", "True Node", "North Node", "South Node", "Node"}

#     # ---- helpers ----
#     from itertools import combinations

#     def _norm_pair(a, b):
#         return tuple(sorted([a, b]))

#     def _index_aspects(aspects_):
#         by_type = {}
#         by_pair_types = {}
#         for a in aspects_:
#             t = a["Aspect"]
#             x = a["Object 1"]
#             y = a["Object 2"]
#             by_type.setdefault(t, []).append(_norm_pair(x, y))
#             by_pair_types.setdefault(_norm_pair(x, y), set()).add(t)
#         return by_type, by_pair_types

#     def _has(aspect_map, p, t):
#         return t in aspect_map.get(_norm_pair(*p), ())

#     def _all_bodies(aspect_map):
#         s = set()
#         for (x, y) in aspect_map.keys():
#             s.add(x); s.add(y)
#         return s

#     def _filter_aspects_for_geometry(aspects_):
#         out = []
#         for a in aspects_:
#             x, y = a["Object 1"], a["Object 2"]
#             if not include_axes and (x in AXES or y in AXES):
#                 continue
#             if not include_nodes and (x in NODE_ALIASES or y in NODE_ALIASES):
#                 continue
#             out.append(a)
#         return out

#     def _tri_all(pairs, t, aspect_map):
#         (a, b, c) = pairs
#         return (_has(aspect_map, (a, b), t) and
#                 _has(aspect_map, (b, c), t) and
#                 _has(aspect_map, (a, c), t))

#     def _enumerate_grand_trines(bodies, aspect_map):
#         out = set()
#         for (a, b, c) in combinations(sorted(bodies), 3):
#             if _tri_all((a, b, c), "Trine", aspect_map):
#                 out.add(tuple(sorted([a, b, c])))
#         return out

#     def _enumerate_t_squares(bodies, aspect_map):
#         out = set()
#         for (a, b, c) in combinations(sorted(bodies), 3):
#             for apex in (a, b, c):
#                 base = sorted(set([a, b, c]) - {apex})
#                 if (_has(aspect_map, tuple(base), "Opposition") and
#                     _has(aspect_map, (apex, base[0]), "Square") and
#                     _has(aspect_map, (apex, base[1]), "Square")):
#                     out.add(tuple(sorted([a, b, c])))
#                     break
#         return out

#     def _enumerate_yods(bodies, aspect_map):
#         out = set()
#         for (a, b, c) in combinations(sorted(bodies), 3):
#             for apex in (a, b, c):
#                 base = sorted(set([a, b, c]) - {apex})
#                 if (_has(aspect_map, tuple(base), "Sextile") and
#                     _has(aspect_map, (apex, base[0]), "Quincunx") and
#                     _has(aspect_map, (apex, base[1]), "Quincunx")):
#                     out.add(tuple(sorted([a, b, c])))
#                     break
#         return out

#     def _kite_from_trine(tri, aspect_map):
#         a, b, c = tri
#         tri_set = {a, b, c}
#         out = set()
#         for d in _all_bodies(aspect_map) - tri_set:
#             for v in (a, b, c):
#                 others = list(tri_set - {v})
#                 if (_has(aspect_map, (d, v), "Opposition") and
#                     _has(aspect_map, (d, others[0]), "Sextile") and
#                     _has(aspect_map, (d, others[1]), "Sextile")):
#                     out.add(tuple(sorted([a, b, c, d])))
#         return out

#     def _enumerate_kites(bodies, aspect_map):
#         out = set()
#         tris = _enumerate_grand_trines(bodies, aspect_map)
#         for tri in tris:
#             for quad in _kite_from_trine(tri, aspect_map):
#                 out.add(quad)
#         return out

#     def _enumerate_mystic_rectangles(bodies, aspect_map):
#         out = set()
#         for (a, b, c, d) in combinations(sorted(bodies), 4):
#             if not (_has(aspect_map, (a, c), "Opposition") and _has(aspect_map, (b, d), "Opposition")):
#                 continue
#             sides1 = [("Sextile", (a, b)), ("Trine", (b, c)), ("Sextile", (c, d)), ("Trine", (d, a))]
#             sides2 = [("Trine", (a, b)), ("Sextile", (b, c)), ("Trine", (c, d)), ("Sextile", (d, a))]
#             def ok(sides): return all(_has(aspect_map, p, t) for (t, p) in sides)
#             if ok(sides1) or ok(sides2):
#                 out.add(tuple(sorted([a, b, c, d])))
#         return out

#     def _enumerate_boomerangs(bodies, aspect_map):
#         out = set()
#         for (a, b, c) in _enumerate_yods(bodies, aspect_map):
#             apex = None; base = None
#             for candidate in (a, b, c):
#                 others = sorted({a, b, c} - {candidate})
#                 if (_has(aspect_map, (candidate, others[0]), "Quincunx") and
#                     _has(aspect_map, (candidate, others[1]), "Quincunx") and
#                     _has(aspect_map, tuple(others), "Sextile")):
#                         apex = candidate; base = others; break
#             if apex is None: continue
#             for d in _all_bodies(aspect_map) - {a, b, c}:
#                 if (_has(aspect_map, (apex, d), "Opposition") and
#                     _has(aspect_map, (d, base[0]), "Sextile") and
#                     _has(aspect_map, (d, base[1]), "Sextile")):
#                     out.add(tuple(sorted([a, b, c, d])))
#         return out

#     def _enumerate_cradles(bodies, aspect_map):
#         out = set()
#         for (a, b, c, d) in combinations(sorted(bodies), 4):
#             if _has(aspect_map, (a, c), "Opposition") or _has(aspect_map, (b, d), "Opposition"):
#                 continue
#             sides1 = [("Sextile", (a, b)), ("Trine", (b, c)), ("Sextile", (c, d)), ("Trine", (d, a))]
#             sides2 = [("Trine", (a, b)), ("Sextile", (b, c)), ("Trine", (c, d)), ("Sextile", (d, a))]
#             def ok(sides): return all(_has(aspect_map, p, t) for (t, p) in sides)
#             if ok(sides1) or ok(sides2):
#                 out.add(tuple(sorted([a, b, c, d])))
#         return out

#     def _enumerate_star_of_david(bodies, aspect_map):
#         out = set()
#         tris = list(_enumerate_grand_trines(bodies, aspect_map))
#         for i in range(len(tris)):
#             for j in range(i + 1, len(tris)):
#                 T1 = set(tris[i]); T2 = set(tris[j])
#                 if T1 & T2: continue
#                 U = tuple(sorted(T1 | T2))
#                 good = True
#                 for x in U:
#                     deg = 0
#                     for y in U:
#                         if x == y: continue
#                         if _has(aspect_map, (x, y), "Sextile"):
#                             deg += 1
#                     if deg != 2:
#                         good = False; break
#                 if good:
#                     out.add(U)
#         return out

#     def _normalize_points(points):
#         return tuple(sorted(points))

#     # --- detectors on filtered aspects (keeps parity with enumeration choices) ---
#     from astrochart_cli_geometry import (
#         detect_grand_trines, detect_t_squares, detect_yods, detect_mystic_rectangles,
#         detect_boomerangs, detect_cradles, detect_star_of_david, detect_kites
#     )

#     asp_det = _filter_aspects_for_geometry(aspects)

#     def _patterns_from_detectors(aspects_):
#         detectors = {
#             "Grand Trine": detect_grand_trines,
#             "T-Square": detect_t_squares,
#             "Yod": detect_yods,
#             "Kite": lambda asp: detect_kites(asp, detect_grand_trines(asp)),
#             "Mystic Rectangle": detect_mystic_rectangles,
#             "Boomerang": lambda asp: detect_boomerangs(asp, detect_yods(asp)),
#             "Cradle": detect_cradles,
#             "Star of David": lambda asp: detect_star_of_david(detect_grand_trines(asp)),
#         }
#         out = {}
#         for name, fn in detectors.items():
#             found = fn(aspects_)
#             s = set()
#             for item in found:
#                 pts = item.get("Points") or item.get("points") or []
#                 s.add(_normalize_points(pts))
#             out[name] = s
#         return out

#     def _patterns_from_enumeration(aspects_):
#         by_type, by_pair_types = _index_aspects(aspects_)
#         bodies = _all_bodies(by_pair_types)
#         if not include_axes:
#             bodies -= AXES
#         if not include_nodes:
#             bodies -= NODE_ALIASES
#         return {
#             "Grand Trine": _enumerate_grand_trines(bodies, by_pair_types),
#             "T-Square": _enumerate_t_squares(bodies, by_pair_types),
#             "Yod": _enumerate_yods(bodies, by_pair_types),
#             "Kite": _enumerate_kites(bodies, by_pair_types),
#             "Mystic Rectangle": _enumerate_mystic_rectangles(bodies, by_pair_types),
#             "Boomerang": _enumerate_boomerangs(bodies, by_pair_types),
#             "Cradle": _enumerate_cradles(bodies, by_pair_types),
#             "Star of David": _enumerate_star_of_david(bodies, by_pair_types),
#         }

#     got = _patterns_from_detectors(asp_det)
#     exp = _patterns_from_enumeration(asp_det)

#     report = {}
#     for typ in exp.keys():
#         expected = exp[typ]
#         detected = got.get(typ, set())
#         missing = expected - detected
#         extra = detected - expected
#         report[typ] = {
#             "expected_count": len(expected),
#             "detected_count": len(detected),
#             "status": "OK" if (not missing and not extra) else ("MISMATCH" if missing else "EXTRA"),
#             "missing": [list(p) for p in sorted(missing)],
#             "extra": [list(p) for p in sorted(extra)],
#         }

#     if print_report:
#         print("\n=== Geometric Pattern Audit ===")
#         for typ, cell in report.items():
#             status_icon = "✅" if cell["status"] == "OK" else ("❌" if cell["status"] == "MISMATCH" else "⚠️")
#             print(f"\n{typ}: {status_icon} {cell['status']}")
#             print(f"  expected: {cell['expected_count']}   detected: {cell['detected_count']}")
#             if cell["missing"]:
#                 print("  MISSING:")
#                 for pts in cell["missing"]:
#                     print("   - " + ", ".join(pts))
#             if cell["extra"]:
#                 print("  EXTRA:")
#                 for pts in cell["extra"]:
#                     print("   + " + ", ".join(pts))
#         print()

#     chart_data["Geometry Audit"] = report
#     return report


# --------------------------------------------------
# Chart Generator
# --------------------------------------------------

def generate_natal_chart(name, dob, tob, city, region, country, latitude=None, longitude=None, house_system="Placidus"):
    dt_str = f"{dob} {tob}"

    if latitude is not None and longitude is not None:
        lat, lon = latitude, longitude
        tz = pytz.timezone("America/New_York") if country.upper() == "USA" else pytz.UTC
        dt_naive = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        dt_local = tz.localize(dt_naive)
    else:
        lat, lon, tz, dt_local = get_timezone_and_coords(city, region, country, dt_str)

    # positions, houses, axes = compute_chart(lat, lon, dt_local, house_system=house_system)
    positions, houses, axes = compute_chart(lat, lon, dt_local)

    # with open("aspects.json") as f:
    #     aspect_defs = json.load(f)
    # aspects = compute_aspects(positions, aspect_defs)

    with open("aspects.json") as f:
        aspect_defs = json.load(f)

    # Orbs tuned a bit looser to match astro-charts’ display behavior
    orb_overrides = {
        "Conjunction": 6.0,
        "Opposition": 6.0,
        "Trine": 7.0,
        "Square": 6.0,
        "Sextile": 6.5,
        "Semi-sextile": 3.0,
        "Semi-square": 3.0,       # (= Octile)
        "Sesquiquadrate": 3.5,
        "Quintile": 3.0,
        "Biquintile": 2.0,
        "Septile": 1.2,           # new
    }

    # Cosmetic renames to mirror common site labels
    alias_map = {
        "Midheaven": "MC",
        "Mean Node": "North Node",
    }

    # Build aspects INCLUDING angles for reporting parity with astro-charts
    aspects = compute_aspects(
        positions,
        aspect_defs,
        default_orb=6,
        axes=axes,
        include_axes=True,
        alias_map=alias_map,
        orb_overrides=orb_overrides,
    )

    # IMPORTANT: keep angles OUT of geometry detection so you don’t get spurious shapes
    AXES_SET = {"Ascendant", "Descendant", "IC", "MC"}
    aspects_for_patterns = [
        a for a in aspects
        if a["Object 1"] not in AXES_SET and a["Object 2"] not in AXES_SET
    ]

    

    # Enforce the participant policy globally for ALL shapes:
    # - include_modern=True  -> allow Angles (ASC/MC/DSC/IC), Nodes, Chiron
    # - include_minor=True   -> allow asteroids/Lilith/POF/Vertex, but
    #                           composition policy caps minors at 1 per pattern
    # - min_core=2           -> require at least two Core planets in each pattern
    # - max_minor=1          -> allow at most one Minor body in each pattern
    patterns = detect_geometric_patterns_with_policy(
        aspects,
        include_modern=True,
        include_minor=True,
        min_core=2,
        max_minor=1,
    )


    # patterns = []
    # patterns += detect_grand_trines(aspects_for_patterns)
    # patterns += detect_t_squares(aspects_for_patterns)
    # patterns += detect_yods(aspects_for_patterns)
    # patterns += detect_kites(aspects_for_patterns, detect_grand_trines(aspects_for_patterns))
    # patterns += detect_mystic_rectangles(aspects_for_patterns)
    # patterns += detect_boomerangs(aspects_for_patterns, detect_yods(aspects_for_patterns))
    # patterns += detect_cradles(aspects_for_patterns)
    # patterns += detect_star_of_david(detect_grand_trines(aspects_for_patterns))

    stars = compute_fixed_star_conjunctions(
        positions,
        "astrochart_cli_fixed_stars.csv",
        orb=1.0,
        axes=axes,          # NEW: include angles
        include_axes=True,  # default True anyway
    )


    return {
        "chart_metadata": {
            "Name": name,
            "Birth": {
                "Date": dob,
                "Time": tob,
                "Place": f"{city}, {region}, {country}",
                "Latitude": lat,
                "Longitude": lon,
                "Timezone": str(tz),
            },
            "House System": house_system,
            "Zodiac Type": ZODIAC_TYPE,
            "Ephemeris": EPHEMERIS,
            "Included Objects": list(positions.keys()),
        },
        "chart_objects": positions,
        "house_cusps": houses,
        "chart_points": axes,
        "chart_aspects": aspects,
        "geometric_patterns": patterns,
        "fixed_star_conjunctions": stars,
    }

def generate_natal_report(chart_data, filename="natal_report.json", geometry_audit=None):
    report = {
        "Chart Metadata": chart_data.get("chart_metadata", {}),
        "Planetary Positions": chart_data.get("chart_objects", {}),
        "House Cusps": chart_data.get("house_cusps", {}),
        "Chart Points (Angles)": chart_data.get("chart_points", {}),
        "Aspects": chart_data.get("chart_aspects", []),
        "Geometric Patterns": chart_data.get("geometric_patterns", []),
        "Fixed Star Conjunctions": chart_data.get("fixed_star_conjunctions", []),
    }
    if geometry_audit is not None:
        report["Geometry Audit"] = geometry_audit
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    return report
