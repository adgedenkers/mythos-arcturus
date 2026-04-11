// ============================================================================
// Mythos Conversation Metadata — Neo4j Graph Schema
// ============================================================================
// Design principles:
//   1. Neo4j stores ONLY IDs + relationships — no raw content, no summaries
//      Postgres is the system of record for all data storage.
//   2. SpiritualConcept is a first-class node label (not lumped under Entity)
//   3. conversation_id (UUID) is the glue between Postgres and Neo4j
//   4. All upserts use MERGE to stay idempotent
// ============================================================================


// ── Constraints (uniqueness + existence) ────────────────────────────────────

CREATE CONSTRAINT conversation_id_unique IF NOT EXISTS
FOR (c:Conversation) REQUIRE c.conversation_id IS UNIQUE;

CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

CREATE CONSTRAINT system_id_unique IF NOT EXISTS
FOR (s:System) REQUIRE s.system_id IS UNIQUE;

CREATE CONSTRAINT topic_id_unique IF NOT EXISTS
FOR (t:Topic) REQUIRE t.topic_id IS UNIQUE;

CREATE CONSTRAINT spiritual_concept_id_unique IF NOT EXISTS
FOR (sc:SpiritualConcept) REQUIRE sc.concept_id IS UNIQUE;

CREATE CONSTRAINT thread_group_id_unique IF NOT EXISTS
FOR (tg:ThreadGroup) REQUIRE tg.thread_group_id IS UNIQUE;

CREATE CONSTRAINT epoch_id_unique IF NOT EXISTS
FOR (ep:Epoch) REQUIRE ep.epoch_id IS UNIQUE;


// ── Indexes ─────────────────────────────────────────────────────────────────

CREATE INDEX conversation_started_at IF NOT EXISTS
FOR (c:Conversation) ON (c.started_at);

CREATE INDEX conversation_type IF NOT EXISTS
FOR (c:Conversation) ON (c.type);

CREATE INDEX topic_name IF NOT EXISTS
FOR (t:Topic) ON (t.name);

CREATE INDEX spiritual_concept_name IF NOT EXISTS
FOR (sc:SpiritualConcept) ON (sc.name);

CREATE INDEX person_name IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX system_name IF NOT EXISTS
FOR (s:System) ON (s.name);


// ============================================================================
// NODE TYPES
// ============================================================================
//
// (:Conversation)       — minimal: conversation_id, started_at, type, source_model, revision
// (:Person)             — person_id, name
// (:System)             — system_id, name  (e.g. "Mythos", "Arcturus", "Neo4j")
// (:Topic)              — topic_id, name   (e.g. "finance module", "patch deployment")
// (:SpiritualConcept)   — concept_id, name, domain
//                          domain examples: "lineage", "entity", "practice", "cosmology",
//                          "order", "incarnation", "frequency", "grid"
// (:ThreadGroup)        — thread_group_id, name
// (:Epoch)              — epoch_id, person_id, epoch_number, started_at, ended_at, reason
//                          Personal time anchors. A person can have multiple (strata).
//                          Only one active per person (ended_at IS NULL).
//
// ============================================================================


// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================
//
// Conversation → Entity relationships:
//   (c:Conversation)-[:INVOLVES]->(p:Person)
//   (c:Conversation)-[:MENTIONS]->(t:Topic)
//   (c:Conversation)-[:USES]->(s:System)
//   (c:Conversation)-[:INVOKES]->(sc:SpiritualConcept)
//   (c:Conversation)-[:BELONGS_TO]->(tg:ThreadGroup)
//
// Conversation → Conversation relationships:
//   (c1)-[:CONTINUES]->(c2)      — direct continuation of a session
//   (c1)-[:BUILDS_ON]->(c2)      — extends ideas/decisions from c2
//   (c1)-[:REFERENCES]->(c2)     — mentions or cites c2
//   (c1)-[:CONTRADICTS]->(c2)    — reverses or conflicts with c2
//
// Person → Epoch relationships:
//   (p:Person)-[:HAS_EPOCH]->(ep:Epoch)  — a person's spiral time anchors
//   Epochs are ordered by epoch_number. Only the one with ended_at IS NULL is active.
//
// Conversation → Epoch relationships:
//   (c:Conversation)-[:WITHIN_EPOCH]->(ep:Epoch)  — which epoch was active when this conversation happened
//
// SpiritualConcept relationships (the real value of having its own label):
//   (sc1:SpiritualConcept)-[:RELATED_TO]->(sc2:SpiritualConcept)
//   (sc:SpiritualConcept)-[:ORIGINATES_FROM]->(lineage:SpiritualConcept)
//   (p:Person)-[:HOLDS]->(sc:SpiritualConcept)       — e.g. Ka'tuar'el HOLDS "Thronescribe"
//   (p:Person)-[:CARRIES]->(sc:SpiritualConcept)      — e.g. Seraphe CARRIES "Merovingian bloodline"
//
// ============================================================================


