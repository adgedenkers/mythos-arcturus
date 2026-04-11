// ============================================================
// Mythos Design Patterns: Neo4j Reference Schemas
// Version: 1.0
// Purpose: Copy-paste ready Cypher for all Neo4j patterns
// Usage: Use as reference when building new features.
//        Do NOT run this wholesale — pick the pattern you need.
// ============================================================


// ============================================================
// P1: ONTOLOGY NODES — Constraints & Indexes
// ============================================================

// Unique constraints on canonical_id for all core types
CREATE CONSTRAINT person_canonical_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.canonical_id IS UNIQUE;

CREATE CONSTRAINT soul_canonical_id IF NOT EXISTS
FOR (s:Soul) REQUIRE s.canonical_id IS UNIQUE;

CREATE CONSTRAINT event_canonical_id IF NOT EXISTS
FOR (e:Event) REQUIRE e.canonical_id IS UNIQUE;

CREATE CONSTRAINT lineage_canonical_id IF NOT EXISTS
FOR (l:Lineage) REQUIRE l.canonical_id IS UNIQUE;

CREATE CONSTRAINT organization_canonical_id IF NOT EXISTS
FOR (o:Organization) REQUIRE o.canonical_id IS UNIQUE;

CREATE CONSTRAINT location_canonical_id IF NOT EXISTS
FOR (loc:Location) REQUIRE loc.canonical_id IS UNIQUE;

CREATE CONSTRAINT conversation_canonical_id IF NOT EXISTS
FOR (c:Conversation) REQUIRE c.canonical_id IS UNIQUE;

// Text indexes for name lookups
CREATE TEXT INDEX person_name_formal IF NOT EXISTS
FOR (p:Person) ON (p.name_formal);

CREATE TEXT INDEX person_name_casual IF NOT EXISTS
FOR (p:Person) ON (p.name_casual);

CREATE TEXT INDEX person_name_spiritual IF NOT EXISTS
FOR (p:Person) ON (p.name_spiritual);


// ============================================================
// P1: ONTOLOGY NODE TEMPLATES
// ============================================================

// --- Person ---
// CREATE (p:Person {
//   canonical_id: randomUUID(),
//   name_formal: '',
//   name_casual: '',
//   name_spiritual: '',
//   date_of_birth: date('YYYY-MM-DD'),
//   place_of_birth: '',
//   created_at: datetime(),
//   updated_at: datetime(),
//   created_by: '',
//   source: ''        // manual | import | channeled | inferred
// })

// --- Soul ---
// CREATE (s:Soul {
//   canonical_id: randomUUID(),
//   name: '',
//   soul_type: '',     // human | angelic | elemental | cosmic
//   origin: '',
//   notes: '',
//   created_at: datetime(),
//   source: ''
// })

// --- Event ---
// CREATE (e:Event {
//   canonical_id: randomUUID(),
//   name: '',
//   event_type: '',    // historical | spiritual | personal | cosmic
//   date_start: date('YYYY-MM-DD'),
//   date_end: date('YYYY-MM-DD'),
//   location: '',
//   description: '',
//   created_at: datetime(),
//   source: ''
// })

// --- Lineage ---
// CREATE (l:Lineage {
//   canonical_id: randomUUID(),
//   name: '',
//   lineage_type: '',  // blood | spiritual | code
//   origin_era: '',
//   description: '',
//   created_at: datetime(),
//   source: ''
// })

// --- Organization ---
// CREATE (o:Organization {
//   canonical_id: randomUUID(),
//   name: '',
//   org_type: '',      // order | brotherhood | council | institution
//   founded_era: '',
//   purpose: '',
//   active: true,
//   created_at: datetime(),
//   source: ''
// })

// --- Location ---
// CREATE (loc:Location {
//   canonical_id: randomUUID(),
//   name: '',
//   location_type: '', // city | site | sacred_site | region | country
//   latitude: 0.0,
//   longitude: 0.0,
//   significance: '',
//   created_at: datetime(),
//   source: ''
// })


// ============================================================
// P2: RELATIONSHIP TYPES — Standard Vocabulary
// ============================================================

// Family
// (parent)-[:PARENT_OF {biological: BOOL, source: ''}]->(child)
// (a)-[:SIBLING_OF {source: ''}]->(b)
// (a)-[:PARTNER_OF {since: date(), source: ''}]->(b)

// Spiritual
// (person)-[:INCARNATION_OF {incarnation_order: INT, era: '', location: '', source: ''}]->(soul)
// (person)-[:CARRIES_LINEAGE {lineage_type: '', activation_status: '', confirmed_by: '', source: ''}]->(lineage)
// (a)-[:ACTIVATED_BY {date: date(), source: ''}]->(b)

// Protection
// (guardian)-[:PROTECTS {protection_type: '', active: BOOL, since: datetime(), source: ''}]->(person)
// (guardian)-[:GUARDS {scope: '', source: ''}]->(thing)
// (anchor)-[:ANCHORS {field_type: '', source: ''}]->(field)

// Organizational
// (person)-[:MEMBER_OF {role: '', since: date(), source: ''}]->(org)
// (person)-[:FOUNDED {date: date(), source: ''}]->(org)
// (person)-[:LEADS {title: '', source: ''}]->(org)

// Temporal / Witness
// (person)-[:WITNESSED {date: date(), role: '', source: ''}]->(event)
// (person)-[:PARTICIPATED_IN {role: '', source: ''}]->(event)
// (event)-[:OCCURRED_AT {source: ''}]->(location)

