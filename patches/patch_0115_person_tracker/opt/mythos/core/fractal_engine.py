"""
Fractal Engine - Numerological date analysis with full provenance tracking.

Every number generated is tagged with its source, reduction step, and origin value.
The complete set of tagged numbers forms a person's "fractal signature" — a fingerprint
that can be compared against Seraphe's or anyone else's signature to find resonance.

Ported from Seraphe's date analysis tool (JS → Python) for Mythos/Neo4j integration.

Author: Ka'tuar'el / Claude
"""

import json
from datetime import datetime, timedelta
from typing import Optional

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MASTER_NUMBERS = {11, 22, 33, 44}

NUMBER_MEANINGS = {
    1: "New beginnings, Leadership, Source",
    2: "Duality, Partnership, Divine Feminine",
    3: "Trinity, Creation, Manifestation",
    4: "Foundation, Stability, Structure",
    5: "Change, Freedom, Human experience",
    6: "Harmony, Love, Balance of opposites",
    7: "Spirituality, Wisdom, Mysticism",
    8: "Infinity, Power, As above so below",
    9: "Completion, Universal love, End of cycle",
    11: "Master: Spiritual messenger, Illumination, Gateway",
    22: "Master: Builder, Divine architecture, Bridge between worlds",
    33: "Master: Teacher, Christ consciousness, Compassion",
    44: "Master: Healer, Foundation of light, Cosmic structure",
}

# Sun sign date ranges (month, day) boundaries — end dates inclusive
SUN_SIGNS = [
    ("capricorn",   "♑", (1, 1),   (1, 19)),
    ("aquarius",    "♒", (1, 20),  (2, 18)),
    ("pisces",      "♓", (2, 19),  (3, 20)),
    ("aries",       "♈", (3, 21),  (4, 19)),
    ("taurus",      "♉", (4, 20),  (5, 20)),
    ("gemini",      "♊", (5, 21),  (6, 20)),
    ("cancer",      "♋", (6, 21),  (7, 22)),
    ("leo",         "♌", (7, 23),  (8, 22)),
    ("virgo",       "♍", (8, 23),  (9, 22)),
    ("libra",       "♎", (9, 23),  (10, 22)),
    ("scorpio",     "♏", (10, 23), (11, 21)),
    ("sagittarius", "♐", (11, 22), (12, 21)),
    ("capricorn",   "♑", (12, 22), (12, 31)),
]

# Category prefixes for PIDs
PID_CATEGORIES = {
    "F": "family",
    "C": "celebrity",
    "S": "spiritual",
    "P": "personal",
    "W": "work",
}


# ═══════════════════════════════════════════════════════════════════
# CORE MATH
# ═══════════════════════════════════════════════════════════════════

def digit_sum(n: int) -> int:
    """Sum all digits of n."""
    return sum(int(d) for d in str(abs(n)))


def is_master(n: int) -> bool:
    """Check if n is a master number."""
    return n in MASTER_NUMBERS


def reduce(n: int) -> dict:
    """
    Reduce a number to a single digit, preserving master numbers in the path.
    Returns: { path: [original, ..., final], final: int, masters: [int, ...] }
    """
    n = abs(int(n))
    path = [n]
    masters = []
    current = n

    if is_master(current):
        masters.append(current)

    while current > 9:
        current = digit_sum(current)
        path.append(current)
        if is_master(current):
            masters.append(current)

    return {"path": path, "final": current, "masters": masters}


def harmonics_of(n: int) -> dict:
    """
    Compute harmonics for a number.
    Returns: { factors, spiral (1-99 reducing to same root), mirrors, root }
    """
    root = reduce(n)["final"]
    factors = [i for i in range(1, n + 1) if n % i == 0] if n > 0 else []
    spiral = [i for i in range(1, 100) if reduce(i)["final"] == root]
    s = str(n)
    mirror = int(s[::-1])
    mirrors = [mirror] if mirror != n and mirror > 0 else []
    return {"factors": factors, "spiral": spiral, "mirrors": mirrors, "root": root}


# ═══════════════════════════════════════════════════════════════════
# SUN SIGN
# ═══════════════════════════════════════════════════════════════════

def get_sun_sign(month: int, day: int) -> tuple:
    """
    Returns (sign_name, glyph) for a given month/day.
    """
    for sign, glyph, (sm, sd), (em, ed) in SUN_SIGNS:
        if (month > sm or (month == sm and day >= sd)) and \
           (month < em or (month == em and day <= ed)):
            return sign, glyph
    return "unknown", "?"


