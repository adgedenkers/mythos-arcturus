# ----- geometry_audit.py (or paste below your existing code) -----
from itertools import combinations

# Helper: index aspects by unordered pair and by type
def _norm_pair(a, b):
    return tuple(sorted([a, b]))

def _index_aspects(aspects):
    by_type = {}
    by_pair_types = {}
    for a in aspects:
        t = a["Aspect"]
        x = a["Object 1"]
        y = a["Object 2"]
        by_type.setdefault(t, []).append(_norm_pair(x, y))
        by_pair_types.setdefault(_norm_pair(x, y), set()).add(t)
    return by_type, by_pair_types

def _has(aspect_map, p, t):
    return t in aspect_map.get(_norm_pair(*p), ())

def _tri_all(pairs, t, aspect_map):
    (a,b,c) = pairs
    return (_has(aspect_map, (a,b), t) and
            _has(aspect_map, (b,c), t) and
            _has(aspect_map, (a,c), t))

def _kite_from_trine(tri, aspect_map):
    # kite: grand trine (a,b,c)
    # add d: d opp one vertex v, and d sextile the other two
    out = set()
    a,b,c = tri
    tri_set = {a,b,c}
    for d in _all_bodies(aspect_map) - tri_set:
        for v in (a,b,c):
            others = list(tri_set - {v})
            if (_has(aspect_map, (d,v), "Opposition") and
                _has(aspect_map, (d,others[0]), "Sextile") and
                _has(aspect_map, (d,others[1]), "Sextile")):
                out.add(tuple(sorted([a,b,c,d])))
    return out

def _all_bodies(aspect_map):
    s = set()
    for (x,y) in aspect_map.keys():
        s.add(x); s.add(y)
    return s

def _enumerate_grand_trines(bodies, aspect_map):
    out = set()
    for (a,b,c) in combinations(sorted(bodies), 3):
        if _tri_all((a,b,c), "Trine", aspect_map):
            out.add(tuple(sorted([a,b,c])))
    return out

def _enumerate_t_squares(bodies, aspect_map):
    out = set()
    for (a,b,c) in combinations(sorted(bodies), 3):
        # try each as apex c
        for apex in (a,b,c):
            base = sorted(set([a,b,c]) - {apex})
            if (_has(aspect_map, tuple(base), "Opposition") and
                _has(aspect_map, (apex, base[0]), "Square") and
                _has(aspect_map, (apex, base[1]), "Square")):
                out.add(tuple(sorted([a,b,c])))
                break
    return out

def _enumerate_yods(bodies, aspect_map):
    out = set()
    for (a,b,c) in combinations(sorted(bodies), 3):
        for apex in (a,b,c):
            base = sorted(set([a,b,c]) - {apex})
            if (_has(aspect_map, tuple(base), "Sextile") and
                _has(aspect_map, (apex, base[0]), "Quincunx") and
                _has(aspect_map, (apex, base[1]), "Quincunx")):
                out.add(tuple(sorted([a,b,c])))
                break
    return out

def _enumerate_kites(bodies, aspect_map):
    out = set()
    tris = _enumerate_grand_trines(bodies, aspect_map)
    for tri in tris:
        for quad in _kite_from_trine(tri, aspect_map):
            out.add(quad)
    return out

def _enumerate_mystic_rectangles(bodies, aspect_map):
    # Two oppositions across the rectangle; sides are 2 trines + 2 sextiles alternating
    out = set()
    for (a,b,c,d) in combinations(sorted(bodies), 4):
        # pick two opposite pairs (a-c) and (b-d)
        if not (_has(aspect_map, (a,c), "Opposition") and _has(aspect_map, (b,d), "Opposition")):
            continue

        # sides in two alternating patterns:
        sides1 = [("Sextile",(a,b)), ("Trine",(b,c)), ("Sextile",(c,d)), ("Trine",(d,a))]
        sides2 = [("Trine",(a,b)), ("Sextile",(b,c)), ("Trine",(c,d)), ("Sextile",(d,a))]

        def ok(sides):
            return all(_has(aspect_map, p, t) for (t,p) in sides)

        if ok(sides1) or ok(sides2):
            out.add(tuple(sorted([a,b,c,d])))
    return out

def _enumerate_boomerangs(bodies, aspect_map):
    # Boomerang: Yod + a planet opposing the yod apex; that opposing planet sextiles both base planets
    out = set()
    for (a,b,c) in _enumerate_yods(bodies, aspect_map):
        # find apex as the one that has quincunx to the other two
        apex = None
        base = None
        for candidate in (a,b,c):
            others = sorted({a,b,c} - {candidate})
            if (_has(aspect_map, (candidate, others[0]), "Quincunx") and
                _has(aspect_map, (candidate, others[1]), "Quincunx") and
                _has(aspect_map, tuple(others), "Sextile")):
                apex = candidate
                base = others
                break
        if apex is None:
            continue

        for d in _all_bodies(aspect_map) - {a,b,c}:
            if (_has(aspect_map, (apex,d), "Opposition") and
                _has(aspect_map, (d, base[0]), "Sextile") and
                _has(aspect_map, (d, base[1]), "Sextile")):
                out.add(tuple(sorted([a,b,c,d])))
    return out

