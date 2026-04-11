"""
Mythos Harmonic Engine
/opt/mythos/harmonics/engine.py

Universal numeric decomposition and resonance comparison.
Extracts harmonics from any number source (dates, positions, names, etc.)
and stores them in PostgreSQL for cross-system matching.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CORE MATH
# ═══════════════════════════════════════════════════════════════════

ROTATABLE_DIGITS = {0: 0, 1: 1, 6: 9, 8: 8, 9: 6}
MASTER_NUMBERS = {11, 22, 33}


def digital_root(n: int) -> int:
    """Reduce any positive integer to single digit (1-9). 0 stays 0."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    """Sum all digits of a number."""
    return sum(int(d) for d in str(abs(n)))


def reduction_chain(n: int) -> List[int]:
    """Full reduction chain preserving intermediates. 78 -> [78, 15, 6]"""
    chain = [n]
    current = n
    while current > 9:
        current = digit_sum(current)
        chain.append(current)
    return chain


def mirror_value(n: int) -> int:
    """Reverse digits of a number. 16 -> 61, 123 -> 321."""
    return int(str(n)[::-1])


def rotation_value(n: int) -> Optional[int]:
    """
    180° rotation. Only valid when ALL digits are in {0, 1, 6, 8, 9}.
    6↔9 swap, 0/1/8 stay. Read reversed.
    Returns None if any digit is not rotatable.
    """
    digits = [int(d) for d in str(n)]
    if not all(d in ROTATABLE_DIGITS for d in digits):
        return None
    rotated = [ROTATABLE_DIGITS[d] for d in reversed(digits)]
    return int(''.join(str(d) for d in rotated))


def decompose_number(raw: int) -> Dict[str, Any]:
    """
    Full harmonic decomposition of a single number.
    Returns all resonance forms.
    """
    s = str(abs(raw))
    d1 = int(s[0]) if len(s) >= 1 else None
    d2 = int(s[1]) if len(s) >= 2 else None
    root = digital_root(raw)
    mir = mirror_value(raw)
    mir_root = digital_root(mir)
    rot = rotation_value(raw)
    rot_root = digital_root(rot) if rot is not None else None
    
    return {
        "raw_value": raw,
        "digit_1": d1,
        "digit_2": d2,
        "root": root,
        "mirror": mir,
        "mirror_root": mir_root,
        "rotation": rot,
        "rotation_root": rot_root,
        "is_master": raw in MASTER_NUMBERS,
    }


# ═══════════════════════════════════════════════════════════════════
# PYRAMID
# ═══════════════════════════════════════════════════════════════════

def generate_pyramid(digits: List[int]) -> List[List[int]]:
    """
    Generate reduction pyramid from list of single digits.
    Each row: sum adjacent pairs, reduce to digital root.
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


def pyramid_signature(digit_string: str) -> Dict[str, Any]:
    """
    Complete pyramid signature from a digit string.
    """
    digits = [int(d) for d in digit_string]
    pyramid = generate_pyramid(digits)
    
    return {
        "input": digit_string,
        "digits": digits,
        "pyramid": pyramid,
        "peak": pyramid[-1][0],
        "row_count": len(pyramid),
        "flat": [n for row in pyramid for n in row],
        "row_sums": [sum(row) for row in pyramid],
        "row_roots": [digital_root(sum(row)) for row in pyramid],
        "digit_sum": sum(digits),
        "digit_sum_chain": reduction_chain(sum(digits)),
        "digital_root": digital_root(sum(digits)),
    }


# ═══════════════════════════════════════════════════════════════════
# DATE EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def date_to_mmddyyyy(d: date) -> str:
    """Convert a date object to MMDDYYYY string."""
    return f"{d.month:02d}{d.day:02d}{d.year}"


def date_to_mmddyy(d: date) -> str:
    """Convert a date object to MMDDYY string."""
    return f"{d.month:02d}{d.day:02d}{d.year % 100:02d}"


