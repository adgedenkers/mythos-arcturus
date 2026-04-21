---
title: "Cross-Stream Request System"
category: streams
status: active
stream: null
location: docs
tags: [requests, stream, coordination]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Cross-Stream Requests

> When a stream needs a change in another stream's territory, log it here.
> The owning stream handles it in its own conversation.

## How to Use

1. **Requesting stream** adds a row with status `PENDING`
2. **Owning stream** picks it up, builds the patch, changes status to `DONE` with the patch ID
3. **Requesting stream** can then build against the change

## Active Requests

| # | From | Needs | Description | Status | Resolved By |
|---|------|-------|-------------|--------|-------------|
|   |      |       |             |        |             |

## Completed Requests

| # | From | Needs | Description | Resolved By |
|---|------|-------|-------------|-------------|
|   |      |       |             |             |

## 2026-04-21 — SYS: PatchBase → Neo4j ontology sync

**From:** SEN (surfaced during SEN-0004 build) | **To:** SYS | **Priority:** Medium

Build a Neo4j-backed ontology of `PatchBase` so Claude's diagnostic dumps can query the live API instead of relying on skill documentation that may have drifted.

**Scope:**
- AST-scrape `/opt/mythos/patches/scripts/patch_base.py` into Neo4j nodes: `PatchBaseMethod`, `PatchBaseAttribute`, with signature, docstring, file:line
- Post-install hook in every patch that touches `patch_base.py` re-runs the scrape
- `patchbase-methods` CLI at `/opt/mythos/bin/` — dumps current API for inclusion in diag bundles
- Add to `mythos-diag` output

**Why:** SEN-0004 v1 failed because Claude's skill doc claimed `patch.str_replace()` exists — it doesn't. A Neo4j-backed source of truth prevents that class of failure. Memory and skill docs are unreliable; the graph is authoritative.

**Status:** Not blocking. Fold into SYS backlog whenever SYS has capacity.
