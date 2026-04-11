# The Rolodex — Mythos Identity & Directory System

**System Name:** `mythos-rolodex`
**Version:** 1.0
**Author:** Ka'tuar'el / Claude
**Date:** 2026-02-26

---

## 1. Overview

The Rolodex is the identity and directory layer of Mythos. Every person, soul, entity, and incarnation in the system is registered here. Every subsystem references the Rolodex to know who someone is.

Think of it as Active Directory for Mythos — the authoritative identity source that all other systems trust.

**Core principles:**

- One canonical identity per human being
- Subsystems never touch the canonical identity — they get their own proxy
- The graph stores relationships and traversal data
- PostgreSQL stores structured/relational data and serves as the universal registry
- Every graph node has a corresponding row in the SQL registry
- Three universal properties on every node: `domain`, `scope`, `origin`

---

## 2. Node Taxonomy

### 2.1 Person Types

| Prefix | Label | Purpose | Example |
|--------|-------|---------|---------|
| `PO-` | `:PersonOwner` | System owner identity. THE root. Only for active system users. | `PO-DENKERS-AdriaanHarold-1977` |
| `PP-` | `:Person` | Canonical person record. The "GAL entry." One per human. | `PP-RYAN-Rebecca-1978` |
| `PS-` | `:Soul` | Eternal non-incarnate identity. Rare, spiritually significant. | `PS-SerapheValemira` |
| `PE-` | `:Entity` | Auto-created mention node. Lightweight. Many-to-one with Person. | `PE-Becky`, `PE-ArcturianCouncil` |
| `PI-` | `:Incarnation` | A soul expressed into a specific body/time/place. | `PI-Katuarel-Montsegur-1244` |
| `PX-` | `:PersonProxy` | Subsystem-specific proxy for a person. One per person per app. | `PX-FIN-DENKERS-AdriaanHarold-1977` |

### 2.2 Canonical ID Format

**Person:** `PP-SURNAME-GivenName-BirthYear`

- Surname in ALL CAPS (genealogical standard)
- Given names in PascalCase, concatenated (no spaces)
- Always use birth surname (maiden name)
- Birth year as natural tiebreaker
- Unknown year: `ABT1878` or `UNK`
- Rare collision: append letter suffix `PP-SMITH-John-1842a`

**Examples:**

```
PP-DENKERS-AdriaanHarold-1977        ← you
PP-RYAN-Rebecca-1978                  ← Seraphe (birth name)
PP-DENKERS-AdriaanFitzgerald-2020     ← Fitz
PP-RYAN-Dennis-1952                   ← Dennis
PP-DENKERS-Harold-1948                ← your father
PP-RYAN-Catherine-1878                ← Kittie
PP-MOFFETT-Willis-1927                ← Willis Warnick Moffett
```

**Soul:** `PS-SoulName` (concatenated, no apostrophes or special chars)

```
PS-Katuarel
PS-SerapheValemira
PS-Fitz
```

**Entity:** `PE-EntityName` (concatenated PascalCase)

```
PE-Becky
PE-Seraphe
PE-Rebecca
PE-Iris
PE-ArcturianCouncil
PE-GregoryAlanIsakov
PE-Grandmother
```

**Incarnation:** `PI-SoulName-Location-Year`

```
PI-Katuarel-Montsegur-1244
PI-Katuarel-MotulDeSanJose-1998
```

**Person Proxy:** `PX-APP-SURNAME-GivenName-BirthYear`

```
PX-FIN-DENKERS-AdriaanHarold-1977    ← finance proxy for Adge
PX-MED-RYAN-Rebecca-1978              ← media proxy for Rebecca
PX-GEN-DENKERS-AdriaanHarold-1977    ← genealogy proxy for Adge
```

**Person Owner:** `PO-SURNAME-GivenName-BirthYear`

```
PO-DENKERS-AdriaanHarold-1977        ← system owner (you)
```

