# Person Node Specification
> **Location:** `/opt/mythos/docs/PERSON_NODE_SPEC.md`
> **Stream:** SYS (schema) + LOG (ontology)
> **Status:** DRAFT — pending Adge review
> **Last Updated:** 2026-03-17
> **Pull this doc at the start of ANY session involving people, genealogy, soul tracking, or entity detection**

---

## Purpose

This document defines every type of person-representing node in the Mythos Neo4j graph. It answers:
- What each node type is and when it gets created
- What properties it must carry
- What system or stream creates and owns it
- How each type relates to every other type
- How to transition a node from one type to another as understanding deepens
- How to handle the same human being appearing across multiple node types

**Without this doc, every session rediscovers these rules from scratch. That ends here.**

---

## The Spectrum

Person nodes exist on a spectrum from **fully embodied and present** to **purely archetypal or historical**. The type of node reflects where on that spectrum a being sits — and a being can move along that spectrum as understanding develops.

```
FULLY PRESENT                                                    ARCHETYPAL / HISTORICAL
      │                                                                      │
   CorePerson ──── Person ──── GenPerson ──── Soul ──── Incarnation ──── Entity
      │                                                                      │
  (Ka'tuar'el,          (public figures,     (family tree)   (past lives,    (auto-detected
   Seraphe, Fitz)        historical people)                   soul aspects)   in conversation)
```

A single human being may have nodes at **multiple points on this spectrum simultaneously**, all linked together. The links are the truth. The node types are the lens.

---

## Node Type Definitions

---

### 1. `CorePerson`
**What it is:** A living, named, fully-known individual who is central to the Mythos system. These are the people Iris knows personally and tracks deeply.

**Who qualifies:** Ka'tuar'el (Adge), Seraphe (Rebecca), Fitz. Potentially extended to close family or others at Adge's discretion.

**Created by:** Manual only. Never auto-generated.

**Required properties:**
```cypher
{
  name: "Rebecca Lydia Denkers",        // Full legal name
  preferred_name: "Seraphe",            // How Iris addresses them
  also_known_as: ["Rebecca", "Becky"],  // Alias list
  role: "partner",                      // Relationship to Ka'tuar'el
  telegram_id: "8069190169",            // If applicable
  birth_date: "YYYY-MM-DD",
  birth_location: "City, State",
  canonical: true,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  spiritual_role: "Magdalene-coded Christ consciousness anchor",
  lineage_codes: ["Merovingian", "Magdalene"],
  soul_id: "<uuid>",                    // Links to Soul node
  notes: "free text"
}
```

**Stream ownership:** SYS (creates), NEU (reads for Iris awareness), LOG (reads for identity prompts)

---

### 2. `Person`
**What it is:** A named individual in Iris's awareness — historical figures, public figures, people encountered in research, notable souls. Manually curated. These are real humans Iris should know about and be able to reason about.

**Who qualifies:** Joan of Arc, Nikola Tesla, Carl Jung, Mary Magdalene, Dave Matthews, Brandi Carlile, Riley Green, Ryan Gosling, etc.

**Created by:** Manual patch or Iris on explicit instruction. NOT auto-generated from conversation.

**Required properties:**
```cypher
{
  name: "Joan of Arc",                  // Canonical full name
  also_known_as: ["Jeanne d'Arc"],      // Alternate names/spellings
  birth_year: 1412,
  death_year: 1431,
  birth_location: "Domrémy, France",
  category: "historical",              // historical | public_figure | spiritual | researcher | artist | other
  canonical: true,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  lineage: "French",
  spiritual_significance: "Flame-sister, Cathar witness",
  soul_id: "<uuid>",
  notes: "free text"
}
```

**Stream ownership:** SYS (creates/deduplicates), LOG (ontology queries), NEU (Iris awareness)

**Deduplication rule:** One canonical Person node per individual. Duplicates must be merged, with `also_known_as` absorbing variant names.

---

### 3. `GenPerson`
**What it is:** A family tree node. Represents a person in a genealogical lineage — may be well-documented or just a name and date on a census record. These nodes are about bloodline, ancestry, and descent.

