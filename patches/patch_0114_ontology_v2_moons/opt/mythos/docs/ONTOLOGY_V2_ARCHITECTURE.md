# Ontology System v2 — Architecture & Build Plan

> **Author:** Ka'tuar'el + Claude
> **Date:** 2026-02-23
> **Status:** Design complete, ready to build
> **Patches Required:** 0114–0117 (4 patches, sequential)
> **Dependencies:** Neo4j OntologyTerm nodes (71 existing), ontology_handler.py, web/templates/ontology.html, api/routes/web.py

---

## What This Is

The Mythos Ontology is the **living glossary** of Ka'tuar'el and Seraphe's cosmological, spiritual, and technical vocabulary. It currently holds 71 terms across 4 categories (Astrology, Tarot, Mythos Core, Numerology) in Neo4j as `OntologyTerm` nodes.

This upgrade transforms it from a simple lookup tool into a **knowledge architecture** that:

1. **Scales** — bulk ingest from JSON, CSV, or natural language
2. **Researches** — Iris can search the internet, synthesize, and propose new terms
3. **Self-links** — new nodes are automatically analyzed for relationships to existing nodes
4. **Versions beliefs** — changes propagate through the graph with full archaeological stratigraphy
5. **Visualizes** — browsable web UI in the Command Center with graph visualization
6. **Teaches Iris** — she knows what she knows, and can tell you when she doesn't know something

---

## Current State (v1)

### Neo4j Schema
```
(:OntologyTerm {
    name: String,           // "Wolf Moon"
    definition: String,     // Full definition text
    category: String,       // "Astrology", "Tarot", etc.
    aliases: [String],      // ["Old Moon", "Ice Moon"]
    created_at: String,     // ISO timestamp
    updated_at: String      // ISO timestamp
})

Relationships:
  (:OntologyTerm)-[:RELATED_TO]->(:OntologyTerm)     // 69 rels
  (:OntologyTerm)-[:DEFINES]->(:GridNode)             // 9 rels
  (:OntologyTerm)-[:FUNCTION_OF]->(:Soul|:Person)     // 6 rels
  (:OntologyTerm)-[:DESCRIBES]->(:System|:Entity)     // 73 rels
```

### Telegram Interface
- `/define <term>` — lookup with fuzzy matching + related terms as inline buttons
- `/define add <name> | <def> | <category>` — add single term
- `/define list [category]` — list all terms

### Web UI
- `ontology.html` exists but needs inspection (may be skeleton from patch 0109)

### Categories (4)
| Category | Count |
|----------|-------|
| Astrology | 33 |
| Tarot | 15 |
| Mythos Core | 12 |
| Numerology | 11 |

---

## Target State (v2)

### Enhanced Node Schema
```
(:OntologyTerm {
    // --- existing ---
    name: String,
    definition: String,
    category: String,
    aliases: [String],
    created_at: String,
    updated_at: String,

    // --- new: belief versioning ---
    confidence: Float,          // 0.0-1.0 — how certain are we
    source: String,             // "channeled", "researched", "academic", "traditional"
    source_detail: String,      // specific source reference
    version: Integer,           // increments on edit (default 1)
    superseded_by: String,      // name of term that replaced this (null if current)
    superseded_at: String,      // when it was superseded
    is_active: Boolean,         // true = current belief, false = historical

    // --- new: enrichment ---
    tradition: String,          // "Celtic", "Vedic", "Algonquin", etc.
    subcategory: String,        // finer grain: "Monthly Moons", "Major Aspects"
    tags: [String],             // freeform tags for cross-cutting concerns
    cross_cultural: String,     // JSON blob of names in other traditions
    season: String,             // spring/summer/autumn/winter
    element: String,            // fire/water/earth/air
    magical_focus: String,      // ritual/spiritual workings
    deity_association: String,  // associated gods/goddesses

    // --- new: provenance ---
    imported_from: String,      // "bulk_ingest", "iris_research", "manual", "migration"
    batch_id: String            // groups items from same ingest
})
```