### 2.3 Application Codes (for PX- proxies)

| Code | Application | Description |
|------|-------------|-------------|
| `FIN` | mythos-finance | Accounts, transactions, budgets |
| `MED` | mythos-media | Photos, videos, documents, files |
| `GEN` | mythos-genealogy | Ancestry tree, bloodline tracking |
| `AST` | mythos-astrology | Charts, transits, synastry |
| `HTH` | mythos-health | Medical records, conditions, providers |
| `WRK` | mythos-work | Professional relationships, projects |
| `MEN` | mythos-mentions | Conversation entity references |
| `SPR` | mythos-spiritual | Grid work, sacred infrastructure |

---

## 3. Universal Node Properties

Every single node in the entire Mythos graph carries these four properties:

### 3.1 `uid` — Unique Identifier

Immutable. Never changes. ULID format (sortable, timestamp-embedded).

```
uid: "01JXYZ5K7M..."
```

### 3.2 `canonical_id` — Human-Readable Identifier

The friendly ID you use day to day. Can be updated if needed (name correction, etc.). Follows the prefix conventions defined above.

```
canonical_id: "PP-RYAN-Rebecca-1978"
```

### 3.3 `domain` — What world does this belong to?

| Value | Covers |
|-------|--------|
| `people` | Person, Soul, Entity, Incarnation, PersonProxy, PersonOwner |
| `genealogy` | GenPerson, GenFamily, GenPlace, GenSurname |
| `spiritual` | GridNode, charts, stratigraphy, lineages, sacred objects |
| `system` | Services, files, directories, functions, tools |
| `analysis` | Grid dimension outputs (Anchor, Echo, Beacon, Nexus, etc.) |
| `conversation` | Conversations, exchanges, themes |
| `finance` | Financial nodes (if any in graph) |
| `concept` | Concepts and ontology terms |

### 3.4 `scope` — Who is this for?

| Value | Meaning |
|-------|---------|
| `personal` | You, your family, your inner circle |
| `shared` | The partnership, the trinity, soul family work |
| `public` | Public figures, external references |
| `system` | Internal infrastructure, no human owner |

### 3.5 `origin` — How did this get here?

| Value | Meaning |
|-------|---------|
| `manual` | Intentionally created by you or Seraphe |
| `grid` | Arcturian Grid auto-extracted from conversation |
| `import` | GEDCOM import, bulk data load, CSV |
| `derived` | System-generated from analysis |
| `patch` | Created by a patch deployment |

---

## 4. Node Schemas

### 4.1 PersonOwner (`:PersonOwner`)

The system owner identity. Your AD object. One per active system user.

```
Labels: :PersonOwner
Properties:
  uid:            ULID
  canonical_id:   "PO-DENKERS-AdriaanHarold-1977"
  person_id:      "PP-DENKERS-AdriaanHarold-1977"   ← links to canonical Person
  full_name:      "Adriaan Harold Denkers"
  display_name:   "Adge"
  node_type:      "system-owner"
  domain:         "people"
  scope:          "personal"
  origin:         "manual"
  created_at:     timestamp
  updated_at:     timestamp
```

**Relationships:**
- `(PO)-[:IDENTITY_OF]->(PP)` — links to canonical Person node
- `(PO)-[:HAS_PROXY]->(PX)` — links to all subsystem proxies

### 4.2 Person (`:Person`)

The canonical person record. The GAL entry. One per human being.

