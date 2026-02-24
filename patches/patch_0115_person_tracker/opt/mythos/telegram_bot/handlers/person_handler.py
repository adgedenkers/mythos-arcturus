"""
Person Tracker Handler - Telegram commands for managing people in Neo4j.

Features:
  - Unique PID system: F001♌, C001♓, etc.
  - Full contact/life data storage
  - Auto-fractal computation on all dates with full provenance
  - Auto-resonance computation against Seraphe on every create/update
  - Relationship tracking (parent, child, sibling, married, etc.)
  - Harmonic and master number graph search

Commands:
  /person add <category> <name> [born MM/DD/YYYY]     - Add person
  /person <PID> date <field> <MM/DD/YYYY>              - Add/update date
  /person <PID> set <field> <value>                    - Set any field
  /person <PID> memo <text>                            - Seraphe's observations
  /person <PID> relate <rel_type> <PID2>               - Add relationship
  /person <PID>                                        - Show full profile
  /person <PID> fractals                               - Full fractal display
  /person <PID> resonance                              - Resonance with Seraphe
  /person find <name>                                  - Search by name
  /person list [category]                              - List tracked people
  /person harmonic <N>                                 - Find by harmonic root
  /person master <N>                                   - Find by master number
  /person remove <PID>                                 - Remove person

Author: Ka'tuar'el / Claude
"""

import re
import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# ─── Neo4j Connection ───────────────────────────────────────────────

def get_neo4j_driver():
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    if not password:
        env_path = "/opt/mythos/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("NEO4J_PASSWORD="):
                        password = line.strip().split("=", 1)[1].strip('"').strip("'")
    return GraphDatabase.driver(uri, auth=(user, password))


# ─── Date Parsing ───────────────────────────────────────────────────

DATE_PATTERN = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})')
PID_PATTERN = re.compile(r'^[FCSPW]\d{3}$', re.IGNORECASE)

VALID_RELATIONSHIPS = [
    "parent", "child", "sibling", "married", "divorced",
    "grandparent", "grandchild", "aunt", "uncle", "cousin",
    "niece", "nephew", "partner", "friend", "mentor", "student",
    "colleague", "teacher",
]

# Relationship pairs (if you add A→B, also add B→A with inverse)
RELATIONSHIP_INVERSES = {
    "parent": "child",
    "child": "parent",
    "grandparent": "grandchild",
    "grandchild": "grandparent",
    "aunt": "niece",  # or nephew, but graph is directional
    "uncle": "nephew",
    "niece": "aunt",
    "nephew": "uncle",
    "mentor": "student",
    "student": "mentor",
    "teacher": "student",
}
# Symmetric relationships
SYMMETRIC_RELS = {"sibling", "married", "divorced", "partner", "friend", "cousin", "colleague"}


SETTABLE_FIELDS = [
    "phone", "email", "address", "birth_time", "birth_place",
    "death_place", "occupation", "nationality", "notes",
]


def parse_date(text: str):
    match = DATE_PATTERN.search(text)
    if match:
        m, d, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= m <= 12 and 1 <= d <= 31 and 1000 <= y <= 9999:
            return m, d, y
    return None


# ─── PID Management ─────────────────────────────────────────────────

def get_next_pid(category_letter: str) -> str:
    """Get next available PID for a category."""
    cat = category_letter.upper()
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson)
                WHERE p.pid STARTS WITH $prefix
                RETURN p.pid as pid
                ORDER BY p.pid DESC
                LIMIT 1
            """, {"prefix": cat})
            record = result.single()
            if record:
                last_num = int(record["pid"][1:4])
                return f"{cat}{last_num + 1:03d}"
            else:
                return f"{cat}001"
    finally:
        driver.close()


# ─── Seraphe's Signature (cached) ──────────────────────────────────

_seraphe_signature_cache = None

def get_seraphe_signature():
    """Get or compute Seraphe's fractal signature."""
    global _seraphe_signature_cache
    if _seraphe_signature_cache is not None:
        return _seraphe_signature_cache

    from core.fractal_engine import analyze_date_with_signature

    # Seraphe: 08/19/1978
    result = analyze_date_with_signature(8, 19, 1978, "birth", "08/19/1978")
    _seraphe_signature_cache = result["signature"]
    return _seraphe_signature_cache


def invalidate_seraphe_cache():
    """Call when Seraphe's numbers change."""
    global _seraphe_signature_cache
    _seraphe_signature_cache = None


# ─── Core Operations ───────────────────────────────────────────────

