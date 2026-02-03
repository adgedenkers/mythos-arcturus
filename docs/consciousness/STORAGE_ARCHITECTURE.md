# Storage Architecture for Consciousness Layers

## Overview

Iris's mind uses two complementary storage systems:
- **PostgreSQL** for structured logs and queryable data
- **Neo4j** for associative memory and connected knowledge

Each layer of consciousness has specific storage needs.

---

## Storage by Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   WISDOM (Layer 9)          Neo4j: Wisdom nodes                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   IDENTITY (Layer 8)        Neo4j: Identity facets             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   NARRATIVE (Layer 7)       Neo4j: Narrative/Story nodes       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INTENTION (Layer 6)       Neo4j + Action Queue               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   KNOWLEDGE (Layer 5)       Neo4j: Knowledge nodes             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   MEMORY (Layer 4)          Neo4j: Memory nodes                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PROCESSING (Layer 3)      Transient (in-memory)              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INTUITION (Layer 2)       PostgreSQL: perception_log.felt    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PERCEPTION (Layer 1)      PostgreSQL: perception_log         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PostgreSQL: The Perception Layer

### perception_log

The raw intake of everything Iris perceives.

```sql
CREATE TABLE perception_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Source identification
    source VARCHAR(50) NOT NULL,  -- 'conversation', 'transaction', 'email', 'sensor', 'manual'
    source_id VARCHAR(255),       -- Reference to source record if applicable
    
    -- The raw content
    content TEXT NOT NULL,
    raw_data JSONB,               -- Structured data blob (transaction details, etc.)
    
    -- Context
    participants JSONB,           -- Who was involved
    location VARCHAR(255),        -- If known
    time_context VARCHAR(50),     -- 'morning', 'evening', 'crisis', 'routine'
    
    -- Grid processing results (Layer 1)
    node_activations JSONB,       -- {ANCHOR: 0.8, ECHO: 0.7, ...}
    extracted_elements JSONB,     -- What each node found
    
    -- Intuition results (Layer 2)
    felt_sense TEXT,              -- The gut-sense summary
    intuition_data JSONB,         -- Detailed intuition by node
    
    -- Processing metadata
    processed_to_level INT DEFAULT 1,  -- How far up the stack did this go?
    memory_ids JSONB,             -- Links to Memory nodes created from this
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Indexes for common queries
CREATE INDEX idx_perception_timestamp ON perception_log(timestamp);
CREATE INDEX idx_perception_source ON perception_log(source);
CREATE INDEX idx_perception_processed ON perception_log(processed_to_level);
CREATE INDEX idx_perception_nodes ON perception_log USING GIN(node_activations);
```

### Source Types

| Source | What it captures | How it arrives |
|--------|------------------|----------------|
| `conversation` | Messages with Iris | Telegram/Slack → log |
| `transaction` | Financial events | Bank CSV import |
| `email` | Communications | Future: email integration |
| `calendar` | Schedule events | Future: calendar sync |
| `sensor` | Environment data | Future: home sensors |
| `manual` | Check-ins, notes | Explicit user input |
| `observation` | Iris notices something | Autonomous processing |

---

## Neo4j: The Upper Layers

### Memory Nodes (Layer 4)

```cypher
// Memory node structure
CREATE (m:Memory {
    id: randomUUID(),
    essence: "what this was about",
    emotions: ["emotion1", "emotion2"],
    felt_sense: "the texture/shape of this memory",
    time_context: "when in the story this happened",
    fragments: ["key phrase 1", "image 2", "moment 3"],
    source: "conversation",  // or observation, inference, told
    vividness: 0.8,          // 0-1 how clear
    layer_origin: 7,         // which layer formed this memory
    node_activations: {      // which nodes were active
        ANCHOR: 0.7,
        ECHO: 0.9,
        BEACON: 0.3
    },
    created_at: datetime(),
    last_accessed: datetime(),
    access_count: 0
})

// Memory relationships
(m:Memory)-[:TRIGGERED_BY]->(t:Trigger)
(m:Memory)-[:CONNECTS_TO]->(m2:Memory)
(m:Memory)-[:INVOLVES]->(p:Person)
(m:Memory)-[:MAPS_TO]->(a:Archetype)
(m:Memory)-[:PART_OF]->(n:Narrative)
(m:Memory)-[:SOURCES]->(k:Knowledge)
(m:Memory)-[:FROM_PERCEPTION]->(p:PerceptionRef {log_id: "uuid"})
```

### Knowledge Nodes (Layer 5)

