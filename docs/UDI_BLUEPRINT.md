# MYTHOS — Unified Data Interface

## Architectural Proposal & Implementation Blueprint

*Prepared for Ka'tuar'el — February 2026*

*Sovereign Infrastructure • No Corporate Dependencies • Graph-First Architecture*

---

## 1. Executive Vision

The Mythos system currently stores knowledge across three evolving data layers: Neo4j for relationships and identity, PostgreSQL for structured records, and a growing body of text documents (session transcripts, channeled transmissions, journal entries). These layers are disconnected. You can query people in Neo4j or finance in Postgres, but there is no single interface that follows a thread across all three.

The Unified Data Interface (UDI) changes this. It treats the Neo4j graph as the master index of everything that exists in the system. Every person, every concept, every event, every document is a node or is linked to a node. When you search for something, the graph tells you what related data exists and where it lives. The interface then pulls from all relevant stores and assembles a complete dossier.

**The core principle: the graph is the spine. Everything else is muscle and skin.**

---

## 2. The Three Data Layers

### 2.1 Neo4j — The Relationship Layer (Identity & Connection)

Neo4j is the map of what exists and how it connects. It answers: Who is this? What are they connected to? What types of data exist for them?

**Current state:** 71 Person/Soul nodes, 21 relationship types, 1,490 GenPerson genealogy nodes, ontology terms, grid assessments, incarnation tracking.

**Role in UDI:** *Master index. Every searchable entity has a node. Relationships act as routing pointers to records in other stores.*

| Node Label | Count | Purpose | Routes To |
|---|---|---|---|
| Person | 4 | Canonical identities (Ka, Seraphe, Fitz, Dennis) | Postgres people, finance, astrology; Documents |
| Person:Entity | 18 | Aspects, contacts, public figures | Postgres people; Exchange mentions |
| Soul / Soul:Person | 6 | Soul-level identities with spiritual data | Astrology charts, stratigraphy, grid assessments |
| Person:GenPerson | 43+ | GEDCOM genealogy imports | Genealogy source records |
| OntologyTerm | ~50 | Defined concepts and vocabulary | Related terms, documents mentioning concept |
| Exchange | varies | Conversation fragments | Full transcript documents |
| Incarnation | ~3 | Past/current life records | Soul connections, lineage data |
| `NEW: Document` | — | Text document references | Filesystem/S3 paths to actual content |
| `NEW: Event` | — | Temporal events & milestones | Related people, documents, dates |
| `NEW: Location` | — | Geographic entities | People born/living there, events |

### 2.2 PostgreSQL — The Structured Record Layer

Postgres holds data that benefits from schemas, constraints, aggregation, and SQL queries. Financial transactions, structured birth records, chart parameters, and system configuration.

| Table | Records | Linked Via | Linkage Key |
|---|---|---|---|
| people | 3 | canonical_id | person-adriaan, etc. |
| finance_transactions | ~500+ | category/payee | Could link to Person nodes |
| finance_accounts | ~10 | account name | System config |
| astrology data | varies | person reference | canonical_id or soul-id |
| `NEW: documents_meta` | — | document_id | Metadata for stored docs |
| `NEW: events` | — | event_id + graph link | Structured event data |

**Key insight:** The Postgres `people` table (3 rows) is now redundant with Neo4j Person nodes (which have richer data). The UDI should treat Neo4j as authoritative for identity and Postgres for transactional/structured records only.

### 2.3 Document Store — The Narrative Layer (Future)

Text content that doesn't fit in structured databases: session transcripts, channeled transmissions, research notes, journal entries, PDFs, and exported conversation logs.

**Storage options (in order of sovereignty):**

- **Filesystem (immediate):** `/opt/mythos/documents/` with directory structure by type and date
- **MinIO/S3-compatible (near-term):** Self-hosted object storage for larger archives
- **Full-text search (future):** Meilisearch or Typesense for content search across all documents

Each document gets a Document node in Neo4j with relationships to the people, concepts, and events it references. The actual content lives in the file store. The graph knows what exists; the file store holds the content.

---

## 3. The Unified Search Model

One search box. Type anything. The system figures out what it is and assembles everything related to it.

### 3.1 Search Flow

1. **Query Classification:** Is this a person name, a concept, a date, a document title, a relationship type? Multiple classifiers run in parallel.
2. **Graph Traversal:** Find matching nodes in Neo4j. Follow relationships outward to discover connected data. Identify which external stores have records.
3. **Parallel Fetch:** Query Postgres tables, document store, and any other data sources identified by the graph. All queries run concurrently.
4. **Assembly:** Merge results into a unified response object. Rank by relevance. Return to the UI.
5. **Render:** The UI displays a dossier with sections for each data type, prioritized by relevance.

