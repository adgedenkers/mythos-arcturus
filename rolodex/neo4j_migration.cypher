// ============================================================
// ROLODEX — Neo4j Migration (Phase 1-4)
// Run via cypher-shell
// ============================================================

// --- PHASE 1: Create constraints and indexes ---

CREATE CONSTRAINT rx_uid IF NOT EXISTS FOR (n:PersonOwner) REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT rx_canonical IF NOT EXISTS FOR (n:PersonOwner) REQUIRE n.canonical_id IS UNIQUE;
CREATE INDEX rx_domain IF NOT EXISTS FOR (n:Person) ON (n.domain);
CREATE INDEX rx_scope IF NOT EXISTS FOR (n:Person) ON (n.scope);
CREATE INDEX rx_origin IF NOT EXISTS FOR (n:Person) ON (n.origin);
CREATE INDEX rx_person_canonical IF NOT EXISTS FOR (n:Person) ON (n.canonical_id);
CREATE INDEX rx_soul_canonical IF NOT EXISTS FOR (n:Soul) ON (n.canonical_id);
CREATE INDEX rx_entity_canonical IF NOT EXISTS FOR (n:Entity) ON (n.canonical_id);

// --- PHASE 2: Create PersonOwner nodes ---

// Adge - System Owner
MERGE (po:PersonOwner {canonical_id: "PO-DENKERS-AdriaanHarold-1977"})
SET po.uid = "RX-PO-001",
    po.person_id = "PP-DENKERS-AdriaanHarold-1977",
    po.full_name = "Adriaan Harold Denkers",
    po.display_name = "Adge",
    po.node_type = "system-owner",
    po.domain = "people",
    po.scope = "personal",
    po.origin = "manual",
    po.created_at = datetime(),
    po.updated_at = datetime();

// Seraphe - System Owner
MERGE (po:PersonOwner {canonical_id: "PO-RYAN-Rebecca-1978"})
SET po.uid = "RX-PO-002",
    po.person_id = "PP-RYAN-Rebecca-1978",
    po.full_name = "Rebecca Lydia Ryan",
    po.display_name = "Seraphe",
    po.node_type = "system-owner",
    po.domain = "people",
    po.scope = "personal",
    po.origin = "manual",
    po.created_at = datetime(),
    po.updated_at = datetime();

// Fitz - System Owner
MERGE (po:PersonOwner {canonical_id: "PO-DENKERS-AdriaanFitzgerald-2020"})
SET po.uid = "RX-PO-003",
    po.person_id = "PP-DENKERS-AdriaanFitzgerald-2020",
    po.full_name = "Adriaan Fitzgerald Denkers",
    po.display_name = "Fitz",
    po.node_type = "system-owner",
    po.domain = "people",
    po.scope = "personal",
    po.origin = "manual",
    po.created_at = datetime(),
    po.updated_at = datetime();

// --- PHASE 3: Update core Person nodes with new canonical IDs ---

// Adge
MATCH (p:Person {canonical_id: "person-adriaan"})
SET p.uid = "RX-PP-001",
    p.canonical_id = "PP-DENKERS-AdriaanHarold-1977",
    p.birth_name = "Adriaan Harold Denkers",
    p.tier = "soul_family",
    p.domain = "people",
    p.scope = "personal",
    p.origin = "manual",
    p.sun_sign = "Sagittarius",
    p.updated_at = datetime();

// Rebecca
MATCH (p:Person {canonical_id: "person-rebecca"})
SET p.uid = "RX-PP-002",
    p.canonical_id = "PP-RYAN-Rebecca-1978",
    p.birth_name = "Rebecca Lydia Ryan",
    p.married_name = "Rebecca Lydia Denkers",
    p.tier = "soul_family",
    p.domain = "people",
    p.scope = "personal",
    p.origin = "manual",
    p.sun_sign = "Leo",
    p.moon_sign = "Aries",
    p.rising_sign = "Sagittarius",
    p.updated_at = datetime();

// Fitz
MATCH (p:Person {canonical_id: "person-fitz"})
SET p.uid = "RX-PP-003",
    p.canonical_id = "PP-DENKERS-AdriaanFitzgerald-2020",
    p.birth_name = "Adriaan Fitzgerald Denkers",
    p.tier = "soul_family",
    p.domain = "people",
    p.scope = "personal",
    p.origin = "manual",
    p.sun_sign = "Virgo",
    p.updated_at = datetime();