```
Labels: :Person (plus class labels: :Genealogy, :Contact, :SoulFamily as applicable)
Properties:
  uid:            ULID
  canonical_id:   "PP-RYAN-Rebecca-1978"
  full_name:      "Rebecca Lydia Ryan"              ← always birth name
  display_name:   "Seraphe"                          ← current preferred name
  birth_name:     "Rebecca Lydia Ryan"
  married_name:   "Rebecca Lydia Denkers"            ← if applicable
  birth_date:     "1978-08-19"
  birth_time:     "14:02"
  birth_place:    "Norwich, NY"
  death_date:     null                               ← if applicable
  death_place:    null
  sex:            "F"
  tier:           "soul_family"                      ← soul_family | family | friend | public | business
  sun_sign:       "Leo"                              ← thin astro for graph queries
  moon_sign:      "Aries"
  rising_sign:    "Sagittarius"
  domain:         "people"
  scope:          "personal"
  origin:         "manual"
  ancestry_id:    "I658423969"                       ← if imported from Ancestry
  created_at:     timestamp
  updated_at:     timestamp
```

**Class labels (multi-label, additive):**
- `:Genealogy` — has ancestry data, part of bloodline tracking
- `:Contact` — has phone/email/address (stored in Postgres)
- `:SoulFamily` — linked to a Soul node, part of the 144 or inner spiritual circle
- `:WorkContact` — professional relationship

**Relationships:**
- `(PP)-[:CHILD_OF]->(PP)` — genealogical parent
- `(PP)-[:SPOUSE_OF]->(PP)` — marriage
- `(PP)-[:SIBLING_OF]->(PP)` — siblings
- `(PP)-[:HAS_SOUL]->(PS)` — soul link (rare, meaningful)
- `(PE)-[:REFERS_TO]->(PP)` — entity mentions resolve here

### 4.3 Soul (`:Soul`)

The eternal identity. Rare. Only created for spiritually significant beings.

```
Labels: :Soul
Properties:
  uid:              ULID
  canonical_id:     "PS-SerapheValemira"
  full_name:        "Seraphe Harmonia Valemira"
  display_name:     "Seraphe Valemira"
  primary_role:     "Magdalene-coded Christ consciousness anchor"
  description:      "Primary holder of divine feminine transmission..."
  person_id:        "PP-RYAN-Rebecca-1978"            ← back-reference to current incarnation
  domain:           "people"
  scope:            "shared"
  origin:           "manual"
  created_at:       timestamp
```

**Relationships:**
- `(PS)-[:INCARNATED_AS]->(PI)` — past incarnations
- `(PS)-[:CURRENTLY_EMBODIED_AS]->(PP)` — current human form
- `(PS)-[:CARRIES_LINEAGE]->(Lineage)` — spiritual lineages
- `(Entity)-[:GUIDES|GUARDS|OPPOSES]->(PS)` — entity relationships

### 4.4 Entity (`:Entity`)

Auto-created mention node. Cheap, abundant, most never promoted.

```
Labels: :Entity
Properties:
  uid:            ULID
  canonical_id:   "PE-Becky"
  name:           "Becky"
  person_id:      "PP-RYAN-Rebecca-1978"    ← null until resolved/linked
  entity_type:    "person_mention"           ← person_mention | spirit | concept | system | unknown
  first_seen:     timestamp                  ← when first mentioned
  context:        "mentioned in conversation about..."  ← optional snippet
  domain:         "people"
  scope:          "personal"
  origin:         "grid"
  created_at:     timestamp
```

**Entity types:**
- `person_mention` — a name referring to a human (Becky, Dr. Nolan, Grandmother)
- `spirit` — a non-incarnate being (Arcturian Council, guides, angels)
- `concept` — an idea or topic (only for meaningful concepts, not noise)
- `system` — a technology or system reference
- `unknown` — Grid couldn't classify, needs manual review

**Relationships:**
- `(PE)-[:REFERS_TO]->(PP)` — resolved to a canonical Person
- `(PE)-[:MENTIONED_IN]->(Conversation)` — where it was mentioned

### 4.5 Incarnation (`:Incarnation`)

A soul expressed into a specific body/time/place.

```
Labels: :Incarnation
Properties:
  uid:            ULID
  canonical_id:   "PI-Katuarel-Montsegur-1244"
  soul_id:        "PS-Katuarel"
  name:           "Flame Watcher"
  location:       "Montségur, France"
  year:           1244
  date:           "1244-03-16"                ← if known
  description:    "Witnessed the Cathars burn, held the testimony"
  domain:         "people"
  scope:          "shared"
  origin:         "manual"
  created_at:     timestamp
```