// Infrastructure
// (agent)-[:CREATED {date: datetime(), tool: '', source: ''}]->(thing)
// (agent)-[:MODIFIED {date: datetime(), description: '', source: ''}]->(thing)


// ============================================================
// P3: SCHEMA-AWARE NODES
// ============================================================

// Person schema
MERGE (s:Schema {node_type: 'Person'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name_formal', 'created_at', 'source'],
    s.optional_properties = ['name_casual', 'name_spiritual', 'date_of_birth', 
                             'place_of_birth', 'lineage_codes', 'notes'],
    s.property_types = '{"canonical_id":"UUID","name_formal":"STRING","name_casual":"STRING","name_spiritual":"STRING","date_of_birth":"DATE","place_of_birth":"STRING","lineage_codes":"STRING[]","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = ['PARENT_OF', 'CARRIES_LINEAGE', 'MEMBER_OF', 'INCARNATION_OF', 
                        'WITNESSED', 'PARTNER_OF', 'FOUNDED', 'LEADS', 'PARTICIPATED_IN'],
    s.valid_incoming = ['CHILD_OF', 'PROTECTS', 'GUARDS', 'ACTIVATED_BY', 'PARENT_OF'],
    s.example_queries = [
      'MATCH (p:Person) WHERE p.name_casual = $name RETURN p',
      'MATCH (p:Person)-[:PARENT_OF]->(c) RETURN p.name_formal, collect(c.name_formal)',
      'MATCH (p:Person {canonical_id: $uuid})-[r]-(n) RETURN type(r), properties(n)'
    ],
    s.updated_at = datetime();

// Soul schema
MERGE (s:Schema {node_type: 'Soul'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name', 'created_at', 'source'],
    s.optional_properties = ['soul_type', 'origin', 'notes'],
    s.property_types = '{"canonical_id":"UUID","name":"STRING","soul_type":"STRING","origin":"STRING","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = ['CARRIES_LINEAGE'],
    s.valid_incoming = ['INCARNATION_OF'],
    s.example_queries = [
      'MATCH (s:Soul)<-[:INCARNATION_OF]-(p:Person) RETURN s.name, collect(p.name_formal)'
    ],
    s.updated_at = datetime();

// Event schema
MERGE (s:Schema {node_type: 'Event'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name', 'event_type', 'created_at', 'source'],
    s.optional_properties = ['date_start', 'date_end', 'location', 'description'],
    s.property_types = '{"canonical_id":"UUID","name":"STRING","event_type":"STRING","date_start":"DATE","date_end":"DATE","location":"STRING","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = ['OCCURRED_AT'],
    s.valid_incoming = ['WITNESSED', 'PARTICIPATED_IN'],
    s.example_queries = [
      'MATCH (p:Person)-[:WITNESSED]->(e:Event) WHERE e.name CONTAINS $term RETURN p, e'
    ],
    s.updated_at = datetime();

// Lineage schema
MERGE (s:Schema {node_type: 'Lineage'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name', 'lineage_type', 'created_at', 'source'],
    s.optional_properties = ['origin_era', 'description'],
    s.property_types = '{"canonical_id":"UUID","name":"STRING","lineage_type":"STRING","origin_era":"STRING","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = [],
    s.valid_incoming = ['CARRIES_LINEAGE'],
    s.example_queries = [
      'MATCH (p)-[:CARRIES_LINEAGE]->(l:Lineage) WHERE l.name = $name RETURN p.name_formal'
    ],
    s.updated_at = datetime();

// Organization schema
MERGE (s:Schema {node_type: 'Organization'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name', 'org_type', 'created_at', 'source'],
    s.optional_properties = ['founded_era', 'purpose', 'active'],
    s.property_types = '{"canonical_id":"UUID","name":"STRING","org_type":"STRING","founded_era":"STRING","purpose":"STRING","active":"BOOLEAN","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = [],
    s.valid_incoming = ['MEMBER_OF', 'FOUNDED', 'LEADS'],
    s.example_queries = [
      'MATCH (p:Person)-[:MEMBER_OF]->(o:Organization) WHERE o.name = $name RETURN p'
    ],
    s.updated_at = datetime();

// Location schema
MERGE (s:Schema {node_type: 'Location'})
SET s.version = '1.0',
    s.required_properties = ['canonical_id', 'name', 'created_at', 'source'],
    s.optional_properties = ['location_type', 'latitude', 'longitude', 'significance'],
    s.property_types = '{"canonical_id":"UUID","name":"STRING","location_type":"STRING","latitude":"FLOAT","longitude":"FLOAT","significance":"STRING","created_at":"DATETIME","source":"STRING"}',
    s.valid_outgoing = [],
    s.valid_incoming = ['OCCURRED_AT'],
    s.example_queries = [
      'MATCH (e:Event)-[:OCCURRED_AT]->(l:Location) WHERE l.name CONTAINS $place RETURN e, l'
    ],
    s.updated_at = datetime();


// ============================================================
// INTROSPECTION QUERIES (for LLM context loading)
// ============================================================

// Get full schema map (run at start of any session)
// MATCH (s:Schema)
// RETURN s.node_type AS type,
//        s.required_properties AS required,
//        s.optional_properties AS optional,
//        s.valid_outgoing AS outgoing_rels,
//        s.valid_incoming AS incoming_rels,
//        s.example_queries AS examples
// ORDER BY s.node_type

// Get relationship inventory (what actually exists)
// MATCH ()-[r]->()
// RETURN type(r) AS rel_type, count(r) AS count
// ORDER BY count DESC

// Get node inventory (what actually exists)
// MATCH (n)
// RETURN labels(n) AS type, count(n) AS count
// ORDER BY count DESC
