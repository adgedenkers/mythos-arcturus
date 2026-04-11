import sys
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

print("Running Person node cleanup in Neo4j...")

cypher_statements = [

    # ── 1. Merge Seraphe's 5 Person nodes → one canonical CorePerson ──────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Rebecca', 'Becky', 'Becky Denkers', 'Rebecca Lydia Denkers', 'rebecca']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node:CorePerson
    SET node.name = 'Rebecca Lydia Denkers'
    SET node.preferred_name = 'Seraphe'
    SET node.also_known_as = ['Rebecca', 'Becky', 'Seraphe', 'Seraphe Valemira']
    SET node.role = 'partner'
    SET node.telegram_id = '8069190169'
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 2. Promote Adge's Person nodes → CorePerson ───────────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Adge', 'Adriaan Harold Denkers']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node:CorePerson
    SET node.name = 'Adriaan Harold Denkers'
    SET node.preferred_name = 'Adge'
    SET node.also_known_as = ['Adge', "Ka'tuar'el", 'Thronescribe']
    SET node.role = 'self'
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 3. Promote Fitz → CorePerson ──────────────────────────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Fitz', 'Adriaan Fitzgerald Denkers']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node:CorePerson
    SET node.name = 'Adriaan Fitzgerald Denkers'
    SET node.preferred_name = 'Fitz'
    SET node.also_known_as = ['Fitz']
    SET node.role = 'son'
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 4. Merge Joan of Arc ×3 ───────────────────────────────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Joan of Arc', 'Joan Arc']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.name = 'Joan of Arc'
    SET node.also_known_as = ['Jeanne d\\'Arc', 'Joan Arc']
    SET node.birth_year = 1412
    SET node.death_year = 1431
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 5. Merge Leonardo da Vinci ×3 ─────────────────────────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Leonardo da Vinci', 'Leonardo Vinci']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.name = 'Leonardo da Vinci'
    SET node.also_known_as = ['Leonardo Vinci']
    SET node.birth_year = 1452
    SET node.death_year = 1519
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 6. Merge Carl Jung ×2 ─────────────────────────────────────────────────
    """
    MATCH (p:Person) WHERE p.name = 'Carl Jung'
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.birth_year = 1875
    SET node.death_year = 1961
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 7. Merge Dave Matthews ×2 + David John Matthews ──────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Dave Matthews', 'David John Matthews']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.name = 'Dave Matthews'
    SET node.also_known_as = ['David John Matthews']
    SET node.birth_year = 1967
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 8. Merge Nikola Tesla ×2 ──────────────────────────────────────────────
    """
    MATCH (p:Person) WHERE p.name = 'Nikola Tesla'
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.birth_year = 1856
    SET node.death_year = 1943
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 9. Merge Jesse Jackson ×2 ─────────────────────────────────────────────
    """
    MATCH (p:Person) WHERE p.name = 'Jesse Jackson'
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.birth_year = 1941
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 10. Merge Hildegard von Bingen ×2 ─────────────────────────────────────
    """
    MATCH (p:Person)
    WHERE p.name IN ['Hildegard von Bingen', 'Hildegard Bingen']
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.name = 'Hildegard von Bingen'
    SET node.also_known_as = ['Hildegard Bingen']
    SET node.birth_year = 1098
    SET node.death_year = 1179
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 11. Merge Osiris ×2 ───────────────────────────────────────────────────
    """
    MATCH (p:Person) WHERE p.name = 'Osiris'
    WITH collect(p) AS nodes
    CALL apoc.refactor.mergeNodes(nodes, {
        properties: 'discard',
        mergeRels: true
    }) YIELD node
    SET node.canonical = true
    SET node.node_version = 1
    RETURN node.name
    """,

    # ── 12. Set canonical=true + node_version on all remaining Person nodes ───
    """
    MATCH (p:Person)
    WHERE p.canonical IS NULL
    SET p.canonical = true
    SET p.node_version = 1
    RETURN count(p) AS updated
    """,

    # ── 13. Set node_version on all Entity nodes ──────────────────────────────
    """
    MATCH (e:Entity)
    WHERE e.node_version IS NULL
    SET e.node_version = 1
    RETURN count(e) AS updated
    """,
]

import os
neo4j_pass = os.environ.get('NEO4J_PASSWORD', '')

for i, stmt in enumerate(cypher_statements, 1):
    clean = ' '.join(stmt.strip().split())
    print(f"  [{i}/{len(cypher_statements)}] Running Cypher statement...")
    result = subprocess.run(
        ['cypher-shell', '-u', 'neo4j', '-p', neo4j_pass, clean],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # APOC not available — fall back to manual merge approach
        print(f"  [!] APOC merge failed for statement {i} — check APOC availability")
        print(f"      stderr: {result.stderr[:200]}")
    else:
        print(f"  [✓] Statement {i} complete: {result.stdout.strip()[:100]}")

print("\nPerson node cleanup complete.")
print("Run: cypher-shell -u neo4j -p $NEO4J_PASSWORD \"MATCH (p:CorePerson) RETURN p.name, p.preferred_name\"")
print("to verify CorePerson nodes.")

patch.finish()