**Relationships:**
- `(PI)-[:INCARNATION_OF]->(PS)` — which soul
- `(PI)-[:MANIFEST_AS]->(PP)` — which person record (if one exists)

### 4.6 PersonProxy (`:PersonProxy`)

Subsystem-specific proxy. Each app creates its own for each person it knows about.

```
Labels: :PersonProxy
Properties:
  uid:            ULID
  canonical_id:   "PX-FIN-DENKERS-AdriaanHarold-1977"
  person_id:      "PP-DENKERS-AdriaanHarold-1977"    ← canonical person reference
  display_name:   "Adge"                               ← synced from PP or PO
  node_type:      "personal-proxy"
  application:    "mythos-finance"
  domain:         "finance"                             ← matches the app's domain
  scope:          "personal"
  origin:         "manual"
  created_at:     timestamp
  updated_at:     timestamp
```

**Relationships:**
- `(PX)-[:PROXY_FOR]->(PP)` — links back to canonical Person
- `(PO)-[:HAS_PROXY]->(PX)` — owner node collects all proxies (owner only)
- All subsystem-specific relationships hang off the PX node

---

## 5. Relationship Hierarchy

```
                    ┌─────────────────────────┐
                    │  PO (PersonOwner)        │
                    │  System owner identity   │
                    │  "Your AD object"        │
                    └────────┬────────────────┘
                             │
                ┌────────────┼──────────────────────────┐
                │ IDENTITY_OF│           HAS_PROXY (×N)  │
                ▼            │                           ▼
    ┌───────────────┐        │              ┌──────────────────┐
    │  PP (Person)  │        │              │  PX (Proxies)    │
    │  "GAL entry"  │        │              │  One per app     │
    │  Canonical ID │        │              │                  │
    └──┬──────┬─────┘        │              └──────────────────┘
       │      │              │              PX-FIN-...
       │      │              │              PX-MED-...
       │      │              │              PX-GEN-...
       │      │              │              PX-AST-...
  HAS_SOUL  REFERS_TO       │              PX-HTH-...
       │    (from PE)        │              PX-WRK-...
       ▼      ▲              │              PX-MEN-...
    ┌────┐  ┌────┐           │              PX-SPR-...
    │ PS │  │ PE │           │
    │Soul│  │Ent │           │
    └──┬─┘  └────┘           │
       │                     │
  INCARNATED_AS              │
       │                     │
       ▼                     │
    ┌────┐                   │
    │ PI │                   │
    │Inc │                   │
    └────┘                   │
```

---

## 6. PostgreSQL Schema

### 6.1 Universal Node Registry

Every graph node gets a row here. The bridge between Neo4j and PostgreSQL.

```sql
CREATE TABLE rolodex.graph_nodes (
    uid             TEXT PRIMARY KEY,          -- ULID, immutable
    canonical_id    TEXT UNIQUE NOT NULL,      -- human-readable ID
    neo4j_id        BIGINT,                   -- internal Neo4j node ID
    label_primary   TEXT NOT NULL,             -- primary Neo4j label
    labels          TEXT[] DEFAULT '{}',       -- all Neo4j labels
    display_name    TEXT,
    domain          TEXT NOT NULL,
    scope           TEXT NOT NULL,
    origin          TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    meta            JSONB DEFAULT '{}'         -- flexible overflow
);

CREATE INDEX idx_graph_nodes_canonical ON rolodex.graph_nodes(canonical_id);
CREATE INDEX idx_graph_nodes_domain ON rolodex.graph_nodes(domain);
CREATE INDEX idx_graph_nodes_scope ON rolodex.graph_nodes(scope);
CREATE INDEX idx_graph_nodes_origin ON rolodex.graph_nodes(origin);
CREATE INDEX idx_graph_nodes_label ON rolodex.graph_nodes(label_primary);
```