def _enumerate_cradles(bodies, aspect_map):
    # Cradle: four bodies with alternating Sextile/Trine sides; no exact oppositions across corners
    out = set()
    for (a,b,c,d) in combinations(sorted(bodies), 4):
        # reject if both diagonals are oppositions (then it's closer to mystic rectangle)
        if _has(aspect_map, (a,c), "Opposition") or _has(aspect_map, (b,d), "Opposition"):
            continue

        sides1 = [("Sextile",(a,b)), ("Trine",(b,c)), ("Sextile",(c,d)), ("Trine",(d,a))]
        sides2 = [("Trine",(a,b)), ("Sextile",(b,c)), ("Trine",(c,d)), ("Sextile",(d,a))]

        def ok(sides):
            return all(_has(aspect_map, p, t) for (t,p) in sides)

        if ok(sides1) or ok(sides2):
            out.add(tuple(sorted([a,b,c,d])))
    return out

def _enumerate_star_of_david(bodies, aspect_map):
    # Two disjoint grand trines (6 bodies total).
    # For each of the 6, within the union it should sextile exactly two bodies (both from the other triangle).
    out = set()
    tris = list(_enumerate_grand_trines(bodies, aspect_map))
    for i in range(len(tris)):
        for j in range(i+1, len(tris)):
            T1 = set(tris[i]); T2 = set(tris[j])
            if T1 & T2:
                continue
            U = tuple(sorted(T1 | T2))
            # check sextile degree-2 condition
            good = True
            for x in U:
                # degree (sextile) within union to the other triangle
                deg = 0
                for y in U:
                    if x == y: continue
                    if _has(aspect_map, (x,y), "Sextile"):
                        deg += 1
                if deg != 2:
                    good = False
                    break
            if good:
                out.add(U)
    return out

def _normalize_points(points):
    # points may already be a list of strings; normalize as sorted tuple
    return tuple(sorted(points))

def _patterns_from_detectors(aspects, detectors):
    """Run your existing detectors and normalize them into {Type: set of point-tuples}."""
    patterns = {}
    for name, fn in detectors.items():
        found = fn(aspects)
        s = set()
        for item in found:
            pts = item.get("Points") or item.get("points") or []
            s.add(_normalize_points(pts))
        patterns[name] = s
    return patterns

def _patterns_from_enumeration(aspects):
    """Enumerate patterns purely from aspect graph."""
    by_type, by_pair_types = _index_aspects(aspects)
    bodies = _all_bodies(by_pair_types)
    return {
        "Grand Trine": _enumerate_grand_trines(bodies, by_pair_types),
        "T-Square": _enumerate_t_squares(bodies, by_pair_types),
        "Yod": _enumerate_yods(bodies, by_pair_types),
        "Kite": _enumerate_kites(bodies, by_pair_types),
        "Mystic Rectangle": _enumerate_mystic_rectangles(bodies, by_pair_types),
        "Boomerang": _enumerate_boomerangs(bodies, by_pair_types),
        "Cradle": _enumerate_cradles(bodies, by_pair_types),
        "Star of David": _enumerate_star_of_david(bodies, by_pair_types),
    }

def run_geometry_audit(chart_data, aspect_defs):
    """
    Compare your detector outputs vs. canonical enumeration from the aspect list.
    Prints a human-readable report with MISSING and EXTRA patterns per type.
    """
    aspects = chart_data.get("chart_aspects", [])
    # Plug in your detector functions (already imported in your module)
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

    got = _patterns_from_detectors(aspects, detectors)
    exp = _patterns_from_enumeration(aspects)

    print("\n=== Geometric Pattern Audit ===")
    for typ in exp.keys():
        expected = exp[typ]
        got_set = got.get(typ, set())

        missing = expected - got_set
        extra = got_set - expected
        ok = (not missing and not extra)

        status = "✅ OK" if ok else ("❌ MISMATCH" if missing else "⚠️ EXTRA")
        print(f"\n{typ}: {status}")
        print(f"  expected: {len(expected)}   detected: {len(got_set)}")
        if missing:
            print("  MISSING:")
            for pts in sorted(missing):
                print("   -", ", ".join(pts))
        if extra:
            print("  EXTRA:")
            for pts in sorted(extra):
                print("   +", ", ".join(pts))
    print("\n(Enumeration uses only your aspects list + standard rules; "
          "if definitions differ in your detector code, this will show where.)")
