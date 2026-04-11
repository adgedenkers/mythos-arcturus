import json
import argparse

# ===== Geometric Shape PARTICIPANT POLICY =====
# Core set (always eligible for shapes)
CORE_BODIES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
}

# Common modern add-ons (opt-in)
MODERN_POINTS = {
    # Angles (+ their opposites auto-included by your pipeline)
    "Ascendant", "Midheaven", "Descendant", "IC",
    # Nodes (we normalize North/True Node -> Mean Node; South Node supported if present)
    "Mean Node", "North Node", "True Node", "South Node",
    # Healer/comet
    "Chiron",
}

# Optional / minor bodies (use sparingly)
MINOR_POINTS = {
    "Ceres", "Pallas", "Juno", "Vesta",
    "Lilith",               # (mean apogee)
    "Part of Fortune",      # aka Pars Fortuna
    "Vertex", "Anti-Vertex"
}

# --- Name normalization (so "North Node"/"True Node" map to "Mean Node")
_NODE_ALIASES = {"North Node": "Mean Node", "True Node": "Mean Node"}
def _norm_name(x: str) -> str:
    return _NODE_ALIASES.get(x, x)

def _allowed_set(include_modern: bool, include_minor: bool):
    allowed = set(CORE_BODIES)
    if include_modern:
        allowed |= MODERN_POINTS
    if include_minor:
        allowed |= MINOR_POINTS
    # Normalize node alias names into the allowed set too
    if "North Node" in allowed:
        allowed.add("Mean Node")
    if "True Node" in allowed:
        allowed.add("Mean Node")
    return allowed

def filter_aspects_by_policy(aspects, *, include_modern=True, include_minor=True):
    """
    Return only aspects whose endpoints are in the allowed set
    (Core + optional Modern + optional Minor).
    Also normalizes node aliases to 'Mean Node'.
    """
    allowed = _allowed_set(include_modern, include_minor)
    out = []
    for a in aspects:
        x = _norm_name(a["Object 1"])
        y = _norm_name(a["Object 2"])
        if x in allowed and y in allowed:
            aa = dict(a)
            aa["Object 1"] = x
            aa["Object 2"] = y
            out.append(aa)
    return out

def _passes_composition_policy(points, *, min_core=2, max_minor=1):
    """
    Enforce: at least 2 Core bodies; at most 1 Minor in any detected pattern.
    Modern points (angles, node, Chiron) are allowed with no cap.
    """
    cores  = sum(1 for p in points if p in CORE_BODIES)
    minors = sum(1 for p in points if p in MINOR_POINTS)
    return (cores >= min_core) and (minors <= max_minor)

def detect_geometric_patterns_with_policy(
    aspects,
    *,
    include_modern=True,
    include_minor=True,
    min_core=2,
    max_minor=1,
):
    """
    Wrapper that:
      1) filters the aspect list by allowed participants,
      2) runs all existing detectors,
      3) applies the composition policy to each result.
    Returns a single list with all pattern dicts that pass policy.
    """
    # 1) filter aspects by participant policy
    aspects_f = filter_aspects_by_policy(aspects, include_modern=include_modern, include_minor=include_minor)

    # 2) run your existing detectors (we assume they are already imported in this module)
    detectors = [
        detect_grand_trines,
        detect_t_squares,
        detect_yods,
        lambda asp: detect_kites(asp, detect_grand_trines(asp)),
        detect_mystic_rectangles,
        lambda asp: detect_boomerangs(asp, detect_yods(asp)),
        detect_cradles,
        lambda asp: detect_star_of_david(detect_grand_trines(asp)),
    ]

    found = []
    for det in detectors:
        for item in det(aspects_f):
            pts = item.get("Points") or item.get("points") or []
            if _passes_composition_policy(pts, min_core=min_core, max_minor=max_minor):
                found.append(item)

    return found
# ===== end policy block =====
# --- shared helpers for detectors ---

def _norm_pair(a, b):
    return (a, b) if a <= b else (b, a)

_ASPECT_ALIASES = {
    "inconjunct": "Quincunx",
    "quincunx":   "Quincunx",
    "sextile":    "Sextile",
    "trine":      "Trine",
    "square":     "Square",
    "opposition": "Opposition",
}