# ═══════════════════════════════════════════════════════════════════
# PID GENERATION
# ═══════════════════════════════════════════════════════════════════

def generate_pid(category_letter: str, sequence: int, sun_sign_glyph: str = "") -> tuple:
    """
    Generate a person ID.
    Returns: (pid_functional, pid_display)
    pid_functional = "C001" (for lookups)
    pid_display = "C001♓" (for display)
    """
    cat = category_letter.upper()
    if cat not in PID_CATEGORIES:
        raise ValueError(f"Invalid category '{cat}'. Use: {list(PID_CATEGORIES.keys())}")
    pid = f"{cat}{sequence:03d}"
    pid_display = f"{pid}{sun_sign_glyph}" if sun_sign_glyph else pid
    return pid, pid_display


# ═══════════════════════════════════════════════════════════════════
# PROVENANCE-TRACKED SIGNATURE GENERATION
# ═══════════════════════════════════════════════════════════════════

def _sig_entry(value: int, source: str, step: str, from_value: int,
               date_str: str = "", position: str = "") -> dict:
    """Create a single signature entry with full provenance."""
    entry = {
        "value": value,
        "source": source,
        "step": step,
        "from": from_value,
    }
    if date_str:
        entry["date"] = date_str
    if position:
        entry["position"] = position
    return entry


def _reduction_signature(reduction: dict, source: str, date_str: str = "",
                         position: str = "") -> list:
    """
    Generate signature entries for a full reduction path.
    Each step in the path gets its own entry.
    """
    entries = []
    path = reduction["path"]

    # Original value
    entries.append(_sig_entry(
        path[0], source, "original", path[0], date_str, position
    ))

    # Each reduction step
    for i in range(1, len(path)):
        step_name = f"reduction_{i}"
        if path[i] == path[-1] and i == len(path) - 1:
            step_name = "final"
        entries.append(_sig_entry(
            path[i], source, step_name, path[i - 1], date_str, position
        ))

    # Master numbers get explicit entries
    for master in reduction["masters"]:
        entries.append(_sig_entry(
            master, source, "master", master, date_str, position
        ))

    return entries


def analyze_date_with_signature(month: int, day: int, year: int,
                                 date_label: str = "birth",
                                 date_str: str = "") -> dict:
    """
    Full numerological analysis of a date with provenance-tracked signature.

    Returns:
        {
            "analysis": { ... full analysis dict ... },
            "signature": [ ... list of provenance entries ... ]
        }
    """
    if not date_str:
        date_str = f"{month:02d}/{day:02d}/{year}"

    sig = []

    # Individual reductions
    m = reduce(month)
    d = reduce(day)
    yy2 = reduce(year % 100)
    yy4 = reduce(year)

    sig.extend(_reduction_signature(m, f"{date_label}_month", date_str, "month"))
    sig.extend(_reduction_signature(d, f"{date_label}_day", date_str, "day"))
    sig.extend(_reduction_signature(yy2, f"{date_label}_year2", date_str, "year2"))
    sig.extend(_reduction_signature(yy4, f"{date_label}_year4", date_str, "year4"))

    # Triangle 1 (M/D/YY)
    triangle1 = [m["final"], d["final"], yy2["final"]]
    t1_sum = reduce(sum(triangle1))
    for i, val in enumerate(triangle1):
        pos = ["month", "day", "year2"][i]
        sig.append(_sig_entry(val, f"{date_label}_triangle1", f"vertex_{i}", val, date_str, pos))
    sig.extend(_reduction_signature(t1_sum, f"{date_label}_triangle1_sum", date_str))

    # Triangle 2 (M/D/YYYY)
    triangle2 = [m["final"], d["final"], yy4["final"]]
    t2_sum = reduce(sum(triangle2))
    for i, val in enumerate(triangle2):
        pos = ["month", "day", "year4"][i]
        sig.append(_sig_entry(val, f"{date_label}_triangle2", f"vertex_{i}", val, date_str, pos))
    sig.extend(_reduction_signature(t2_sum, f"{date_label}_triangle2_sum", date_str))

    # Folds
    md_num = int(f"{month}{day:02d}")
    md = reduce(md_num)
    sig.extend(_reduction_signature(md, f"{date_label}_fold_md", date_str))

    md_yyyy_num = int(f"{month}{day:02d}{year}")
    md_yyyy = reduce(md_yyyy_num)
    sig.extend(_reduction_signature(md_yyyy, f"{date_label}_fold_md_yyyy", date_str))

    yy2raw = f"{year % 100:02d}"
    md_yy_num = int(f"{month}{day:02d}{yy2raw}")
    md_yy = reduce(md_yy_num)
    sig.extend(_reduction_signature(md_yy, f"{date_label}_fold_md_yy", date_str))

    # Life path
    lifepath = reduce(m["final"] + d["final"] + yy4["final"])
    sig.extend(_reduction_signature(lifepath, f"{date_label}_lifepath", date_str))

    # Birthstring as a number
    birthstring = f"{month:02d}{day:02d}{year}"
    birthstring_red = reduce(int(birthstring))
    sig.extend(_reduction_signature(birthstring_red, f"{date_label}_birthstring", date_str))

    # Harmonics for triangle vertices (factors, mirrors)
    all_triangle_values = set(triangle1 + triangle2)
    for val in all_triangle_values:
        h = harmonics_of(val)
        for mirror in h["mirrors"]:
            sig.append(_sig_entry(
                mirror, f"{date_label}_mirror", "mirror_of", val, date_str
            ))

    # Collect all unique numbers
    all_numbers = set()
    for entry in sig:
        all_numbers.add(entry["value"])

    # Spiral roots
    spiral_roots = set()
    for val in triangle1 + triangle2:
        spiral_roots.add(reduce(val)["final"])

    analysis = {
        "month": m,
        "day": d,
        "year2": yy2,
        "year4": yy4,
        "triangle1": triangle1,
        "triangle2": triangle2,
        "triangle1_sum": t1_sum,
        "triangle2_sum": t2_sum,
        "md": md,
        "md_yyyy": md_yyyy,
        "md_yy": md_yy,
        "birthstring": birthstring,
        "lifepath": lifepath,
        "all_numbers": sorted(all_numbers),
        "spiral_roots": sorted(spiral_roots),
        "raw": {"month": month, "day": day, "year": year},
    }

    return {"analysis": analysis, "signature": sig}