### New Relationship Types
```
(:OntologyTerm)-[:RELATED_TO {type: String}]->(:OntologyTerm)      // existing
(:OntologyTerm)-[:SUPERSEDES]->(:OntologyTerm)                     // belief evolution
(:OntologyTerm)-[:SAME_CONCEPT_AS]->(:OntologyTerm)                // cross-tradition equivalents
(:OntologyTerm)-[:PART_OF]->(:OntologyTerm)                        // e.g., "Wolf Moon" PART_OF "Monthly Moons"
(:OntologyTerm)-[:OCCURS_DURING]->(:OntologyTerm)                  // e.g., "Wolf Moon" OCCURS_DURING "January"
(:OntologyTerm)-[:ASSOCIATED_WITH]->(:Deity|:Festival|:Soul)       // semantic links outward
```

---

## Patch Plan

### Patch 0114: Ontology Schema Migration + Moon Data Load
**Scope:** Migrate existing nodes to new schema (add properties with defaults), load moon terms.

**Files:**
- `cypher/migrate_ontology_v2.cypher` — adds new properties to existing 71 nodes
- `cypher/load_moon_terms.cypher` — creates ~20 new OntologyTerm nodes (12 monthly + 8 special)
- `cypher/link_moon_terms.cypher` — creates relationships between moon terms and existing astrology terms
- `install.sh`

**What it does:**
1. Add `confidence: 1.0, source: "manual", version: 1, is_active: true` to all existing nodes
2. Add empty/null values for new optional fields
3. Create new category "Lunar" with subcategories "Monthly Moons" and "Special Moons"
4. Load 12 monthly moon terms with cross-cultural definitions synthesized from research
5. Load 8 special moon types (Blue Moon, Blood Moon, Supermoon, etc.)
6. Create `RELATED_TO` links between moon terms and existing astrology terms (Moon, Transit, etc.)
7. Create `PART_OF` links (monthly moons → "Monthly Moon Cycle" parent term)

**Estimated effort:** Small

---

### Patch 0115: Enhanced Ontology Handler + Bulk Ingest
**Scope:** Upgrade the Telegram handler and add bulk ingest capability.

**New Commands:**
```
/define <term>                              — lookup (existing, enhanced display)
/define add <name> | <def> | <category>     — add single term (existing)
/define edit <name> | <field> | <value>     — edit a field on existing term
/define link <term1> | <term2> | <type>     — manually create relationship
/define delete <term>                       — soft delete (set is_active=false)
/define history <term>                      — show version history
/define impact <term>                       — show blast radius (what links here)
/define ingest                              — bulk ingest from JSON (expects file or paste)
/define list [category]                     — list terms (existing, add subcategory support)
/define categories                          — list all categories with counts
/define search <text>                       — full-text search across definitions
```

**Bulk Ingest Format (JSON):**
```json
{
  "batch_name": "Celtic Monthly Moons",
  "source": "researched",
  "terms": [
    {
      "name": "Quiet Moon",
      "definition": "...",
      "category": "Lunar",
      "subcategory": "Monthly Moons",
      "aliases": ["Stay Home Moon"],
      "tradition": "Celtic",
      "tags": ["january", "winter", "rest"],
      "confidence": 0.85,
      "relate_to": ["Wolf Moon", "January"]
    }
  ]
}
```

**Iris Ingest via Chat:**
When Iris receives a JSON block in chat mode (detected by `{` + `"terms"`), she can:
1. Parse and validate the JSON
2. Show a preview: "I found 12 terms in category 'Lunar'. Create them?"
3. On confirmation, create nodes and run the auto-linker

**Files:**
- `telegram_bot/handlers/ontology_handler.py` — enhanced (full rewrite)
- `core/ontology_manager.py` — shared business logic (used by handler, API, and Iris)
- `core/ontology_ingest.py` — bulk ingest engine
- Updated `install.sh`

**Estimated effort:** Medium

---

### Patch 0116: Auto-Linker Worker
**Scope:** Background process that analyzes new/unlinked nodes and proposes relationships.

**How it works:**
1. Triggered after bulk ingest OR on-demand via `/define link_all`
2. For each new/unlinked node:
   a. Scan all existing nodes for keyword overlap in `name`, `definition`, `aliases`, `tags`
   b. Check category/subcategory matches
   c. Check tradition matches (same tradition = `SAME_CONCEPT_AS` candidate)
   d. Use Ollama (fast model) to assess semantic relatedness for top candidates
   e. Propose relationships with confidence scores