### 3.2 Search Examples

| Query | Classification | Graph Path | Data Assembled |
|---|---|---|---|
| "Ka'tuar'el" | Person (Entity) | Entity → ASPECT_OF → Person → Soul, Fitz, Seraphe | Identity, family, soul data, finance, charts, mentions |
| "Merovingian" | Concept/Lineage | OntologyTerm + Lineage nodes | Definition, related people, documents, genealogy branches |
| "finance March 2026" | Temporal + Domain | Date range → transactions | Monthly summary, categorized spending, trends |
| "Montségur" | Location/Event | Location → related people, events | Historical context, incarnation links, documents |
| "Grid Assessment Ka" | Compound | Person → HAS_ASSESSMENT | All 9-node grid assessments for Ka |
| "session 2026-02-20" | Document/Date | Exchange/Document nodes by date | Full transcript, extracted entities, topics discussed |

---

## 4. The Dossier Model

When you land on any entity in the system, you see a dossier — a complete picture assembled from all data layers. This replaces the current siloed views (people page shows Neo4j only, finance page shows Postgres only).

### 4.1 Person Dossier

Everything known about a person, assembled from all sources:

| Section | Source | Content |
|---|---|---|
| Identity | Neo4j Person/Soul node | Names, aliases, canonical_id, person_type, labels |
| Vital Records | Neo4j + Postgres | Birth date/time/place, death date, current location |
| Relationships | Neo4j relationships | Family (PARENT_OF, SPOUSE_OF), soul (ASPECT_OF, EMBODIED_AS), trinity, lineage |
| Graph Neighborhood | Neo4j ego graph | Interactive Cytoscape visualization of 2-hop connections |
| Astrology | Postgres astrology tables | Charts (natal, progressed), numerology, stratigraphy if HAS_CHART exists |
| Finance | Postgres finance tables | Transactions linked to this person, spending patterns |
| Documents | Document store | Transcripts, notes, journals mentioning or authored by this person |
| Conversation History | Neo4j Exchange nodes | Past discussions where this person was MENTIONED |
| Grid Assessments | Neo4j assessment nodes | Arcturian Grid 9-node assessments if they exist |
| Genealogy | Neo4j GenPerson tree | Ancestral connections from GEDCOM if GenPerson-linked |
| Timeline | All sources | Chronological view of events, documents, transactions related to this person |

### 4.2 Concept Dossier

For ontology terms, lineages, or abstract concepts:

- **Definition & Category:** From OntologyTerm node
- **Related Concepts:** RELATED_TO edges to other terms
- **Associated People:** Who is linked to this concept (via CARRIES_LINEAGE, EMBODIES, etc.)
- **Documents:** All documents that reference this concept
- **Timeline:** When was this concept discussed, referenced, or updated?

### 4.3 Event Dossier

For temporal events (sessions, historical dates, milestones):

- **Event metadata:** Date, location, type, description
- **Participants:** People linked to the event
- **Documents:** Transcripts, notes, or records from the event
- **Related events:** What happened before/after, what it connects to

### 4.4 Document Dossier

For text documents, transcripts, and narrative content:

- **Content preview:** First section or summary of the document
- **Metadata:** Author, date, type, word count, source
- **Extracted entities:** People, places, concepts mentioned (auto-extracted or manually tagged)
- **Related documents:** Other documents that share entities or topics

---

## 5. Concept & Topic Mapping

The ontology system already tracks defined terms. The UDI extends this into a full knowledge graph where concepts connect to everything else.

### 5.1 Knowledge Graph Extensions

New node types and relationships for concept mapping:

| Relationship | From → To | Purpose |
|---|---|---|
| RELATES_TO_CONCEPT | Person → OntologyTerm | This person is associated with this concept |
| EXPERT_IN / STUDIES | Person → OntologyTerm | Directed expertise or research interest |
| MENTIONED_IN | OntologyTerm → Document | This concept appears in this document |
| DERIVED_FROM | OntologyTerm → OntologyTerm | Concept lineage (Thelema DERIVED_FROM Hermeticism) |
| PRACTICED_AT | OntologyTerm → Location | Where a tradition is/was practiced |
| ORIGINATED_IN | OntologyTerm → Event | When/where a concept emerged |
| CONTRADICTS | OntologyTerm → OntologyTerm | Competing frameworks or interpretations |
| SYNTHESIZES | OntologyTerm → OntologyTerm | Concepts that combine into new understanding |