def _index_aspects(aspects):
    """
    Map normalized (A,B) -> set of canonical aspect names present between them.
    Also keep the best (smallest) orb per type for debugging/printing.
    NOTE: structured to avoid RHS-before-LHS KeyError.
    """
    by_pair = {}
    best_orb = {}

    for a in aspects:
        # normalize aspect name
        t_raw = str(a.get("Aspect", "")).strip()
        t = _ASPECT_ALIASES.get(t_raw.lower(), t_raw) if t_raw else ""
        x = a.get("Object 1")
        y = a.get("Object 2")
        if not x or not y or not t:
            continue

        p = _norm_pair(x, y)

        # collect types
        by_pair.setdefault(p, set()).add(t)

        # ensure container BEFORE reading it (avoid KeyError)
        cell = best_orb.setdefault(p, {})
        try:
            orb = float(a.get("Orb", 999))
        except Exception:
            orb = 999.0

        prev = cell.get(t, orb)
        cell[t] = min(prev, orb)

    return by_pair, best_orb


# def _index_aspects(aspects):
#     """
#     Map normalized (A,B) -> set of canonical aspect names present between them.
#     Also keep the best (smallest) orb per type so we can later print/debug if needed.
#     """
#     by_pair = {}
#     best_orb = {}
#     for a in aspects:
#         t_raw = a.get("Aspect", "")
#         t = _ASPECT_ALIASES.get(t_raw.strip().lower(), t_raw)
#         x, y = a["Object 1"], a["Object 2"]
#         p = _norm_pair(x, y)
#         by_pair.setdefault(p, set()).add(t)
#         best_orb.setdefault(p, {})[t] = min(best_orb[p].get(t, 1e9), float(a.get("Orb", 999)))
#     return by_pair, best_orb

def _has(by_pair, p, t):
    return t in by_pair.get(_norm_pair(*p), set())
# --- end helpers ---


def detect_grand_trines(aspects):
    trines = [a for a in aspects if a["Aspect"] == "Trine"]
    trine_pairs = [(a["Object 1"], a["Object 2"]) for a in trines]
    trine_graph = {}
    for a, b in trine_pairs:
        trine_graph.setdefault(a, set()).add(b)
        trine_graph.setdefault(b, set()).add(a)

    grand_trines = []
    for a in trine_graph:
        for b in trine_graph[a]:
            for c in trine_graph[b]:
                if c in trine_graph[a] and len({a, b, c}) == 3:
                    triplet = sorted([a, b, c])
                    if triplet not in [sorted(g["Points"]) for g in grand_trines]:
                        grand_trines.append({
                            "Type": "Grand Trine",
                            "Points": triplet,
                            "Aspects": [f"{triplet[0]}-{triplet[1]}", f"{triplet[1]}-{triplet[2]}", f"{triplet[2]}-{triplet[0]}"]
                        })
    return grand_trines

def detect_t_squares(aspects):
    oppositions = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Opposition"]
    squares = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Square"]
    t_squares = []
    for a, b in oppositions:
        for c1, c2 in squares:
            if {a, c1, c2} == {a, b, c1} or {b, c1, c2} == {a, b, c2}:
                apex = c2 if c1 in (a, b) else c1
                if apex not in (a, b):
                    triad = sorted([a, b, apex])
                    if triad not in [sorted(p["Points"]) for p in t_squares]:
                        t_squares.append({
                            "Type": "T-Square",
                            "Points": triad,
                            "Aspects": [f"{a}-{b} (Opposition)", f"{a}-{apex} (Square)", f"{b}-{apex} (Square)"]
                        })
    return t_squares

def detect_yods(aspects, include_bodies=None, exclude_bodies=None):
    """
    Detect Yods using strict graph rules consistent with the audit:
      - Choose 3 bodies (a,b,c)
      - One is apex: apex-base1 = Quincunx, apex-base2 = Quincunx
      - Base (base1-base2) = Sextile
    include_bodies: optional whitelist set
    exclude_bodies: optional blacklist set
    """
    from itertools import combinations
    by_pair, _ = _index_aspects(aspects)

    def ok_body(b):
        if include_bodies and b not in include_bodies: return False
        if exclude_bodies and b in exclude_bodies: return False
        return True

    bodies = set()
    for (x, y) in by_pair.keys():
        if ok_body(x): bodies.add(x)
        if ok_body(y): bodies.add(y)

    out = []
    seen = set()
    for (a, b, c) in combinations(sorted(bodies), 3):
        for apex in (a, b, c):
            base = sorted({a, b, c} - {apex})
            if (_has(by_pair, (apex, base[0]), "Quincunx") and
                _has(by_pair, (apex, base[1]), "Quincunx") and
                _has(by_pair, tuple(base), "Sextile")):
                pts = tuple(sorted((a, b, c)))
                if pts not in seen:
                    seen.add(pts)
                    out.append({"Type": "Yod", "Points": list(pts), "Apex": apex})
                break
    return out