# ═══════════════════════════════════════════════════════════════════
# CONCEPTION DATE
# ═══════════════════════════════════════════════════════════════════

def compute_conception_signature(birth_month: int, birth_day: int,
                                  birth_year: int) -> dict:
    """
    Estimate conception date and generate its fractal signature.
    Uses 266-day estimate (fertilization-based).
    """
    birth = datetime(birth_year, birth_month, birth_day)
    conception = birth - timedelta(days=266)
    c_date_str = f"{conception.month:02d}/{conception.day:02d}/{conception.year}"

    result = analyze_date_with_signature(
        conception.month, conception.day, conception.year,
        date_label="conception",
        date_str=c_date_str
    )
    result["conception_date"] = c_date_str
    result["conception_month"] = conception.month
    result["conception_day"] = conception.day
    result["conception_year"] = conception.year
    return result


# ═══════════════════════════════════════════════════════════════════
# FLATTEN FOR NEO4J
# ═══════════════════════════════════════════════════════════════════

def flatten_for_neo4j(analysis: dict, prefix: str = "birth_") -> dict:
    """
    Flatten a date analysis into Neo4j-ready properties.
    Signature stored separately as JSON array string.
    """
    p = prefix
    props = {}

    props[f"{p}month"] = analysis["raw"]["month"]
    props[f"{p}day"] = analysis["raw"]["day"]
    props[f"{p}year"] = analysis["raw"]["year"]
    props[f"{p}birthstring"] = analysis["birthstring"]

    props[f"{p}month_root"] = analysis["month"]["final"]
    props[f"{p}day_root"] = analysis["day"]["final"]
    props[f"{p}year2_root"] = analysis["year2"]["final"]
    props[f"{p}year4_root"] = analysis["year4"]["final"]

    props[f"{p}month_path"] = " → ".join(str(n) for n in analysis["month"]["path"])
    props[f"{p}day_path"] = " → ".join(str(n) for n in analysis["day"]["path"])
    props[f"{p}year4_path"] = " → ".join(str(n) for n in analysis["year4"]["path"])

    # Master numbers
    all_masters = set()
    for key in ["month", "day", "year2", "year4", "md", "md_yyyy", "md_yy", "lifepath"]:
        all_masters.update(analysis[key]["masters"])
    props[f"{p}master_numbers"] = sorted(all_masters)

    # Triangles
    props[f"{p}triangle1"] = analysis["triangle1"]
    props[f"{p}triangle2"] = analysis["triangle2"]
    props[f"{p}triangle1_sum"] = analysis["triangle1_sum"]["final"]
    props[f"{p}triangle2_sum"] = analysis["triangle2_sum"]["final"]

    # Folds
    props[f"{p}md_fold"] = analysis["md"]["final"]
    props[f"{p}md_fold_path"] = " → ".join(str(n) for n in analysis["md"]["path"])
    props[f"{p}md_yyyy_fold"] = analysis["md_yyyy"]["final"]
    props[f"{p}md_yy_fold"] = analysis["md_yy"]["final"]

    # Life path
    props[f"{p}lifepath"] = analysis["lifepath"]["final"]
    props[f"{p}lifepath_path"] = " → ".join(str(n) for n in analysis["lifepath"]["path"])

    # All numbers and spiral roots
    props[f"{p}all_numbers"] = analysis["all_numbers"]
    props[f"{p}spiral_roots"] = analysis["spiral_roots"]

    return props