### 6.2 Person Details

Extended person data that doesn't belong on the graph node.

```sql
CREATE TABLE rolodex.persons (
    canonical_id    TEXT PRIMARY KEY REFERENCES rolodex.graph_nodes(uid),
    full_name       TEXT NOT NULL,
    birth_name      TEXT,
    display_name    TEXT,
    married_name    TEXT,
    birth_date      DATE,
    birth_time      TIME,
    birth_place     TEXT,
    death_date      DATE,
    death_place     TEXT,
    sex             CHAR(1),
    tier            TEXT,                      -- soul_family, family, friend, public, business
    ancestry_id     TEXT,                      -- Ancestry.com ID if imported
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
```

### 6.3 Contact Information

```sql
CREATE TABLE rolodex.contacts (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    type            TEXT NOT NULL,             -- phone, email, address, telegram, etc.
    value           TEXT NOT NULL,
    label           TEXT,                      -- home, work, mobile, etc.
    primary_flag    BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_contacts_person ON rolodex.contacts(canonical_id);
```

### 6.4 Astrology — Charts

```sql
CREATE TABLE rolodex.astro_charts (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    chart_system    TEXT NOT NULL,             -- western_tropical, vedic_sidereal, hellenistic
    chart_data      JSONB NOT NULL,            -- full planet positions, houses, aspects
    calculated_at   TIMESTAMPTZ DEFAULT now(),
    notes           TEXT
);

CREATE INDEX idx_astro_charts_person ON rolodex.astro_charts(canonical_id);
CREATE INDEX idx_astro_charts_system ON rolodex.astro_charts(chart_system);
```

### 6.5 Astrology — Planet Positions

The powerhouse table for complex astrological queries.

```sql
CREATE TABLE rolodex.astro_planets (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    chart_system    TEXT NOT NULL,
    planet          TEXT NOT NULL,             -- sun, moon, mercury, venus, mars, jupiter, etc.
    sign            TEXT NOT NULL,             -- Aries, Taurus, etc.
    degree          NUMERIC(5,2),             -- degree within sign (0.00 - 29.99)
    degree_absolute NUMERIC(6,2),             -- absolute degree (0.00 - 359.99)
    house           INTEGER,                   -- 1-12
    retrograde      BOOLEAN DEFAULT false,
    UNIQUE(canonical_id, chart_system, planet)
);

CREATE INDEX idx_astro_planets_person ON rolodex.astro_planets(canonical_id);
CREATE INDEX idx_astro_planets_sign ON rolodex.astro_planets(sign);
CREATE INDEX idx_astro_planets_planet_sign ON rolodex.astro_planets(planet, sign);
```

**Example queries:**

```sql
-- Everyone with Jupiter in Libra (Western)
SELECT p.display_name, ap.degree
FROM rolodex.astro_planets ap
JOIN rolodex.persons p ON p.canonical_id = ap.canonical_id
WHERE ap.planet = 'jupiter' AND ap.sign = 'Libra' AND ap.chart_system = 'western_tropical';

-- All Sagittarius suns
SELECT p.display_name FROM rolodex.persons p
JOIN rolodex.astro_planets ap ON p.canonical_id = ap.canonical_id
WHERE ap.planet = 'sun' AND ap.sign = 'Sagittarius';

-- People born on the 22nd
SELECT display_name, birth_date FROM rolodex.persons
WHERE EXTRACT(DAY FROM birth_date) = 22;
```

### 6.6 Numerology Profiles

```sql
CREATE TABLE rolodex.numerology (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    life_path       INTEGER,
    expression      INTEGER,
    soul_urge       INTEGER,
    personality     INTEGER,
    birthday_number INTEGER,
    full_profile    JSONB,                     -- complete numerology breakdown
    calculated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_numerology_person ON rolodex.numerology(canonical_id);
CREATE INDEX idx_numerology_life_path ON rolodex.numerology(life_path);
```