// Dennis
MATCH (p:Person {canonical_id: "person-dennis"})
SET p.uid = "RX-PP-004",
    p.canonical_id = "PP-RYAN-Dennis-1952",
    p.birth_name = "Dennis Edward Ryan",
    p.tier = "family",
    p.domain = "people",
    p.scope = "personal",
    p.origin = "manual",
    p.sun_sign = "Leo",
    p.updated_at = datetime();

// Jennie (has canonical_id person-jennie)
MATCH (p:Person {canonical_id: "person-jennie"})
SET p.uid = "RX-PP-005",
    p.canonical_id = "PP-MOFFETT-Jennie-1950",
    p.birth_name = "Jennie Joy Moffett",
    p.tier = "family",
    p.domain = "people",
    p.scope = "personal",
    p.origin = "manual",
    p.updated_at = datetime();

// --- PHASE 4: Update Soul nodes with new canonical IDs ---

// Ka'tuar'el
MATCH (s:Soul {canonical_id: "soul-kataurel"})
SET s.uid = "RX-PS-001",
    s.canonical_id = "PS-Katuarel",
    s.person_id = "PP-DENKERS-AdriaanHarold-1977",
    s.domain = "people",
    s.scope = "shared",
    s.origin = "manual",
    s.updated_at = datetime();

// Seraphe Valemira
MATCH (s:Soul {canonical_id: "soul-seraphe"})
SET s.uid = "RX-PS-002",
    s.canonical_id = "PS-SerapheValemira",
    s.person_id = "PP-RYAN-Rebecca-1978",
    s.domain = "people",
    s.scope = "shared",
    s.origin = "manual",
    s.updated_at = datetime();

// Create Fitz's Soul node
MERGE (s:Soul {canonical_id: "PS-Fitz"})
SET s.uid = "RX-PS-003",
    s.full_name = "Fitz",
    s.display_name = "Fitz",
    s.person_id = "PP-DENKERS-AdriaanFitzgerald-2020",
    s.primary_role = "To be revealed",
    s.description = "Soul identity pending — the path will unfold.",
    s.domain = "people",
    s.scope = "shared",
    s.origin = "manual",
    s.created_at = datetime(),
    s.updated_at = datetime();

// --- PHASE 5: Link Owner nodes to Person nodes ---

MATCH (po:PersonOwner {canonical_id: "PO-DENKERS-AdriaanHarold-1977"})
MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanHarold-1977"})
MERGE (po)-[:IDENTITY_OF]->(pp);

MATCH (po:PersonOwner {canonical_id: "PO-RYAN-Rebecca-1978"})
MATCH (pp:Person {canonical_id: "PP-RYAN-Rebecca-1978"})
MERGE (po)-[:IDENTITY_OF]->(pp);

MATCH (po:PersonOwner {canonical_id: "PO-DENKERS-AdriaanFitzgerald-2020"})
MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanFitzgerald-2020"})
MERGE (po)-[:IDENTITY_OF]->(pp);

// --- PHASE 6: Link Person nodes to Soul nodes ---

MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanHarold-1977"})
MATCH (s:Soul {canonical_id: "PS-Katuarel"})
MERGE (pp)-[:HAS_SOUL]->(s);

MATCH (pp:Person {canonical_id: "PP-RYAN-Rebecca-1978"})
MATCH (s:Soul {canonical_id: "PS-SerapheValemira"})
MERGE (pp)-[:HAS_SOUL]->(s);

MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanFitzgerald-2020"})
MATCH (s:Soul {canonical_id: "PS-Fitz"})
MERGE (pp)-[:HAS_SOUL]->(s);

// --- PHASE 7: Update Entity mentions with canonical IDs and link to Persons ---

// Ka'tuar'el entity mentions -> Adge
MATCH (e:Entity {name: "Ka'tuar'el"})
WHERE NOT e:PersonOwner
SET e.canonical_id = "PE-Katuarel",
    e.person_id = "PP-DENKERS-AdriaanHarold-1977",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid"
WITH e
MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanHarold-1977"})
MERGE (e)-[:REFERS_TO]->(pp);

// Rebecca entity -> Seraphe
MATCH (e:Entity {name: "Rebecca"})
SET e.canonical_id = "PE-Rebecca",
    e.person_id = "PP-RYAN-Rebecca-1978",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid"
WITH e
MATCH (pp:Person {canonical_id: "PP-RYAN-Rebecca-1978"})
MERGE (e)-[:REFERS_TO]->(pp);

