---
title: "Mythos Rolodex Identity System"
category: consciousness
status: active
stream: NEU
location: docs
tags: [identity, directory, registry]
created: 2026-02-26
updated: 2026-03-12
author: Adge Denkers
---

# The Rolodex — Mythos Identity & Directory System

**System Name:** `mythos-rolodex`
**Prefix:** `RX`
**Version:** 1.0
**Author:** Ka'tuar'el / Claude
**Date:** 2026-02-26

---

## Overview

The Rolodex is the identity and directory layer of Mythos. Every person, soul, entity, and incarnation in the system is registered here. Every subsystem references the Rolodex to know who someone is.

**Core principles:**
- One canonical identity per human being
- Subsystems never touch the canonical identity — they get their own proxy
- The graph stores relationships and traversal data
- PostgreSQL stores structured/relational data and serves as the universal registry
- Every graph node has a corresponding row in the SQL registry
- Three universal properties on every node: `domain`, `scope`, `origin`
- Three system owners: Adge, Seraphe, Fitz

---

## Node Types

| Prefix | Label | Purpose |
|--------|-------|---------|
| `PO-` | `:PersonOwner` | System owner identity (AD object) |
| `PP-` | `:Person` | Canonical person record (GAL entry) |
| `PS-` | `:Soul` | Eternal non-incarnate identity |
| `PE-` | `:Entity` | Auto-created mention node |
| `PI-` | `:Incarnation` | Soul expressed in specific body/time |
| `PX-` | `:PersonProxy` | Subsystem-specific proxy |

## ID Conventions

- Person: `PP-SURNAME-GivenName-BirthYear`
- Soul: `PS-SoulName`
- Entity: `PE-EntityName`
- Incarnation: `PI-SoulName-Location-Year`
- Proxy: `PX-APP-SURNAME-GivenName-BirthYear`
- Owner: `PO-SURNAME-GivenName-BirthYear`

## Universal Properties (all nodes)

- `uid` — ULID, immutable
- `canonical_id` — human-readable, updatable
- `domain` — what world (people, genealogy, spiritual, system, analysis, conversation, finance, concept)
- `scope` — who cares (personal, shared, public, system)
- `origin` — how created (manual, grid, import, derived, patch)

## PostgreSQL Schema

Location: `rolodex.*`

Tables: graph_nodes, persons, contacts, entity_aliases, proxies, astro_charts, astro_planets, numerology, node_documents, node_notes, sync_log

## Full Specification

See: `/opt/mythos/docs/ROLODEX_FULL.md`