def extract_date_harmonics(d: date) -> List[Dict[str, Any]]:
    """
    Extract ALL harmonic values from a date.
    Returns list of dicts ready for DB insertion.
    Each dict has: source_type, source_label, source_raw, 
                   pyramid_row, pyramid_col, + decompose_number fields
    """
    results = []
    
    mm = d.month
    dd = d.day
    yy = d.year % 100
    yyyy = d.year
    cc = d.year // 100  # century
    
    dob_str = date_to_mmddyyyy(d)
    dobh1_str = date_to_mmddyy(d)
    
    # ─── Component values ───
    components = [
        ("component_month", f"Month: {mm}", mm),
        ("component_day", f"Day: {dd}", dd),
        ("component_yy", f"Year 2-digit: {yy}", yy),
        ("component_yyyy", f"Year 4-digit: {yyyy}", yyyy),
        ("component_century", f"Century: {cc}", cc),
    ]
    
    for src_type, label, val in components:
        dec = decompose_number(val)
        dec["source_type"] = src_type
        dec["source_label"] = label
        dec["source_raw"] = str(val)
        dec["pyramid_row"] = None
        dec["pyramid_col"] = None
        results.append(dec)
        
        # Also add intermediate reduction values if multi-step
        chain = reduction_chain(val)
        if len(chain) > 2:  # has intermediates beyond raw and root
            for step_idx, intermediate in enumerate(chain[1:-1], 1):
                idec = decompose_number(intermediate)
                idec["source_type"] = f"{src_type}_reduce_{step_idx}"
                idec["source_label"] = f"{label} reduction step {step_idx}: {intermediate}"
                idec["source_raw"] = str(intermediate)
                idec["pyramid_row"] = None
                idec["pyramid_col"] = None
                results.append(idec)
    
    # ─── Digit sums ───
    dob_dsum = sum(int(c) for c in dob_str)
    dobh1_dsum = sum(int(c) for c in dobh1_str)
    
    for src_type, label, val in [
        ("digit_sum_dob", f"DOB digit sum: {dob_dsum}", dob_dsum),
        ("digit_sum_dobh1", f"DOBh1 digit sum: {dobh1_dsum}", dobh1_dsum),
    ]:
        dec = decompose_number(val)
        dec["source_type"] = src_type
        dec["source_label"] = label
        dec["source_raw"] = str(val)
        dec["pyramid_row"] = None
        dec["pyramid_col"] = None
        results.append(dec)
    
    # ─── Triangles ───
    t1 = [digital_root(mm) if mm > 0 else 0, digital_root(dd), digital_root(yy)]
    t2 = [digital_root(mm) if mm > 0 else 0, digital_root(dd), digital_root(yyyy)]
    t1_sum = sum(t1)
    t2_sum = sum(t2)
    
    for src_type, label, val in [
        ("triangle_t1_sum", f"T1 sum: {t1} = {t1_sum}", t1_sum),
        ("triangle_t2_sum", f"T2 sum: {t2} = {t2_sum}", t2_sum),
        ("triangle_t1_root", f"T1 root", digital_root(t1_sum)),
        ("triangle_t2_root", f"T2 root", digital_root(t2_sum)),
    ]:
        dec = decompose_number(val)
        dec["source_type"] = src_type
        dec["source_label"] = label
        dec["source_raw"] = str(val)
        dec["pyramid_row"] = None
        dec["pyramid_col"] = None
        results.append(dec)
    
    # Triangle individual points
    for i, (point_val, point_name) in enumerate([
        (t1[0], "month"), (t1[1], "day"), (t1[2], "yy")
    ]):
        dec = decompose_number(point_val)
        dec["source_type"] = f"triangle_t1_p{i}"
        dec["source_label"] = f"T1 point {i} ({point_name}): {point_val}"
        dec["source_raw"] = str(point_val)
        dec["pyramid_row"] = None
        dec["pyramid_col"] = None
        results.append(dec)
    
    for i, (point_val, point_name) in enumerate([
        (t2[0], "month"), (t2[1], "day"), (t2[2], "yyyy")
    ]):
        dec = decompose_number(point_val)
        dec["source_type"] = f"triangle_t2_p{i}"
        dec["source_label"] = f"T2 point {i} ({point_name}): {point_val}"
        dec["source_raw"] = str(point_val)
        dec["pyramid_row"] = None
        dec["pyramid_col"] = None
        results.append(dec)
    
    # ─── Pyramids ───
    for pyr_name, pyr_input in [("pyramid_dob", dob_str), ("pyramid_dobh1", dobh1_str)]:
        sig = pyramid_signature(pyr_input)
        
        # Peak
        dec = decompose_number(sig["peak"])
        dec["source_type"] = f"{pyr_name}_peak"
        dec["source_label"] = f"{pyr_name} peak: {sig['peak']}"
        dec["source_raw"] = pyr_input
        dec["pyramid_row"] = sig["row_count"] - 1
        dec["pyramid_col"] = 0
        results.append(dec)
        
        # Every cell in the pyramid
        for r, pyr_row in enumerate(sig["pyramid"]):
            for c, val in enumerate(pyr_row):
                dec = decompose_number(val)
                dec["source_type"] = f"{pyr_name}_cell"
                dec["source_label"] = f"{pyr_name} R{r+1}C{c+1}: {val}"
                dec["source_raw"] = pyr_input
                dec["pyramid_row"] = r
                dec["pyramid_col"] = c
                results.append(dec)
        
        # Row roots
        for r, rr in enumerate(sig["row_roots"]):
            dec = decompose_number(rr)
            dec["source_type"] = f"{pyr_name}_row_root"
            dec["source_label"] = f"{pyr_name} row {r+1} root: {rr}"
            dec["source_raw"] = pyr_input
            dec["pyramid_row"] = r
            dec["pyramid_col"] = None
            results.append(dec)
    
    return results