### 5.2 Auto-Extraction Pipeline

When documents are ingested, a local LLM (via Ollama) can auto-extract:

- **Named entities:** People, places, organizations → matched to existing graph nodes or flagged for creation
- **Concepts:** Ontology terms mentioned → MENTIONED_IN relationships
- **Temporal markers:** Dates and time references → linked to Event nodes
- **Sentiment/tone:** Emotional register of the content (for session transcripts)
- **Summary:** Auto-generated abstract stored as a property on the Document node

This pipeline runs asynchronously after document upload. Results are written back into the graph. The extraction quality improves as the ontology grows — more defined terms means better matching.

---

## 6. Capabilities You Haven't Built Yet (But Should)

### 6.1 Temporal Graph — Time as a First-Class Dimension

Every node and relationship can carry temporal metadata. When was this relationship created? When did it end? This enables:

- **Timeline views:** See any entity's history as a chronological stream across all data sources
- **Temporal queries:** "What was Ka's financial state when the Grid was channeled?" — correlate events across domains by time
- **Relationship evolution:** Track how connections change over time (someone shifts from Contact to Personal to Family)
- **Spiral Time overlay:** Map events onto the 9-day spiral cycle. Which spiral day did significant events fall on?

### 6.2 Cross-Domain Correlation Engine

The most powerful capability of a unified interface: finding patterns across data types that no single view could reveal.

- **Astro-Finance correlation:** Do spending patterns correlate with planetary transits? The data exists in both stores.
- **Session-Entity tracking:** Which people or concepts keep appearing across sessions? Frequency analysis on Exchange/Document mentions.
- **Lineage activation patterns:** When lineage claims are made in sessions, do they cluster around specific astrological configurations?
- **Grid assessment trends:** How do the 9-node assessments change over time? Track the evolution of consciousness states.

### 6.3 Provenance Tracking

Every piece of data should know where it came from:

- **Source attribution:** Was this entered manually, extracted from a document, imported from GEDCOM, channeled in a session?
- **Confidence levels:** Birth times with Rodden rating vs. unverified. Genealogy connections confirmed vs. speculative.
- **Edit history:** Who changed what, when. Stored as properties or separate Audit nodes.
- **Lineage of knowledge:** This fact was stated in session X, corroborated by document Y, contradicted by source Z.

### 6.4 Computed Properties & Derived Nodes

The graph can store computed results as first-class data:

- **Age (auto-computed):** From birth_date, always current
- **Relationship degree:** How many hops between any two people
- **Centrality scores:** Who is the most connected node in the graph? Graph analytics.
- **Cluster detection:** Auto-identify communities of related nodes (family clusters, lineage groups, concept domains)
- **Missing data detection:** Identify nodes that should have relationships but don't (a Person with no birth_date, a Soul with no CURRENTLY_EMBODIED_AS)

### 6.5 Multi-Modal Input

The system should accept data in any form:

- **Voice transcription:** Already partially built. Transcripts become Documents linked to the graph.
- **Photo metadata:** EXIF data from images → Location + Date + Person tags
- **Email/message import:** Extract entities and relationships from communications
- **Web clipping:** Save articles with auto-extraction of entities and concepts
- **Telegram integration:** Already exists. Extend bot commands to create any node type, not just people.

### 6.6 Access Control & Sharing

As the system grows, some data needs different visibility:

- **Personal vs. shared:** Financial data is private. Ontology terms could be shared with a community.
- **Export formats:** Generate reports, dossiers, or data packages for specific entities or time ranges
- **API access tiers:** Read-only for some consumers (e.g., a public-facing lineage viewer), full CRUD for the owner

---

## 7. Technical Architecture

### 7.1 API Layer

The UDI introduces a new top-level API that orchestrates across all data stores:

| Endpoint | Method | Purpose |
|---|---|---|
| /api/search | GET | Unified search across all data types |
| /api/dossier/{node_type}/{eid} | GET | Assemble full dossier for any node |
| /api/dossier/{eid}/section/{name} | GET | Lazy-load individual dossier sections |
| /api/timeline/{eid} | GET | Chronological stream for an entity |
| /api/correlate | POST | Cross-domain correlation queries |
| /api/documents/ | CRUD | Document store management |
| /api/documents/{id}/extract | POST | Trigger entity extraction on a document |
| /api/graph/analytics | GET | Centrality, clustering, path queries |

### 7.2 Data Flow

