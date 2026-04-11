#!/usr/bin/env python3
"""
Astrological Rectification Engine

Given a birth date, location, and a set of dated life events, determines the
most likely birth time by scoring candidate charts against transit-to-angle
alignments for each event.

Approach:
  1. Sweep 24 hours in configurable increments (default: 10 minutes = 144 candidates)
  2. For each candidate time, compute natal chart (ASC, MC, DSC, IC)
  3. For each life event, compute transits at the event date
  4. Score: how many events produce tight transit aspects to the candidate's angles
  5. Refine: take top candidates and re-sweep at 1-minute resolution
  6. Return ranked results with confidence scores

Event categories and their expected transit signatures:
  - career:    Saturn/Jupiter/Pluto to MC, Sun to MC
  - marriage:  Jupiter/Venus to DSC, Saturn to DSC (binding)
  - divorce:   Uranus/Pluto to DSC, Saturn square DSC
  - children:  Jupiter to IC/5th cusp, transits to Moon
  - health:    Saturn/Pluto to ASC, Mars to ASC
  - death_family: Saturn/Pluto to IC, transits to Moon
  - legal:     Saturn/Jupiter to MC, Pluto to MC
  - award:     Jupiter to MC/ASC, Sun to MC
  - scandal:   Pluto/Uranus to MC, Neptune to MC

Usage:
    from rectification import rectify_birth_time
    
    events = [
        {"date": "1994-09-22", "category": "career", "description": "Friends premiered"},
        {"date": "2000-07-29", "category": "marriage", "description": "Married Brad Pitt"},
    ]
    
    results = rectify_birth_time(
        year=1969, month=2, day=11,
        lat=34.0522, lon=-118.2437,  # Los Angeles
        tz_offset=-8,
        events=events
    )
"""

import sys
import os
import json
from math import floor

# Add the tools directory to path for ephemeris import
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from ephemeris import (
    calculate_planets, calculate_houses, calculate_aspect,
    ASPECT_DEFINITIONS, lon_to_sign, format_position
)
import swisseph as swe


# ─── Transit Signature Definitions ───────────────────────────────────────────

# Which transiting planets are significant for each event category,
# and which natal angles/points they should aspect.
# Weight reflects how diagnostic that combination is for rectification.

EVENT_SIGNATURES = {
    "career": {
        "transit_planets": {
            "Saturn": 3.0, "Jupiter": 2.5, "Pluto": 3.0,
            "Uranus": 2.0, "Neptune": 1.5, "Sun": 1.0, "Mars": 0.5
        },
        "natal_targets": ["MC", "ASC"],
        "description": "Career peaks, job changes, promotions, launches"
    },
    "marriage": {
        "transit_planets": {
            "Jupiter": 2.5, "Venus": 2.0, "Saturn": 3.0,
            "Pluto": 2.0, "Neptune": 1.5, "Sun": 1.0
        },
        "natal_targets": ["DSC", "IC", "ASC"],
        "description": "Marriages, committed partnerships"
    },
    "divorce": {
        "transit_planets": {
            "Uranus": 3.0, "Pluto": 3.0, "Saturn": 2.5,
            "Mars": 1.5, "Neptune": 2.0
        },
        "natal_targets": ["DSC", "ASC", "MC"],
        "description": "Divorces, separations, relationship endings"
    },
    "children": {
        "transit_planets": {
            "Jupiter": 3.0, "Saturn": 2.0, "Pluto": 1.5,
            "Venus": 1.5, "Moon": 1.0
        },
        "natal_targets": ["IC", "DSC", "ASC"],
        "description": "Birth of children"
    },
    "health": {
        "transit_planets": {
            "Saturn": 3.0, "Pluto": 3.0, "Mars": 2.0,
            "Uranus": 2.0, "Neptune": 2.0
        },
        "natal_targets": ["ASC", "MC"],
        "description": "Health crises, surgeries, accidents"
    },
    "death_family": {
        "transit_planets": {
            "Saturn": 3.0, "Pluto": 3.0, "Neptune": 2.0,
            "Uranus": 1.5, "Mars": 1.0
        },
        "natal_targets": ["IC", "ASC", "MC"],
        "description": "Death of parent or close family member"
    },
    "legal": {
        "transit_planets": {
            "Saturn": 3.0, "Jupiter": 2.5, "Pluto": 2.5,
            "Uranus": 2.0, "Neptune": 1.5, "Mars": 1.0
        },
        "natal_targets": ["MC", "ASC"],
        "description": "Legal issues, lawsuits, public legal matters"
    },
    "award": {
        "transit_planets": {
            "Jupiter": 3.0, "Sun": 2.0, "Venus": 1.5,
            "Saturn": 1.5, "Pluto": 1.0
        },
        "natal_targets": ["MC", "ASC"],
        "description": "Awards, honors, major public recognition"
    },
    "scandal": {
        "transit_planets": {
            "Pluto": 3.0, "Uranus": 2.5, "Neptune": 3.0,
            "Saturn": 2.0, "Mars": 1.5
        },
        "natal_targets": ["MC", "ASC", "IC"],
        "description": "Public scandals, reputation crises"
    }
}

