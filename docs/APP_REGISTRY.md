---
title: "Neo4j Application Registry"
category: grid
status: active
stream: SYS
location: docs
tags: [registry, neo4j, system]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Neo4j Application Registry
> **Version:** 1.0.0
> **Last Updated:** 2026-02-27
> **Total Registered Apps:** 9
> **Total Graph Nodes:** ~5,668

---

## ⚠️ CRITICAL: READ BEFORE TOUCHING NEO4J

**Every node in the Neo4j graph belongs to a registered application.**

Before creating, modifying, or deleting ANY nodes:
1. Check this registry to see which app owns the label
2. Only modify nodes belonging to the app you are working on
3. If adding a NEW label, register it here first
4. If removing an app, use the cleanup queries in this document

**This file is the source of truth.** The `:AppRegistry` nodes in Neo4j mirror this document.

---

## Registered Applications

### 1. `genealogy` — Genealogical Research Data

**Purpose:** GEDCOM-imported family tree data from genealogical research.
**Source code:** Imported via external tools, managed via `db_manager.py`
**Node count:** ~3,872 nodes (68% of graph)

| Label | Count | Description |
|-------|-------|-------------|
| `GenPerson` | 1,490 | Individuals from genealogical records |
| `GenPlace` | 1,280 | Birth/death/marriage locations |
| `GenFamily` | 653 | Family unit groupings |
| `GenSurname` | 449 | Surname tracking nodes |

| Relationship | Description |
|-------------|-------------|
| `PARENT_OF` | Parent → child (within GenPerson) |
| `CHILD_OF` | Child → parent (within GenPerson) |
| `BORN_IN` | GenPerson → GenPlace |
| `DIED_IN` | GenPerson → GenPlace |
| `MARRIED_TO` | GenPerson ↔ GenPerson |
| `MARRIED_IN` | GenPerson → GenPlace |
| `BELONGS_TO_FAMILY` | GenPerson → GenFamily |
| `HAS_SURNAME` | GenPerson → GenSurname |

**Cleanup query:**
```cypher
// Count all genealogy nodes
MATCH (n) WHERE n:GenPerson OR n:GenPlace OR n:GenFamily OR n:GenSurname
RETURN labels(n)[0] AS label, count(*) AS count

// DELETE all genealogy data (DESTRUCTIVE)
MATCH (n) WHERE n:GenPerson OR n:GenPlace OR n:GenFamily OR n:GenSurname
DETACH DELETE n
```

---

### 2. `grid_worker` — Arcturian Grid Processing

**Purpose:** 9-node consciousness grid analysis. Processes messages through the grid and stores dimensional analysis results.
**Source code:** `/opt/mythos/workers/grid_worker.py`
**Node count:** ~9 permanent GridNodes + ~100 output nodes per full analysis

| Label | Count | Description |
|-------|-------|-------------|
| `GridNode` | 9 | The 9 permanent grid dimensions (Anchor, Echo, Beacon, etc.) |
| `Theme` | 311 | Themes extracted from grid analysis |
| `AnchorOutput` | 1 | Anchor dimension analysis result |
| `EchoOutput` | 1 | Echo dimension analysis result |
| `BeaconOutput` | 1 | Beacon dimension analysis result |
| `SynthOutput` | 1 | Synth dimension analysis result |
| `NexusOutput` | 1 | Nexus dimension analysis result |
| `MirrorOutput` | 1 | Mirror dimension analysis result |
| `GlyphOutput` | 1 | Glyph dimension analysis result |
| `HarmoniaOutput` | 1 | Harmonia dimension analysis result |
| `GatewayOutput` | 1 | Gateway dimension analysis result |
| `GridMasterOutput` | 1 | Master synthesis output |
| `GatewaySafetyCheck` | 1 | Gateway safety validation |

**Grid output sub-nodes** (created by grid analysis, linked to output nodes):