def add_person(name: str, category: str, dates: dict = None,
               fields: dict = None) -> dict:
    """
    Add a TrackedPerson node with auto-fractal computation and Seraphe resonance.

    category: one of F, C, S, P, W
    dates: { 'birth': (m,d,y), 'death': (m,d,y), ... }
    fields: { 'phone': '...', 'birth_time': '...', 'birth_place': '...', etc }
    """
    from core.fractal_engine import (
        analyze_date_with_signature, compute_conception_signature,
        flatten_for_neo4j, get_sun_sign, generate_pid,
        compare_signatures, resonance_summary
    )

    cat = category.upper()
    pid = get_next_pid(cat)

    # Determine sun sign
    sun_sign = ""
    sun_glyph = ""
    if dates and "birth" in dates:
        m, d, y = dates["birth"]
        sun_sign, sun_glyph = get_sun_sign(m, d)

    pid_func, pid_display = generate_pid(cat, int(pid[1:4]), sun_glyph)

    props = {
        "pid": pid_func,
        "pid_display": pid_display,
        "name": name,
        "name_lower": name.lower(),
        "category": cat,
        "category_name": {"F": "family", "C": "celebrity", "S": "spiritual",
                          "P": "personal", "W": "work"}.get(cat, "other"),
        "sun_sign": sun_sign,
        "sun_sign_glyph": sun_glyph,
        "created_at": datetime.now().isoformat(),
    }

    # Set extra fields
    if fields:
        for k, v in fields.items():
            if k in SETTABLE_FIELDS:
                props[k] = v

    # Process dates and build combined signature
    full_signature = []
    date_analyses = {}

    if dates:
        for date_key, (m, d, y) in dates.items():
            date_str = f"{m:02d}/{d:02d}/{y}"
            props[f"{date_key}_date"] = date_str

            result = analyze_date_with_signature(m, d, y, date_key, date_str)
            analysis = result["analysis"]
            sig = result["signature"]

            flat = flatten_for_neo4j(analysis, f"{date_key}_")
            props.update(flat)
            full_signature.extend(sig)
            date_analyses[date_key] = analysis

            # Auto-compute conception from birth
            if date_key == "birth":
                c_result = compute_conception_signature(m, d, y)
                c_flat = flatten_for_neo4j(c_result["analysis"], "conception_")
                props.update(c_flat)
                props["conception_date"] = c_result["conception_date"]
                full_signature.extend(c_result["signature"])
                date_analyses["conception"] = c_result["analysis"]

    # Store signature as JSON
    props["fractal_signature"] = json.dumps(full_signature)
    props["signature_count"] = len(full_signature)

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            # Create node
            session.run("""
                CREATE (p:TrackedPerson)
                SET p = $props
            """, {"props": props})

            # Create HarmonicRoot links
            if dates and "birth" in dates:
                analysis = date_analyses["birth"]
                for root in set(analysis["triangle1"] + analysis["triangle2"]):
                    session.run("""
                        MERGE (h:HarmonicRoot {value: $root})
                        WITH h
                        MATCH (p:TrackedPerson {pid: $pid})
                        MERGE (p)-[:HAS_HARMONIC_ROOT {source: 'birth_triangle'}]->(h)
                    """, {"root": root, "pid": pid_func})

                # Life path root
                session.run("""
                    MERGE (h:HarmonicRoot {value: $root})
                    WITH h
                    MATCH (p:TrackedPerson {pid: $pid})
                    MERGE (p)-[:HAS_HARMONIC_ROOT {source: 'lifepath'}]->(h)
                """, {"root": analysis["lifepath"]["final"], "pid": pid_func})

                # Master numbers
                all_masters = set()
                for key in ["month", "day", "year2", "year4", "lifepath"]:
                    all_masters.update(analysis[key]["masters"])
                for master in all_masters:
                    session.run("""
                        MERGE (m:MasterNumber {value: $master})
                        WITH m
                        MATCH (p:TrackedPerson {pid: $pid})
                        MERGE (p)-[:CARRIES_MASTER]->(m)
                    """, {"master": master, "pid": pid_func})

            # Auto-compute resonance with Seraphe
            if full_signature:
                seraphe_sig = get_seraphe_signature()
                matches = compare_signatures(full_signature, seraphe_sig, name, "Seraphe")
                summary = resonance_summary(matches)

                # Find or create Seraphe's TrackedPerson node
                seraphe_exists = session.run(
                    "MATCH (s:TrackedPerson {pid: 'F001'}) RETURN s.pid"
                ).single()

                if seraphe_exists:
                    session.run("""
                        MATCH (p:TrackedPerson {pid: $pid})
                        MATCH (s:TrackedPerson {pid: 'F001'})
                        MERGE (p)-[r:RESONATES_WITH]->(s)
                        SET r.matches = $matches,
                            r.score = $score,
                            r.total_matches = $total,
                            r.computed_at = datetime()
                    """, {
                        "pid": pid_func,
                        "matches": json.dumps(matches[:100]),  # cap stored matches
                        "score": summary["score"],
                        "total": summary["total"],
                    })

            return {
                "pid": pid_func,
                "pid_display": pid_display,
                "name": name,
                "sun_sign": sun_sign,
                "sun_glyph": sun_glyph,
                "dates_processed": list(date_analyses.keys()),
                "signature_count": len(full_signature),
                "resonance_score": summary["score"] if full_signature else None,
                "resonance_total": summary["total"] if full_signature else None,
            }
    finally:
        driver.close()