# def detect_yods(aspects):
#     quincunxes = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Quincunx"]
#     sextiles = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Sextile"]
#     yods = []
#     for a1, b1 in quincunxes:
#         for a2, b2 in quincunxes:
#             if a1 != a2 and len({a1, b1, a2, b2}) == 3:
#                 base = list({a1, b1, a2, b2})
#                 apex = next(p for p in base if base.count(p) == 1)
#                 base.remove(apex)
#                 if tuple(sorted(base)) in [tuple(sorted(p)) for p in sextiles]:
#                     triad = sorted([*base, apex])
#                     if triad not in [sorted(p["Points"]) for p in yods]:
#                         yods.append({
#                             "Type": "Yod",
#                             "Points": triad,
#                             "Aspects": [f"{apex}-{base[0]} (Quincunx)", f"{apex}-{base[1]} (Quincunx)", f"{base[0]}-{base[1]} (Sextile)"]
#                         })
#     return yods

from itertools import combinations

def detect_kites(
    aspects,
    grand_trines=None,
    include_modern=True,   # Angles + Nodes + Chiron
    include_minor=True,    # Ceres, Pallas, Juno, Vesta, Lilith, POF, Vertex/AV
    min_core=2,            # require ≥2 core planets in the 4 points
    max_minor=1,           # allow ≤1 minor body in the 4 points
):
    """
    Detect Kites using the same participation policy as run_geometry_audit.

    Definition used:
      - Start from a Grand Trine (three bodies all mutually Trine).
      - A 4th body 'd' (the apex) forms:
          * Opposition to one vertex of the trine, and
          * Sextile to the other two trine vertices.

    Returns a list of dicts: {"Type": "Kite", "Points": [ .... ], "Aspects": [ ... ]}.
    """

    # ---- policy sets (mirror audit) ----
    CORE_BODIES = {
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    }
    ANGLES = {"Ascendant", "Descendant", "Midheaven", "IC"}
    MINOR_POINTS = {
        "Ceres", "Pallas", "Juno", "Vesta",
        "Lilith",
        "Part of Fortune",
        "Vertex", "Anti-Vertex",
    }
    NODE_ALIASES = {"Mean Node", "True Node", "North Node", "South Node", "Node"}
    NODE_NORMALIZE = {"True Node": "Mean Node", "North Node": "Mean Node", "Node": "Mean Node"}

    def _norm_name(x: str) -> str:
        return NODE_NORMALIZE.get(x, x)

    allow_angles = include_modern
    allow_nodes  = include_modern
    allow_chiron = include_modern

    ALLOWED = set(CORE_BODIES)
    if include_minor:
        ALLOWED |= MINOR_POINTS
    if allow_angles:
        ALLOWED |= ANGLES
    if allow_nodes:
        ALLOWED |= NODE_ALIASES
        ALLOWED.add("Mean Node")
    if allow_chiron:
        ALLOWED.add("Chiron")

    def _is_core(p: str) -> bool:
        return p in CORE_BODIES

    def _is_minor(p: str) -> bool:
        return p in MINOR_POINTS

    def _composition_ok(points):
        cores = sum(1 for p in points if _is_core(p))
        minors = sum(1 for p in points if _is_minor(p))
        return (cores >= min_core) and (minors <= max_minor)

    # ---- normalize & filter aspects to the allowed set ----
    asp = []
    for a in aspects:
        x = _norm_name(a["Object 1"])
        y = _norm_name(a["Object 2"])
        if x in ALLOWED and y in ALLOWED:
            aa = dict(a)
            aa["Object 1"] = x
            aa["Object 2"] = y
            asp.append(aa)

    # ---- index aspects ----
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

    by_type, by_pair_types = _index_aspects(asp)

    def _has(p, t):
        return t in by_pair_types.get(_norm_pair(*p), ())

    def _all_bodies():
        s = set()
        for (x, y) in by_pair_types.keys():
            s.add(x); s.add(y)
        return s

    # ---- get (or build) grand trines, normalized to point tuples ----
    tris = set()
    if grand_trines is not None and len(grand_trines) > 0:
        # Handle both list-of-dicts ({"Points":[...]}) and list-of-tuples
        for item in grand_trines:
            if isinstance(item, dict):
                pts = tuple(sorted(item.get("Points") or item.get("points") or []))
            else:
                pts = tuple(sorted(item))
            if len(pts) == 3:
                tris.add(pts)
    else:
        # enumerate from the aspect map
        bodies = sorted(_all_bodies())
        for (a, b, c) in combinations(bodies, 3):
            if (_has((a, b), "Trine") and
                _has((b, c), "Trine") and
                _has((a, c), "Trine")):
                tris.add(tuple(sorted([a, b, c])))

    # ---- find kites from each trine ----
    out = []
    seen = set()  # avoid duplicates
    bodies = _all_bodies()

    for tri in tris:
        a, b, c = tri
        tri_set = {a, b, c}
        for d in bodies - tri_set:
            # try each vertex of the trine as the opposition target
            for v in (a, b, c):
                others = [x for x in (a, b, c) if x != v]
                if (_has((d, v), "Opposition") and
                    _has((d, others[0]), "Sextile") and
                    _has((d, others[1]), "Sextile")):
                    pts = tuple(sorted([a, b, c, d]))
                    if not _composition_ok(pts):
                        continue
                    if pts in seen:
                        continue
                    seen.add(pts)
                    # optional: include a short aspect list for readability
                    aspects_used = [
                        f"{a}–{b} (Trine)", f"{b}–{c} (Trine)", f"{a}–{c} (Trine)",
                        f"{d}–{v} (Opposition)",
                        f"{d}–{others[0]} (Sextile)",
                        f"{d}–{others[1]} (Sextile)",
                    ]
                    out.append({
                        "Type": "Kite",
                        "Points": list(pts),
                        "Aspects": aspects_used,
                    })
                    break  # don’t add the same kite twice via a different apex choice

    return out