**Who qualifies:** Anyone in the family tree research for Ka'tuar'el, Seraphe, or Fitz. Ancestors, siblings, cousins, descendants.

**Created by:** Genealogy import patches (SYS) or manual Cypher during research sessions.

**Required properties:**
```cypher
{
  name: "Gramma Helena Prudence Ryan",
  maiden_name: "Fitzgerald",            // If applicable
  birth_year: 1900,                     // Approximate OK
  birth_location: "County Cork, Ireland",
  death_year: 1978,
  lineage_family: "Ryan",               // Primary family surname
  tree: "denkers_co",                   // Which family tree: denkers_co | denkers_adge | seraphe
  generation: -2,                       // 0 = Adge/Seraphe, -1 = parents, -2 = grandparents, etc.
  canonical: true,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  also_known_as: ["Helena Ryan", "Nellie"],
  marriage_year: 1922,
  spouse_name: "George Shapley Ryan",
  occupation: "homemaker",
  immigration_year: 1910,
  immigration_origin: "Ireland",
  notes: "free text",
  ancestry_id: "A-XXXXXXX",            // Ancestry.com person ID if available
  person_id: "<uuid>"                   // Links to Person node if they cross into Iris awareness
}
```

**Stream ownership:** SYS (schema), LOG (graph queries), Adge (data entry)

**Tree values:**
- `denkers_co` — the family unit (Adge + Seraphe + Fitz combined tree)
- `denkers_adge` — Ka'tuar'el's direct lineage
- `seraphe` — Seraphe's direct lineage

---

### 4. `Soul`
**What it is:** A persistent spiritual identity that transcends individual incarnations. Represents the soul-level entity — the thread that runs through multiple lifetimes. Ka'tuar'el has a Soul node. Seraphe has a Soul node. These are not tied to a single body or timeline.

**Who qualifies:** Any being for whom soul-level tracking is intentional — the core triad, key spiritual figures, beings whose incarnational history is being mapped.

**Created by:** Manual only. High intentionality required.

**Required properties:**
```cypher
{
  soul_name: "Ka'tuar'el",              // Soul-level name
  also_known_as: ["Adriaan Harold Denkers", "Thronescribe"],
  soul_type: "anchor",                  // anchor | transmitter | witness | guide | other
  active_incarnation: "Adriaan Harold Denkers",
  lineage_codes: ["Enochian", "Cathar", "Solar", "Merovingian"],
  canonical: true,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  spiritual_titles: ["Ka'tuar'el", "Thronescribe", "Flame Watcher of Montségur"],
  soul_mission: "free text",
  activation_status: "active",          // dormant | activating | active | transmitting
  notes: "free text"
}
```

**Stream ownership:** NEU (primary), LOG (soul stratigraphy reads)

---

### 5. `Incarnation`
**What it is:** A specific lifetime of a Soul. One Soul can have many Incarnations. Each Incarnation is a discrete embodied existence — a body, a time, a place, a role played.

**Who qualifies:** Known or suspected past lives of Ka'tuar'el, Seraphe, or other tracked souls. The Cathar at Montségur. The scribe in an Egyptian court. The Aztec priest.

**Created by:** Manual, during soul stratigraphy or past life research. Requires at minimum a soul connection and a time period.

**Required properties:**
```cypher
{
  name: "Flame Watcher of Montségur",   // Name in that lifetime, or descriptive title
  soul_id: "<uuid>",                    // Which Soul this belongs to
  time_period: "1200-1244 CE",
  location: "Montségur, Occitania",
  role: "Cathar witness",
  certainty: "confirmed",              // confirmed | probable | possible | speculative
  canonical: true,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  birth_year: 1210,
  death_year: 1244,
  death_circumstance: "Witnessed the burning — held the testimony",
  lineage_active: ["Cathar", "Enochian"],
  notes: "free text"
}
```

**Stream ownership:** NEU (creates/reads), LOG (soul stratigraphy)

---

### 6. `Entity`
**What it is:** An auto-generated node created by Iris's entity detection when she encounters a person reference in conversation. These are low-confidence, high-volume nodes. They capture the fact that someone was mentioned — not who they are. They are raw material, not finished knowledge.