def add_date_to_person(pid: str, date_field: str, month: int, day: int,
                        year: int) -> dict:
    """Add/update a date on an existing TrackedPerson, recompute fractals."""
    from core.fractal_engine import (
        analyze_date_with_signature, flatten_for_neo4j,
        compare_signatures, resonance_summary, get_sun_sign
    )

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            record = session.run(
                "MATCH (p:TrackedPerson {pid: $pid}) RETURN p",
                {"pid": pid.upper()}
            ).single()
            if not record:
                return {"error": f"No person found with PID '{pid}'"}

            person = dict(record["p"])
            date_str = f"{month:02d}/{day:02d}/{year}"

            result = analyze_date_with_signature(month, day, year, date_field, date_str)
            flat = flatten_for_neo4j(result["analysis"], f"{date_field}_")
            flat[f"{date_field}_date"] = date_str

            # If adding birth date, also update sun sign and conception
            if date_field == "birth":
                sun_sign, sun_glyph = get_sun_sign(month, day)
                flat["sun_sign"] = sun_sign
                flat["sun_sign_glyph"] = sun_glyph
                flat["pid_display"] = f"{pid.upper()}{sun_glyph}"

                from core.fractal_engine import compute_conception_signature
                c_result = compute_conception_signature(month, day, year)
                c_flat = flatten_for_neo4j(c_result["analysis"], "conception_")
                flat.update(c_flat)
                flat["conception_date"] = c_result["conception_date"]

            # Rebuild full signature from all dates
            existing_sig_str = person.get("fractal_signature", "[]")
            try:
                existing_sig = json.loads(existing_sig_str)
            except (json.JSONDecodeError, TypeError):
                existing_sig = []

            # Remove old entries for this date_field and add new ones
            existing_sig = [e for e in existing_sig if not e.get("source", "").startswith(f"{date_field}_")]
            existing_sig.extend(result["signature"])

            flat["fractal_signature"] = json.dumps(existing_sig)
            flat["signature_count"] = len(existing_sig)

            # Update node
            session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                SET p += $props
            """, {"pid": pid.upper(), "props": flat})

            # Update harmonic roots
            for root in set(result["analysis"]["triangle1"] + result["analysis"]["triangle2"]):
                session.run("""
                    MERGE (h:HarmonicRoot {value: $root})
                    WITH h
                    MATCH (p:TrackedPerson {pid: $pid})
                    MERGE (p)-[:HAS_HARMONIC_ROOT {source: $source}]->(h)
                """, {"root": root, "pid": pid.upper(), "source": f"{date_field}_triangle"})

            # Recompute Seraphe resonance
            seraphe_sig = get_seraphe_signature()
            matches = compare_signatures(existing_sig, seraphe_sig, person.get("name", pid), "Seraphe")
            summary = resonance_summary(matches)

            seraphe_exists = session.run(
                "MATCH (s:TrackedPerson {pid: 'F001'}) RETURN s.pid"
            ).single()
            if seraphe_exists:
                session.run("""
                    MATCH (p:TrackedPerson {pid: $pid})
                    MATCH (s:TrackedPerson {pid: 'F001'})
                    MERGE (p)-[r:RESONATES_WITH]->(s)
                    SET r.matches = $matches,
                        r.score = $score,
                        r.total_matches = $total,
                        r.computed_at = datetime()
                """, {
                    "pid": pid.upper(),
                    "matches": json.dumps(matches[:100]),
                    "score": summary["score"],
                    "total": summary["total"],
                })

            return {
                "name": person.get("name", pid),
                "pid": pid.upper(),
                "date_field": date_field,
                "date": date_str,
                "lifepath": result["analysis"]["lifepath"]["final"],
                "triangle1": result["analysis"]["triangle1"],
                "triangle2": result["analysis"]["triangle2"],
                "resonance_score": summary["score"],
            }
    finally:
        driver.close()


def set_person_field(pid: str, field: str, value: str) -> dict:
    """Set a field on an existing TrackedPerson."""
    if field not in SETTABLE_FIELDS:
        return {"error": f"Field '{field}' not settable. Valid: {', '.join(SETTABLE_FIELDS)}"}

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                SET p[$field] = $value
                RETURN p.name as name
            """, {"pid": pid.upper(), "field": field, "value": value})
            # Neo4j doesn't support dynamic property keys in SET p[$field]
            # Use a different approach
            result = session.run(f"""
                MATCH (p:TrackedPerson {{pid: $pid}})
                SET p.{field} = $value
                RETURN p.name as name
            """, {"pid": pid.upper(), "value": value})
            record = result.single()
            if not record:
                return {"error": f"No person found with PID '{pid}'"}
            return {"name": record["name"], "pid": pid.upper(), "field": field, "value": value}
    finally:
        driver.close()