# ═══════════════════════════════════════════════════════════════════
# RESONANCE COMPARISON
# ═══════════════════════════════════════════════════════════════════

def find_resonance(harmonics_a: List[Dict], harmonics_b: List[Dict],
                   match_types: Optional[List[str]] = None) -> List[Dict]:
    """
    Compare two sets of harmonic values and find all resonance matches.
    
    Match types:
    - exact:      raw_value == raw_value
    - root:       root == root (different raw values)
    - mirror:     raw_value == mirror of other
    - rotation:   raw_value == rotation of other
    - complement: root + other_root == 9
    
    Returns list of match records.
    """
    if match_types is None:
        match_types = ['exact', 'root', 'mirror', 'rotation', 'complement']
    
    matches = []
    seen = set()  # avoid duplicate matches
    
    for a in harmonics_a:
        for b in harmonics_b:
            
            # Exact match (same raw value)
            if 'exact' in match_types and a["raw_value"] == b["raw_value"]:
                key = ('exact', a.get("source_type"), b.get("source_type"), 
                       a.get("pyramid_row"), a.get("pyramid_col"),
                       b.get("pyramid_row"), b.get("pyramid_col"))
                if key not in seen:
                    seen.add(key)
                    matches.append({
                        "match_type": "exact",
                        "source_a": a["source_type"],
                        "source_b": b["source_type"],
                        "value_a": a["raw_value"],
                        "value_b": b["raw_value"],
                        "pyramid_row_a": a.get("pyramid_row"),
                        "pyramid_col_a": a.get("pyramid_col"),
                        "pyramid_row_b": b.get("pyramid_row"),
                        "pyramid_col_b": b.get("pyramid_col"),
                    })
            
            # Root match (same root, different raw)
            if 'root' in match_types and a["root"] == b["root"] and a["raw_value"] != b["raw_value"]:
                key = ('root', a.get("source_type"), b.get("source_type"),
                       a.get("pyramid_row"), a.get("pyramid_col"),
                       b.get("pyramid_row"), b.get("pyramid_col"))
                if key not in seen:
                    seen.add(key)
                    matches.append({
                        "match_type": "root",
                        "source_a": a["source_type"],
                        "source_b": b["source_type"],
                        "value_a": a["raw_value"],
                        "value_b": b["raw_value"],
                        "pyramid_row_a": a.get("pyramid_row"),
                        "pyramid_col_a": a.get("pyramid_col"),
                        "pyramid_row_b": b.get("pyramid_row"),
                        "pyramid_col_b": b.get("pyramid_col"),
                    })
            
            # Mirror match (A's raw == B's mirror)
            if 'mirror' in match_types and b.get("mirror") is not None:
                if a["raw_value"] == b["mirror"] and a["raw_value"] != b["raw_value"]:
                    key = ('mirror', a.get("source_type"), b.get("source_type"),
                           a.get("pyramid_row"), a.get("pyramid_col"),
                           b.get("pyramid_row"), b.get("pyramid_col"))
                    if key not in seen:
                        seen.add(key)
                        matches.append({
                            "match_type": "mirror",
                            "source_a": a["source_type"],
                            "source_b": b["source_type"],
                            "value_a": a["raw_value"],
                            "value_b": b["raw_value"],
                            "pyramid_row_a": a.get("pyramid_row"),
                            "pyramid_col_a": a.get("pyramid_col"),
                            "pyramid_row_b": b.get("pyramid_row"),
                            "pyramid_col_b": b.get("pyramid_col"),
                        })
            
            # Rotation match (A's raw == B's rotation)
            if 'rotation' in match_types and b.get("rotation") is not None:
                if a["raw_value"] == b["rotation"] and a["raw_value"] != b["raw_value"]:
                    key = ('rotation', a.get("source_type"), b.get("source_type"),
                           a.get("pyramid_row"), a.get("pyramid_col"),
                           b.get("pyramid_row"), b.get("pyramid_col"))
                    if key not in seen:
                        seen.add(key)
                        matches.append({
                            "match_type": "rotation",
                            "source_a": a["source_type"],
                            "source_b": b["source_type"],
                            "value_a": a["raw_value"],
                            "value_b": b["raw_value"],
                            "pyramid_row_a": a.get("pyramid_row"),
                            "pyramid_col_a": a.get("pyramid_col"),
                            "pyramid_row_b": b.get("pyramid_row"),
                            "pyramid_col_b": b.get("pyramid_col"),
                        })
            
            # Complement (roots sum to 9)
            if 'complement' in match_types:
                if a["root"] + b["root"] == 9 and a["root"] != b["root"]:
                    key = ('complement', a.get("source_type"), b.get("source_type"),
                           a.get("pyramid_row"), a.get("pyramid_col"),
                           b.get("pyramid_row"), b.get("pyramid_col"))
                    if key not in seen:
                        seen.add(key)
                        matches.append({
                            "match_type": "complement",
                            "source_a": a["source_type"],
                            "source_b": b["source_type"],
                            "value_a": a["raw_value"],
                            "value_b": b["raw_value"],
                            "pyramid_row_a": a.get("pyramid_row"),
                            "pyramid_col_a": a.get("pyramid_col"),
                            "pyramid_row_b": b.get("pyramid_row"),
                            "pyramid_col_b": b.get("pyramid_col"),
                        })
    
    return matches