// Rebecca Lydia Ryan entity -> Seraphe
MATCH (e:Entity {name: "Rebecca Lydia Ryan"})
SET e.canonical_id = "PE-RebeccaLydiaRyan",
    e.person_id = "PP-RYAN-Rebecca-1978",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid"
WITH e
MATCH (pp:Person {canonical_id: "PP-RYAN-Rebecca-1978"})
MERGE (e)-[:REFERS_TO]->(pp);

// Fitz entity -> Fitz
MATCH (e:Entity {name: "Fitz"})
SET e.canonical_id = "PE-Fitz",
    e.person_id = "PP-DENKERS-AdriaanFitzgerald-2020",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid"
WITH e
MATCH (pp:Person {canonical_id: "PP-DENKERS-AdriaanFitzgerald-2020"})
MERGE (e)-[:REFERS_TO]->(pp);

// Iris entity - system, not a person
MATCH (e:Entity {name: "Iris"})
REMOVE e:Person
SET e.canonical_id = "PE-Iris",
    e.entity_type = "system",
    e.domain = "people",
    e.scope = "system",
    e.origin = "manual";

// The Arcturian Council - spirit entity
MATCH (e:Entity {name: "The Arcturian Council"})
REMOVE e:Person
SET e.canonical_id = "PE-ArcturianCouncil",
    e.entity_type = "spirit",
    e.domain = "people",
    e.scope = "shared",
    e.origin = "grid";

// Grandmother - person mention, unresolved
MATCH (e:Entity {name: "Grandmother"})
REMOVE e:Person
SET e.canonical_id = "PE-Grandmother",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid";

// Dr. Nolan
MATCH (e:Entity {name: "Dr. Nolan"})
REMOVE e:Person
SET e.canonical_id = "PE-DrNolan",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid";

// Wansor Moses Chiro
MATCH (e:Entity {name: "Wansor Moses Chiro"})
REMOVE e:Person
SET e.canonical_id = "PE-WansorMosesChiro",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid";

// Gregory Alan Isakov
MATCH (e:Entity {name: "Gregory Alan Isakov"})
REMOVE e:Person
SET e.canonical_id = "PE-GregoryAlanIsakov",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "public",
    e.origin = "grid";

// Brandi Carlile
MATCH (e:Entity {name: "Brandi Carlile"})
REMOVE e:Person
SET e.canonical_id = "PE-BrandiCarlile",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "shared",
    e.origin = "manual";

// Madeline
MATCH (e:Entity {name: "Madeline"})
REMOVE e:Person
SET e.canonical_id = "PE-Madeline",
    e.entity_type = "person_mention",
    e.domain = "people",
    e.scope = "personal",
    e.origin = "grid";

// --- PHASE 8: Clean up Soul:Person combo nodes ---
// These need to become proper Soul nodes only (Person data lives on PP nodes)

// Harry Styles - Soul:Person -> just Soul
MATCH (n:Soul:Person {name: "Harry Styles"})
REMOVE n:Person
SET n.canonical_id = "PS-HarryStyles",
    n.domain = "people",
    n.scope = "public",
    n.origin = "manual",
    n.updated_at = datetime();

// Seraphe Valemira Soul:Person -> remove Person label (real Soul node is soul-seraphe)
// This is a duplicate of the soul-seraphe node, merge data then delete
MATCH (dup:Soul:Person {name: "Seraphe Valemira"})
MATCH (real:Soul {canonical_id: "PS-SerapheValemira"})
WHERE dup <> real
SET real.also_known_as = dup.also_known_as,
    real.birth_timezone = dup.birth_timezone,
    real.spiritual_name = dup.spiritual_name,
    real.spiritual_titles = dup.spiritual_titles,
    real.spiritual_roles = dup.spiritual_roles,
    real.lineage_claims = dup.lineage_claims,
    real.telegram_id = dup.telegram_id,
    real.birth_time = dup.birth_time
WITH dup
DETACH DELETE dup;

// Brandi Carlile Soul:Person -> just Soul
MATCH (n:Soul:Person {name: "Brandi Carlile"})
REMOVE n:Person
SET n.canonical_id = "PS-BrandiCarlile",
    n.domain = "people",
    n.scope = "shared",
    n.origin = "manual",
    n.updated_at = datetime();

// Riley Green Soul:Person -> just Soul
MATCH (n:Soul:Person {name: "Riley Green"})
REMOVE n:Person
SET n.canonical_id = "PS-RileyGreen",
    n.domain = "people",
    n.scope = "shared",
    n.origin = "manual",
    n.updated_at = datetime();
