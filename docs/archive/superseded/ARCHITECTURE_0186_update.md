# Conversation Metadata System — Architecture Notes

## Plain English Summary

Every conversation you have with any LLM gets normalized into one Python object, stored in one Postgres table (with raw logs included), and mirrored as lightweight nodes in Neo4j for relationship traversal. Spiritual concepts get their own Neo4j label so you can trace lineage threads, concept evolution, and cross-session patterns without digging through generic entity buckets.

---

## Storage Responsibilities (No Duplication)

| What | Postgres | Neo4j |
|------|----------|-------|
| Raw conversation logs | ✅ `raw_payload` JSONB column | ❌ Never |
| Summaries, decisions, actions | ✅ Searchable via FTS | ❌ Never |
| Structured turns | ✅ `conversation_turns` table | ❌ Never |
| Participant list | ✅ `conversation_participants` table | Only as relationship edges |
| Entity name cache | ✅ `entities` JSONB (for FTS) | ❌ Names on nodes, but no content |
| Conversation-to-conversation edges | ✅ `edges` JSONB (hint/cache) | ✅ Canonical (CONTINUES, BUILDS_ON, etc.) |
| Spiritual concept relationships | ❌ | ✅ INVOKES, RELATED_TO, ORIGINATES_FROM, HOLDS, CARRIES |
| Thread groups | ✅ `thread_groups` table + FK | ✅ (:ThreadGroup) node + BELONGS_TO |
| Full-text search | ✅ `search_doc` tsvector | ❌ |

### The one intentional "overlap"

`edges` exists in both stores. Postgres has a JSONB hint column so you can see connections without hitting Neo4j for simple queries. Neo4j is canonical — if they ever disagree, Neo4j wins. The Postgres column is a read cache, not a source of truth.

### Raw payload vs. turns: not duplication

`raw_payload` is the **verbatim archive** — the exact JSON export from Claude, the Ollama chat dump, the pasted text. Never modified after ingest. `conversation_turns` is the **structured, indexed, queryable** version. Same underlying data, completely different access patterns. This is like keeping both the original receipt and the ledger entry — you need both.

---

## Spiritual Concepts as First-Class Nodes

Why `:SpiritualConcept` gets its own Neo4j label instead of being a generic `:Entity`:

1. **Domain-specific traversals**: "Show me every conversation that invokes the Arcturian Grid" is a one-hop query, not a filtered generic entity scan.
2. **Concept-to-concept relationships**: `(:SpiritualConcept)-[:RELATED_TO]->(:SpiritualConcept)` and `[:ORIGINATES_FROM]` let you map lineage trees, cosmological hierarchies, and practice dependencies.
3. **Person-to-concept edges**: `(Person)-[:HOLDS]->(SpiritualConcept)` (titles, roles) vs. `(Person)-[:CARRIES]->(SpiritualConcept)` (bloodlines, codes) captures the distinction between acquired and inherited spiritual attributes.
4. **Domain categorization**: Each concept has a `domain` field (lineage, entity, practice, cosmology, order, incarnation, frequency, grid) for filtering without extra labels.

---

## Ingest Pipeline (How Data Flows)

```
Raw Input (Claude JSON, Ollama dump, paste, Telegram)
    │
    ▼
Normalize → ConversationRecord (Pydantic)
    │
    ▼
Compute content_hash (SHA-256 of canonical fields)
    │
    ├──▶ Postgres: UPSERT by (source_provider, session_id, started_at)
    │       - If content_hash matches existing → skip
    │       - If content_hash differs → increment revision, update
    │       - Insert turns into conversation_turns
    │       - Insert participants into conversation_participants
    │
    └──▶ Neo4j: MERGE by conversation_id
            - Set minimal fields (started_at, type, source_model, revision)
            - MERGE entity nodes + relationship edges
            - MERGE spiritual concept nodes + INVOKES edges
            - MERGE conversation-to-conversation edges
```

---

## Key Queries This Enables

### Postgres
- "All conversations where I decided X" → FTS on `search_doc` or JSONB search on `key_decisions`
- "All channeling sessions this month" → `WHERE conversation_type = 'channeling' AND started_at > ...`
- "Everything tagged 'mythos'" → `WHERE topic_tags @> ARRAY['mythos']`
- "Raw log for session ABC" → `SELECT raw_payload WHERE session_id = 'ABC'`

### Neo4j
- "Trace Cathar lineage across all sessions" → `MATCH (sc:SpiritualConcept {name: "Cathar lineage"})<-[:INVOKES]-(c) RETURN c ORDER BY c.started_at`
- "What spiritual concepts does Seraphe carry?" → `MATCH (p:Person {name: "Seraphe"})-[:CARRIES]->(sc) RETURN sc`
- "Show me the build chain for the finance module" → `MATCH path = (c)-[:BUILDS_ON|CONTINUES*]->(chain) WHERE ...`
- "All conversations in the 'Mythos patch system' thread group" → `MATCH (tg:ThreadGroup {name: ...})<-[:BELONGS_TO]-(c) RETURN c`

---

## File Manifest

| File | Purpose |
|------|---------|
| `schema.sql` | Complete Postgres DDL — tables (incl. spiral_epochs), indexes, FTS trigger, views |
| `neo4j_schema.cypher` | Neo4j constraints, indexes, Epoch nodes, and canonical MERGE patterns |
| `models.py` | Pydantic v2 model — canonical object + spiral time computation |
| `SPIRAL_TIME.md` | Nested cycle architecture — the full base-9 temporal system design |
| `ARCHITECTURE.md` | This file — design rationale and no-duplication accounting |

---

## Spiral Time Integration

Spiral time is a nested cycle system inspired by Maya calendar architecture, rebuilt in base-9 to align with the Arcturian Grid. See `SPIRAL_TIME.md` for the full design.

**How it connects to conversations:**
- Each conversation gets a `spiral_context` JSONB field computed at ingest
- The context includes the person's active epoch, days since epoch, and full spiral signature
- Signature = position across Pulse (9d), Weave (81d), Arc (729d), and Long Spiral (6561d)
- Epochs are personal, sovereign, and resettable — stored in `spiral_epochs` table and as `(:Epoch)` nodes in Neo4j

**What this enables:**
- "Show me all conversations from Day 7 across any epoch"
- "What happened during Weave cycle 3?"
- "Which Node 5 days produced the most decisions?"
- Cross-person resonance window detection (where personal spirals align)