# ═══════════════════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def get_db_connection():
    """Get PostgreSQL connection to mythos database."""
    import psycopg2
    return psycopg2.connect(
        dbname="mythos",
        user="postgres",
        host="/var/run/postgresql"
    )


def populate_harmonics_for_person_date(person_date_id: int, person_id: int, 
                                         d: date, conn=None) -> int:
    """
    Extract all harmonics from a date and insert into harmonic_values.
    Returns count of rows inserted.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    
    # Clear existing harmonics for this person_date
    cur.execute("DELETE FROM harmonic_values WHERE person_date_id = %s", (person_date_id,))
    
    harmonics = extract_date_harmonics(d)
    count = 0
    
    for h in harmonics:
        cur.execute("""
            INSERT INTO harmonic_values 
                (person_date_id, person_id, source_system, source_type, source_label,
                 source_raw, pyramid_row, pyramid_col, raw_value, digit_1, digit_2,
                 root, mirror, mirror_root, rotation, rotation_root, is_master)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            person_date_id, person_id, 'numerology', h["source_type"], h["source_label"],
            h.get("source_raw"), h.get("pyramid_row"), h.get("pyramid_col"),
            h["raw_value"], h["digit_1"], h.get("digit_2"),
            h["root"], h.get("mirror"), h.get("mirror_root"),
            h.get("rotation"), h.get("rotation_root"), h["is_master"],
        ))
        count += 1
    
    conn.commit()
    
    if close_conn:
        conn.close()
    
    logger.info(f"Populated {count} harmonic values for person_date {person_date_id}")
    return count