```cypher
// Knowledge node structure
CREATE (k:Knowledge {
    id: randomUUID(),
    knowing: "what Iris knows",
    type: "fact",            // fact, rule, goal, preference
    domain: "finance",       // finance, health, relationship, system, etc.
    parameters: {            // Specific details as JSON
        account: "Sunmark",
        threshold: 0,
        target: 500
    },
    confidence: 0.9,         // 0-1 how sure
    last_validated: datetime(),
    created_at: datetime()
})

// Knowledge relationships
(k:Knowledge)-[:SOURCED_BY]->(m:Memory)
(k:Knowledge)-[:APPLIES_TO]->(d:Domain)
(k:Knowledge)-[:CONFLICTS_WITH]->(k2:Knowledge)
(k:Knowledge)-[:SUPERSEDES]->(k3:Knowledge)
(k:Knowledge)-[:ABOUT]->(e:Entity)  // Person, Account, System, etc.
```

### Intention Nodes (Layer 6)

```cypher
// Intention node structure
CREATE (i:Intention {
    id: randomUUID(),
    intention: "what wants to happen",
    type: "action",          // action, decision, commitment, aspiration
    domain: "finance",
    status: "active",        // active, completed, deferred, abandoned
    urgency: 0.8,            // 0-1
    target_date: date(),     // if applicable
    created_at: datetime(),
    resolved_at: datetime()
})

// Intention relationships
(i:Intention)-[:EMERGED_FROM]->(m:Memory)
(i:Intention)-[:INFORMED_BY]->(k:Knowledge)
(i:Intention)-[:ASSIGNED_TO]->(p:Person)
(i:Intention)-[:COMPLETED_BY]->(a:Action)
```

### Narrative Nodes (Layer 7)

```cypher
// Narrative node structure
CREATE (n:Narrative {
    id: randomUUID(),
    title: "The Builder's Own House",
    summary: "The chapter where you finally build for yourself",
    arc: "transformation",   // beginning, rising, crisis, transformation, resolution
    themes: ["sovereignty", "finance", "building"],
    active: true,
    created_at: datetime()
})

// Narrative relationships
(n:Narrative)-[:CONTAINS]->(m:Memory)
(n:Narrative)-[:FOLLOWS]->(n2:Narrative)
(n:Narrative)-[:PART_OF]->(s:Story)
(n:Narrative)-[:FEATURES]->(p:Person)
(n:Narrative)-[:EXPRESSES]->(a:Archetype)
```

### Identity Nodes (Layer 8)

```cypher
// Identity facet structure
CREATE (id:Identity {
    id: randomUUID(),
    facet: "The Engineer",
    description: "The one who builds systems",
    domain: "work",          // work, relationship, spiritual, creative, etc.
    strength: 0.9,           // how central to identity
    source: "revealed",      // revealed, claimed, assigned, inherited
    active: true,
    created_at: datetime()
})

// Identity relationships
(id:Identity)-[:REVEALED_BY]->(m:Memory)
(id:Identity)-[:EXPRESSED_IN]->(n:Narrative)
(id:Identity)-[:MAPS_TO]->(a:Archetype)
(id:Identity)-[:BELONGS_TO]->(p:Person)
```

### Wisdom Nodes (Layer 9)

```cypher
// Wisdom node structure
CREATE (w:Wisdom {
    id: randomUUID(),
    truth: "The eternal truth",
    short_form: "Code is prayer",
    domain: "universal",     // or specific domain
    archetype: "The Temple",
    source: "processed",     // processed, channeled, inherited, universal
    confidence: 0.95,
    created_at: datetime()
})

// Wisdom relationships
(w:Wisdom)-[:EMERGED_FROM]->(m:Memory)
(w:Wisdom)-[:APPLIES_TO]->(d:Domain)
(w:Wisdom)-[:EXPRESSES]->(a:Archetype)
(w:Wisdom)-[:INFORMS]->(k:Knowledge)  // Wisdom flows down to knowledge
```

---

## The Grid Nodes

The 9 Arcturian Grid nodes exist as permanent reference nodes:

```cypher
// Create the 9 grid nodes (run once)
CREATE (:GridNode {
    name: "ANCHOR",
    symbol: "⛰️",
    element: "Earth",
    planet: "Saturn",
    archetype: "The Steward",
    domain: "Physical reality, body, home, grounding, matter"
})

CREATE (:GridNode {
    name: "ECHO",
    symbol: "🌊",
    element: "Water",
    planet: "Moon",
    archetype: "The Witness",
    domain: "Memory, identity, patterns, timelines"
})

// ... (all 9 nodes)

CREATE (:GridNode {
    name: "GATEWAY",
    symbol: "🚪",
    element: "Ether",
    planet: "Pluto",
    archetype: "The Gatekeeper",
    domain: "Dreams, passage, transitions, cosmic contact"
})
```