# Aspect weights for rectification scoring
# Conjunctions and oppositions to angles are most diagnostic
RECT_ASPECT_WEIGHTS = {
    "conjunction": 5.0,
    "opposition": 4.0,
    "square": 3.0,
    "trine": 1.5,
    "sextile": 1.0,
}

# Tighter orbs for rectification than general natal work
RECT_ORBS = {
    "conjunction": 3.0,
    "opposition": 3.0,
    "square": 2.5,
    "trine": 2.0,
    "sextile": 1.5,
}


# ─── Scoring Functions ───────────────────────────────────────────────────────

def score_event_against_angles(transit_jd, natal_angles, event_category):
    """
    Score how well a single event's transits hit the natal angles.
    
    Returns a score and list of matching aspects.
    """
    swe.set_ephe_path(None)
    sigs = EVENT_SIGNATURES.get(event_category, EVENT_SIGNATURES["career"])
    
    transit_planets = calculate_planets(transit_jd)
    
    total_score = 0.0
    matches = []
    
    for t_name, t_weight in sigs["transit_planets"].items():
        if t_name not in transit_planets or "longitude" not in transit_planets[t_name]:
            continue
        t_lon = transit_planets[t_name]["longitude"]
        
        for angle_name in sigs["natal_targets"]:
            if angle_name not in natal_angles:
                continue
            a_lon = natal_angles[angle_name]
            
            # Check aspects with tight rectification orbs
            diff = abs(t_lon - a_lon) % 360
            if diff > 180:
                diff = 360 - diff
            
            for asp_name, asp_weight in RECT_ASPECT_WEIGHTS.items():
                target_angle = {"conjunction": 0, "opposition": 180, "square": 90,
                               "trine": 120, "sextile": 60}[asp_name]
                orb = abs(diff - target_angle)
                max_orb = RECT_ORBS[asp_name]
                
                if orb <= max_orb:
                    # Score = planet_weight × aspect_weight × (1 - orb/max_orb)
                    # Tighter orbs score exponentially higher
                    tightness = (1 - orb / max_orb) ** 2
                    score = t_weight * asp_weight * tightness
                    total_score += score
                    matches.append({
                        "transit_planet": t_name,
                        "natal_angle": angle_name,
                        "aspect": asp_name,
                        "orb": round(orb, 2),
                        "score": round(score, 2)
                    })
    
    return total_score, matches