def set_person_memo(pid: str, memo: str) -> dict:
    """Set Seraphe's observations memo on a person."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                SET p.notes = $memo
                RETURN p.name as name
            """, {"pid": pid.upper(), "memo": memo})
            record = result.single()
            if not record:
                return {"error": f"No person found with PID '{pid}'"}
            return {"name": record["name"], "pid": pid.upper()}
    finally:
        driver.close()


def add_relationship(pid1: str, rel_type: str, pid2: str) -> dict:
    """Add a relationship between two tracked people."""
    rel = rel_type.lower().strip()
    if rel not in VALID_RELATIONSHIPS:
        return {"error": f"Unknown relationship '{rel}'. Valid: {', '.join(VALID_RELATIONSHIPS)}"}

    rel_label = rel.upper()
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            # Verify both exist
            p1 = session.run(
                "MATCH (p:TrackedPerson {pid: $pid}) RETURN p.name as name",
                {"pid": pid1.upper()}
            ).single()
            p2 = session.run(
                "MATCH (p:TrackedPerson {pid: $pid}) RETURN p.name as name",
                {"pid": pid2.upper()}
            ).single()

            if not p1:
                return {"error": f"PID '{pid1}' not found"}
            if not p2:
                return {"error": f"PID '{pid2}' not found"}

            # Create primary relationship
            session.run(f"""
                MATCH (a:TrackedPerson {{pid: $pid1}})
                MATCH (b:TrackedPerson {{pid: $pid2}})
                MERGE (a)-[:{rel_label}]->(b)
            """, {"pid1": pid1.upper(), "pid2": pid2.upper()})

            # Create inverse relationship
            if rel in SYMMETRIC_RELS:
                session.run(f"""
                    MATCH (a:TrackedPerson {{pid: $pid1}})
                    MATCH (b:TrackedPerson {{pid: $pid2}})
                    MERGE (b)-[:{rel_label}]->(a)
                """, {"pid1": pid1.upper(), "pid2": pid2.upper()})
            elif rel in RELATIONSHIP_INVERSES:
                inv = RELATIONSHIP_INVERSES[rel].upper()
                session.run(f"""
                    MATCH (a:TrackedPerson {{pid: $pid1}})
                    MATCH (b:TrackedPerson {{pid: $pid2}})
                    MERGE (b)-[:{inv}]->(a)
                """, {"pid1": pid1.upper(), "pid2": pid2.upper()})

            return {
                "person1": f"{p1['name']} ({pid1.upper()})",
                "person2": f"{p2['name']} ({pid2.upper()})",
                "relationship": rel,
            }
    finally:
        driver.close()


def get_person_profile(pid: str) -> dict:
    """Get full profile for a person."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                OPTIONAL MATCH (p)-[r:RESONATES_WITH]->(s:TrackedPerson {pid: 'F001'})
                OPTIONAL MATCH (p)-[rel]->(other:TrackedPerson)
                WHERE type(rel) <> 'RESONATES_WITH' AND type(rel) <> 'HAS_HARMONIC_ROOT' AND type(rel) <> 'CARRIES_MASTER'
                RETURN p, r.score as resonance_score, r.total_matches as resonance_total,
                       collect(DISTINCT {type: type(rel), name: other.name, pid: other.pid}) as relationships
            """, {"pid": pid.upper()})
            record = result.single()
            if not record:
                return None

            person = dict(record["p"])
            person["resonance_score"] = record["resonance_score"]
            person["resonance_total"] = record["resonance_total"]
            person["relationships"] = [r for r in record["relationships"] if r["name"] is not None]
            return person
    finally:
        driver.close()


def find_person(search: str) -> list:
    """Search people by name."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson)
                WHERE toLower(p.name) CONTAINS $search
                OPTIONAL MATCH (p)-[r:RESONATES_WITH]->(s:TrackedPerson {pid: 'F001'})
                RETURN p.pid as pid, p.pid_display as pid_display, p.name as name,
                       p.birth_date as birth_date, p.sun_sign_glyph as glyph,
                       p.birth_lifepath as lifepath, p.birth_triangle1 as t1,
                       r.score as resonance_score
                ORDER BY p.name
                LIMIT 20
            """, {"search": search.lower()})
            return [dict(r) for r in result]
    finally:
        driver.close()