Every query flows through the same pipeline: **Search → Graph Resolve → Parallel Fetch → Assemble → Render**. The graph is always the first stop. It determines what exists and where to look. External stores are only queried for data the graph says is there.

The routing logic lives in the graph itself through relationship types:

| Graph Relationship | Implies | Action |
|---|---|---|
| HAS_CHART | Astrology data exists | Query Postgres astrology tables |
| HAS_NUMEROLOGY | Numerology data exists | Query Postgres numerology tables |
| MENTIONED (to Exchange) | Conversation history | Fetch Exchange content |
| `HAS_DOCUMENT` | Document exists | Fetch from document store |
| `HAS_FINANCE` | Financial records | Query Postgres finance tables |
| `HAS_ASSESSMENT` | Grid assessment data | Fetch assessment nodes from Neo4j |
| BORN_IN / DIED_IN | Location data | Include in vital records section |

### 7.3 Web UI Architecture

The current page-per-domain model (separate pages for People, Finance, Ontology) evolves into:

1. **Command Center (Home):** Unified search bar + recent activity stream + quick stats
2. **Dossier View:** Replaces individual detail pages. One layout that adapts to any entity type.
3. **Graph Explorer:** Full-screen Cytoscape view with filters, search, and click-to-dossier navigation
4. **Timeline View:** Chronological stream across all data types for any entity or globally
5. **Domain Pages (preserved):** Finance, Ontology, etc. still exist as focused views for domain-specific work

---

## 8. Implementation Roadmap

Phased approach. Each phase delivers usable features. No big-bang rewrite.

### Phase 1: Graph as Index (Patches 0120–0125)

*Goal: Make the graph aware of what data exists in Postgres.*

- Add HAS_FINANCE relationships from Person nodes to indicate finance data exists
- Add HAS_CHART relationships where astrology data exists
- Build /api/dossier/{eid} endpoint that follows graph relationships and queries relevant Postgres tables
- Update People detail view to show Postgres-sourced sections (finance summary, chart data) when relationships exist
- Migrate remaining Postgres people data into Neo4j properties (merge the 3 SQL rows into existing Neo4j nodes)

### Phase 2: Document Store (Patches 0126–0132)

*Goal: Ingest, store, and link text content.*

- Create /opt/mythos/documents/ directory structure
- Build Document node type in Neo4j with metadata properties
- Build /api/documents/ CRUD endpoints
- Web UI for document upload and browsing
- Link documents to existing nodes (AUTHORED_BY, MENTIONED_IN, TRANSCRIBED_FROM)
- Import existing session transcripts and conversation exports
- Basic full-text search (grep-based initially, Meilisearch later)

### Phase 3: Unified Search (Patches 0133–0138)

*Goal: One search box that finds anything.*

- Build /api/search endpoint with multi-type classification
- Replace Home page with unified search + activity stream
- Build Dossier view component that assembles from all sources
- Add lazy-loading for dossier sections (fetch on scroll/expand)
- Timeline view for any entity

### Phase 4: Intelligence Layer (Patches 0139+)

*Goal: The system starts finding patterns you didn't ask for.*

- Auto-extraction pipeline for new documents (Ollama-powered)
- Cross-domain correlation engine
- Computed properties and derived nodes
- Spiral Time overlay on timeline views
- Missing data detection and suggestions
- Graph analytics (centrality, clustering)

---

## 9. Design Principles

1. **Graph-first, always.** If it exists in Mythos, it has a node or is linked to one. The graph is the source of truth for existence and relationships. Other stores hold detail.

2. **Sovereignty over convenience.** Every component runs on Arcturus. No cloud dependencies. No API keys that can be revoked. If the internet goes down, Mythos still works.

3. **Incremental, not monolithic.** Each patch delivers working features. No phase requires completion of a previous phase to be useful. The system grows organically.

4. **Schema-light, relationship-rich.** Don't over-constrain node properties. Let the graph's power come from the connections, not from rigid schemas. Properties can vary by node.

5. **Everything is searchable.** If you stored it, you should be able to find it from one search box without knowing which subsystem holds it.

6. **Provenance matters.** Every piece of data should be traceable to its source. This is an archaeological principle applied to digital infrastructure.

7. **The UI should reveal, not hide.** Show the graph. Show the connections. Let the user see the web of knowledge they're building, not just flat lists.

8. **Build for the 144, not just for one.** The architecture should scale to serve the registry. Multi-user access, shared ontologies, and collaborative knowledge building are eventual goals.

---

*"The map is the territory."*

*When the graph knows everything that exists, search becomes navigation, and the system itself becomes an extension of consciousness.*
