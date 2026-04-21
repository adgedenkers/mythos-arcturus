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

## 2026-04-21 — SYS: Full graph coverage + post-patch verification gate
**From:** SEN (surfaced during astrology v2 build) | **To:** SYS | **Priority:** Medium
Every tool and script deployed across all Mythos systems must be mapped in Neo4j as queryable nodes. Integrity scans at the end of each patch probably already do most of this — verify coverage is complete. Then add a post-scan gate: after integrity scan runs, assert the graph accurately reflects deployed state, or the patch fails.
**Scope:**
- Audit Neo4j for coverage gaps — what deployed files/tools/services are NOT in the graph?
- Extend integrity scanner if needed to close gaps
- Add `graph-verify` step to `patch-install` post-install pipeline — fails patch if graph state drifts from disk state
- The graph becomes the canonical source for "what does Mythos have right now" — Claude's diagnostics query Neo4j instead of grepping filesystem
**Why:** Letter B's first install failed because Claude's skill doc drifted from PatchBase's actual API. If the graph were authoritative and queryable, Claude could have checked before building.
**Status:** Scheduled for after Astrology v2 A→F completes. Do not start until SEN stream is clear.

## 2026-04-21 — SYS: PatchBase microtool kit (with Ollama integration)
**From:** SEN (surfaced during astrology v2 build) | **To:** SYS | **Priority:** Medium
Expand PatchBase from a Python class with ~17 methods into a full microtool kit that patches can invoke during `apply_patch.py`. The headline addition: an `ollama-analyze` microtool that lets patches invoke the local LLM for structured analysis during install.
**Scope:**
- `patchbase-methods` CLI at `/opt/mythos/bin/patchbase-methods` — dumps the live API surface of PatchBase from Neo4j (assumes graph coverage patch above is done first)
- `ollama-analyze` microtool — `patch.ollama_analyze(file_path, prompt)` returns structured JSON. E.g.: "check this new SQL migration for potential drift with existing schema", "extract function signatures from this .py", "does this code match the style conventions of its neighbors?"
- `graph-verify` microtool exposed from PatchBase — same as the post-install gate but callable mid-patch
- All microtools registered in Neo4j as first-class patch tooling nodes
**Why:** Letter B's speed bug (flags=0 silently returned zero speeds) would have been caught if `apply_patch.py` had run an ollama-analyze against the new ephemeris.py asking "does this code have any Swiss Ephemeris footguns?" — the local LLM would have flagged the missing SEFLG_SPEED flag. This makes patches LLM-augmented during build, not just post-hoc review.
**Depends on:** Graph coverage patch above (shares Neo4j infrastructure)
**Status:** Scheduled for after Astrology v2 A→F completes.

## 2026-04-21 — SEN: Comprehensive astrology tool audit + dedup
**From:** SEN | **To:** SEN | **Priority:** Medium
After Astrology v2 A→F ships, run a comprehensive audit of ALL astrology tools currently on the system — not just the 5 in the Letter C scope. Unify them around `ephemeris.py`, dedup one-offs, and fold any unique features from one-offs into canonical versions.
**Scope:**
- Inventory all 23+ Python files under `/opt/mythos/astrology/` and related directories (`/opt/mythos/observatory/geometry/`, `/opt/mythos/workers/lunar_calendar_worker.py`, `/opt/mythos/tools/seraphe-moon-calcs/`, etc.)
- Classify each: (a) uses canonical `ephemeris.py`, (b) has its own copy of constants/helpers that should be migrated, (c) is a one-off with unique features to fold into canonical, (d) is dead code to archive
- For each one-off with unique features (e.g., `seraphe_lunar_generator.py`'s S2b lunar system, `astrochart_cli_geometry.py`'s geometric pattern detection), identify what's worth keeping and port those features into `ephemeris.py` or a proper sibling module
- Archive dead code to `/opt/mythos/astrology/archive/`
- Goal: single coherent module tree where there's exactly one canonical place for each astrology capability
**Distinct from Letter C:** Letter C only touches the 5 files with hardcoded ephemeris paths. This is broader — it's about architectural coherence across the entire astrology domain.
**Status:** Scheduled for after Astrology v2 A→F completes. May be Letter G or a separate SEN patch arc (SEN-v2.1 consolidation).