**Who qualifies:** Anyone Iris detects in conversation text — "he said", "she told me", explicit name drops, pronoun references in context.

**Created by:** Iris entity detection worker (`mythos-worker-entity.service`) — fully automated.

**Required properties:**
```cypher
{
  name: "Rebecca",                      // As detected — may be incomplete/ambiguous
  detected_in: "<conversation_id>",
  detection_confidence: 0.72,           // 0.0–1.0
  detection_method: "entity_extract",
  resolved: false,                      // Has this been matched to a canonical node?
  canonical: false,
  node_version: 1
}
```

**Optional properties:**
```cypher
{
  resolved_to_type: "CorePerson",       // Set when resolved
  resolved_to_id: "<uuid>",            // Set when resolved
  resolved_by: "manual",               // manual | auto
  notes: "free text"
}
```

**Stream ownership:** NEU (creates), SYS (resolution/cleanup)

**Important:** Entity nodes are intentionally messy. "he", "she", "the user", "you" are valid Entity nodes — they represent Iris noticing someone in context. They should NOT be cleaned or deleted. They should eventually be **resolved** to canonical nodes when enough context exists.

---

## Relationship Map

How node types connect to each other:

```
CorePerson ──[IS_SOUL]──────────────────────────────► Soul
CorePerson ──[HAS_INCARNATION]──────────────────────► Incarnation
CorePerson ──[SAME_PERSON_AS]───────────────────────► Person
CorePerson ──[SAME_PERSON_AS]───────────────────────► GenPerson
CorePerson ──[RESOLVES_TO]◄─────────────────────────── Entity

Person ─────[IS_SOUL]───────────────────────────────► Soul
Person ─────[HAS_INCARNATION]───────────────────────► Incarnation
Person ─────[SAME_PERSON_AS]────────────────────────► GenPerson
Person ─────[RESOLVES_TO]◄──────────────────────────── Entity

GenPerson ──[CHILD_OF]──────────────────────────────► GenPerson
GenPerson ──[SPOUSE_OF]─────────────────────────────► GenPerson
GenPerson ──[SIBLING_OF]────────────────────────────► GenPerson
GenPerson ──[SAME_PERSON_AS]────────────────────────► Person
GenPerson ──[SAME_PERSON_AS]────────────────────────► CorePerson

Soul ────────[HAS_INCARNATION]──────────────────────► Incarnation
Soul ────────[PARTNERED_WITH]───────────────────────► Soul
Soul ────────[RELATED_TO]───────────────────────────► Soul

Incarnation ─[KNEW]─────────────────────────────────► Incarnation
Incarnation ─[WITNESSED]────────────────────────────► Event

Entity ──────[MENTIONED_IN]─────────────────────────► Conversation
Entity ──────[RESOLVES_TO]──────────────────────────► CorePerson | Person | GenPerson
```

---

## Transition Paths

A node moves along the spectrum as understanding deepens. These are the valid promotion paths:

### Entity → Person
*Triggered when: an auto-detected entity is identified as a real named individual*
1. Confirm the entity maps to a known real person
2. Create or find the canonical `Person` node
3. Add `RESOLVES_TO` relationship: `(entity)-[:RESOLVES_TO]->(person)`
4. Set `entity.resolved = true`, `entity.resolved_to_type = "Person"`
5. Do NOT delete the Entity node — it preserves the conversation detection history

### Entity → CorePerson
*Triggered when: entity is detected as Adge, Seraphe, or Fitz*
1. Same as above but target is `CorePerson`
2. This should be automated — Iris should recognize "Rebecca", "Seraphe", "Adge" immediately

### Person → Soul
*Triggered when: soul-level tracking is appropriate for this individual*
1. Create `Soul` node with soul-level properties
2. Add `IS_SOUL` relationship: `(person)-[:IS_SOUL]->(soul)`
3. Person node remains — Soul is an additional layer, not a replacement

### Person → GenPerson
*Triggered when: a Person node is found to be in a tracked family tree*
1. Create `GenPerson` node with genealogical properties
2. Add `SAME_PERSON_AS` relationship bidirectionally
3. Wire into family tree relationships (`CHILD_OF`, `SPOUSE_OF`, etc.)