| Label | Description |
|-------|-------------|
| `Value` | Values identified in Beacon analysis |
| `Emotion` | Emotions in Mirror analysis |
| `EmotionalNeed` | Needs in Mirror analysis |
| `Symbol` | Symbols in Glyph analysis |
| `Relationship` | Relationships in Harmonia analysis |
| `Event` | Events across multiple dimensions |
| `Direction` | Directional guidance from Beacon |
| `Location` | Locations from Anchor analysis |
| `Integration` | Integration points from Synth |
| `IntegrationGap` | Gaps identified by Synth |
| `Commitment` | Commitments from Nexus |
| `DecisionGate` | Decision points from Nexus |
| `Shadow` | Shadow elements from Mirror |
| `Wound` | Wounds from Mirror |
| `Archetype` | Archetypes from Glyph |
| `SacredObject` | Sacred objects from Glyph |
| `Role` | Roles from Harmonia |
| `Threshold` | Thresholds from Gateway |
| `Portal` | Portals from Gateway |
| `Dream` | Dreams from Gateway |
| `Defense` | Defenses from Mirror |
| `PotentialTrigger` | Triggers from Mirror |
| `MagicalAct` | Magical acts from Glyph |
| `SupportGap` | Support gaps from Harmonia |
| `Transmission` | Transmissions from Gateway |
| `Activation` | Activations from Gateway |
| `Rupture` | Ruptures from Harmonia |
| `Repair` | Repairs from Harmonia |
| `CommunicationGap` | Communication gaps from Harmonia |
| `BoundaryNeeded` | Boundaries from Nexus |
| `CapacityAssessment` | Capacity from Nexus |
| `ConvergencePoint` | Convergence from Nexus |
| `Boundary` | Boundaries from Nexus |
| `FinancialCondition` | Financial state from Beacon |
| `PlannedExpense` | Planned expenses from Beacon |
| `Manifestation` | Manifestations from Beacon |
| `ValueTension` | Value tensions from Beacon |
| `RitualElement` | Ritual elements from Glyph |
| `RitualGap` | Ritual gaps from Glyph |
| `Concern` | Concerns from Anchor |