# ═══════════════════════════════════════════════════════════════════
# RESONANCE COMPARISON
# ═══════════════════════════════════════════════════════════════════

def compare_signatures(sig_a: list, sig_b: list, name_a: str = "A",
                       name_b: str = "B") -> list:
    """
    Compare two fractal signatures and find all resonance matches.

    A match occurs when two entries share the same value.
    The match report includes WHERE in each person the number comes from.

    Returns list of:
    {
        "value": 5,
        "a_source": "birth_day",
        "a_step": "final",
        "a_from": 14,
        "a_date": "03/14/1879",
        "a_position": "day",
        "b_source": "birth_triangle1",
        "b_step": "vertex_1",
        "b_from": 5,
        "b_date": "08/19/1978",
        "b_position": "day",
        "strength": "positional"  // or "value", "master", "triangle"
    }
    """
    matches = []
    seen_pairs = set()  # avoid duplicate match reports

    for ea in sig_a:
        for eb in sig_b:
            if ea["value"] == eb["value"]:
                # Create a dedup key
                pair_key = (
                    ea["value"],
                    ea["source"], ea["step"],
                    eb["source"], eb["step"]
                )
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                # Determine match strength
                strength = "value"  # default: same number exists somewhere

                # Positional match: same position in triangle
                if (ea.get("position") and eb.get("position") and
                        ea["position"] == eb["position"] and
                        "triangle" in ea["source"] and "triangle" in eb["source"]):
                    strength = "positional"

                # Master match
                if ea["step"] == "master" or eb["step"] == "master":
                    strength = "master"

                # Triangle vertex match (same vertex index)
                if (ea["step"] == eb["step"] and
                        ea["step"].startswith("vertex_") and
                        ea["source"].split("_")[-1] == eb["source"].split("_")[-1]):
                    strength = "triangle_exact"

                # Life path match
                if "lifepath" in ea["source"] and "lifepath" in eb["source"]:
                    strength = "lifepath"

                match = {
                    "value": ea["value"],
                    "a_source": ea["source"],
                    "a_step": ea["step"],
                    "a_from": ea["from"],
                    "a_date": ea.get("date", ""),
                    "a_position": ea.get("position", ""),
                    "b_source": eb["source"],
                    "b_step": eb["step"],
                    "b_from": eb["from"],
                    "b_date": eb.get("date", ""),
                    "b_position": eb.get("position", ""),
                    "strength": strength,
                }
                matches.append(match)

    # Sort: strongest matches first
    strength_order = {
        "triangle_exact": 0,
        "positional": 1,
        "lifepath": 2,
        "master": 3,
        "value": 4,
    }
    matches.sort(key=lambda m: (strength_order.get(m["strength"], 99), m["value"]))

    return matches


def resonance_summary(matches: list) -> dict:
    """
    Summarize a list of matches into counts by strength.
    Returns: { "triangle_exact": N, "positional": N, ... , "total": N, "score": N }
    """
    counts = {}
    for m in matches:
        s = m["strength"]
        counts[s] = counts.get(s, 0) + 1

    # Score: weighted
    weights = {
        "triangle_exact": 10,
        "positional": 8,
        "lifepath": 7,
        "master": 6,
        "value": 1,
    }
    score = sum(counts.get(k, 0) * v for k, v in weights.items())
    counts["total"] = len(matches)
    counts["score"] = score
    return counts


# ═══════════════════════════════════════════════════════════════════
# TELEGRAM FORMATTING
# ═══════════════════════════════════════════════════════════════════