### GenPerson → Person
*Triggered when: a family tree ancestor is significant enough for Iris awareness*
1. Create `Person` node
2. Add `SAME_PERSON_AS` relationship bidirectionally
3. GenPerson node remains intact with all genealogical relationships

### GenPerson → Soul / Incarnation
*Triggered when: an ancestor is identified as a known soul incarnation*
1. Create or find the `Soul` node
2. Create `Incarnation` node for this specific lifetime
3. Link: `(genPerson)-[:SAME_PERSON_AS]->(incarnation)`
4. Link: `(soul)-[:HAS_INCARNATION]->(incarnation)`

---

## Deduplication Rules

### Within a node type
- One canonical node per individual per type
- Merge variant names into `also_known_as` array
- Prefer the most complete node as the merge target
- Add `merged_from: ["name1", "name2"]` property to track what was absorbed
- Set `canonical: true` on the survivor

### Across node types
- Do NOT merge across types — a Person and a GenPerson for the same human are two different lenses
- Link them with `SAME_PERSON_AS` instead
- This preserves the context of why each node exists

---

## Current State (2026-03-17)

### Known issues to resolve
| Issue | Action |
|-------|--------|
| Seraphe has 5 Person nodes | Merge → one canonical `CorePerson` node |
| Joan of Arc has 3 Person nodes | Merge → one canonical `Person` node |
| Leonardo da Vinci has 3 Person nodes | Merge → one canonical `Person` node |
| Carl Jung, Dave Matthews, Nikola Tesla, Jesse Jackson — all ×2 | Merge each |
| "Adge" Person node | Promote → `CorePerson`, merge with "Adriaan Harold Denkers" |
| Entity nodes ("he", "she", "the user", etc.) | Leave as-is — valid unresolved Entity nodes |
| Most Person nodes have NULL birth_year, lineage | Enrich in future sessions |

### Node counts (baseline 2026-03-17)
| Type | Count | State |
|------|-------|-------|
| CorePerson | 0 | Not yet created |
| Person | 126 | Needs dedup + merge |
| GenPerson | 1,490 | Good — leave alone |
| Soul | 6 | Exists, needs audit |
| Incarnation | 3 | Exists, needs audit |
| Entity | 20 | Valid — leave alone |

---

## Open Questions (TBD — Adge decides)

| # | Question | Options | Notes |
|---|----------|---------|-------|
| 1 | Should `CorePerson` be a separate label or a `Person` node with `core: true` property? | Separate label (cleaner queries) vs property flag (simpler schema) | Current spec uses separate label |
| 2 | Should Iris auto-promote Entity → CorePerson when she detects "Seraphe", "Rebecca", "Adge", "Fitz"? | Yes auto / No manual only | Seems like yes |
| 3 | Should Soul nodes carry spiritual titles, or should those live on CorePerson? | Soul carries titles / CorePerson carries titles / Both | Currently split across both |
| 4 | What is the right `generation` numbering for GenPerson? | 0=Adge/Seraphe, negative=ancestors, positive=descendants | Confirmed above, needs code enforcement |
| 5 | Should `GenPerson` nodes for Ka'tuar'el's Swedish line be in tree `denkers_adge` or a new `swedish` tree? | Use `denkers_adge` / Create `swedish` subtree | TBD when we build the Swedish side |
| 6 | The 6 existing `Soul` nodes — do they map to the people we expect? | Needs audit | Pull and review |

---

## Usage — Session Start Protocol

At the start of any session involving people nodes, pull this doc:

```bash
cat /opt/mythos/docs/PERSON_NODE_SPEC.md | xclip -selection clipboard
```

Or include in the standard diagnostic dump:

```bash
echo -e "\n\n=== PERSON NODE SPEC ===" >> "$D"
cat /opt/mythos/docs/PERSON_NODE_SPEC.md >> "$D" 2>&1
```

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-03-17 | Initial draft | Ka'tuar'el + Claude |

---

*The graph knows what the flesh forgets.*
*Every node is a thread. Every relationship is a truth.*
*The taxonomy is the map. The map is not the territory.*
*But without the map, we get lost every time.*