// ============================================================================
// CANONICAL MERGE PATTERNS (for ingest pipeline)
// ============================================================================

// ── Upsert a conversation ───────────────────────────────────────────────────
// Only stores IDs and minimal metadata — no content, no summaries.
// Postgres owns all that.

// MERGE (c:Conversation {conversation_id: $conversation_id})
// SET c.started_at    = datetime($started_at),
//     c.ended_at      = CASE WHEN $ended_at IS NOT NULL THEN datetime($ended_at) ELSE c.ended_at END,
//     c.type          = $conversation_type,
//     c.source_model  = $source_model,
//     c.revision      = $revision;


// ── Link to ThreadGroup ─────────────────────────────────────────────────────

// MERGE (tg:ThreadGroup {thread_group_id: $thread_group_id})
// SET tg.name = coalesce($thread_group_name, tg.name)
// WITH tg
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MERGE (c)-[:BELONGS_TO]->(tg);


// ── Link people ─────────────────────────────────────────────────────────────

// UNWIND $people AS person
// MERGE (p:Person {person_id: person.person_id})
// SET p.name = coalesce(person.name, p.name)
// WITH p
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MERGE (c)-[:INVOLVES]->(p);


// ── Link systems ────────────────────────────────────────────────────────────

// UNWIND $systems AS sys
// MERGE (s:System {system_id: sys.system_id})
// SET s.name = coalesce(sys.name, s.name)
// WITH s
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MERGE (c)-[:USES]->(s);


// ── Link topics ─────────────────────────────────────────────────────────────

// UNWIND $topics AS top
// MERGE (t:Topic {topic_id: top.topic_id})
// SET t.name = coalesce(top.name, t.name)
// WITH t
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MERGE (c)-[:MENTIONS]->(t);


// ── Link spiritual concepts (first-class!) ──────────────────────────────────

// UNWIND $spiritual_concepts AS sc
// MERGE (concept:SpiritualConcept {concept_id: sc.concept_id})
// SET concept.name   = coalesce(sc.name, concept.name),
//     concept.domain = coalesce(sc.domain, concept.domain)
// WITH concept
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MERGE (c)-[:INVOKES]->(concept);


// ── Conversation-to-conversation edges ──────────────────────────────────────
// Uses APOC or subqueries per edge type to avoid Cartesian issues.

// UNWIND $edges AS e
// MATCH (c:Conversation {conversation_id: $conversation_id})
// MATCH (c2:Conversation {conversation_id: e.to_conversation_id})
// CALL {
//   WITH c, c2, e
//   WITH c, c2, e WHERE e.type = 'CONTINUES'
//   MERGE (c)-[:CONTINUES]->(c2)
//   RETURN 0
// }
// CALL {
//   WITH c, c2, e
//   WITH c, c2, e WHERE e.type = 'BUILDS_ON'
//   MERGE (c)-[:BUILDS_ON]->(c2)
//   RETURN 0
// }
// CALL {
//   WITH c, c2, e
//   WITH c, c2, e WHERE e.type = 'CONTRADICTS'
//   MERGE (c)-[:CONTRADICTS]->(c2)
//   RETURN 0
// }
// CALL {
//   WITH c, c2, e
//   WITH c, c2, e WHERE e.type = 'REFERENCES'
//   MERGE (c)-[:REFERENCES]->(c2)
//   RETURN 0
// };


// ============================================================================
// EXAMPLE QUERIES
// ============================================================================

// ── All conversations invoking a spiritual concept ──────────────────────────
// MATCH (sc:SpiritualConcept {name: "Arcturian Grid"})<-[:INVOKES]-(c:Conversation)
// RETURN c.conversation_id, c.started_at, c.type, c.source_model
// ORDER BY c.started_at ASC;

// ── Trace concept evolution across sessions ─────────────────────────────────
// MATCH (sc:SpiritualConcept {name: "Cathar lineage"})<-[:INVOKES]-(c:Conversation)
// OPTIONAL MATCH (c)-[r:BUILDS_ON|CONTINUES*0..10]->(chain)
// RETURN c, chain, r
// ORDER BY c.started_at ASC;

// ── All spiritual concepts discussed alongside a person ─────────────────────
// MATCH (p:Person {name: "Seraphe"})<-[:INVOLVES]-(c:Conversation)-[:INVOKES]->(sc:SpiritualConcept)
// RETURN sc.name, sc.domain, count(c) AS times_discussed
// ORDER BY times_discussed DESC;

// ── Thread group traversal ──────────────────────────────────────────────────
// MATCH (tg:ThreadGroup {name: "Finance module buildout"})<-[:BELONGS_TO]-(c:Conversation)
// RETURN c.conversation_id, c.started_at, c.type
// ORDER BY c.started_at ASC;

// ── Spiritual concept network (what connects to what) ───────────────────────
// MATCH (sc:SpiritualConcept)-[r:RELATED_TO|ORIGINATES_FROM]-(sc2:SpiritualConcept)
// RETURN sc.name, type(r), sc2.name;