def score_candidate_time(year, month, day, hour, minute, lat, lon, tz_offset, events):
    """
    Score a single candidate birth time against all life events.
    
    Returns total score, per-event breakdown, and angle positions.
    """
    swe.set_ephe_path(None)
    ut_hour = hour + minute / 60.0 - tz_offset
    jd = swe.julday(year, month, day, ut_hour)
    
    houses = calculate_houses(jd, lat, lon, 'P')
    angles = {
        "ASC": houses["angles"]["ASC"]["longitude"],
        "MC": houses["angles"]["MC"]["longitude"],
        "DSC": (houses["angles"]["ASC"]["longitude"] + 180) % 360,
        "IC": (houses["angles"]["MC"]["longitude"] + 180) % 360,
    }
    
    total_score = 0.0
    event_scores = []
    
    for event in events:
        # Parse event date
        parts = event["date"].split("-")
        e_year, e_month, e_day = int(parts[0]), int(parts[1]), int(parts[2])
        e_jd = swe.julday(e_year, e_month, e_day, 12.0)  # noon UT for event
        
        category = event.get("category", "career")
        e_score, e_matches = score_event_against_angles(e_jd, angles, category)
        
        total_score += e_score
        event_scores.append({
            "event": event.get("description", event["date"]),
            "date": event["date"],
            "category": category,
            "score": round(e_score, 2),
            "matches": e_matches
        })
    
    return {
        "time": f"{hour:02d}:{minute:02d}",
        "hour": hour,
        "minute": minute,
        "total_score": round(total_score, 2),
        "angles": {
            "ASC": {"longitude": round(angles["ASC"], 4), "formatted": format_position(angles["ASC"]), "sign": lon_to_sign(angles["ASC"])[0]},
            "MC": {"longitude": round(angles["MC"], 4), "formatted": format_position(angles["MC"]), "sign": lon_to_sign(angles["MC"])[0]},
            "DSC": {"longitude": round(angles["DSC"], 4), "formatted": format_position(angles["DSC"])},
            "IC": {"longitude": round(angles["IC"], 4), "formatted": format_position(angles["IC"])},
        },
        "event_scores": event_scores
    }


# ─── Main Rectification Function ────────────────────────────────────────────