# def detect_kites(aspects, grand_trines):
#     oppositions = {(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Opposition"}
#     sextiles = {(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Sextile"}
#     kites = []
#     for gt in grand_trines:
#         a, b, c = gt["Points"]
#         for d1, d2 in oppositions:
#             if d1 in (a, b, c) and d2 not in (a, b, c):
#                 triangle = [a, b, c]
#                 point = d2
#                 sextile_to = [p for p in triangle if (p, point) in sextiles or (point, p) in sextiles]
#                 if len(sextile_to) == 2:
#                     kite = sorted(triangle + [point])
#                     if kite not in [sorted(k["Points"]) for k in kites]:
#                         kites.append({
#                             "Type": "Kite",
#                             "Points": kite,
#                             "Aspects": gt["Aspects"] + [f"{d1}-{d2} (Opposition)"] + [f"{point}-{p} (Sextile)" for p in sextile_to]
#                         })
#     return kites

def detect_mystic_rectangles(aspects):
    oppositions = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Opposition"]
    sextiles = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Sextile"]
    rectangles = []
    for (a, b) in oppositions:
        for (c, d) in oppositions:
            if len({a, b, c, d}) == 4:
                pair1 = sorted([a, b])
                pair2 = sorted([c, d])
                if all((x, y) in sextiles or (y, x) in sextiles for x in pair1 for y in pair2):
                    rect = sorted(pair1 + pair2)
                    if rect not in [sorted(r["Points"]) for r in rectangles]:
                        rectangles.append({
                            "Type": "Mystic Rectangle",
                            "Points": rect,
                            "Aspects": [f"{a}-{b} (Opposition)", f"{c}-{d} (Opposition)"] +
                                        [f"{x}-{y} (Sextile)" for x in pair1 for y in pair2]
                        })
    return rectangles