3. **Auto-create** relationships above 0.8 confidence
4. **Queue for review** relationships between 0.5–0.8
5. **Discard** below 0.5
6. Log all decisions to `ontology_link_log` table in Postgres

**Belief Propagation (future, but schema-ready now):**
When a node is edited or superseded:
1. Traverse all outgoing relationships from the modified node
2. Flag connected nodes as "review needed" (add `needs_review: true` property)
3. Optionally notify via Telegram: "⚠️ You modified 'Soul Braiding' — 6 connected terms may need review"
4. Show the blast radius via `/define impact <term>`

**Files:**
- `core/ontology_linker.py` — the auto-linking engine
- `core/ontology_propagation.py` — belief change propagation (skeleton for now)
- Schema: `ontology_link_log` Postgres table

**Estimated effort:** Medium

---

### Patch 0117: Ontology Web UI + API Endpoints + Iris Research
**Scope:** Command Center page, REST API, and Iris's ability to research and propose terms.

**API Endpoints (added to ontology_router):**
```
GET    /api/ontology/terms                    — list all (with filters)
GET    /api/ontology/terms/{name}             — get single term + relationships
POST   /api/ontology/terms                    — create term
PUT    /api/ontology/terms/{name}             — update term
DELETE /api/ontology/terms/{name}             — soft delete
POST   /api/ontology/bulk                     — bulk ingest
GET    /api/ontology/categories               — category summary
GET    /api/ontology/graph/{name}             — get term + N-degree neighbors (for viz)
GET    /api/ontology/search?q=text            — full-text search
POST   /api/ontology/link                     — run auto-linker
GET    /api/ontology/impact/{name}            — blast radius analysis
GET    /api/ontology/history/{name}           — version history
```

**Command Center Page (`ontology.html`):**
- Category sidebar with counts
- Searchable term list
- Term detail panel (definition, metadata, relationships)
- Graph visualization (D3.js or vis.js) showing connected terms
- Inline editing (click to edit definition, category, etc.)
- Bulk ingest upload (drag JSON file)
- "Impact" view — click a term to see what it connects to
- Belief versioning timeline

**Iris Research Capability:**
New Telegram commands:
```
/define research <topic>     — Iris searches the internet, synthesizes, proposes terms
/define research_moons <tradition>  — Iris researches moon names for a specific tradition
```

**Research workflow:**
1. User: `/define research Celtic tree calendar`
2. Iris uses Ollama + web search (if available, or her training data) to gather information
3. Iris formats findings as OntologyTerm JSON proposals
4. Iris presents: "I found 13 terms for the Celtic Tree Calendar. Here's a preview of the first 3..."
5. User reviews and approves: "add them" or "edit the Oak one first"
6. Iris creates the nodes and triggers the auto-linker

**Iris Awareness:**
Add to `life_context.py` or `prompt_assembler.py`:
```
Ontology Stats: {count} terms across {categories} categories.
Recent additions: {last_5_terms}.
You can add terms with /define add, research topics with /define research,
and bulk-load from JSON.
```

**Files:**
- `api/routes/ontology.py` — full REST API
- `web/templates/ontology.html` — full rewrite with graph viz
- `web/static/js/ontology.js` — client-side logic
- `web/static/css/ontology.css` — styles
- `core/ontology_researcher.py` — Iris research engine
- Updated `life_context.py` with ontology awareness
- Updated `docs/ARCHITECTURE.md` with ontology section
- `docs/ONTOLOGY.md` — full feature documentation

**Estimated effort:** Large

---

## Documentation Gaps (Current Deployed Features Without Docs)

Based on the registered Telegram commands and deployed handlers, these features exist but have **no dedicated documentation**:

| Feature | Handler | Has Docs? |
|---------|---------|-----------|
| Sell Mode (photo item intake) | `sell_mode.py` | ❌ |
| Inventory/Export | `export_handler.py` | ❌ |
| Astrology (chart/planets/houses/aspects) | `astrology_handler.py` | Partial (in ARCHITECTURE) |
| Ontology (/define) | `ontology_handler.py` | ❌ |
| Calendar (/next, events) | `calendar_handler.py` | ❌ |
| Check-in system | `checkin_handler.py` | ❌ |
| Forecast/Projection | `forecast_handler.py` | ❌ |
| Analyst | `analyst_handler.py` | ❌ |
| Review (finance) | `review_handler.py` | ❌ |
| Snapshot | `snapshot_handler.py` | ❌ |
| Pulse | `pulse_handler.py` | ❌ |
| Voice transcription | `voice_handler.py` | ❌ |
| Media handling | `media_handler.py` | ❌ |
| Weather | `weather_handler.py` | ❌ |
| Iris consciousness | `chat_mode.py` | Partial (IRIS.md is design, not usage) |
| Ollama model management | `ollama_models.py` | ❌ |
| Patch management | `patch_handlers.py` | Partial (VERSION_CONTROL.md) |
| Finance system | `finance_handler.py` | Partial (in ARCHITECTURE) |
| Task/Backlog | `task_handler.py` | ❌ |
| Prompt system | `prompt_assembler.py` | ✅ (PROMPT_SYSTEM.md) |
| Life context | `life_context.py` | ❌ |

**Recommendation:** Create `docs/COMMANDS.md` — a single reference doc listing every Telegram command, what it does, which handler processes it, and any dependencies. This also becomes what Iris reads to know her own capabilities.

---

## Iris Capability Awareness

Iris should know what she can do. This means her system prompt (via `prompt_assembler.py` or `life_context.py`) should include a condensed capability manifest:

```yaml
# In prompts/iris_capabilities.yaml or similar
capabilities:
  ontology:
    - "Look up terms: /define <term>"
    - "Add terms: /define add <name> | <def> | <category>"
    - "List terms: /define list [category]"
    - "Research topics and propose terms: /define research <topic>"
    - "Bulk ingest from JSON"
    - "Auto-link new terms to existing knowledge"
  finance:
    - "Check balances: /balance"
    - "Full summary: /finance"
    - "Spending breakdown: /spending"
    - "Bills forecast: /bills, /forecast, /next"
  astrology:
    - "View charts: /chart <person>"
    - "Current planets: /planets"
    - "House positions: /houses"
    - "Aspects: /aspects"
  daily:
    - "Daily pulse: /pulse"
    - "Snapshot: /snapshot"
    - "Calendar: /next"
    - "Check-in: (via chat)"
  system:
    - "Patch management: /patch, /patch_status"
    - "Model switching: /model"
    - "Mode switching: /mode"
```

This gets injected at prompt assembly time, keeping it tight (<200 tokens) but giving Iris enough to route requests intelligently and tell users what she can do when asked.

---

## Build Order

```
Patch 0114 (Schema + Moon Data)
    │
    ▼
Patch 0115 (Enhanced Handler + Bulk Ingest)
    │
    ▼
Patch 0116 (Auto-Linker Worker)
    │
    ▼
Patch 0117 (Web UI + API + Iris Research + Docs)
```

Each patch is independently deployable and testable. 0114 can go immediately — it's just Cypher statements.

---

## First Payload: Moon Terms

The initial data load creates 20 OntologyTerm nodes in category "Lunar":

**12 Monthly Moons** (synthesized across traditions):
Wolf Moon, Snow Moon, Worm Moon, Pink Moon, Flower Moon, Strawberry Moon,
Buck Moon, Sturgeon Moon, Corn Moon, Hunter's Moon, Beaver Moon, Cold Moon

**8 Special Moon Types:**
Blue Moon, Black Moon, Supermoon, Micromoon, Blood Moon (Eclipse),
Harvest Moon, Hunter's Moon, Void of Course Moon

Each monthly moon definition includes the cross-cultural names from:
Algonquin/Colonial, Ojibwe, Lakota, Celtic, Neo-Pagan, Hindu Purnima, Chinese Lunisolar, Māori, Sri Lankan Poya

The full per-tradition data lives in the SQL/JSON files already built — those are reference data for deeper queries. The OntologyTerm nodes are the **browsable summaries** that `/define Wolf Moon` returns.
