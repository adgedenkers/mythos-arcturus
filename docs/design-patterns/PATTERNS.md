---
title: "Mythos Design Patterns"
category: design-patterns
status: active
stream: null
location: docs
tags: [design, patterns, ontology, database]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Mythos Design Patterns Library

**Version:** 1.0  
**Purpose:** Reference patterns for Iris and any LLM working with Mythos infrastructure.  
**Usage:** When building a new feature, check this library first. Pick the pattern that fits, adapt as needed.

---

## How to Use This Library

Each pattern includes:

1. **When to use it** — what problem it solves
2. **Schema** — the actual SQL or Cypher (copy-paste ready)
3. **Query examples** — common operations
4. **Integration notes** — how it connects to other Mythos subsystems
5. **Anti-patterns** — what NOT to do

Patterns are organized by storage layer:

| Section | Database | Use For |
|---------|----------|---------|
| [P1–P3](#neo4j-patterns) | Neo4j | Entities, relationships, ontology, lineage |
| [P4–P6](#postgresql-patterns) | PostgreSQL | Logs, transactions, time-series, structured records |
| [P7–P8](#cross-database-patterns) | Both | Patterns that bridge Neo4j ↔ PostgreSQL |

---

## Neo4j Patterns

### P1: Ontology Node (Entity Registry)

**When to use:** Storing any named entity that participates in relationships — people, souls, spiritual identities, places, events, organizations.

**Core principle:** Every entity gets a `canonical_id` (UUID) that is the same across Neo4j and PostgreSQL. This is the bridge.

```cypher
-- Base pattern: any entity node
CREATE (e:Person {
  canonical_id: randomUUID(),          -- Bridge key (same in Postgres)
  
  -- Display names (mode-dependent)
  name_formal: 'Rebecca Lydia Denkers',
  name_casual: 'Becky',
  name_spiritual: 'Seraphe Valemira',
  
  -- Core data
  date_of_birth: date('1982-07-15'),
  place_of_birth: 'Oneonta, NY',
  
  -- Metadata
  created_at: datetime(),
  updated_at: datetime(),
  created_by: 'ka_tuarel',             -- Who added this
  source: 'manual'                      -- manual | import | channeled | inferred
})
```

**Multi-label pattern:** Nodes can (and should) have multiple labels for different query contexts:

```cypher
-- A person who is also a soul carrier and lineage holder
CREATE (s:Person:SoulCarrier:LineageHolder {
  canonical_id: randomUUID(),
  name_formal: 'Rebecca Lydia Denkers',
  name_spiritual: 'Seraphe Valemira',
  lineage_codes: ['merovingian', 'magdalene'],
  created_at: datetime()
})
```

**Required properties for ALL ontology nodes:**
- `canonical_id` (STRING, UUID format)
- At least one name field
- `created_at` (DATETIME)
- `source` (STRING)

**Query examples:**

```cypher
-- Find by any name
MATCH (p:Person)
WHERE p.name_formal CONTAINS 'Denkers'
   OR p.name_casual = 'Becky'
   OR p.name_spiritual = 'Seraphe'
RETURN p

-- Find all entities with a canonical_id (cross-DB lookup)
MATCH (n {canonical_id: $uuid})
RETURN labels(n) AS types, properties(n) AS data

-- Count by label
MATCH (n)
RETURN labels(n) AS type, count(n) AS count
ORDER BY count DESC
```

**Anti-patterns:**
- ❌ Don't create nodes without `canonical_id` — you lose the Postgres bridge
- ❌ Don't use Neo4j-internal `id()` as a reference — it can change on restart
- ❌ Don't store large text blobs in Neo4j — put them in Postgres, reference by `canonical_id`

---

### P2: Relationship Web (Typed Edges)

**When to use:** Connecting entities. Relationships are first-class citizens in Neo4j — they carry properties and have direction.

**Core principle:** Relationships have types (verbs), properties (metadata), and direction. Use specific types, not generic ones.

```cypher
-- Family relationships
CREATE (parent)-[:PARENT_OF {
  biological: true,
  established_at: datetime(),
  source: 'genealogy_research'
}]->(child)

-- Spiritual relationships
CREATE (soul)-[:INCARNATION_OF {
  incarnation_order: 3,
  era: 'medieval',
  location: 'Montségur',
  date_range: '1200-1244',
  source: 'channeled'
}]->(spiritual_identity)

-- Lineage relationships
CREATE (person)-[:CARRIES_LINEAGE {
  lineage_type: 'blood',           -- blood | spiritual | code
  activation_status: 'active',
  confirmed_by: 'genealogy',       -- genealogy | channeling | dna
  source: 'research'
}]->(lineage)

-- Protection relationships
CREATE (guardian)-[:PROTECTS {
  protection_type: 'galactic',     -- galactic | elemental | ancestral | angelic
  active: true,
  since: datetime(),
  source: 'channeled'
}]->(person)
```

**Standard relationship types (use these, don't invent synonyms):**

| Category | Relationship | Direction |
|----------|-------------|-----------|
| Family | `PARENT_OF`, `CHILD_OF`, `SIBLING_OF`, `PARTNER_OF` | parent→child, etc. |
| Spiritual | `INCARNATION_OF`, `CARRIES_LINEAGE`, `ACTIVATED_BY` | carrier→source |
| Protection | `PROTECTS`, `GUARDS`, `ANCHORS` | protector→protected |
| Organizational | `MEMBER_OF`, `FOUNDED`, `LEADS` | person→org |
| Temporal | `WITNESSED`, `PARTICIPATED_IN`, `PRESENT_AT` | person→event |
| Infrastructure | `CREATED`, `MODIFIED`, `OWNS` | agent→thing |

**Query examples:**

```cypher
-- Full relationship map for a person (1 hop)
MATCH (p:Person {name_casual: 'Becky'})-[r]-(connected)
RETURN type(r) AS relationship, 
       properties(r) AS details,
       labels(connected) AS connected_type,
       connected.name_formal AS connected_name

-- Lineage chain (variable depth)
MATCH path = (p:Person {name_spiritual: 'Seraphe'})-[:CARRIES_LINEAGE*1..5]->(ancestor)
RETURN [n IN nodes(path) | n.name_formal] AS chain

-- All protectors of a person
MATCH (guardian)-[:PROTECTS]->(p:Person {canonical_id: $uuid})
RETURN guardian.name_formal, guardian.protection_type
```

**Anti-patterns:**
- ❌ Don't use generic `RELATED_TO` — always use specific typed relationships
- ❌ Don't store relationship data as node properties — that's what edges are for
- ❌ Don't create bidirectional duplicates — pick a direction convention and stick to it

---

### P3: Schema-Aware Node (Self-Describing Graph)

**When to use:** Making the graph introspectable so Iris (or any LLM) can discover what node types exist, what properties they have, and how to query them.

**Core principle:** The graph describes itself. Schema nodes define what's expected for each entity type.

```cypher
-- Schema definition node
CREATE (s:Schema {
  node_type: 'Person',
  version: '1.0',
  
  required_properties: ['canonical_id', 'name_formal', 'created_at', 'source'],
  optional_properties: ['name_casual', 'name_spiritual', 'date_of_birth', 
                        'place_of_birth', 'lineage_codes', 'notes'],
  
  -- Property type hints for LLM
  property_types: '{"canonical_id": "UUID", "name_formal": "STRING", 
                     "date_of_birth": "DATE", "lineage_codes": "STRING[]",
                     "created_at": "DATETIME"}',
  
  -- Valid relationships FROM this node type
  valid_outgoing: ['PARENT_OF', 'CARRIES_LINEAGE', 'MEMBER_OF', 
                   'INCARNATION_OF', 'WITNESSED', 'PARTNER_OF'],
  
  -- Valid relationships TO this node type  
  valid_incoming: ['CHILD_OF', 'PROTECTS', 'GUARDS', 'ACTIVATED_BY'],
  
  -- Mode-specific display rules
  mode_display: '{
    "conversation": {"show": ["name_casual", "age"], "format": "inline"},
    "genealogy": {"show": ["name_formal", "date_of_birth", "children"], "format": "hierarchical"},
    "lineage": {"show": ["name_spiritual", "lineage_codes", "protectors"], "format": "narrative"},
    "technical": {"show": ["*"], "format": "table"}
  }',
  
  -- Example queries for this node type
  example_queries: [
    'MATCH (p:Person) WHERE p.name_casual = $name RETURN p',
    'MATCH (p:Person)-[:PARENT_OF]->(c) RETURN p.name_formal, collect(c.name_formal)'
  ],
  
  updated_at: datetime()
})
```

**Schema introspection query (for LLM context loading):**

```cypher
-- Get full schema map (run at session start)
MATCH (s:Schema)
RETURN s.node_type AS type,
       s.required_properties AS required,
       s.optional_properties AS optional,
       s.valid_outgoing AS outgoing_rels,
       s.valid_incoming AS incoming_rels,
       s.example_queries AS examples
ORDER BY s.node_type
```

**Anti-patterns:**
- ❌ Don't skip Schema nodes — without them, every new LLM session starts blind
- ❌ Don't let Schema drift from actual data — update Schema when you add new properties
- ❌ Don't put mode display logic in application code — keep it in the graph where Iris can read it

---

## PostgreSQL Patterns

### P4: Conversation Log (Chat History)

**When to use:** Storing all chat messages, voice transcripts, and interaction logs. This is the backbone of Iris's memory.

**Core principle:** Messages are immutable append-only records. Summaries are derived. The raw log is sacred.

```sql
-- Extensions needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";        -- pgvector for embeddings

-- Conversations (container for message threads)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_uuid UUID NOT NULL,                    -- Who started this
    platform VARCHAR(50) NOT NULL,              -- telegram | web | api | voice
    mode VARCHAR(50) DEFAULT 'chat',            -- chat | genealogy | lineage | db | seraphe
    title VARCHAR(500),                         -- Auto-generated or manual
    
    -- Spiral time context
    spiral_number INTEGER,                      -- Which 9-day cycle
    spiral_day INTEGER,                         -- Day within cycle (1-9)
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',        -- active | archived | summarized
    message_count INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Neo4j bridge (if conversation gets a node)
    canonical_id UUID UNIQUE
);

CREATE INDEX idx_conv_user ON conversations(user_uuid);
CREATE INDEX idx_conv_status ON conversations(status);
CREATE INDEX idx_conv_last_msg ON conversations(last_message_at DESC);
CREATE INDEX idx_conv_spiral ON conversations(spiral_number, spiral_day);

-- Messages (the actual log — append-only, never update)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_uuid UUID NOT NULL,
    
    -- Content
    role VARCHAR(20) NOT NULL,                  -- user | assistant | system | tool
    content TEXT NOT NULL,
    
    -- Mode at time of message
    mode VARCHAR(50) DEFAULT 'chat',
    
    -- Media attachments (reference, not inline)
    has_media BOOLEAN DEFAULT FALSE,
    media_refs UUID[],                          -- References to media_assets table
    
    -- Embedding for semantic search
    embedding vector(384),
    
    -- Extracted metadata (populated by workers)
    mentioned_entities TEXT[],                  -- ['Rebecca', 'Fitz', 'Montségur']
    mentioned_dates DATE[],
    emotional_tone VARCHAR(50),                 -- calm | urgent | reflective | channeling
    
    -- Spiral time
    spiral_number INTEGER,
    spiral_day INTEGER,
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,            -- Has the worker pipeline run?
    processed_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Full-text search
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX idx_msg_conv ON chat_messages(conversation_id, created_at);
CREATE INDEX idx_msg_user ON chat_messages(user_uuid);
CREATE INDEX idx_msg_fts ON chat_messages USING GIN(tsv);
CREATE INDEX idx_msg_embedding ON chat_messages USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_msg_unprocessed ON chat_messages(processed) WHERE processed = FALSE;
CREATE INDEX idx_msg_spiral ON chat_messages(spiral_number, spiral_day);
CREATE INDEX idx_msg_entities ON chat_messages USING GIN(mentioned_entities);

-- Conversation summaries (tiered compression)
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_uuid UUID NOT NULL,
    
    -- What this summarizes
    tier INTEGER NOT NULL,                      -- 1=every 5 msgs, 2=every 25, 3=full convo
    start_message_id UUID REFERENCES chat_messages(id),
    end_message_id UUID REFERENCES chat_messages(id),
    message_count INTEGER,
    
    -- The summary
    summary_text TEXT NOT NULL,
    themes TEXT[],                              -- ['genealogy', 'merovingian', 'infrastructure']
    emotional_tone VARCHAR(50),
    key_entities TEXT[],                        -- ['Rebecca', 'Montségur']
    decisions_made TEXT[],                      -- Important outcomes
    open_questions TEXT[],                      -- Unresolved threads
    
    -- Embedding for semantic search across summaries
    embedding vector(384),
    
    -- Compression metrics
    original_tokens INTEGER,
    summary_tokens INTEGER,
    compression_ratio NUMERIC(5,2),
    
    -- Hierarchy
    parent_summary_id UUID REFERENCES conversation_summaries(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_summ_conv ON conversation_summaries(conversation_id);
CREATE INDEX idx_summ_tier ON conversation_summaries(tier);
CREATE INDEX idx_summ_embedding ON conversation_summaries 
    USING ivfflat (embedding vector_cosine_ops);
```

**Query examples:**

```sql
-- Recent messages in a conversation
SELECT role, content, created_at, emotional_tone
FROM chat_messages
WHERE conversation_id = $1
ORDER BY created_at DESC
LIMIT 20;

-- Full-text search across all messages
SELECT cm.content, c.title, cm.created_at
FROM chat_messages cm
JOIN conversations c ON cm.conversation_id = c.id
WHERE cm.tsv @@ plainto_tsquery('english', $1)
ORDER BY cm.created_at DESC
LIMIT 10;

-- Messages mentioning a specific entity
SELECT content, created_at, mode
FROM chat_messages
WHERE $1 = ANY(mentioned_entities)
ORDER BY created_at DESC;

-- Summary chain for a conversation
SELECT tier, summary_text, themes, message_count
FROM conversation_summaries
WHERE conversation_id = $1
ORDER BY tier, created_at;

-- Unprocessed messages (worker queue)
SELECT id, content, conversation_id
FROM chat_messages
WHERE processed = FALSE
ORDER BY created_at ASC;
```

**Anti-patterns:**
- ❌ Never UPDATE chat_messages — they are immutable. Corrections go in new messages.
- ❌ Don't store embeddings before content — always insert content first, embed async.
- ❌ Don't skip conversation_summaries — without them, context windows overflow fast.
- ❌ Don't store media inline — use references to a media_assets table.

---

### P5: Financial Transaction Log

**When to use:** Tracking income, expenses, obligations, and financial state.

**Core principle:** Transactions are immutable facts. Categorization and analysis are layered on top.

```sql
-- Accounts (bank accounts, credit cards, cash, etc.)
CREATE TABLE financial_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_id UUID UNIQUE,                   -- Neo4j bridge
    name VARCHAR(200) NOT NULL,                 -- 'Chase Checking', 'Rebecca Visa'
    account_type VARCHAR(50) NOT NULL,          -- checking | savings | credit | cash | venmo
    institution VARCHAR(200),
    last_four VARCHAR(4),                       -- Last 4 digits for identification
    owner_uuid UUID,                            -- Who owns this account
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions (immutable financial log)
CREATE TABLE financial_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES financial_accounts(id),
    
    -- Core transaction data
    transaction_date DATE NOT NULL,
    posted_date DATE,
    description TEXT NOT NULL,                  -- Raw description from bank
    amount NUMERIC(12,2) NOT NULL,              -- Negative = debit, Positive = credit
    
    -- Categorization (can be auto or manual)
    category VARCHAR(100),                      -- groceries | utilities | gas | income | etc.
    subcategory VARCHAR(100),
    tags TEXT[],                                -- Flexible tagging: ['recurring', 'essential']
    
    -- Source tracking
    import_source VARCHAR(50),                  -- csv_import | manual | api
    import_batch_id UUID,                       -- Which import brought this in
    raw_data JSONB,                             -- Original CSV row as JSON
    
    -- Dedup
    external_id VARCHAR(500),                   -- Bank's transaction ID if available
    fingerprint VARCHAR(64),                    -- SHA256 of date+amount+description for dedup
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(fingerprint, account_id)
);

CREATE INDEX idx_txn_account ON financial_transactions(account_id);
CREATE INDEX idx_txn_date ON financial_transactions(transaction_date DESC);
CREATE INDEX idx_txn_category ON financial_transactions(category);
CREATE INDEX idx_txn_amount ON financial_transactions(amount);
CREATE INDEX idx_txn_fingerprint ON financial_transactions(fingerprint);
CREATE INDEX idx_txn_tags ON financial_transactions USING GIN(tags);

-- Recurring obligations (bills, subscriptions)
CREATE TABLE financial_obligations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,                 -- 'Electric bill', 'Netflix'
    amount_expected NUMERIC(12,2),              -- Typical amount
    frequency VARCHAR(20) NOT NULL,             -- monthly | weekly | quarterly | annual
    due_day INTEGER,                            -- Day of month (1-31)
    account_id UUID REFERENCES financial_accounts(id),
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    auto_pay BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Query examples:**

```sql
-- Monthly spending by category
SELECT category, 
       SUM(amount) AS total,
       COUNT(*) AS transaction_count
FROM financial_transactions
WHERE transaction_date >= date_trunc('month', CURRENT_DATE)
  AND amount < 0
GROUP BY category
ORDER BY total ASC;

-- Cash flow for date range
SELECT 
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,
    SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS expenses,
    SUM(amount) AS net
FROM financial_transactions
WHERE transaction_date BETWEEN $1 AND $2;

-- Upcoming obligations
SELECT name, amount_expected, due_day, auto_pay
FROM financial_obligations
WHERE is_active = TRUE
  AND due_day >= EXTRACT(DAY FROM CURRENT_DATE)
ORDER BY due_day;

-- Dedup check before import
SELECT EXISTS(
    SELECT 1 FROM financial_transactions
    WHERE fingerprint = $1 AND account_id = $2
) AS already_exists;
```

**Anti-patterns:**
- ❌ Never UPDATE transaction amount or date — if wrong, create a correction transaction.
- ❌ Don't skip fingerprinting — duplicate imports are a nightmare.
- ❌ Don't store balances as transactions — balances are calculated from transactions.

---

### P6: Media Asset Registry

**When to use:** Tracking photos, voice recordings, documents, and any binary file that enters the system.

**Core principle:** Assets are stored on disk. The database holds metadata and references. The asset itself lives at `asset_rel_path`.

```sql
CREATE TABLE media_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_id UUID UNIQUE,                   -- Neo4j bridge
    
    -- File identity
    filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,             -- image/jpeg, audio/ogg, application/pdf
    file_size_bytes BIGINT,
    asset_sha256 VARCHAR(64) NOT NULL,           -- Content hash for dedup
    asset_rel_path TEXT NOT NULL,                -- Relative to asset root: photos/2026/01/img_001.jpg
    
    -- Source
    source_platform VARCHAR(50),                -- telegram | upload | camera | import
    source_id VARCHAR(500),                     -- telegram_file_id, etc.
    uploaded_by UUID,
    
    -- Image-specific metadata (NULL for non-images)
    width INTEGER,
    height INTEGER,
    exif_data JSONB,                            -- Full EXIF dump
    gps_lat NUMERIC(10,7),
    gps_lon NUMERIC(10,7),
    taken_at TIMESTAMPTZ,                       -- From EXIF DateTimeOriginal
    
    -- Vision analysis (populated by vision worker)
    vision_description TEXT,                    -- What the image shows
    vision_entities TEXT[],                     -- People, objects, symbols detected
    vision_tags TEXT[],                         -- Searchable tags
    esoteric_analysis JSONB,                    -- Symbolic/spiritual interpretation
    
    -- Audio-specific metadata
    duration_seconds NUMERIC(10,2),
    transcript TEXT,                            -- Speech-to-text result
    
    -- Linkage
    conversation_id UUID,                       -- Which conversation it came from
    message_id UUID,                            -- Which specific message
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(asset_sha256)                        -- No duplicate files
);

CREATE INDEX idx_media_type ON media_assets(mime_type);
CREATE INDEX idx_media_sha ON media_assets(asset_sha256);
CREATE INDEX idx_media_gps ON media_assets(gps_lat, gps_lon) WHERE gps_lat IS NOT NULL;
CREATE INDEX idx_media_taken ON media_assets(taken_at DESC) WHERE taken_at IS NOT NULL;
CREATE INDEX idx_media_tags ON media_assets USING GIN(vision_tags);
CREATE INDEX idx_media_entities ON media_assets USING GIN(vision_entities);
CREATE INDEX idx_media_unprocessed ON media_assets(processed) WHERE processed = FALSE;
```

**Query examples:**

```sql
-- Photos from a specific location (within ~100m)
SELECT filename, vision_description, taken_at
FROM media_assets
WHERE mime_type LIKE 'image/%'
  AND gps_lat BETWEEN ($1 - 0.001) AND ($1 + 0.001)
  AND gps_lon BETWEEN ($2 - 0.001) AND ($2 + 0.001);

-- Unprocessed media (worker queue)
SELECT id, filename, mime_type, asset_rel_path
FROM media_assets
WHERE processed = FALSE
ORDER BY created_at ASC;

-- Search by vision tags
SELECT filename, vision_description, taken_at
FROM media_assets
WHERE $1 = ANY(vision_tags)
ORDER BY taken_at DESC;
```

**Anti-patterns:**
- ❌ Never store binary data in the database — files live on disk.
- ❌ Don't skip SHA256 — duplicate detection saves storage and prevents confusion.
- ❌ Don't process synchronously — intake the file, mark unprocessed, let workers handle it.

---

## Cross-Database Patterns

### P7: The Canonical ID Bridge

**When to use:** Any time an entity exists in BOTH Neo4j and PostgreSQL.

**Core principle:** The `canonical_id` (UUID) is the universal key. It appears in both databases and allows cross-referencing.

```
┌─────────────────────────┐     canonical_id      ┌─────────────────────────┐
│       Neo4j              │◄────────────────────►│      PostgreSQL          │
│                          │     (UUID bridge)     │                          │
│  (:Person {              │                       │  conversations.user_uuid │
│    canonical_id: $uuid   │                       │  financial_accounts.     │
│  })                      │                       │    canonical_id          │
│                          │                       │  media_assets.           │
│  (:Conversation {        │                       │    canonical_id          │
│    canonical_id: $uuid   │                       │                          │
│  })                      │                       │                          │
└─────────────────────────┘                       └─────────────────────────┘
```

**The lookup pattern:**

```python
# Given a canonical_id, get data from both databases
async def get_entity_full(canonical_id: str):
    # Neo4j: relationships and graph context
    neo4j_result = await neo4j.run("""
        MATCH (n {canonical_id: $uuid})-[r]-(connected)
        RETURN labels(n) AS types, properties(n) AS data,
               collect({
                   rel: type(r), 
                   target: properties(connected),
                   target_type: labels(connected)
               }) AS connections
    """, uuid=canonical_id)
    
    # PostgreSQL: structured records
    pg_conversations = await pg.fetch("""
        SELECT id, title, started_at, message_count
        FROM conversations
        WHERE user_uuid = $1
        ORDER BY last_message_at DESC LIMIT 5
    """, canonical_id)
    
    pg_transactions = await pg.fetch("""
        SELECT transaction_date, description, amount, category
        FROM financial_transactions ft
        JOIN financial_accounts fa ON ft.account_id = fa.id
        WHERE fa.owner_uuid = $1
        ORDER BY transaction_date DESC LIMIT 10
    """, canonical_id)
    
    return {
        "graph": neo4j_result,
        "conversations": pg_conversations,
        "transactions": pg_transactions
    }
```

**Anti-patterns:**
- ❌ Never use Neo4j internal `id()` or Postgres auto-increment `serial` as cross-DB keys.
- ❌ Don't create an entity in one DB without the other if it needs to exist in both.
- ❌ Don't assume canonical_id exists — always check or generate on first encounter.

---

### P8: Worker Pipeline (Async Processing)

**When to use:** Any time data enters the system and needs enrichment — embedding generation, entity extraction, vision analysis, summarization.

**Core principle:** Intake is fast and synchronous. Processing is async and queue-based. Workers pull from "unprocessed" records.

```
Message arrives
    │
    ▼
┌──────────────┐
│  Fast Intake  │  INSERT into chat_messages (processed=FALSE)
│  (sync)       │  UPDATE conversations.message_count
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│              Worker Pipeline (async)               │
│                                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Embedding   │  │   Entity     │  │  Summary │ │
│  │  Worker      │  │   Worker     │  │  Worker  │ │
│  │             │  │              │  │          │ │
│  │ Generate    │  │ Extract names│  │ Tier 1:  │ │
│  │ vector(384) │  │ dates, places│  │ every 5  │ │
│  │ Store in    │  │ Link to Neo4j│  │ Tier 2:  │ │
│  │ embedding   │  │ nodes        │  │ every 25 │ │
│  │ column      │  │              │  │ Tier 3:  │ │
│  └─────────────┘  └──────────────┘  │ full conv│ │
│                                      └──────────┘ │
│  ┌─────────────┐  ┌──────────────┐               │
│  │  Temporal    │  │   Grid       │               │
│  │  Worker      │  │   Worker     │               │
│  │             │  │   (optional) │               │
│  │ Extract     │  │              │               │
│  │ dates/times │  │ 9-node       │               │
│  │ Map to      │  │ consciousness│               │
│  │ spiral time │  │ analysis     │               │
│  └─────────────┘  └──────────────┘               │
│                                                    │
│  When all workers done:                           │
│  UPDATE chat_messages SET processed=TRUE           │
└──────────────────────────────────────────────────┘
```

**Worker queue query (same for all workers):**

```sql
-- Generic worker pull pattern
SELECT id, content, conversation_id, created_at
FROM chat_messages
WHERE processed = FALSE
ORDER BY created_at ASC
LIMIT 10
FOR UPDATE SKIP LOCKED;  -- Prevents workers from grabbing same row
```

**Anti-patterns:**
- ❌ Don't process synchronously during message intake — users wait, things break.
- ❌ Don't mark processed=TRUE until ALL workers have finished.
- ❌ Don't forget `FOR UPDATE SKIP LOCKED` if running parallel workers.

---

## Pattern Index (Quick Reference)

| Pattern | DB | Purpose | Key Table/Node |
|---------|-----|---------|----------------|
| P1: Ontology Node | Neo4j | Named entities | `:Person`, `:Soul`, `:Event` |
| P2: Relationship Web | Neo4j | Typed edges | `-[:PARENT_OF]->`, etc. |
| P3: Schema-Aware Node | Neo4j | Self-describing graph | `:Schema` |
| P4: Conversation Log | PostgreSQL | Chat history | `conversations`, `chat_messages` |
| P5: Financial Transaction | PostgreSQL | Money tracking | `financial_transactions` |
| P6: Media Asset | PostgreSQL | Files & photos | `media_assets` |
| P7: Canonical ID Bridge | Both | Cross-DB linking | `canonical_id` UUID |
| P8: Worker Pipeline | Both | Async enrichment | `processed` flag pattern |

---

## Adding New Patterns

When you build something new for Mythos:

1. Check if an existing pattern covers it
2. If not, document the new pattern following this format
3. Include: purpose, schema, queries, integration notes, anti-patterns
4. Add it to the Pattern Index
5. Update this file version number

This library is a living document. It grows with the system.