def list_people(category: str = None) -> list:
    """List all tracked people, optionally filtered by category."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            if category:
                query = """
                    MATCH (p:TrackedPerson)
                    WHERE p.category = $cat
                    OPTIONAL MATCH (p)-[r:RESONATES_WITH]->(s:TrackedPerson {pid: 'F001'})
                    RETURN p.pid as pid, p.pid_display as pid_display, p.name as name,
                           p.birth_date as birth_date, p.sun_sign_glyph as glyph,
                           p.birth_lifepath as lifepath, p.birth_triangle1 as t1,
                           r.score as resonance_score
                    ORDER BY p.pid
                """
                result = session.run(query, {"cat": category.upper()})
            else:
                query = """
                    MATCH (p:TrackedPerson)
                    OPTIONAL MATCH (p)-[r:RESONATES_WITH]->(s:TrackedPerson {pid: 'F001'})
                    RETURN p.pid as pid, p.pid_display as pid_display, p.name as name,
                           p.birth_date as birth_date, p.sun_sign_glyph as glyph,
                           p.birth_lifepath as lifepath, p.birth_triangle1 as t1,
                           r.score as resonance_score
                    ORDER BY p.pid
                """
                result = session.run(query)
            return [dict(r) for r in result]
    finally:
        driver.close()


def search_by_harmonic(root_value: int) -> list:
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson)-[r:HAS_HARMONIC_ROOT]->(h:HarmonicRoot {value: $root})
                RETURN p.pid as pid, p.pid_display as pid_display, p.name as name,
                       r.source as source, p.birth_lifepath as lifepath,
                       p.birth_triangle1 as t1
                ORDER BY p.name
            """, {"root": root_value})
            return [dict(r) for r in result]
    finally:
        driver.close()


def search_by_master(master_value: int) -> list:
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson)-[:CARRIES_MASTER]->(m:MasterNumber {value: $master})
                RETURN p.pid as pid, p.pid_display as pid_display, p.name as name,
                       p.birth_lifepath as lifepath, p.birth_master_numbers as masters
                ORDER BY p.name
            """, {"master": master_value})
            return [dict(r) for r in result]
    finally:
        driver.close()


def remove_person(pid: str) -> dict:
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                WITH p, p.name as name
                DETACH DELETE p
                RETURN name
            """, {"pid": pid.upper()})
            record = result.single()
            if record:
                return {"name": record["name"], "pid": pid.upper(), "removed": True}
            return {"error": f"No person found with PID '{pid}'"}
    finally:
        driver.close()


def get_resonance_detail(pid: str) -> dict:
    """Get detailed resonance between a person and Seraphe."""
    from core.fractal_engine import compare_signatures, resonance_summary

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:TrackedPerson {pid: $pid})
                RETURN p.fractal_signature as sig, p.name as name, p.pid_display as pid_display
            """, {"pid": pid.upper()})
            record = result.single()
            if not record:
                return {"error": f"No person found with PID '{pid}'"}
            if not record["sig"]:
                return {"error": f"{record['name']} has no fractal signature yet"}

            try:
                person_sig = json.loads(record["sig"])
            except (json.JSONDecodeError, TypeError):
                return {"error": "Invalid signature data"}

            seraphe_sig = get_seraphe_signature()
            matches = compare_signatures(person_sig, seraphe_sig, record["name"], "Seraphe")
            summary = resonance_summary(matches)

            return {
                "name": record["name"],
                "pid": pid.upper(),
                "pid_display": record["pid_display"],
                "matches": matches,
                "summary": summary,
            }
    finally:
        driver.close()


# ─── Seed Family Members ───────────────────────────────────────────

def seed_family():
    """Seed Ka'tuar'el, Seraphe, and Fitz if not already present."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            existing = session.run(
                "MATCH (p:TrackedPerson) WHERE p.pid IN ['F001', 'F002', 'F003'] RETURN collect(p.pid) as pids"
            ).single()["pids"]

            if "F001" not in existing:
                logger.info("Seeding Seraphe (F001)")
                add_person("Seraphe Valemira", "F", {"birth": (8, 19, 1978)},
                           {"birth_time": "2:02 PM", "birth_place": "Norwich, NY"})

            if "F002" not in existing:
                logger.info("Seeding Ka'tuar'el (F002)")
                add_person("Ka'tuar'el", "F", {"birth": (11, 22, 1977)},
                           {"birth_time": "8:30 AM", "birth_place": "Albany, NY"})

            if "F003" not in existing:
                logger.info("Seeding Fitz (F003)")
                add_person("Fitz", "F", {"birth": (9, 8, 2010)},
                           {"birth_time": "2:39 PM", "birth_place": "Schenectady, NY"})

            # Add family relationships if all three exist
            if len(existing) < 3:  # we just added some, set up relationships
                for pid_pair, rel in [
                    ("F001", "F003", "PARENT"),
                    ("F002", "F003", "PARENT"),
                    ("F001", "F002", "MARRIED"),
                ]:
                    try:
                        session.run(f"""
                            MATCH (a:TrackedPerson {{pid: $p1}})
                            MATCH (b:TrackedPerson {{pid: $p2}})
                            MERGE (a)-[:{rel}]->(b)
                        """, {"p1": pid_pair, "p2": rel})
                    except Exception:
                        pass  # relationships may already exist
    finally:
        driver.close()