def populate_all_harmonics(conn=None) -> Dict[str, int]:
    """Populate harmonics for ALL person_dates that don't have them yet."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    cur.execute("""
        SELECT pd.id, pd.person_id, pd.date_value
        FROM person_dates pd
        LEFT JOIN harmonic_values hv ON hv.person_date_id = pd.id
        WHERE hv.id IS NULL
    """)
    
    pending = cur.fetchall()
    results = {}
    
    for pd_id, person_id, date_val in pending:
        count = populate_harmonics_for_person_date(pd_id, person_id, date_val, conn)
        results[f"person_date_{pd_id}"] = count
    
    if close_conn:
        conn.close()
    
    return results


def compute_resonance(person_date_id_a: int, person_date_id_b: int,
                      conn=None) -> int:
    """
    Compute and store all resonance matches between two person_dates.
    Returns count of matches found.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    
    # Get person_ids
    cur.execute("SELECT person_id FROM person_dates WHERE id = %s", (person_date_id_a,))
    person_id_a = cur.fetchone()[0]
    cur.execute("SELECT person_id FROM person_dates WHERE id = %s", (person_date_id_b,))
    person_id_b = cur.fetchone()[0]
    
    # Clear existing resonance for this pair
    cur.execute("""
        DELETE FROM harmonic_resonance 
        WHERE person_date_id_a = %s AND person_date_id_b = %s
    """, (person_date_id_a, person_date_id_b))
    
    # Load harmonics
    cur.execute("""
        SELECT id, source_type, raw_value, root, mirror, mirror_root,
               rotation, rotation_root, is_master, pyramid_row, pyramid_col
        FROM harmonic_values WHERE person_date_id = %s
    """, (person_date_id_a,))
    rows_a = cur.fetchall()
    
    cur.execute("""
        SELECT id, source_type, raw_value, root, mirror, mirror_root,
               rotation, rotation_root, is_master, pyramid_row, pyramid_col
    FROM harmonic_values WHERE person_date_id = %s
    """, (person_date_id_b,))
    rows_b = cur.fetchall()
    
    def row_to_dict(row):
        return {
            "id": row[0], "source_type": row[1], "raw_value": row[2],
            "root": row[3], "mirror": row[4], "mirror_root": row[5],
            "rotation": row[6], "rotation_root": row[7], "is_master": row[8],
            "pyramid_row": row[9], "pyramid_col": row[10],
        }
    
    harmonics_a = [row_to_dict(r) for r in rows_a]
    harmonics_b = [row_to_dict(r) for r in rows_b]
    
    matches = find_resonance(harmonics_a, harmonics_b)
    
    # Build ID lookup for harmonic_id foreign keys
    a_lookup = {(h["source_type"], h.get("pyramid_row"), h.get("pyramid_col")): h["id"] 
                for h in harmonics_a}
    b_lookup = {(h["source_type"], h.get("pyramid_row"), h.get("pyramid_col")): h["id"] 
                for h in harmonics_b}
    
    count = 0
    for m in matches:
        hid_a = a_lookup.get((m["source_a"], m.get("pyramid_row_a"), m.get("pyramid_col_a")))
        hid_b = b_lookup.get((m["source_b"], m.get("pyramid_row_b"), m.get("pyramid_col_b")))
        
        cur.execute("""
            INSERT INTO harmonic_resonance
                (person_date_id_a, person_date_id_b, person_id_a, person_id_b,
                 harmonic_id_a, harmonic_id_b, match_type,
                 source_a, source_b, value_a, value_b,
                 pyramid_row_a, pyramid_col_a, pyramid_row_b, pyramid_col_b,
                 discovered_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            person_date_id_a, person_date_id_b, person_id_a, person_id_b,
            hid_a, hid_b, m["match_type"],
            m["source_a"], m["source_b"], m["value_a"], m["value_b"],
            m.get("pyramid_row_a"), m.get("pyramid_col_a"),
            m.get("pyramid_row_b"), m.get("pyramid_col_b"),
            "auto",
        ))
        count += 1
    
    conn.commit()
    
    if close_conn:
        conn.close()
    
    logger.info(f"Found {count} resonance matches between pd:{person_date_id_a} and pd:{person_date_id_b}")
    return count


def compute_resonance_with_seraphe(person_date_id: int, conn=None) -> int:
    """
    Compare a person_date against ALL of Seraphe's dates.
    Seraphe = people.id = 2.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM person_dates WHERE person_id = 2")
    seraphe_dates = [row[0] for row in cur.fetchall()]
    
    total = 0
    for sd_id in seraphe_dates:
        if sd_id != person_date_id:  # don't compare seraphe to herself
            total += compute_resonance(sd_id, person_date_id, conn)
    
    if close_conn:
        conn.close()
    
    return total


def compute_resonance_pair(person_id_a: int, person_id_b: int, conn=None) -> int:
    """
    Compare ALL dates of person A against ALL dates of person B.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    cur.execute("SELECT id FROM person_dates WHERE person_id = %s", (person_id_a,))
    dates_a = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM person_dates WHERE person_id = %s", (person_id_b,))
    dates_b = [row[0] for row in cur.fetchall()]
    
    total = 0
    for da in dates_a:
        for db in dates_b:
            total += compute_resonance(da, db, conn)
    
    if close_conn:
        conn.close()
    
    return total


# ═══════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════

def resonance_summary(person_id_a: int, person_id_b: int, conn=None) -> Dict[str, Any]:
    """
    Generate a resonance summary between two people.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    cur = conn.cursor()
    
    # Get names
    cur.execute("SELECT display_text FROM people WHERE id = %s", (person_id_a,))
    name_a = cur.fetchone()[0]
    cur.execute("SELECT display_text FROM people WHERE id = %s", (person_id_b,))
    name_b = cur.fetchone()[0]
    
    # Count by match type
    cur.execute("""
        SELECT match_type, COUNT(*) 
        FROM harmonic_resonance
        WHERE person_id_a = %s AND person_id_b = %s
        GROUP BY match_type
        ORDER BY COUNT(*) DESC
    """, (person_id_a, person_id_b))
    type_counts = dict(cur.fetchall())
    
    # Total
    total = sum(type_counts.values())
    
    # Top positional matches (pyramid cells that align)
    cur.execute("""
        SELECT source_a, source_b, value_a, value_b, match_type,
               pyramid_row_a, pyramid_col_a, pyramid_row_b, pyramid_col_b
        FROM harmonic_resonance
        WHERE person_id_a = %s AND person_id_b = %s
          AND pyramid_row_a IS NOT NULL AND pyramid_row_b IS NOT NULL
        ORDER BY match_type, pyramid_row_a
        LIMIT 50
    """, (person_id_a, person_id_b))
    positional = cur.fetchall()
    
    if close_conn:
        conn.close()
    
    return {
        "person_a": name_a,
        "person_b": name_b,
        "total_matches": total,
        "by_type": type_counts,
        "positional_matches": [
            {
                "source_a": r[0], "source_b": r[1],
                "value_a": r[2], "value_b": r[3],
                "match_type": r[4],
                "pos_a": f"R{r[5]+1}C{r[6]+1}" if r[5] is not None else None,
                "pos_b": f"R{r[7]+1}C{r[8]+1}" if r[7] is not None else None,
            }
            for r in positional
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python engine.py populate          — populate harmonics for all dates")
        print("  python engine.py resonate <id_a> <id_b>  — compare two people")
        print("  python engine.py seraphe <person_id>     — compare person to Seraphe")
        print("  python engine.py summary <id_a> <id_b>   — resonance summary")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "populate":
        results = populate_all_harmonics()
        print(f"Populated harmonics: {json.dumps(results, indent=2)}")
    
    elif cmd == "resonate":
        pid_a, pid_b = int(sys.argv[2]), int(sys.argv[3])
        count = compute_resonance_pair(pid_a, pid_b)
        print(f"Found {count} resonance matches between person {pid_a} and {pid_b}")
    
    elif cmd == "seraphe":
        pid = int(sys.argv[2])
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM person_dates WHERE person_id = %s", (pid,))
        for (pd_id,) in cur.fetchall():
            count = compute_resonance_with_seraphe(pd_id, conn)
            print(f"  person_date {pd_id}: {count} matches with Seraphe")
        conn.close()
    
    elif cmd == "summary":
        pid_a, pid_b = int(sys.argv[2]), int(sys.argv[3])
        result = resonance_summary(pid_a, pid_b)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