def format_fractals_telegram(name: str, pid_display: str,
                              analysis: dict, signature: list) -> str:
    """Format fractal analysis for Telegram display."""
    lines = []
    lines.append(f"🔢 *{name}* (`{pid_display}`)")
    lines.append("")

    raw = analysis["raw"]
    lines.append(f"📅 {raw['month']}/{raw['day']}/{raw['year']}")

    # Life path
    lp = analysis["lifepath"]
    lp_str = " → ".join(str(n) for n in lp["path"])
    lines.append(f"🔮 *Life Path:* {lp_str}")
    if lp["final"] in NUMBER_MEANINGS:
        lines.append(f"   _{NUMBER_MEANINGS[lp['final']]}_")
    lines.append("")

    # Triangles
    t1 = analysis["triangle1"]
    t2 = analysis["triangle2"]
    t1s = analysis["triangle1_sum"]
    t2s = analysis["triangle2_sum"]
    lines.append(f"🔺 *T1* (M/D/YY): {t1[0]}·{t1[1]}·{t1[2]} → {t1s['final']}")
    lines.append(f"🔺 *T2* (M/D/YYYY): {t2[0]}·{t2[1]}·{t2[2]} → {t2s['final']}")
    lines.append("")

    # Masters
    all_masters = set()
    for key in ["month", "day", "year2", "year4", "md", "md_yyyy", "md_yy", "lifepath"]:
        all_masters.update(analysis[key]["masters"])
    if all_masters:
        lines.append(f"⭐ *Masters:* {', '.join(str(m) for m in sorted(all_masters))}")
        lines.append("")

    # Folds
    md = analysis["md"]
    md_yyyy = analysis["md_yyyy"]
    md_yy = analysis["md_yy"]
    lines.append("📐 *Folds:*")
    lines.append(f"   M/D: {' → '.join(str(n) for n in md['path'])}")
    lines.append(f"   M/D+YYYY: {' → '.join(str(n) for n in md_yyyy['path'])}")
    lines.append(f"   M/D+YY: {' → '.join(str(n) for n in md_yy['path'])}")
    lines.append("")

    # Reductions
    lines.append("🌀 *Reductions:*")
    lines.append(f"   Month: {' → '.join(str(n) for n in analysis['month']['path'])}")
    lines.append(f"   Day: {' → '.join(str(n) for n in analysis['day']['path'])}")
    lines.append(f"   Year: {' → '.join(str(n) for n in analysis['year4']['path'])}")
    lines.append("")

    # Signature size
    lines.append(f"📊 *Signature:* {len(signature)} provenance entries")

    return "\n".join(lines)


def format_resonance_telegram(name_a: str, pid_a: str,
                               name_b: str, pid_b: str,
                               matches: list, summary: dict) -> str:
    """Format resonance comparison for Telegram display."""
    lines = []
    lines.append(f"🌊 *Resonance: {name_a}* (`{pid_a}`) ↔ *{name_b}* (`{pid_b}`)")
    lines.append(f"Score: *{summary['score']}* ({summary['total']} matches)")
    lines.append("")

    # Group by strength
    strength_icons = {
        "triangle_exact": "🔴",
        "positional": "🟠",
        "lifepath": "🟡",
        "master": "⭐",
        "value": "⚪",
    }
    strength_labels = {
        "triangle_exact": "Triangle Exact",
        "positional": "Positional",
        "lifepath": "Life Path",
        "master": "Master Number",
        "value": "Value Match",
    }

    # Show strongest matches (cap at 30 to avoid Telegram message limits)
    shown = 0
    current_strength = None
    for m in matches:
        if shown >= 30:
            remaining = len(matches) - shown
            lines.append(f"\n_...and {remaining} more value matches_")
            break

        if m["strength"] != current_strength:
            current_strength = m["strength"]
            icon = strength_icons.get(current_strength, "⚪")
            label = strength_labels.get(current_strength, current_strength)
            count = summary.get(current_strength, 0)
            lines.append(f"\n{icon} *{label}* ({count}):")

        # Format the match
        a_src = m["a_source"].replace("birth_", "").replace("death_", "†")
        b_src = m["b_source"].replace("birth_", "").replace("death_", "†")
        a_pos = f" [{m['a_position']}]" if m.get("a_position") else ""
        b_pos = f" [{m['b_position']}]" if m.get("b_position") else ""

        lines.append(f"  `{m['value']}` ← {a_src}{a_pos} | {b_src}{b_pos}")
        shown += 1

    return "\n".join(lines)
