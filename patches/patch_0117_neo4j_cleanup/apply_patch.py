#!/usr/bin/env python3
"""
Patch 0117: Neo4j Entity Cleanup + ASPECT_OF Linking + Web Route Fix

1. Deletes junk Person:Entity nodes (ASSISTANT, USER, planets, etc.)
2. Merges duplicate Ka'tuar'el Entity (id 449 → 299)
3. Links soul-aspect Entity nodes → ASPECT_OF → canonical Person nodes
4. Standardizes a few relationship inconsistencies
5. Fixes duplicate /people route registrations in web.py
6. Verifies core family + soul relationships
"""
import os
import sys
import shutil
import py_compile
from datetime import datetime

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = '/opt/mythos'
WEB_ROUTES = f'{MYTHOS}/api/routes/web.py'

sys.path.insert(0, MYTHOS)
from dotenv import load_dotenv
load_dotenv(f'{MYTHOS}/.env')

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def backup(path):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f"{path}.bak.{ts}"
    shutil.copy2(path, bak)
    print(f"  Backed up → {bak}")
    return bak


def get_neo4j_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def neo4j_cleanup():
    """Full Neo4j entity cleanup and ASPECT_OF linking."""
    driver = get_neo4j_driver()

    with driver.session() as session:

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 1: Pre-cleanup counts
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 1: Pre-cleanup counts ──")
        r = session.run("MATCH (p:Person) RETURN count(p) AS c").single()
        total_before = r['c']
        print(f"  Total Person nodes: {total_before}")
        r = session.run("MATCH (p:Person:Entity) RETURN count(p) AS c").single()
        entity_before = r['c']
        print(f"  Person:Entity nodes: {entity_before}")
        r = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()
        rels_before = r['c']
        print(f"  Total relationships: {rels_before}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 2: Delete pure junk nodes
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 2: Deleting junk Person:Entity nodes ──")
        junk_names = [
            # Bot-as-person
            'ASSISTANT', 'Assistant', 'assistant',
            # User-as-generic-entity
            'USER', 'User', 'user', 'You', 'you',
            # Astro objects misclassified as people
            'Arabic', 'Mercury', 'Neptune', 'Ceres', 'Juno', 'Vesta',
            # Abstract terms misclassified as people
            'fortune', 'spirit',
        ]

        total_junk_deleted = 0
        total_junk_rels = 0
        for name in junk_names:
            r = session.run("""
                MATCH (p:Person:Entity {name: $name})-[r]-()
                RETURN count(r) AS rc
            """, name=name).single()
            rel_count = r['rc']

            r = session.run("""
                MATCH (p:Person:Entity {name: $name})
                DETACH DELETE p
                RETURN count(p) AS deleted
            """, name=name).single()
            deleted = r['deleted']
            if deleted > 0:
                print(f"  🗑️  {name}: {deleted} node(s), {rel_count} relationship(s) removed")
                total_junk_deleted += deleted
                total_junk_rels += rel_count

        print(f"  Total junk removed: {total_junk_deleted} nodes, {total_junk_rels} relationships")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 3: Merge duplicate Ka'tuar'el (id 449 → 299)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 3: Merging duplicate Ka'tuar'el nodes ──")

        r = session.run("""
            MATCH (p:Person:Entity)
            WHERE p.name = "Ka'tuar'el"
            RETURN id(p) AS nid
            ORDER BY id(p)
        """)
        ka_ids = [rec['nid'] for rec in r]
        print(f"  Ka'tuar'el Entity node IDs: {ka_ids}")

        if len(ka_ids) >= 2:
            keep_id = ka_ids[0]   # 299 — the one with more relationships
            merge_id = ka_ids[1]  # 449

            # Move outgoing MENTIONED from duplicate to keeper
            r = session.run("""
                MATCH (src:Person:Entity)-[r:MENTIONED]->(target)
                WHERE id(src) = $merge_id
                WITH src, target
                MATCH (keep:Person:Entity) WHERE id(keep) = $keep_id
                MERGE (keep)-[:MENTIONED]->(target)
                RETURN count(*) AS moved
            """, merge_id=merge_id, keep_id=keep_id).single()
            print(f"  Moved {r['moved']} outgoing MENTIONED → {keep_id}")

            # Move incoming relationships
            r = session.run("""
                MATCH (source)-[r]->(dest:Person:Entity)
                WHERE id(dest) = $merge_id
                WITH source, type(r) AS rtype
                MATCH (keep:Person:Entity) WHERE id(keep) = $keep_id
                FOREACH (_ IN CASE WHEN rtype = 'MENTIONED' THEN [1] ELSE [] END |
                    MERGE (source)-[:MENTIONED]->(keep)
                )
                FOREACH (_ IN CASE WHEN rtype = 'DISCUSSED' THEN [1] ELSE [] END |
                    MERGE (source)-[:DISCUSSED]->(keep)
                )
                RETURN count(*) AS moved
            """, merge_id=merge_id, keep_id=keep_id).single()
            print(f"  Moved {r['moved']} incoming relationships → {keep_id}")

            # Delete the duplicate
            session.run("MATCH (p) WHERE id(p) = $mid DETACH DELETE p", mid=merge_id)
            print(f"  🗑️  Deleted duplicate Ka'tuar'el (id={merge_id})")
        else:
            print(f"  Only {len(ka_ids)} Ka'tuar'el Entity node(s) — no merge needed")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 4: Create ASPECT_OF relationships
        # Link soul-aspect Entity nodes → canonical Person nodes
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 4: Creating ASPECT_OF relationships ──")

        aspect_mappings = [
            # Ka'tuar'el aspects → person-adriaan
            ("Ka'tuar'el",         "person-adriaan", "soul_name"),

            # Seraphe/Rebecca aspects → person-rebecca
            ("Rebecca",            "person-rebecca", "birth_name"),
            ("Seraphe",            "person-rebecca", "spiritual_name"),
            ("Becky",              "person-rebecca", "familiar_name"),
            ("Rebecca Lydia Ryan", "person-rebecca", "maiden_name"),

            # Fitz aspects → person-fitz
            ("Fitz",               "person-fitz",    "familiar_name"),
        ]

        for entity_name, canonical_id, aspect_type in aspect_mappings:
            # Check entity exists
            exists = session.run(
                "MATCH (e:Person:Entity {name: $n}) RETURN count(e) AS c",
                n=entity_name
            ).single()['c']

            if exists == 0:
                print(f"  ⚠️  Entity '{entity_name}' not found — skipped")
                continue

            r = session.run("""
                MATCH (e:Person:Entity {name: $ename})
                MATCH (p:Person {canonical_id: $cid})
                MERGE (e)-[r:ASPECT_OF]->(p)
                ON CREATE SET r.type = $atype, r.created_at = datetime()
                ON MATCH SET r.type = $atype
                RETURN
                    CASE WHEN r.created_at = datetime() THEN 'created' ELSE 'exists' END AS status
            """, ename=entity_name, cid=canonical_id, atype=aspect_type).single()

            status = r['status'] if r else 'created'
            icon = "✅" if status == 'created' else "✓ "
            print(f"  {icon} {entity_name} -[ASPECT_OF {{type: '{aspect_type}'}}]-> {canonical_id}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 5: Standardize relationship names
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 5: Standardizing relationship names ──")

        renames = [
            ("CONNECTED_TO", "CONNECTS_TO"),
        ]

        for old_type, new_type in renames:
            r = session.run(f"""
                MATCH (a)-[r:{old_type}]->(b)
                RETURN count(r) AS cnt
            """).single()
            cnt = r['cnt']

            if cnt > 0:
                session.run(f"""
                    MATCH (a)-[r:{old_type}]->(b)
                    WITH a, b, properties(r) AS props
                    CREATE (a)-[nr:{new_type}]->(b)
                    SET nr = props
                """)
                session.run(f"MATCH ()-[r:{old_type}]->() DELETE r")
                print(f"  ✅ Renamed {cnt}x: {old_type} → {new_type}")
            else:
                print(f"  ✓  No {old_type} relationships found")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 6: Verify core relationships
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 6: Verifying core relationships ──")

        checks = [
            # Family
            ("Ka ↔ Seraphe (SPOUSE_OF)",
             "MATCH (a:Person {canonical_id:'person-adriaan'})-[:SPOUSE_OF]->(b:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            ("Ka → Fitz (PARENT_OF)",
             "MATCH (a:Person {canonical_id:'person-adriaan'})-[:PARENT_OF]->(b:Person {canonical_id:'person-fitz'}) RETURN count(*) AS c"),
            ("Seraphe → Fitz (PARENT_OF)",
             "MATCH (a:Person {canonical_id:'person-rebecca'})-[:PARENT_OF]->(b:Person {canonical_id:'person-fitz'}) RETURN count(*) AS c"),
            ("Dennis → Rebecca (PARENT_OF)",
             "MATCH (a:Person {canonical_id:'person-dennis'})-[:PARENT_OF]->(b:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            # Soul → Person
            ("Soul Ka'tuar'el → Person Adriaan (CURRENTLY_EMBODIED_AS)",
             "MATCH (s:Soul {canonical_id:'soul-kataurel'})-[:CURRENTLY_EMBODIED_AS]->(p:Person {canonical_id:'person-adriaan'}) RETURN count(*) AS c"),
            ("Soul Seraphe → Person Rebecca (CURRENTLY_EMBODIED_AS)",
             "MATCH (s:Soul {canonical_id:'soul-seraphe'})-[:CURRENTLY_EMBODIED_AS]->(p:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            # ASPECT_OF links
            ("Ka'tuar'el Entity → Person Adriaan (ASPECT_OF)",
             """MATCH (e:Person:Entity {name:"Ka'tuar'el"})-[:ASPECT_OF]->(p:Person {canonical_id:'person-adriaan'}) RETURN count(*) AS c"""),
            ("Seraphe Entity → Person Rebecca (ASPECT_OF)",
             "MATCH (e:Person:Entity {name:'Seraphe'})-[:ASPECT_OF]->(p:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            ("Rebecca Entity → Person Rebecca (ASPECT_OF)",
             "MATCH (e:Person:Entity {name:'Rebecca'})-[:ASPECT_OF]->(p:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            ("Becky Entity → Person Rebecca (ASPECT_OF)",
             "MATCH (e:Person:Entity {name:'Becky'})-[:ASPECT_OF]->(p:Person {canonical_id:'person-rebecca'}) RETURN count(*) AS c"),
            ("Fitz Entity → Person Fitz (ASPECT_OF)",
             "MATCH (e:Person:Entity {name:'Fitz'})-[:ASPECT_OF]->(p:Person {canonical_id:'person-fitz'}) RETURN count(*) AS c"),
            # Trinity
            ("Seraphe Valemira → Brandi Carlile (TRINITY_CENTER_OF)",
             "MATCH (s:Soul {name:'Seraphe Valemira'})-[:TRINITY_CENTER_OF]->(b:Soul {name:'Brandi Carlile'}) RETURN count(*) AS c"),
            ("Seraphe Valemira → Riley Green (TRINITY_CENTER_OF)",
             "MATCH (s:Soul {name:'Seraphe Valemira'})-[:TRINITY_CENTER_OF]->(b:Soul {name:'Riley Green'}) RETURN count(*) AS c"),
        ]

        all_good = True
        for label, query in checks:
            r = session.run(query).single()
            count = r['c']
            if count > 0:
                print(f"  ✅ {label}")
            else:
                print(f"  ❌ MISSING: {label}")
                all_good = False

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Phase 7: Post-cleanup summary
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n── Phase 7: Post-cleanup summary ──")
        r = session.run("MATCH (p:Person) RETURN count(p) AS c").single()
        total_after = r['c']
        r = session.run("MATCH (p:Person:Entity) RETURN count(p) AS c").single()
        entity_after = r['c']
        r = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()
        rels_after = r['c']

        print(f"  Person nodes: {total_before} → {total_after} (removed {total_before - total_after})")
        print(f"  Person:Entity nodes: {entity_before} → {entity_after}")
        print(f"  Total relationships: {rels_before} → {rels_after}")

        # Show remaining Person:Entity nodes
        r = session.run("""
            MATCH (p:Person:Entity)
            WHERE p.name IS NOT NULL
            OPTIONAL MATCH (p)-[a:ASPECT_OF]->(canonical:Person)
            RETURN p.name AS name, id(p) AS nid,
                   canonical.canonical_id AS linked_to,
                   a.type AS aspect_type,
                   size([(p)-[:MENTIONED]->() | 1]) AS mention_count
            ORDER BY p.name
        """)
        remaining = list(r)
        if remaining:
            print(f"\n  Remaining Person:Entity nodes ({len(remaining)}):")
            for rec in remaining:
                linked = f" → {rec['linked_to']} ({rec['aspect_type']})" if rec['linked_to'] else ""
                mentions = f" [{rec['mention_count']} mentions]" if rec['mention_count'] else ""
                print(f"    • {rec['name']}{linked}{mentions}")

    driver.close()
    return all_good


def fix_web_routes():
    """Fix duplicate /people route registrations in web.py"""
    print("\n── Fix: Duplicate web routes ──")

    with open(WEB_ROUTES, 'r') as f:
        content = f.read()

    count = content.count('async def people_page')
    if count <= 1:
        print("  ✓ No duplicate people routes found")
        return True

    print(f"  Found {count} definitions of people_page — removing duplicates")
    backup(WEB_ROUTES)

    lines = content.split('\n')
    new_lines = []
    seen_people_func = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if 'async def people_page' in line:
            if not seen_people_func:
                seen_people_func = True
                new_lines.append(line)
                i += 1
                continue
            else:
                # Remove decorators we already added for this duplicate
                while new_lines and (new_lines[-1].strip().startswith('@router.get("/people') or new_lines[-1].strip() == ''):
                    new_lines.pop()
                # Skip async def + body
                i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                    if lines[i].strip().startswith('@') or (lines[i].strip().startswith('async def') and 'people_page' not in lines[i]):
                        break
                    i += 1
                print(f"  Removed duplicate people_page")
                continue

        new_lines.append(line)
        i += 1

    with open(WEB_ROUTES, 'w') as f:
        f.write('\n'.join(new_lines))

    try:
        py_compile.compile(WEB_ROUTES, doraise=True)
        print(f"  ✓ web.py syntax OK")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ web.py syntax error: {e}")
        return False


def main():
    print("=" * 60)
    print("  Patch 0117: Neo4j Entity Cleanup + ASPECT_OF Linking")
    print("=" * 60)

    print("\n[1/2] Neo4j Cleanup & Linking")
    relationships_ok = neo4j_cleanup()

    print("\n[2/2] Web Route Dedup Fix")
    routes_ok = fix_web_routes()

    if routes_ok:
        print("\n=== Restarting mythos-api ===")
        os.system("sudo systemctl restart mythos-api.service")
        import time
        time.sleep(3)
        rc = os.system("sudo systemctl is-active --quiet mythos-api.service")
        if rc == 0:
            print("✓ mythos-api is running")
        else:
            print("✗ mythos-api failed — check journalctl")

    print("\n" + "=" * 60)
    print("  RELATIONSHIP NAMING CONVENTION")
    print("=" * 60)
    print("""
  Domain          Convention              Examples
  ──────────────  ──────────────────────  ──────────────────────────────
  Genealogy       VERB_PREPOSITION        PARENT_OF, CHILD_OF, SPOUSE_OF,
                                          MARRIED_TO, BORN_IN, DIED_IN
  Soul/Spiritual  VERB_PREPOSITION        ASPECT_OF, INCARNATED_AS,
                                          CURRENTLY_EMBODIED_AS,
                                          CARRIES_LINEAGE, EMBODIES
  Trinity         TRINITY_ROLE            TRINITY_CENTER_OF,
                                          TRINITY_MIRROR_OF
  Identity        KNOWN_AS                Alias nodes (name variants)
  Knowledge       VERB                    MENTIONED, DISCUSSED,
                                          RELATED_TO, DEFINES
  Grid Nodes      NODE_QUALIFIER          ANCHOR_OBJECT, ECHO_EVENT,
                                          BEACON_VALUE, MIRROR_SHADOW,
                                          GATEWAY_PORTAL, etc.
  Grid Assess     NODE_ASSESSMENT         ANCHOR_ASSESSMENT,
                                          ECHO_ASSESSMENT, etc.
  System/Code     VERB                    RUNS, CALLS, IMPORTS,
                                          CONTAINS, RUNS_SERVICE
  Charts          HAS_TYPE                HAS_CHART, HAS_NUMEROLOGY,
                                          HAS_STRATIGRAPHY
  Genealogy(Gen)  VERB_PREPOSITION        HAS_SURNAME, BELONGS_TO_FAMILY,
                                          MARRIED_IN
    """)

    if relationships_ok:
        print("✅ All core relationships verified")
    else:
        print("⚠️  Some relationships missing — review output above")
    print("=" * 60)


if __name__ == '__main__':
    main()
