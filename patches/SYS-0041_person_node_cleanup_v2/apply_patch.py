import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=41,
    description='person node cleanup and CorePerson taxonomy',
    patch_type='MINOR',
)
patch.begin()

neo4j_pass = os.environ.get('NEO4J_PASSWORD', '')

def cypher(stmt, label=""):
    clean = ' '.join(stmt.strip().split())
    result = subprocess.run(
        ['cypher-shell', '-u', 'neo4j', '-p', neo4j_pass, clean],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  [!] {label}: {result.stderr[:300]}")
        return False
    out = result.stdout.strip()
    if out:
        print(f"  [✓] {label}: {out[:120]}")
    else:
        print(f"  [✓] {label}")
    return True

print("=== Step 1: Merge Seraphe nodes → CorePerson ===")

# Pick the most complete node as target, redirect all rels from others, delete others
cypher("""
MATCH (target:Person {name: 'Rebecca Lydia Denkers'})
MATCH (dupe:Person)
WHERE dupe.name IN ['Rebecca', 'Becky', 'Becky Denkers', 'rebecca']
  AND elementId(dupe) <> elementId(target)
WITH target, collect(dupe) AS dupes
UNWIND dupes AS d
CALL {
  WITH d, target
  MATCH (d)-[r]->(x) WHERE elementId(x) <> elementId(target)
  MERGE (target)-[r2:RELATED_TO]->(x)
  DELETE r
}
CALL {
  WITH d, target
  MATCH (x)-[r]->(d) WHERE elementId(x) <> elementId(target)
  MERGE (x)-[r2:RELATED_TO]->(target)
  DELETE r
}
DETACH DELETE d
""", "Delete Seraphe dupes")

cypher("""
MATCH (p:Person {name: 'Rebecca Lydia Denkers'})
SET p:CorePerson
SET p.preferred_name = 'Seraphe'
SET p.also_known_as = ['Rebecca', 'Becky', 'Seraphe', 'Seraphe Valemira']
SET p.role = 'partner'
SET p.telegram_id = '8069190169'
SET p.canonical = true
SET p.node_version = 1
RETURN p.name
""", "Set Seraphe CorePerson properties")

print("\n=== Step 2: Merge Adge nodes → CorePerson ===")

cypher("""
MATCH (target:Person {name: 'Adriaan Harold Denkers'})
MATCH (dupe:Person {name: 'Adge'})
WHERE elementId(dupe) <> elementId(target)
DETACH DELETE dupe
""", "Delete Adge dupe")

cypher("""
MATCH (p:Person {name: 'Adriaan Harold Denkers'})
SET p:CorePerson
SET p.preferred_name = 'Adge'
SET p.also_known_as = ['Adge', "Ka'tuar'el", 'Thronescribe']
SET p.role = 'self'
SET p.canonical = true
SET p.node_version = 1
RETURN p.name
""", "Set Adge CorePerson properties")

print("\n=== Step 3: Merge Fitz nodes → CorePerson ===")

cypher("""
MATCH (target:Person {name: 'Adriaan Fitzgerald Denkers'})
WITH target LIMIT 1
MATCH (dupe:Person {name: 'Adriaan Fitzgerald Denkers'})
WHERE elementId(dupe) <> elementId(target)
DETACH DELETE dupe
""", "Delete Fitz dupes")

cypher("""
MATCH (p:Person {name: 'Adriaan Fitzgerald Denkers'})
WITH p LIMIT 1
SET p:CorePerson
SET p.preferred_name = 'Fitz'
SET p.also_known_as = ['Fitz']
SET p.role = 'son'
SET p.canonical = true
SET p.node_version = 1
RETURN p.name
""", "Set Fitz CorePerson properties")

cypher("""
MATCH (p:Person {name: 'Fitz'})
DETACH DELETE p
""", "Delete standalone Fitz node")

print("\n=== Step 4: Deduplicate Person nodes ===")

dupes = [
    ('Joan of Arc',          ['Joan Arc'],                        1412, 1431),
    ('Leonardo da Vinci',    ['Leonardo Vinci'],                  1452, 1519),
    ('Carl Jung',            [],                                  1875, 1961),
    ('Dave Matthews',        ['David John Matthews'],             1967, None),
    ('Nikola Tesla',         [],                                  1856, 1943),
    ('Jesse Jackson',        [],                                  1941, None),
    ('Hildegard von Bingen', ['Hildegard Bingen'],                1098, 1179),
    ('Osiris',               [],                                  None, None),
]

for canonical_name, alt_names, birth, death in dupes:
    all_names = [canonical_name] + alt_names

    # Delete alternates
    for alt in alt_names:
        cypher(f"""
        MATCH (p:Person {{name: '{alt}'}})
        DETACH DELETE p
        """, f"Delete alt '{alt}'")

    # Dedupe canonical (keep one, delete rest)
    cypher(f"""
    MATCH (p:Person {{name: '{canonical_name}'}})
    WITH collect(p) AS nodes
    UNWIND nodes[1..] AS extra
    DETACH DELETE extra
    """, f"Dedupe '{canonical_name}'")

    # Set properties on survivor
    props = [
        f"p.canonical = true",
        f"p.node_version = 1",
    ]
    if alt_names:
        also = str(alt_names).replace('"', "'")
        props.append(f"p.also_known_as = {also}")
    if birth:
        props.append(f"p.birth_year = {birth}")
    if death:
        props.append(f"p.death_year = {death}")

    set_clause = '\nSET '.join(props)
    cypher(f"""
    MATCH (p:Person {{name: '{canonical_name}'}})
    SET {set_clause}
    RETURN p.name
    """, f"Properties '{canonical_name}'")

print("\n=== Step 5: Stamp remaining Person + Entity nodes ===")

cypher("""
MATCH (p:Person)
WHERE p.canonical IS NULL
SET p.canonical = true
SET p.node_version = 1
RETURN count(p) AS stamped
""", "Stamp remaining Person nodes")

cypher("""
MATCH (e:Entity)
WHERE e.node_version IS NULL
SET e.node_version = 1
RETURN count(e) AS stamped
""", "Stamp Entity nodes")

print("\n=== Verification ===")
cypher("""
MATCH (p:CorePerson)
RETURN p.name, p.preferred_name, p.role
ORDER BY p.role
""", "CorePerson nodes")

cypher("""
MATCH (p:Person)
RETURN count(p) AS total_person_nodes
""", "Total Person nodes remaining")

patch.finish()