| Relationship | Description |
|-------------|-------------|
| `HAS_THEME` | Various → Theme |
| `ACTIVATED` | Grid processing activation |
| `DISCUSSED` | Exchange → Theme/Concept |
| `INVOLVES` | Various → Entity/Person |
| `ANCHOR_OBJECT` | AnchorOutput → Object |
| `ANCHOR_LOCATION` | AnchorOutput → Location |
| `ANCHOR_CONCERN` | AnchorOutput → Concern |
| `ANCHOR_ASSESSMENT` | AnchorOutput → assessment |
| `ECHO_EVENT` | EchoOutput → Event |
| `ECHO_PATTERN` | EchoOutput → Pattern |
| `ECHO_IDENTITY` | EchoOutput → IdentityThread |
| `ECHO_ASSESSMENT` | EchoOutput → assessment |
| `BEACON_VALUE` | BeaconOutput → Value |
| `BEACON_DIRECTION` | BeaconOutput → Direction |
| `BEACON_FINANCIAL` | BeaconOutput → FinancialCondition |
| `BEACON_EXPENSE` | BeaconOutput → PlannedExpense |
| `BEACON_MANIFESTED` | BeaconOutput → Manifestation |
| `BEACON_TENSION` | BeaconOutput → ValueTension |
| `BEACON_ASSESSMENT` | BeaconOutput → assessment |
| `SYNTH_SYSTEM` | SynthOutput → system analysis |
| `SYNTH_INTEGRATION` | SynthOutput → Integration |
| `SYNTH_GAP` | SynthOutput → IntegrationGap |
| `SYNTH_TOOL_NEEDED` | SynthOutput → tool needed |
| `SYNTH_TOOL_USED` | SynthOutput → tool used |
| `SYNTH_ASSESSMENT` | SynthOutput → assessment |
| `NEXUS_COMMITMENT` | NexusOutput → Commitment |
| `NEXUS_GATE` | NexusOutput → DecisionGate |
| `NEXUS_BOUNDARY_NEEDED` | NexusOutput → BoundaryNeeded |
| `NEXUS_CAPACITY` | NexusOutput → CapacityAssessment |
| `NEXUS_CONVERGENCE` | NexusOutput → ConvergencePoint |
| `NEXUS_BOUNDARY` | NexusOutput → Boundary |
| `NEXUS_ASSESSMENT` | NexusOutput → assessment |
| `MIRROR_EMOTION` | MirrorOutput → Emotion |
| `MIRROR_NEED` | MirrorOutput → EmotionalNeed |
| `MIRROR_SHADOW` | MirrorOutput → Shadow |
| `MIRROR_WOUND` | MirrorOutput → Wound |
| `MIRROR_DEFENSE` | MirrorOutput → Defense |
| `MIRROR_TRIGGER_POTENTIAL` | MirrorOutput → PotentialTrigger |
| `MIRROR_ASSESSMENT` | MirrorOutput → assessment |
| `GLYPH_SYMBOL` | GlyphOutput → Symbol |
| `GLYPH_ARCHETYPE` | GlyphOutput → Archetype |
| `GLYPH_SACRED_OBJECT` | GlyphOutput → SacredObject |
| `GLYPH_MAGIC` | GlyphOutput → MagicalAct |
| `GLYPH_RITUAL` | GlyphOutput → RitualElement |
| `GLYPH_RITUAL_GAP` | GlyphOutput → RitualGap |
| `GLYPH_ASSESSMENT` | GlyphOutput → assessment |
| `HARMONIA_RELATIONSHIP` | HarmoniaOutput → Relationship |
| `HARMONIA_ROLE` | HarmoniaOutput → Role |
| `HARMONIA_SUPPORT_GAP` | HarmoniaOutput → SupportGap |
| `HARMONIA_RUPTURE` | HarmoniaOutput → Rupture |
| `HARMONIA_REPAIR` | HarmoniaOutput → Repair |
| `HARMONIA_COMM_GAP` | HarmoniaOutput → CommunicationGap |
| `HARMONIA_ASSESSMENT` | HarmoniaOutput → assessment |
| `GATEWAY_THRESHOLD` | GatewayOutput → Threshold |
| `GATEWAY_PORTAL` | GatewayOutput → Portal |
| `GATEWAY_TRANSMISSION` | GatewayOutput → Transmission |
| `GATEWAY_ACTIVATION` | GatewayOutput → Activation |
| `GATEWAY_DREAM` | GatewayOutput → Dream |
| `GATEWAY_ASSESSMENT` | GatewayOutput → assessment |
| `SAFETY_CHECK` | GatewayOutput → GatewaySafetyCheck |
| `GRID_MASTER_OUTPUT` | → GridMasterOutput |

**Cleanup query:**
```cypher
// Count grid output nodes (excludes permanent GridNode)
MATCH (n) WHERE n:Theme OR n:AnchorOutput OR n:EchoOutput OR n:BeaconOutput
  OR n:SynthOutput OR n:NexusOutput OR n:MirrorOutput OR n:GlyphOutput
  OR n:HarmoniaOutput OR n:GatewayOutput OR n:GridMasterOutput
  OR n:GatewaySafetyCheck
RETURN labels(n)[0] AS label, count(*) AS count

// DELETE grid outputs only (keeps permanent GridNode)
MATCH (n) WHERE n:Theme OR n:AnchorOutput OR n:EchoOutput OR n:BeaconOutput
  OR n:SynthOutput OR n:NexusOutput OR n:MirrorOutput OR n:GlyphOutput
  OR n:HarmoniaOutput OR n:GatewayOutput OR n:GridMasterOutput
  OR n:GatewaySafetyCheck
DETACH DELETE n
```