def rectify_birth_time(year, month, day, lat, lon, tz_offset, events,
                       coarse_step_minutes=10, fine_step_minutes=1,
                       top_n_refine=5):
    """
    Two-pass rectification: coarse sweep then fine refinement.
    
    Args:
        year, month, day: Birth date
        lat, lon: Birth location
        tz_offset: Hours from UTC
        events: List of dicts with 'date', 'category', 'description'
        coarse_step_minutes: First pass resolution (default 10 min = 144 candidates)
        fine_step_minutes: Second pass resolution (default 1 min)
        top_n_refine: How many top candidates to refine
    
    Returns:
        Dict with ranked candidates, best time, confidence assessment
    """
    
    # ── Pass 1: Coarse sweep ──
    coarse_results = []
    for total_minutes in range(0, 24 * 60, coarse_step_minutes):
        hour = total_minutes // 60
        minute = total_minutes % 60
        result = score_candidate_time(year, month, day, hour, minute,
                                      lat, lon, tz_offset, events)
        coarse_results.append(result)
    
    # Sort by score descending
    coarse_results.sort(key=lambda x: x["total_score"], reverse=True)
    
    # ── Pass 2: Fine refinement around top candidates ──
    fine_results = []
    refined_windows = set()  # avoid re-scanning overlapping windows
    
    for candidate in coarse_results[:top_n_refine]:
        center_minutes = candidate["hour"] * 60 + candidate["minute"]
        window_start = max(0, center_minutes - coarse_step_minutes)
        window_end = min(24 * 60 - 1, center_minutes + coarse_step_minutes)
        
        # Skip if we've already refined this window
        window_key = (window_start // coarse_step_minutes)
        if window_key in refined_windows:
            continue
        refined_windows.add(window_key)
        
        for total_minutes in range(window_start, window_end + 1, fine_step_minutes):
            hour = total_minutes // 60
            minute = total_minutes % 60
            result = score_candidate_time(year, month, day, hour, minute,
                                          lat, lon, tz_offset, events)
            fine_results.append(result)
    
    # Sort fine results
    fine_results.sort(key=lambda x: x["total_score"], reverse=True)
    
    # ── Confidence Assessment ──
    best = fine_results[0] if fine_results else coarse_results[0]
    second = fine_results[1] if len(fine_results) > 1 else (coarse_results[1] if len(coarse_results) > 1 else None)
    
    # How many events scored above zero for the best time?
    events_hitting = sum(1 for e in best["event_scores"] if e["score"] > 0)
    events_total = len(events)
    hit_ratio = events_hitting / events_total if events_total > 0 else 0
    
    # Score gap between #1 and #2
    score_gap = (best["total_score"] - second["total_score"]) / best["total_score"] if (second and best["total_score"] > 0) else 1.0
    
    # Check if top candidates cluster (same rising sign = higher confidence)
    top_signs = [r["angles"]["ASC"]["sign"] for r in fine_results[:10]] if fine_results else []
    sign_consensus = max(top_signs.count(s) for s in set(top_signs)) / len(top_signs) if top_signs else 0
    
    # Composite confidence
    confidence_score = (hit_ratio * 0.4 + score_gap * 0.3 + sign_consensus * 0.3) * 100
    
    if confidence_score >= 75:
        confidence_label = "HIGH"
        confidence_note = "Strong convergence across multiple events. Rising sign and degree are reliable."
    elif confidence_score >= 50:
        confidence_label = "MODERATE"
        confidence_note = "Good convergence on rising sign. Degree may have ±5° uncertainty."
    elif confidence_score >= 30:
        confidence_label = "LOW"
        confidence_note = "Rising sign is plausible but not confirmed. More events would help narrow it."
    else:
        confidence_label = "SPECULATIVE"
        confidence_note = "Insufficient event alignment. Treat as exploratory — rising sign uncertain."
    
    return {
        "meta": {
            "birth_date": f"{year}-{month:02d}-{day:02d}",
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz_offset,
            "events_provided": events_total,
            "events_hitting": events_hitting,
            "coarse_candidates_tested": len(coarse_results),
            "fine_candidates_tested": len(fine_results),
        },
        "best_time": {
            "time": best["time"],
            "hour": best["hour"],
            "minute": best["minute"],
            "score": best["total_score"],
            "angles": best["angles"],
            "event_detail": best["event_scores"],
        },
        "confidence": {
            "score": round(confidence_score, 1),
            "label": confidence_label,
            "note": confidence_note,
            "hit_ratio": round(hit_ratio * 100, 1),
            "score_gap_pct": round(score_gap * 100, 1),
            "sign_consensus_pct": round(sign_consensus * 100, 1),
        },
        "top_candidates": [
            {
                "time": r["time"],
                "score": r["total_score"],
                "asc": r["angles"]["ASC"]["formatted"],
                "mc": r["angles"]["MC"]["formatted"],
            }
            for r in (fine_results if fine_results else coarse_results)[:10]
        ],
        "rising_sign_distribution": _sign_distribution(
            fine_results if fine_results else coarse_results
        )
    }


def _sign_distribution(results):
    """Show which rising signs score highest overall."""
    sign_scores = {}
    for r in results:
        sign = r["angles"]["ASC"]["sign"]
        if sign not in sign_scores:
            sign_scores[sign] = {"total_score": 0, "count": 0, "best_time": None, "best_score": 0}
        sign_scores[sign]["total_score"] += r["total_score"]
        sign_scores[sign]["count"] += 1
        if r["total_score"] > sign_scores[sign]["best_score"]:
            sign_scores[sign]["best_score"] = r["total_score"]
            sign_scores[sign]["best_time"] = r["time"]
    
    return {
        sign: {
            "avg_score": round(data["total_score"] / data["count"], 2),
            "best_score": round(data["best_score"], 2),
            "best_time": data["best_time"],
            "candidates": data["count"]
        }
        for sign, data in sorted(sign_scores.items(),
                                  key=lambda x: x[1]["total_score"] / x[1]["count"],
                                  reverse=True)
    }


# ─── CLI Interface ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Astrological Birth Time Rectification")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--tz", type=float, default=0)
    parser.add_argument("--events", type=str, required=True, help="Path to events JSON file")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--coarse-step", type=int, default=10)
    parser.add_argument("--fine-step", type=int, default=1)
    
    args = parser.parse_args()
    
    with open(args.events) as f:
        events = json.load(f)
    
    results = rectify_birth_time(
        args.year, args.month, args.day,
        args.lat, args.lon, args.tz,
        events,
        coarse_step_minutes=args.coarse_step,
        fine_step_minutes=args.fine_step
    )
    
    output = json.dumps(results, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)