def detect_boomerangs(aspects, yods=None, include_bodies=None, exclude_bodies=None):
    """
    Boomerang = Yod + a 4th body d such that:
      apex-d = Opposition
      d-base1 = Sextile
      d-base2 = Sextile
    We use the SAME Yods as detect_yods() to avoid mismatches.
    """
    from itertools import combinations
    by_pair, _ = _index_aspects(aspects)

    def ok_body(b):
        if include_bodies and b not in include_bodies: return False
        if exclude_bodies and b in exclude_bodies: return False
        return True

    # Ensure we start from the *same* Yods
    if yods is None:
        yods = detect_yods(aspects, include_bodies=include_bodies, exclude_bodies=exclude_bodies)

    bodies = set()
    for (x, y) in by_pair.keys():
        if ok_body(x): bodies.add(x)
        if ok_body(y): bodies.add(y)

    out = []
    seen = set()
    for y in yods:
        a, b, c = y["Points"]
        apex = y.get("Apex")
        if apex is None:
            # recompute apex if missing
            for candidate in (a, b, c):
                others = sorted({a, b, c} - {candidate})
                if (_has(by_pair, (candidate, others[0]), "Quincunx") and
                    _has(by_pair, (candidate, others[1]), "Quincunx") and
                    _has(by_pair, tuple(others), "Sextile")):
                    apex = candidate
                    break
        if apex is None:
            continue
        base = sorted({a, b, c} - {apex})

        for d in bodies - {a, b, c}:
            if (_has(by_pair, (apex, d), "Opposition") and
                _has(by_pair, (d, base[0]), "Sextile") and
                _has(by_pair, (d, base[1]), "Sextile")):
                pts = tuple(sorted((a, b, c, d)))
                if pts not in seen:
                    seen.add(pts)
                    out.append({"Type": "Boomerang", "Points": list(pts), "Apex": apex, "Anchor": d})
    return out


# def detect_boomerangs(aspects, yods):
#     oppositions = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Opposition"]
#     boomerangs = []
#     for yod in yods:
#         apex = [p for p in yod["Points"] if yod["Points"].count(p) == 1][0]
#         base = [p for p in yod["Points"] if p != apex]
#         for a, b in oppositions:
#             if apex in (a, b) and (a if apex == b else b) not in yod["Points"]:
#                 opp_pt = a if apex == b else b
#                 boomerangs.append({
#                     "Type": "Boomerang",
#                     "Points": yod["Points"] + [opp_pt],
#                     "Aspects": yod["Aspects"] + [f"{apex}-{opp_pt} (Opposition)"]
#                 })
#     return boomerangs


def detect_cradles(aspects, include_bodies=None, exclude_bodies=None):
    """
    Cradle (strict): 4 bodies a,b,c,d forming
      - ab Sextile, bc Trine, cd Sextile, da Trine
      - and NO oppositions across the shape's cross-pairs (a-c) nor (b(.venv) ubuntu@ip-172-31-7-253:/opt/astrochart_cli$ python astrochart_cli_tool.py -f "becky_input.yaml" --prefix becky_t1000
Traceback (most recent call last):
  File "/opt/astrochart_cli/astrochart_cli_tool.py", line 93, in <module>
    main()
  File "/opt/astrochart_cli/astrochart_cli_tool.py", line 60, in main
    chart_data = chart_engine.generate_natal_chart(
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/astrochart_cli/astrochart_cli_engine.py", line 577, in generate_natal_chart
    patterns += detect_yods(aspects)
                ^^^^^^^^^^^^^^^^^^^^
  File "/opt/astrochart_cli/astrochart_cli_geometry.py", line 88, in detect_yods
    by_pair, _ = _index_aspects(aspects)
                 ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/astrochart_cli/astrochart_cli_geometry.py", line 30, in _index_aspects
    best_orb.setdefault(p, {})[t] = min(best_orb[p].get(t, 1e9), float(a.get("Orb", 999)))
                                        ~~~~~~~~^^^
KeyError: ('Mercury', 'Sun')
(.venv) ubuntu@ip-172-31-7-253:/opt/astrochart_cli$ -d)
    This matches the audit's definition.
    """
    from itertools import combinations
    by_pair, _ = _index_aspects(aspects)

    def ok_body(b):
        if include_bodies and b not in include_bodies: return False
        if exclude_bodies and b in exclude_bodies: return False
        return True

    bodies = set()
    for (x, y) in by_pair.keys():
        if ok_body(x): bodies.add(x)
        if ok_body(y): bodies.add(y)

    out = []
    seen = set()

    def is_cradle(a, b, c, d):
        # disallow oppositions on the cross-pairs
        if _has(by_pair, (a, c), "Opposition") or _has(by_pair, (b, d), "Opposition"):
            return False
        sides1 = [("Sextile", (a, b)), ("Trine", (b, c)), ("Sextile", (c, d)), ("Trine", (d, a))]
        sides2 = [("Trine", (a, b)), ("Sextile", (b, c)), ("Trine", (c, d)), ("Sextile", (d, a))]
        def ok(sides): return all(_has(by_pair, p, t) for (t, p) in sides)
        return ok(sides1) or ok(sides2)

    for (a, b, c, d) in combinations(sorted(bodies), 4):
        if is_cradle(a, b, c, d):
            pts = tuple(sorted((a, b, c, d)))
            if pts not in seen:
                seen.add(pts)
                out.append({"Type": "Cradle", "Points": list(pts)})
    return out