---

### 3. `ontology` — Ontology & Concept System

**Purpose:** Ontological terms and concepts that define the Mythos vocabulary and knowledge structure.
**Source code:** `/opt/mythos/core/ontology_seed.py`, `/opt/mythos/api/routes/ontology.py`
**Node count:** ~448 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `OntologyTerm` | 94 | Defined ontological vocabulary terms |
| `Concept` | 354 | Abstract concepts and ideas |

| Relationship | Description |
|-------------|-------------|
| `RELATED_TO` | Concept ↔ Concept associations |
| `DESCRIBES` | OntologyTerm → Concept |
| `DEFINES` | OntologyTerm → definition relationships |
| `CONTAINS` | Grouping/hierarchy |
| `PART_OF` | Hierarchical membership |
| `REFERS_TO` | Cross-references |

**Cleanup query:**
```cypher
MATCH (n) WHERE n:OntologyTerm OR n:Concept
RETURN labels(n)[0] AS label, count(*) AS count

MATCH (n) WHERE n:OntologyTerm OR n:Concept
DETACH DELETE n
```

---

### 4. `conversation_logger` — Conversation & Exchange Tracking

**Purpose:** Logs conversations and individual message exchanges to the graph for context retrieval and analysis.
**Source code:** `/opt/mythos/llm_diagnostics/src/conversation_logger.py`, grid worker exchange creation
**Node count:** ~169 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Exchange` | 163 | Individual message/response pairs |
| `Conversation` | 6 | Conversation thread containers |

| Relationship | Description |
|-------------|-------------|
| `HAD_CONVERSATION` | Person → Conversation |
| `INCLUDES` | Conversation → Exchange |
| `FOLLOWED_BY` | Exchange → Exchange (sequence) |
| `MENTIONED` | Exchange → Entity/Person (entity extraction) |

**Cleanup query:**
```cypher
MATCH (n) WHERE n:Exchange OR n:Conversation
RETURN labels(n)[0] AS label, count(*) AS count

MATCH (n) WHERE n:Exchange OR n:Conversation
DETACH DELETE n
```

---

### 5. `people_manager` — People & Contact Management

**Purpose:** People tracked through the Telegram `/person` command and people API. Distinct from GenPerson (genealogy) — these are living contacts and known individuals.
**Source code:** `/opt/mythos/api/routes/people.py`, `/opt/mythos/api/routes/rolodex.py`
**Node count:** ~50 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Person` | 47 | Living people, contacts, known individuals |
| `PersonOwner` | 3 | Ownership/creator tracking |

| Relationship | Description |
|-------------|-------------|
| `INVOLVES` | Various → Person |
| `MENTIONED` | Exchange → Person |
| `IDENTITY_OF` | PersonOwner → Person |
| `BETWEEN` | Relationship → Person |

**Cleanup query:**
```cypher
MATCH (n) WHERE n:Person OR n:PersonOwner
RETURN labels(n)[0] AS label, count(*) AS count
```

---

### 6. `system_monitor` — System Infrastructure Mapping

**Purpose:** Maps the Arcturus system infrastructure — services, processes, files, directories — into the graph for self-awareness.
**Source code:** `/opt/mythos/graph_logging/src/system_monitor.py`, `/opt/mythos/graph_logging/src/event_logger.py`
**Node count:** ~649 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Process` | 514 | Running/historical processes |
| `System` | 106 | System state snapshots |
| `Service` | 11 | Systemd services |
| `File` | 11 | Tracked files |
| `Directory` | 7 | Tracked directories |
| `Function` | 5 | Tracked functions |
| `Tool` | 3 | System tools |
| `TestMachine` | 1 | Test infrastructure |
| `TestRun` | 1 | Test execution records |

| Relationship | Description |
|-------------|-------------|
| `RUNS` | System → Process |
| `RUNS_SERVICE` | System → Service |
| `CONTAINS` | Directory → File |
| `CALLS` | Function → Function |
| `READS_CONFIG` | Service → File |
| `IMPLEMENTS` | Code → Function |
| `IMPORTS` | File → Module |
| `USES` | Service → Tool |
| `HAD_TEST_RUN` | TestMachine → TestRun |
| `TESTED_BY` | System → TestRun |
| `CONNECTS_TO` | Service → Service |

**Cleanup query:**
```cypher
MATCH (n) WHERE n:Process OR n:System OR n:Service OR n:File
  OR n:Directory OR n:Function OR n:Tool OR n:TestMachine OR n:TestRun
