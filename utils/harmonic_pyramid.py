"""
Mythos Harmonic Pyramid Generator
For use in /opt/mythos/utils/harmonic_pyramid.py

Generates numerological reduction pyramids from date strings.
Stores as JSON arrays on Neo4j TrackedPerson nodes.
"""

import json
from typing import List, Dict, Any, Optional


def digital_root(n: int) -> int:
    """Reduce any positive integer to single digit (1-9). 0 stays 0."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    """Sum all digits of a number."""
    return sum(int(d) for d in str(abs(n)))


def reduction_chain(n: int) -> List[int]:
    """
    Full reduction chain preserving intermediates.
    Example: 78 -> [78, 15, 6]
    """
    chain = [n]
    current = n
    while current > 9:
        current = digit_sum(current)
        chain.append(current)
    return chain


def generate_pyramid(digits: List[int]) -> List[List[int]]:
    """
    Generate the full reduction pyramid from a list of single digits.
    Each row: sum adjacent pairs, reduce to digital root.
    Returns list of lists (rows top to bottom).
    """
    pyramid = [list(digits)]
    current_row = list(digits)
    while len(current_row) > 1:
        next_row = []
        for i in range(len(current_row) - 1):
            pair_sum = current_row[i] + current_row[i + 1]
            next_row.append(digital_root(pair_sum))
        pyramid.append(next_row)
        current_row = next_row
    return pyramid


def pyramid_signature(date_str: str) -> Dict[str, Any]:
    """
    Complete harmonic pyramid signature from a date string.
    Input: "08191978" (MMDDYYYY) or "819178" (MMDDYY variant)
    
    Returns dict suitable for JSON storage on Neo4j node:
    {
        "input": "08191978",
        "digits": [0, 8, 1, 9, 1, 9, 7, 8],
        "pyramid": [[0,8,1,9,1,9,7,8], [8,9,1,1,1,7,6], ...],
        "peak": 7,
        "row_count": 8,
        "flat": [0,8,1,9,...],  # all pyramid values flattened
        "row_sums": [43, 33, ...],
        "row_roots": [7, 6, ...],
        "digit_sum": 43,
        "digit_sum_chain": [43, 7],
        "digital_root": 7
    }
    """
    digits = [int(d) for d in date_str]
    pyramid = generate_pyramid(digits)
    ds = sum(digits)
    
    return {
        "input": date_str,
        "digits": digits,
        "pyramid": pyramid,
        "peak": pyramid[-1][0],
        "row_count": len(pyramid),
        "flat": [n for row in pyramid for n in row],
        "row_sums": [sum(row) for row in pyramid],
        "row_roots": [digital_root(sum(row)) for row in pyramid],
        "digit_sum": ds,
        "digit_sum_chain": reduction_chain(ds),
        "digital_root": digital_root(ds),
    }


def date_harmonics(dob: str) -> Dict[str, Any]:
    """
    Full harmonic extraction from a MMDDYYYY date string.
    Generates both DOB and DOBh1 pyramids plus all component analysis.
    
    This is the main entry point for TrackedPerson creation.
    """
    mm = dob[:2]
    dd = dob[2:4]
    yyyy = dob[4:8]
    yy = dob[6:8]
    
    dobh1 = mm.lstrip('0') + dd + yy if mm.startswith('0') else mm + dd + yy
    # Actually: MMDDYY with leading zeros preserved for consistency
    dobh1_v2 = mm + dd + yy  # 6-digit version
    
    month_val = int(mm)
    day_val = int(dd)
    yy_val = int(yy)
    yyyy_val = int(yyyy)
    
    return {
        "dob": dob,
        "dobh1": dobh1_v2,
        "components": {
            "month": month_val,
            "day": day_val,
            "year_short": yy_val,
            "year_full": yyyy_val,
        },
        "roots": {
            "month": digital_root(month_val) if month_val > 0 else 0,
            "day": digital_root(day_val),
            "year_short": digital_root(yy_val),
            "year_full": digital_root(yyyy_val),
        },
        "chains": {
            "month": reduction_chain(month_val),
            "day": reduction_chain(day_val),
            "year_short": reduction_chain(yy_val),
            "year_full": reduction_chain(yyyy_val),
        },
        "triangles": {
            "t1": [digital_root(month_val) if month_val > 0 else 0, 
                   digital_root(day_val), 
                   digital_root(yy_val)],
            "t2": [digital_root(month_val) if month_val > 0 else 0, 
                   digital_root(day_val), 
                   digital_root(yyyy_val)],
        },
        "pyramids": {
            "dob": pyramid_signature(dob),
            "dobh1": pyramid_signature(dobh1_v2),
        },
        "master_numbers": {
            "month": month_val if month_val in (11, 22, 33) else None,
            "day": day_val if day_val in (11, 22, 33) else None,
            "year_short": yy_val if yy_val in (11, 22, 33) else None,
            "digit_sum_dob": sum(int(d) for d in dob) if sum(int(d) for d in dob) in (11, 22, 33) else None,
        },
    }


def compare_pyramids(sig_a: Dict, sig_b: Dict) -> Dict[str, Any]:
    """
    Compare two pyramid signatures for harmonic resonance.
    Pass in the output of pyramid_signature() for each person.
    """
    matches = {
        "peak_match": sig_a["peak"] == sig_b["peak"],
        "peak_values": [sig_a["peak"], sig_b["peak"]],
        "row_matches": [],
        "positional_matches": [],
        "shared_flat_values": sorted(list(set(sig_a["flat"]) & set(sig_b["flat"]))),
    }
    
    min_rows = min(sig_a["row_count"], sig_b["row_count"])
    for r in range(min_rows):
        row_a = sig_a["pyramid"][r]
        row_b = sig_b["pyramid"][r]
        if row_a == row_b:
            matches["row_matches"].append(r)
        min_cols = min(len(row_a), len(row_b))
        for c in range(min_cols):
            if row_a[c] == row_b[c]:
                matches["positional_matches"].append({
                    "row": r, "col": c, "value": row_a[c]
                })
    
    total_cells = sum(len(row) for row in sig_a["pyramid"][:min_rows])
    match_count = len(matches["positional_matches"])
    matches["resonance_score"] = match_count
    matches["resonance_pct"] = round(match_count / total_cells * 100, 1) if total_cells > 0 else 0
    
    return matches


def full_resonance_report(dob_a: str, dob_b: str) -> Dict[str, Any]:
    """
    Full resonance comparison between two people by DOB (MMDDYYYY).
    Compares all four pyramid combinations.
    """
    ha = date_harmonics(dob_a)
    hb = date_harmonics(dob_b)
    
    return {
        "person_a": {"dob": dob_a, "harmonics": ha},
        "person_b": {"dob": dob_b, "harmonics": hb},
        "comparisons": {
            "dob_vs_dob": compare_pyramids(ha["pyramids"]["dob"], hb["pyramids"]["dob"]),
            "dobh1_vs_dobh1": compare_pyramids(ha["pyramids"]["dobh1"], hb["pyramids"]["dobh1"]),
            "dob_a_vs_dobh1_b": compare_pyramids(ha["pyramids"]["dob"], hb["pyramids"]["dobh1"]),
            "dobh1_a_vs_dob_b": compare_pyramids(ha["pyramids"]["dobh1"], hb["pyramids"]["dob"]),
        },
    }


# Example usage / test
if __name__ == "__main__":
    # Ka'tuar'el
    ka = date_harmonics("11221977")
    print(json.dumps(ka, indent=2))
    
    # Seraphe
    ser = date_harmonics("08191978")
    print(json.dumps(ser, indent=2))
    
    # Resonance
    res = full_resonance_report("11221977", "08191978")
    print(json.dumps(res, indent=2))