# def detect_cradles(aspects):
#     trines = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Trine"]
#     sextiles = [(a["Object 1"], a["Object 2"]) for a in aspects if a["Aspect"] == "Sextile"]
#     cradles = []
#     for t1 in trines:
#         for t2 in trines:
#             if t1 != t2 and len(set(t1 + t2)) == 4:
#                 a, b, c, d = set(t1 + t2)
#                 sextile_count = sum(1 for x, y in [(a, c), (a, d), (b, c), (b, d)] if (x, y) in sextiles or (y, x) in sextiles)
#                 if sextile_count >= 2:
#                     group = sorted([a, b, c, d])
#                     if group not in [sorted(p["Points"]) for p in cradles]:
#                         cradles.append({
#                             "Type": "Cradle",
#                             "Points": group,
#                             "Aspects": [f"{t1[0]}-{t1[1]} (Trine)", f"{t2[0]}-{t2[1]} (Trine)"]
#                         })
#     return cradles

def detect_star_of_david(grand_trines):
    stars = []
    for i in range(len(grand_trines)):
        for j in range(i+1, len(grand_trines)):
            combined = sorted(set(grand_trines[i]["Points"] + grand_trines[j]["Points"]))
            if len(combined) == 6:
                if combined not in [sorted(s["Points"]) for s in stars]:
                    stars.append({
                        "Type": "Star of David",
                        "Points": combined,
                        "Aspects": grand_trines[i]["Aspects"] + grand_trines[j]["Aspects"]
                    })
    return stars

def detect_buckets(chart_objects):
    longitudes = [obj["Longitude"] for obj in chart_objects if obj["Object"] not in ["Ascendant", "Midheaven", "Descendant", "IC"]]
    if len(longitudes) < 10:
        return []
    longitudes.sort()
    spans = [(longitudes[i], longitudes[i+1] if i+1 < len(longitudes) else longitudes[0]+360) for i in range(len(longitudes))]
    gaps = [(j - i) % 360 for i, j in spans]
    if max(gaps) > 120:
        return [{"Type": "Bucket", "Description": "Chart shows a large empty space opposite a focus of planets."}]
    return []

def detect_seesaws(chart_objects):
    longitudes = [obj["Longitude"] for obj in chart_objects if obj["Object"] not in ["Ascendant", "Midheaven", "Descendant", "IC"]]
    if len(longitudes) < 10:
        return []
    sectors = [0]*12
    for lon in longitudes:
        sectors[int(lon // 30)] += 1
    half1 = sum(sectors[:6])
    half2 = sum(sectors[6:])
    if abs(half1 - half2) <= 2:
        return [{"Type": "Seesaw", "Description": "Chart objects are distributed in two opposing groups."}]
    return []

def detect_splays(chart_objects):
    longitudes = sorted(obj["Longitude"] for obj in chart_objects if obj["Object"] not in ["Ascendant", "Midheaven", "Descendant", "IC"])
    segments = []
    for i in range(len(longitudes)):
        group = [longitudes[i]]
        for j in range(i+1, len(longitudes)):
            if abs(longitudes[j] - group[-1]) < 90:
                group.append(longitudes[j])
            else:
                break
        if len(group) >= 3:
            segments.append(group)
    if len(segments) >= 3:
        return [{"Type": "Splay", "Description": "Chart has three or more clusters spread across the zodiac."}]
    return []

def detect_bundles(chart_objects):
    longitudes = sorted(obj["Longitude"] for obj in chart_objects if obj["Object"] not in ["Ascendant", "Midheaven", "Descendant", "IC"])
    min_span = 360
    for i in range(len(longitudes)):
        span = (longitudes[(i + len(longitudes)//2) % len(longitudes)] - longitudes[i]) % 360
        min_span = min(min_span, span)
    if min_span < 120:
        return [{"Type": "Bundle", "Description": "Chart objects are tightly clustered within a third of the zodiac."}]
    return []