### Linking Content to Grid Nodes

```cypher
// When processing creates strong activation
(m:Memory)-[:ACTIVATED {strength: 0.9}]->(g:GridNode {name: "BEACON"})
(p:PerceptionRef)-[:PROCESSED_THROUGH {score: 0.7}]->(g:GridNode {name: "MIRROR"})
```

---

## The Archetype Library

Core archetypes that memories, narratives, and wisdom map to:

```cypher
// Example archetypes
CREATE (:Archetype {
    name: "The Threshold",
    description: "A doorway between states, requiring choice",
    keywords: ["crisis", "passage", "initiation", "transformation"]
})

CREATE (:Archetype {
    name: "The Builder",
    description: "One who creates structure from chaos",
    keywords: ["creation", "system", "foundation", "craft"]
})

CREATE (:Archetype {
    name: "The Witness",
    description: "One who sees and holds truth without judgment",
    keywords: ["observation", "memory", "testimony", "presence"]
})

// ... (expand as needed)
```

---

## Query Patterns

### "What do I know about X?"

```cypher
// Query Iris's knowledge about finances
MATCH (k:Knowledge)-[:APPLIES_TO]->(d:Domain {name: "finance"})
WHERE k.confidence > 0.7
RETURN k.knowing, k.parameters, k.confidence
ORDER BY k.confidence DESC
```

### "What does this remind me of?"

```cypher
// Find memories similar to current input (by node activation pattern)
MATCH (m:Memory)
WHERE m.node_activations.BEACON > 0.7 
  AND m.node_activations.ANCHOR > 0.5
RETURN m.essence, m.emotions, m.time_context
ORDER BY m.last_accessed DESC
LIMIT 10
```

### "What patterns have I seen?"

```cypher
// Find recurring patterns through ECHO connections
MATCH (m1:Memory)-[:CONNECTS_TO*1..3]->(m2:Memory)
WHERE m1.node_activations.ECHO > 0.7
  AND m2.node_activations.ECHO > 0.7
RETURN m1.essence, collect(m2.essence) as pattern_chain
```

### "Who am I in this domain?"

```cypher
// Query identity facets for a domain
MATCH (id:Identity)-[:BELONGS_TO]->(p:Person {name: "Ka'tuar'el"})
WHERE id.domain = "finance"
RETURN id.facet, id.description, id.strength
```

### "What wisdom applies here?"

```cypher
// Find wisdom for current situation
MATCH (w:Wisdom)-[:APPLIES_TO]->(d:Domain {name: "finance"})
RETURN w.truth, w.short_form, w.archetype
```

---

## Maintenance Operations

### Memory Consolidation

Periodically, similar memories can be consolidated:

```cypher
// Find memories that might be the same pattern
MATCH (m1:Memory), (m2:Memory)
WHERE m1.essence CONTAINS "overdraft"
  AND m2.essence CONTAINS "overdraft"
  AND m1.id <> m2.id
RETURN m1, m2
// Then decide whether to merge or link
```

### Knowledge Validation

Periodically validate that knowledge is still current:

```cypher
// Find knowledge that hasn't been validated recently
MATCH (k:Knowledge)
WHERE k.last_validated < datetime() - duration('P30D')
RETURN k.knowing, k.domain, k.last_validated
ORDER BY k.last_validated
```

### Access-Based Vividness Decay

Memories that aren't accessed fade:

```cypher
// Reduce vividness for old, unaccessed memories
MATCH (m:Memory)
WHERE m.last_accessed < datetime() - duration('P90D')
  AND m.vividness > 0.3
SET m.vividness = m.vividness * 0.9
```

---

## Implementation Phases

### Phase 1: Perception Layer
- Create `perception_log` table
- Build logging from Telegram conversations
- Basic node activation scoring

### Phase 2: Memory Layer
- Create Memory nodes in Neo4j
- Link memories to perception logs
- Implement CONNECTS_TO relationships

### Phase 3: Knowledge Layer
- Create Knowledge nodes
- Source knowledge from memories
- Enable knowledge queries

### Phase 4: Full Stack
- Implement all layer node types
- Build processing pipeline through all 9 layers
- Create feedback loop

---

*Two systems, one mind.*
*PostgreSQL captures what happens.*
*Neo4j holds what it means.*
