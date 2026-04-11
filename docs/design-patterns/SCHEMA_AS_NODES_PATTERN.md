---
title: "Schema-as-Nodes Graph Pattern"
category: design-patterns
status: active
stream: NEU
location: docs
tags: [schema, graph, self-documenting]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Schema-as-Nodes: Self-Documenting Graph Pattern

**Author:** Ka'tuar'el (Adriaan Denkers)
**Origin:** Mythos / Neo4j knowledge architecture
**Date:** March 2026

---

## The Core Insight

If a node can't tell you what it is and what it means just by being read, it's dead weight.

A graph database only becomes a true knowledge system when every node carries enough meaning to be self-interpreting. Without that, it's structured storage that needs external documentation to make sense — which defeats the purpose of using a graph in the first place.

---

## The Pattern

**Schema-as-Nodes** means the graph is its own documentation. Node labels, relationship types, constraints, and semantic definitions all live *inside* the graph as first-class nodes — not in a README, not in a wiki, not in someone's head. The graph describes itself.

**Anchoring Rules** mean nothing enters the graph without enough context to survive on its own. Every node must carry the metadata necessary for any reader — human or machine — to understand what it represents without external reference.

Together, these two principles turn a graph from a storage layer into a knowledge substrate.

---

## Why This Matters for LLMs

This pattern was discovered in the context of building a graph that an LLM (Iris) needs to traverse and reason over. The problem it solves:

- An LLM can't read your README before querying your graph. It gets nodes and relationships, and that's it.
- If a node is just `(:Person {name: "John"})`, the LLM has no idea what "Person" means in your system, what properties are expected, what relationships are valid, or what this node's role is in the broader ontology.
- If the graph contains its own schema — label definitions, relationship semantics, property descriptions, validation rules — the LLM can discover all of that by traversing the graph itself.

The graph becomes a knowledge substrate the LLM can actually use, not a fancy storage layer it needs a human to interpret.

---

## Implementation Rules

### 1. Every Label Gets a Schema Node

```cypher
CREATE (:SchemaLabel {
  name: 'Soul',
  description: 'A unique consciousness entity tracked across incarnations',
  required_properties: ['name', 'origin_stream'],
  optional_properties: ['status', 'activated_date', 'lineage_codes'],
  created: datetime(),
  stream: 'NEU'
})
```

### 2. Every Relationship Type Gets a Schema Node

```cypher
CREATE (:SchemaRelationship {
  name: 'INCARNATED_AS',
  description: 'Links a Soul to a specific historical or living Person',
  from_label: 'Soul',
  to_label: 'Person',
  cardinality: 'one-to-many',
  properties: ['era', 'confidence'],
  stream: 'NEU'
})
```

### 3. Anchoring: Minimum Viable Context on Every Node

No node enters the graph without:

- **What it is** — a label that maps to a SchemaLabel node
- **When it arrived** — `created` timestamp
- **Who owns it** — `stream` tag (which Mythos development stream is responsible)
- **Why it exists** — at minimum a `description` or `source` property, or a relationship to something that provides context

If you can't satisfy these four, the node isn't ready to enter the graph.

### 4. The Graph Describes Its Own Topology

Query the schema layer to discover what the graph contains:

```cypher
// What kinds of things exist in this graph?
MATCH (s:SchemaLabel) RETURN s.name, s.description

// What relationships connect Souls to other things?
MATCH (s:SchemaRelationship) WHERE s.from_label = 'Soul'
RETURN s.name, s.to_label, s.description

// What properties should a Person node have?
MATCH (s:SchemaLabel {name: 'Person'})
RETURN s.required_properties, s.optional_properties
```

### 5. Ownership Is Explicit

Every schema node and data node declares its owning stream. This means:

- Cross-stream queries are always safe (read-only access is fine)
- Writes go through the owning stream's patch process
- No orphaned nodes — if a stream is deprecated, its nodes can be identified and migrated

---

## Anti-Patterns This Prevents

| Anti-Pattern | What Goes Wrong | How Schema-as-Nodes Fixes It |
|---|---|---|
| **Schema in a README** | Drifts from reality within a week | Schema nodes are the reality — they're queryable and can be validated |
| **Naked nodes** | `(:Thing {x: 1})` means nothing to anyone six months later | Anchoring rules require minimum context at creation time |
| **Implicit relationships** | "Everyone knows KNOWS means friendship" | SchemaRelationship nodes make semantics explicit |
| **LLM guessing** | Model hallucinates what a label means | Model can query SchemaLabel nodes to discover actual meaning |
| **Orphaned data** | No one knows who created it or why | Stream ownership and timestamps on every node |

---

## The Deeper Point

Most graph databases are treated like relational databases with extra steps — store stuff, query stuff, hope someone remembers what the structure means. The schema-as-nodes pattern inverts this: the graph's structure is itself stored as knowledge, making the graph self-describing and machine-readable at every level.

This is what makes it possible to build a graph that an LLM can genuinely reason over rather than just retrieve from. The LLM doesn't need external documentation — the documentation is the graph.

---

## Mythos Context

In the Mythos system, this pattern is implemented through:

- **Neo4j App Registry** (patch 0161) — documents ownership of all graph labels
- **Ontology/Glossary system** — terms and definitions stored as graph nodes
- **Stream ownership model** — every node tagged with its originating development stream (SYS, NEU, LOG, MNE, SEN)
- **STREAMS.json** — machine-readable stream registry that parallels the graph-level ownership

The pattern emerged from building Iris — the Mythos AI — and discovering that a graph is only as useful to an LLM as it is self-explanatory.