# ─── Telegram Command Handler ──────────────────────────────────────

async def person_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main /person command dispatcher."""
    from core.fractal_engine import (
        analyze_date_with_signature, format_fractals_telegram,
        format_resonance_telegram
    )

    text = update.message.text.strip()
    args = text[len("/person"):].strip()

    if not args:
        await update.message.reply_text(
            "👤 *Person Tracker*\n\n"
            "*Add:*\n"
            "`/person add F|C|S|P|W <name> born MM/DD/YYYY`\n"
            "`/person add C Albert Einstein born 03/14/1879`\n\n"
            "*Update:*\n"
            "`/person <PID> date <field> MM/DD/YYYY`\n"
            "`/person <PID> set <field> <value>`\n"
            "`/person <PID> memo <text>`\n"
            "`/person <PID> relate <type> <PID2>`\n\n"
            "*View:*\n"
            "`/person <PID>` — profile\n"
            "`/person <PID> fractals` — full analysis\n"
            "`/person <PID> resonance` — Seraphe comparison\n\n"
            "*Search:*\n"
            "`/person find <name>`\n"
            "`/person list [F|C|S|P|W]`\n"
            "`/person harmonic <1-9>`\n"
            "`/person master <11|22|33|44>`\n\n"
            "*Other:*\n"
            "`/person remove <PID>`\n\n"
            "Categories: *F*amily *C*elebrity *S*piritual *P*ersonal *W*ork",
            parse_mode="Markdown"
        )
        return

    # ── ADD ──────────────────────────────────────────────────────
    if args.lower().startswith("add "):
        add_text = args[4:].strip()

        if not add_text or len(add_text) < 2:
            await update.message.reply_text("Usage: `/person add <F|C|S|P|W> <name> [born MM/DD/YYYY]`", parse_mode="Markdown")
            return

        # First char should be category
        cat = add_text[0].upper()
        if cat not in "FCSPW":
            await update.message.reply_text(
                f"❌ First character must be category: F, C, S, P, or W\n"
                f"Got: '{add_text[0]}'\n\n"
                f"Example: `/person add C Albert Einstein born 03/14/1879`",
                parse_mode="Markdown"
            )
            return

        rest = add_text[1:].strip()

        dates = {}
        # Extract death date
        death_match = re.search(r'died\s+(\d{1,2}/\d{1,2}/\d{4})', rest, re.IGNORECASE)
        if death_match:
            d = parse_date(death_match.group(1))
            if d:
                dates["death"] = d
            rest = rest[:death_match.start()].strip()

        # Extract birth date
        birth_match = re.search(r'born\s+(\d{1,2}/\d{1,2}/\d{4})', rest, re.IGNORECASE)
        if birth_match:
            d = parse_date(birth_match.group(1))
            if d:
                dates["birth"] = d
            name = rest[:birth_match.start()].strip()
        else:
            name = rest.strip()

        if not name:
            await update.message.reply_text("❌ Please provide a name.")
            return

        try:
            result = add_person(name, cat, dates if dates else None)

            msg = f"✅ *{result['name']}* added as `{result['pid_display']}`"
            if result.get("sun_sign"):
                msg += f" ({result['sun_sign'].title()} {result['sun_glyph']})"

            if result["dates_processed"]:
                msg += f"\n📊 Fractals: {', '.join(result['dates_processed'])}"
                msg += f" ({result['signature_count']} provenance entries)"

            if result.get("resonance_score") is not None:
                msg += f"\n🌊 Seraphe resonance: *{result['resonance_score']}* ({result['resonance_total']} matches)"

            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error adding person: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {e}")

    # ── FIND ─────────────────────────────────────────────────────
    elif args.lower().startswith("find "):
        search = args[5:].strip()
        try:
            results = find_person(search)
            if not results:
                await update.message.reply_text(f"No results for '{search}'")
                return

            lines = [f"🔍 *Results for '{search}':*\n"]
            for p in results:
                line = f"• `{p.get('pid_display', p['pid'])}` *{p['name']}*"
                if p.get("birth_date"):
                    line += f" — {p['birth_date']}"
                if p.get("lifepath"):
                    line += f" LP:{p['lifepath']}"
                if p.get("t1"):
                    line += f" T1:{p['t1']}"
                if p.get("resonance_score"):
                    line += f" 🌊{p['resonance_score']}"
                lines.append(line)

            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error finding person: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {e}")

    # ── LIST ─────────────────────────────────────────────────────
    elif args.lower().startswith("list"):
        cat_filter = args[4:].strip().upper() if len(args) > 4 else None
        if cat_filter and cat_filter not in "FCSPW":
            cat_filter = None

        try:
            results = list_people(cat_filter)
            if not results:
                await update.message.reply_text("No people tracked yet.")
                return

            lines = [f"👥 *Tracked People ({len(results)}):*\n"]
            current_cat = None
            for p in results:
                pid = p.get("pid", "")
                cat = pid[0] if pid else "?"
                if cat != current_cat:
                    current_cat = cat
                    cat_name = {"F": "Family", "C": "Celebrity", "S": "Spiritual",
                                "P": "Personal", "W": "Work"}.get(cat, "Other")
                    lines.append(f"\n*{cat_name}:*")

                line = f"  `{p.get('pid_display', pid)}` {p['name']}"
                if p.get("birth_date"):
                    line += f" — {p['birth_date']}"
                if p.get("lifepath"):
                    line += f" LP:{p['lifepath']}"
                if p.get("resonance_score"):
                    line += f" 🌊{p['resonance_score']}"
                lines.append(line)

            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error listing: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {e}")

    # ── HARMONIC ─────────────────────────────────────────────────
    elif args.lower().startswith("harmonic "):
        try:
            val = int(args[9:].strip())
            results = search_by_harmonic(val)
            if not results:
                await update.message.reply_text(f"No people with harmonic root {val}")
                return
            lines = [f"🌀 *Harmonic Root {val}:*\n"]
            for p in results:
                lines.append(f"• `{p.get('pid_display', p['pid'])}` *{p['name']}* (via {p['source']})")
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Provide a number 1-9")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    # ── MASTER ───────────────────────────────────────────────────
    elif args.lower().startswith("master "):
        try:
            val = int(args[7:].strip())
            if val not in {11, 22, 33, 44}:
                await update.message.reply_text("❌ Master numbers: 11, 22, 33, 44")
                return
            results = search_by_master(val)
            if not results:
                await update.message.reply_text(f"No people carrying master {val}")
                return
            lines = [f"⭐ *Master {val}:*\n"]
            for p in results:
                lines.append(f"• `{p.get('pid_display', p['pid'])}` *{p['name']}*")
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Provide 11, 22, 33, or 44")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    # ── REMOVE ───────────────────────────────────────────────────
    elif args.lower().startswith("remove "):
        pid = args[7:].strip().upper()
        if not PID_PATTERN.match(pid):
            await update.message.reply_text("❌ Invalid PID format. Example: C001")
            return
        try:
            result = remove_person(pid)
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
            else:
                await update.message.reply_text(f"🗑️ *{result['name']}* (`{pid}`) removed", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    # ── PID-BASED COMMANDS ───────────────────────────────────────
    elif PID_PATTERN.match(args.split()[0].upper()):
        parts = args.split(None, 1)
        pid = parts[0].upper()
        subcommand = parts[1].strip() if len(parts) > 1 else ""

        # /person <PID> (no subcommand = profile)
        if not subcommand:
            try:
                person = get_person_profile(pid)
                if not person:
                    await update.message.reply_text(f"❌ PID `{pid}` not found", parse_mode="Markdown")
                    return

                lines = []
                lines.append(f"👤 *{person.get('name')}* (`{person.get('pid_display', pid)}`)")
                if person.get("sun_sign"):
                    lines.append(f"☀️ {person['sun_sign'].title()} {person.get('sun_sign_glyph', '')}")
                lines.append("")

                # Contact info
                for field in ["phone", "email", "address"]:
                    if person.get(field):
                        icon = {"phone": "📱", "email": "📧", "address": "📍"}.get(field, "")
                        lines.append(f"{icon} {person[field]}")

                # Dates
                date_fields = [k for k in person.keys() if k.endswith("_date") and not k.startswith("conception")]
                for df in sorted(date_fields):
                    label = df.replace("_date", "").title()
                    lines.append(f"📅 {label}: {person[df]}")

                if person.get("birth_time"):
                    lines.append(f"🕐 Birth time: {person['birth_time']}")
                if person.get("birth_place"):
                    lines.append(f"📍 Birth place: {person['birth_place']}")
                if person.get("conception_date"):
                    lines.append(f"🌱 Conception est: {person['conception_date']}")

                # Quick numerology
                if person.get("birth_lifepath"):
                    lines.append("")
                    lines.append(f"🔮 Life Path: {person['birth_lifepath']}")
                if person.get("birth_triangle1"):
                    lines.append(f"🔺 T1: {person['birth_triangle1']}")
                if person.get("birth_triangle2"):
                    lines.append(f"🔺 T2: {person['birth_triangle2']}")
                if person.get("birth_master_numbers"):
                    lines.append(f"⭐ Masters: {person['birth_master_numbers']}")

                # Resonance
                if person.get("resonance_score") is not None:
                    lines.append(f"\n🌊 Seraphe resonance: *{person['resonance_score']}* ({person.get('resonance_total', '?')} matches)")

                # Relationships
                rels = person.get("relationships", [])
                if rels:
                    lines.append("\n🔗 *Relationships:*")
                    for r in rels:
                        lines.append(f"  {r['type'].lower()} → {r['name']} (`{r['pid']}`)")

                # Notes
                if person.get("notes"):
                    lines.append(f"\n📝 {person['notes']}")

                lines.append(f"\n📊 Signature: {person.get('signature_count', 0)} entries")

                await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error getting profile: {e}", exc_info=True)
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> fractals
        elif subcommand.lower().startswith("fractals"):
            try:
                person = get_person_profile(pid)
                if not person:
                    await update.message.reply_text(f"❌ PID `{pid}` not found", parse_mode="Markdown")
                    return
                if not person.get("birth_month"):
                    await update.message.reply_text(
                        f"*{person['name']}* has no birth date.\n"
                        f"Add: `/person {pid} date birth MM/DD/YYYY`",
                        parse_mode="Markdown"
                    )
                    return

                result = analyze_date_with_signature(
                    person["birth_month"], person["birth_day"], person["birth_year"],
                    "birth"
                )
                msg = format_fractals_telegram(
                    person["name"], person.get("pid_display", pid),
                    result["analysis"], result["signature"]
                )
                await update.message.reply_text(msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error getting fractals: {e}", exc_info=True)
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> resonance
        elif subcommand.lower().startswith("resonance"):
            try:
                result = get_resonance_detail(pid)
                if "error" in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                    return

                msg = format_resonance_telegram(
                    result["name"], result.get("pid_display", pid),
                    "Seraphe", "F001♌",
                    result["matches"], result["summary"]
                )
                await update.message.reply_text(msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error computing resonance: {e}", exc_info=True)
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> date <field> <MM/DD/YYYY>
        elif subcommand.lower().startswith("date "):
            date_args = subcommand[5:].strip().split(None, 1)
            if len(date_args) < 2:
                await update.message.reply_text("Usage: `/person <PID> date <field> MM/DD/YYYY`", parse_mode="Markdown")
                return

            field = date_args[0].lower().replace(" ", "_")
            date = parse_date(date_args[1])
            if not date:
                await update.message.reply_text("❌ Invalid date. Use MM/DD/YYYY")
                return

            try:
                result = add_date_to_person(pid, field, *date)
                if "error" in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                else:
                    msg = f"✅ `{pid}` *{result['name']}* — {field} = {result['date']}\n"
                    msg += f"🔮 LP: {result['lifepath']} | T1: {result['triangle1']} | T2: {result['triangle2']}\n"
                    msg += f"🌊 Seraphe resonance: *{result['resonance_score']}*"
                    await update.message.reply_text(msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error adding date: {e}", exc_info=True)
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> set <field> <value>
        elif subcommand.lower().startswith("set "):
            set_args = subcommand[4:].strip().split(None, 1)
            if len(set_args) < 2:
                await update.message.reply_text(
                    f"Usage: `/person {pid} set <field> <value>`\n"
                    f"Fields: {', '.join(SETTABLE_FIELDS)}",
                    parse_mode="Markdown"
                )
                return

            field = set_args[0].lower().replace(" ", "_")
            value = set_args[1]
            try:
                result = set_person_field(pid, field, value)
                if "error" in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                else:
                    await update.message.reply_text(
                        f"✅ `{pid}` *{result['name']}* — {field} = {value}",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> memo <text>
        elif subcommand.lower().startswith("memo "):
            memo = subcommand[5:].strip()
            try:
                result = set_person_memo(pid, memo)
                if "error" in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                else:
                    await update.message.reply_text(
                        f"📝 Memo saved for `{pid}` *{result['name']}*",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")

        # /person <PID> relate <type> <PID2>
        elif subcommand.lower().startswith("relate "):
            rel_args = subcommand[7:].strip().split()
            if len(rel_args) < 2:
                await update.message.reply_text(
                    f"Usage: `/person {pid} relate <type> <PID2>`\n"
                    f"Types: {', '.join(VALID_RELATIONSHIPS)}",
                    parse_mode="Markdown"
                )
                return

            rel_type = rel_args[0]
            pid2 = rel_args[1].upper()
            try:
                result = add_relationship(pid, rel_type, pid2)
                if "error" in result:
                    await update.message.reply_text(f"❌ {result['error']}")
                else:
                    await update.message.reply_text(
                        f"🔗 {result['person1']} —*{result['relationship']}*→ {result['person2']}",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")

        else:
            await update.message.reply_text(
                f"❓ Unknown subcommand for `{pid}`. Try:\n"
                f"`/person {pid}` (profile)\n"
                f"`/person {pid} fractals`\n"
                f"`/person {pid} resonance`\n"
                f"`/person {pid} date <field> MM/DD/YYYY`\n"
                f"`/person {pid} set <field> <value>`\n"
                f"`/person {pid} memo <text>`\n"
                f"`/person {pid} relate <type> <PID2>`",
                parse_mode="Markdown"
            )

    else:
        await update.message.reply_text(
            "❓ Unknown command. Try `/person` for help.",
            parse_mode="Markdown"
        )