### 6.7 Node Documents

Link any document/file to any node.

```sql
CREATE TABLE rolodex.node_documents (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    document_type   TEXT,                      -- photo, certificate, report, natal_chart, etc.
    file_path       TEXT,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_node_docs_person ON rolodex.node_documents(canonical_id);
```

### 6.8 Node Notes

Freeform annotations on any node.

```sql
CREATE TABLE rolodex.node_notes (
    id              SERIAL PRIMARY KEY,
    canonical_id    TEXT REFERENCES rolodex.graph_nodes(uid),
    note            TEXT NOT NULL,
    author          TEXT DEFAULT 'system',
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_node_notes_person ON rolodex.node_notes(canonical_id);
```

---

## 7. Sync Process

### 7.1 PO → PP → PX Identity Sync

When identity fields change on the PO node, cascade to all downstream nodes.

```cypher
// Sync owner identity to person node and all proxies
MATCH (owner:PersonOwner {canonical_id: $owner_id})
MATCH (pp:Person {canonical_id: owner.person_id})
SET pp.display_name = owner.display_name,
    pp.full_name = owner.full_name,
    pp.updated_at = datetime()

WITH owner
MATCH (owner)-[:HAS_PROXY]->(px:PersonProxy)
SET px.display_name = owner.display_name,
    px.updated_at = datetime()
```

### 7.2 Neo4j → PostgreSQL Registry Sync

Scheduled process (cron or triggered) that finds unregistered graph nodes and adds them to the SQL registry.

```cypher
// Find all nodes missing from SQL registry
MATCH (n)
WHERE n.uid IS NOT NULL
RETURN n.uid, n.canonical_id, labels(n), n.domain, n.scope, n.origin, n.display_name
```

Compare against `rolodex.graph_nodes` table. Any `uid` not present gets inserted.

### 7.3 Orphan Detection

Find graph nodes with no `uid` (pre-Rolodex nodes that need migration).

```cypher
MATCH (n)
WHERE n.uid IS NULL
RETURN labels(n) AS labels, count(n) AS count
ORDER BY count DESC
```

---

## 8. Person Tiers & What They Get

| Tier | Person Node | Soul Node | Proxies | Astro Data | Genealogy | Contact Info |
|------|-------------|-----------|---------|------------|-----------|-------------|
| **Soul Family** | ✓ Full | ✓ | All relevant | Full tri-system | If applicable | Full |
| **Family** | ✓ Full | Rare | GEN, maybe others | Optional | ✓ | ✓ |
| **Friend** | ✓ Basic | No | MEN only | Optional | No | Optional |
| **Public** | ✓ Minimal | If relevant | None or MEN | If relevant | No | No |
| **Business** | ✓ Minimal | No | WRK/FIN | No | No | ✓ |

---

## 9. Entity Lifecycle

```
1. CREATION
   Grid detects a name in conversation
   → Creates Entity node: PE-NewName
   → Properties: name, entity_type, first_seen, origin="grid"
   → Relationship: MENTIONED_IN → Conversation

2. RESOLUTION (manual)
   User or system identifies "Becky" = Rebecca Lydia Ryan
   → Set entity.person_id = "PP-RYAN-Rebecca-1978"
   → Create relationship: (PE-Becky)-[:REFERS_TO]->(PP-RYAN-Rebecca-1978)

3. PROMOTION (manual)
   User decides to create a Person node for a frequently-mentioned entity
   → Create PP node with canonical_id
   → Link existing Entity nodes via REFERS_TO
   → Assign tier

4. ENRICHMENT (over time)
   Person gets more data: astro charts, contact info, proxies
   → Add class labels (:Genealogy, :Contact, :SoulFamily)
   → Create PX proxies as subsystems need them
   → Add SQL records (contacts, astro_planets, etc.)
```