RETURN labels(n)[0] AS label, count(*) AS count

MATCH (n) WHERE n:Process OR n:System OR n:Service OR n:File
  OR n:Directory OR n:Function OR n:Tool OR n:TestMachine OR n:TestRun
DETACH DELETE n
```

---

### 7. `astrology` — Natal Charts & Numerology

**Purpose:** Astrological chart data, numerological analysis, and Soul Stratigraphy results.
**Source code:** `/opt/mythos/patches/astrology_system/charts/chart_calculator.py`
**Node count:** ~10 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Chart` | 6 | Natal/transit chart data |
| `Numerology` | 2 | Numerological analysis |
| `SoulStratigraphy` | 2 | Tri-field astro analysis results |

| Relationship | Description |
|-------------|-------------|
| `HAS_CHART` | Person → Chart |
| `HAS_NUMEROLOGY` | Person → Numerology |
| `HAS_STRATIGRAPHY` | Person → SoulStratigraphy |

**Cleanup query:**
```cypher
MATCH (n) WHERE n:Chart OR n:Numerology OR n:SoulStratigraphy
RETURN labels(n)[0] AS label, count(*) AS count
```

---

### 8. `spiritual_core` — Soul Identity & Incarnation Registry

**Purpose:** The sacred core — soul identities, incarnation records, and lineage tracking. This is the foundational spiritual infrastructure.
**Source code:** Manual creation, `db_manager.py`
**Node count:** ~11 nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Soul` | 6 | Eternal spiritual identities |
| `Incarnation` | 3 | Specific lifetime instances |
| `Lineage` | 2 | Bloodline/spiritual lineage chains |

| Relationship | Description |
|-------------|-------------|
| `CURRENTLY_EMBODIED_AS` | Soul → Person |
| `INCARNATED_AS` | Soul → Incarnation |
| `MANIFESTED_AS` | Incarnation → Person |
| `HAS_SOUL` | Person → Soul |
| `EMBODIES` | Person → spiritual identity |
| `ACTIVATED_BY` | Spiritual activation |
| `CARRIES_LINEAGE` | Person → Lineage |

**⚠️ DO NOT DELETE without explicit instruction from Ka'tuar'el. This is sacred infrastructure.**

---

### 9. `research_framework` — Research & Analysis Engine

**Purpose:** Research routing, convergence analysis, and entity extraction from deep analysis sessions.
**Source code:** `/opt/mythos/core/research_router.py`, `/opt/mythos/core/convergence.py`, `/opt/mythos/core/node_executor.py`
**Node count:** ~20+ nodes

| Label | Count | Description |
|-------|-------|-------------|
| `Entity` | 20 | Entities extracted from research/analysis |
| `Pattern` | 3 | Identified patterns |
| `IdentityThread` | 3 | Identity continuity threads |
| `Object` | 3 | Physical/conceptual objects |
| `Quote` | 2 | Significant quotes |

| Relationship | Description |
|-------------|-------------|
| `INVOLVES` | Research → Entity |
| `SYNTHESIZES` | Analysis → synthesis |
| `ASPECT_OF` | Detail → parent concept |
| `PRECEDES` | Temporal ordering |
| `FEEDS_INTO` | Causal chain |
| `MOTIVATES` | Causal chain |
| `LEADS_TO` | Causal chain |
| `ADDRESSES` | Solution → problem |

---

## Unregistered / Orphan Labels

If you find nodes with labels NOT listed above, they are orphans. Query:

```cypher
// Find any nodes whose label doesn't match a registered app
MATCH (n)
WITH labels(n)[0] AS label, count(*) AS cnt
WHERE NOT label IN [
  'GenPerson', 'GenPlace', 'GenFamily', 'GenSurname',
  'GridNode', 'Theme', 'AnchorOutput', 'EchoOutput', 'BeaconOutput',
  'SynthOutput', 'NexusOutput', 'MirrorOutput', 'GlyphOutput',
  'HarmoniaOutput', 'GatewayOutput', 'GridMasterOutput', 'GatewaySafetyCheck',
  'OntologyTerm', 'Concept',
  'Exchange', 'Conversation',
  'Person', 'PersonOwner',
  'Process', 'System', 'Service', 'File', 'Directory', 'Function', 'Tool', 'TestMachine', 'TestRun',
  'Chart', 'Numerology', 'SoulStratigraphy',
  'Soul', 'Incarnation', 'Lineage',
  'Entity', 'Pattern', 'IdentityThread', 'Object', 'Quote',
  'AppRegistry',
  'Value', 'Emotion', 'EmotionalNeed', 'Symbol', 'Relationship', 'Event',
  'Direction', 'Location', 'Integration', 'IntegrationGap', 'Commitment',
  'DecisionGate', 'Shadow', 'Wound', 'Archetype', 'SacredObject', 'Role',
  'Threshold', 'Portal', 'Dream', 'Defense', 'PotentialTrigger', 'MagicalAct',
  'SupportGap', 'Transmission', 'Activation', 'Rupture', 'Repair',
  'CommunicationGap', 'BoundaryNeeded', 'CapacityAssessment', 'ConvergencePoint',
  'Boundary', 'FinancialCondition', 'PlannedExpense', 'Manifestation',
  'ValueTension', 'RitualElement', 'RitualGap', 'Concern'
]
RETURN label, cnt ORDER BY cnt DESC
```

---

## Adding a New Application

When adding a new app that writes to Neo4j:

1. **Add a section to this document** with app name, purpose, source code, labels, and relationships
2. **Run the registration query:**
```cypher
CREATE (a:AppRegistry {
  app_id: 'your_app_name',
  display_name: 'Your App Name',
  description: 'What it does',
  source_files: ['/opt/mythos/path/to/code.py'],
  owned_labels: ['Label1', 'Label2'],
  owned_relationships: ['REL_TYPE_1', 'REL_TYPE_2'],
  registered_at: datetime(),
  updated_at: datetime()
})
```
3. **Update the orphan query** in the section above

---

## Quick Reference: Label → App Lookup

| Label | App |
|-------|-----|
| `GenPerson`, `GenPlace`, `GenFamily`, `GenSurname` | `genealogy` |
| `GridNode`, `Theme`, `*Output`, `GatewaySafetyCheck` | `grid_worker` |
| `OntologyTerm`, `Concept` | `ontology` |
| `Exchange`, `Conversation` | `conversation_logger` |
| `Person`, `PersonOwner` | `people_manager` |
| `Process`, `System`, `Service`, `File`, `Directory`, `Function`, `Tool` | `system_monitor` |
| `Chart`, `Numerology`, `SoulStratigraphy` | `astrology` |
| `Soul`, `Incarnation`, `Lineage` | `spiritual_core` |
| `Entity`, `Pattern`, `IdentityThread`, `Object`, `Quote` | `research_framework` |
| All grid sub-nodes (Value, Emotion, Shadow, etc.) | `grid_worker` |
| `AppRegistry` | `app_registry` (this system) |

---

*This registry is the law of the graph. If it's not registered here, it doesn't belong.*