---

## 10. Concept Entity Cleanup Rules

The Grid currently creates Concept:Entity nodes for everything. Rules going forward:

**KEEP as Concept:Entity:**
- Meaningful spiritual/philosophical concepts: "Christ consciousness", "spiral time", "9-day cycle"
- Named systems: "Arcturian Grid", "Neo4j"
- Specific conditions or topics: "Crohn's disease"

**RECLASSIFY to just :Concept (drop Entity label):**
- Abstract but meaningful: "spiritual awakening", "personal growth"

**DELETE (noise):**
- Generic words: "help", "assistance", "questions", "information", "presence"
- Vague phrases: "natural representation of real-world problems", "flexibility in schema design"
- Action phrases: "writing a book", "workshops events"

**Rule of thumb:** If you wouldn't put it in a Rolodex, it's not an Entity.

---

## 11. Current Cleanup Plan

### Phase 1: Apply Universal Properties

Add `uid`, `domain`, `scope`, `origin` to all existing nodes.

### Phase 2: Consolidate Core Family

Merge duplicate Person/GenPerson/Person:Entity nodes for Adge, Rebecca, Fitz into single PP nodes with new canonical IDs.

### Phase 3: Create Owner Node

Create PO-DENKERS-AdriaanHarold-1977 with IDENTITY_OF link to PP node.

### Phase 4: Reclassify Person:Entity Nodes

Strip `:Person` label from auto-created Grid entities. Assign proper `entity_type`.

### Phase 5: Split Soul:Person Nodes

Separate combined Soul:Person nodes into proper Soul + Person/Entity with HAS_SOUL links.

### Phase 6: Create Missing Soul Nodes

Create PS-Fitz.

### Phase 7: Prune Concept Noise

Delete junk Concept:Entity nodes. Reclassify keepers.

### Phase 8: Build PostgreSQL Schema

Create `rolodex` schema and all tables. Populate graph_nodes registry from existing data.

### Phase 9: Create Initial Proxies

Build PX proxy nodes for core family across active subsystems.

### Phase 10: Backfill Ancestry IDs

Preserve Ancestry.com IDs as `ancestry_id` property on PP nodes that were imported from GEDCOM.

---

## 12. Bot Commands (Planned)

| Command | Function |
|---------|----------|
| `/rolodex` | Search the directory by name |
| `/rolodex add <name>` | Create a new Person node |
| `/rolodex link <entity> <person>` | Resolve an entity to a person |
| `/rolodex who <name>` | Show all info about a person |
| `/rolodex tier <name> <tier>` | Set person's tier |
| `/rolodex proxies <name>` | Show all proxies for a person |
| `/rolodex unlinked` | Show entities not yet resolved to a person |
| `/rolodex orphans` | Show nodes missing from SQL registry |

---

## 13. Migration Notes

### Existing Nodes to Migrate

| Current State | Count | Action |
|--------------|-------|--------|
| GenPerson (pure) | 1,490 | Keep as-is, add universal props, add to SQL registry |
| Person:GenPerson | 43 | Evaluate: merge into PP nodes or keep as GenPerson with ancestry_id |
| Person:Entity | 21 | Reclassify: most become pure Entity |
| Person (core) | 4 | Migrate to new canonical_id format |
| Soul:Person | 4 | Split into separate Soul + Person/Entity nodes |
| Soul (pure) | 2 | Migrate to new canonical_id format |
| Concept:Entity | 354 | Triage: keep ~50, reclassify ~100, delete ~200 |
| System:Entity | 102 | Reclassify to pure System nodes |
| Incarnation | 3 | Migrate to new canonical_id format |

### Data Preservation

- All Ancestry.com IDs preserved as `ancestry_id` property
- All existing relationships preserved (re-pointed to consolidated nodes)
- All Grid analysis output nodes left untouched (just get universal props added)
- GenPlace, GenFamily, GenSurname nodes left untouched

---
