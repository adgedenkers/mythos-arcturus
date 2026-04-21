---
title: "Mythos Sub-Systems Pattern"
category: architecture
status: draft
stream: null
location: docs
tags: [architecture, pattern, sub-system, finance, astrology]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
reviewed_at: pending
---

# Mythos Sub-Systems Pattern

> **Status: DRAFT.** This pattern is derived from Finance v2 alone (N=1).
> Astrology v2 is the first test implementation. Expect revisions at
> Astrology Letter E (first functional ship) and Letter F (integration).
> Do not cite this doc as canonical until at least two sub-systems have
> shipped end-to-end against it.

---

## What a sub-system is

A **sub-system** is a coherent feature domain on Mythos that has its own
data model, its own state evolution, and its own long-lived build arc
spanning many patches. Examples:

- **Finance v2** — double-entry ledger on Postgres
- **Astrology v2** — chart calculation + transit engine on Swiss Ephemeris
- Future candidates: **Voice Memos v2**, **Iris Memory v3**, **Calendar v2**

A sub-system is bigger than a feature and smaller than a stream. A
stream (NEU, LOG, MNE, SEN, SYS) is the ownership boundary; a sub-system
is a build arc within a stream.

---

## What this pattern is not

**This is not a design pattern.** Design patterns (see
`/opt/mythos/docs/design-patterns/`) are single-purpose reusable
techniques — how to store schema-as-nodes in Neo4j, how to do a
schema-as-nodes migration, how to track a thing with a sidecar JSON
file. A sub-system is an assembly that can use multiple patterns.

A design pattern answers "how do I model this one thing?" A sub-system
pattern answers "how do I ship a multi-patch coherent domain?"

---

## The pattern

### 1. Three docs per sub-system

Every sub-system maintains exactly three canonical docs:

| Doc | Location | Purpose | Mutability |
|---|---|---|---|
| `SYSTEM_<NAME>.md` | `/opt/mythos/docs/` | Canonical current state | Updated after **every** patch lands |
| `<NAME>_V2.md` (or `_VN.md`) | `/opt/mythos/docs/` | Design plan, locked letter sequence | Stable once locked |
| `<name>/NEXT_PATCH_SPEC.md` | `/opt/mythos/docs/<name>/` | Exactly one patch ahead | **Rewritten wholesale** after each patch |

Plus the two auto-maintained pattern-level docs:

| Doc | Location | Purpose | Mutability |
|---|---|---|---|
| `STREAMS.json` | `/opt/mythos/docs/` | Machine-readable patch counters | `PatchBase.finish()` handles |
| `PATCH_HISTORY.md` | `/opt/mythos/docs/` | Append-only patch log | `PatchBase.finish()` handles |

**Exemplar: Finance v2.** See `/opt/mythos/docs/SYSTEM_FINANCE.md`,
`/opt/mythos/docs/FINANCE_V2.md`, `/opt/mythos/docs/finance/NEXT_PATCH_SPEC.md`.

### 2. Locked letter sequence

Each sub-system has a **letter sequence** describing its logical build
order: A, B, C, D, E, F, ... Letters are chosen when the design plan is
locked and **never change** — even when a single letter requires
multiple patch numbers to land cleanly (Finance's Letter C.1 took
patches SYS-0078 through SYS-0081, four real patches under one
logical letter).

**Why letters, not numbers?** Patch numbers come live from
`mythos-diag streams` and will drift with unrelated work in the stream.
Letters are the sub-system's private, stable build arc. A reviewer six
months later should be able to say "what shipped in Astrology Patch E?"
and get a canonical answer regardless of which SEN-NNNN it was.

**Common letter patterns:**

| Letter | Typical Scope |
|---|---|
| A | Anchor — docs, design plan, validation harness, patch tooling |
| B | First code — shared libraries, wrappers, infrastructure |
| C | Consolidation — migrate legacy state to match new architecture |
| D | Core feature — the primary domain logic |
| E | Integration — wire the feature into Mythos (CLI, API, Telegram) |
| F+ | Refinement — tests, hardening, optional features |

The Finance sequence ran A→L (12 letters, planned). Astrology v2 runs
A→F (6 letters). Both work.

### 3. The `SYSTEM_<NAME>.md` structure

Eight sections in order:

```
1. Frontmatter (YAML)
2. Status — last patch letter shipped, next patch letter, build phase
3. Architecture Summary — 2–4 paragraphs of plain English
4. Patch Ledger — table of letters, numbers, scope, shipped date
5. Current State — what's live on disk and in DBs as of last patch
6. Next Up — pointer to NEXT_PATCH_SPEC.md
7. Open Questions — numbered, with resolution target per item
8. Incoming Notes — append-only, date-stamped
```

**Incoming Notes** is the rolling backlog of "things we noticed
during patch work that don't belong in the current patch but shouldn't
be lost." Review and triage at the start of each new patch.

### 4. The `<NAME>_V2.md` structure

Design plan. Covers:

- Context and constraints
- What the previous version got wrong (if a rewrite)
- Core architectural decisions (locked)
- The letter sequence with scope per letter
- Open questions for review
- Prior review attribution (who caught what in which round)

The plan is written BEFORE Letter A ships and is reviewed by at least
one external model (Castor/Gemini, Jeff Pro/ChatGPT). Review attributions
are preserved verbatim in the plan.

### 5. The `<name>/NEXT_PATCH_SPEC.md` structure

Exactly one patch ahead. Rewritten wholesale at the end of every
feature patch. Covers:

- Patch letter + proposed stream + description
- Scope — what files change, what SQL runs, what services restart
- Verification criteria — how we know it worked
- Rollback — how we undo it if it didn't

When Letter B ships, the last thing Letter B's `apply_patch.py` does
is deploy a new `NEXT_PATCH_SPEC.md` describing Letter C. The spec is
always one patch ahead of the ledger.

### 6. `mythos-handoff <subsystem>` tool

Bundles the three docs + live DB state + validation output into the
clipboard for starting a new conversation about the sub-system. This
is what keeps sub-system work grounded across context boundaries.

Finance exemplar: `mythos-handoff finance` outputs
`SYSTEM_FINANCE.md` + `FINANCE_V2.md` + `finance/NEXT_PATCH_SPEC.md` +
current Postgres state for the finance schema + latest golden fixture
validation output.

Each sub-system registers with the handoff tool via a small config
block declaring its docs and its validation command.

### 7. Golden fixture validation (non-negotiable)

Every sub-system ships a validation harness in Letter A **before any
refactoring starts**. The harness is a Python script that:

- Loads a set of known-good inputs from fixtures
- Runs them through the current (possibly messy) sub-system
- Compares output to known-good expected values
- Reports pass/fail

If the harness can't pass against the current state, that's information
— you know which parts of the pipeline are giving wrong answers before
you start changing things.

Every subsequent patch runs the harness as the last step of
`apply_patch.py` and rolls back on failure.

This was a hard lesson from Finance v2: validation shipped late (Letter
L in the plan), which meant for months nobody could prove that a given
refactor hadn't silently shifted a calculation. Don't repeat this.

### 8. MANIFEST.yaml per patch

Every sub-system patch carries a `MANIFEST.yaml` declaring:

```yaml
stream: SEN
number: 4
letter: A
subsystem: astrology
description: "astrology v2 anchor — docs + golden fixtures"
patch_type: MINOR
services_restarted: []
tables_touched: []
blast_radius: low  # low/medium/high
review_link: null  # URL to Gemini/ChatGPT review if blast_radius >= medium
```

Blast radius ≥ medium triggers a review requirement before shipping
(see Finance Phase 2.5 workflow).

---

## Build workflow

```
Plan → Review → Letter A (anchor) → Letter B → ... → Letter N (done)
  ↓       ↓          ↓
SYSTEM_ V2.md   NEXT_PATCH_SPEC.md      Ship Letter B, rewrite NEXT_PATCH_SPEC as Letter C
docs      &                             Run golden fixtures at end of every patch
          Castor review
```

1. **Write `<NAME>_V2.md` design plan.** Get external review (Castor,
   Jeff Pro, etc.). Lock the letter sequence.
2. **Write Letter A patch.** Ships:
   - `SYSTEM_<NAME>.md` (initial state, patch ledger with only A)
   - `<NAME>_V2.md` (locked design plan)
   - `<name>/NEXT_PATCH_SPEC.md` (describes Letter B in full)
   - Golden fixture harness (runs today, passes against current state)
   - Update to `ARCHITECTURE.md` (SYSTEM docs pointer section)
3. **Ship Letter A.** It's docs-only, minimal risk, fast feedback.
4. **Ship Letter B** per the spec. End of patch: rewrite
   `NEXT_PATCH_SPEC.md` for Letter C, update `SYSTEM_<NAME>.md` patch
   ledger, run golden fixtures.
5. **Repeat** through the letter sequence.

---

## Stream boundary rules (inherited from `STREAMS.md`)

A sub-system lives primarily in one stream. But:

- **Read-only cross-stream access is always fine.** A SEN sub-system
  can query MNE tables.
- **Shared table migrations go through SYS** regardless of which
  sub-system drives them (`people`, `transactions`, `system_manifest`).
- **Telegram `/commands` register through SYS** — the handler code can
  live in the originating sub-system, but the `application.add_handler`
  call goes in a SYS patch.
- **CLI symlinks go to `/opt/mythos/bin/`** only. The symlink itself
  can be created by the originating sub-system's patch.

---

## Known limitations of this document

1. **N=1.** This pattern is extrapolated from Finance v2 alone. Until
   Astrology v2 ships Letter F end-to-end, treat anything here as
   provisional.

2. **Finance is transactional; astrology is not.** The Postgres-first
   rule in §4 ("Database vs. JSON") was derived from Finance, which
   streams observations into an append-only ledger. Astrology writes
   static snapshots. The JSON-as-artifact / Postgres-as-source-of-truth
   balance may need revision once Astrology Letter D ships.

3. **Golden fixtures assume deterministic computation.** Finance
   validates via balanced trial balance. Astrology validates via
   exact ephemeris positions to two decimal places. A sub-system
   with stochastic behavior (e.g., an LLM-driven pipeline) would need
   a different validation approach.

4. **No third sub-system has been built.** The third one is where
   the pattern either solidifies or gets revised. Planned candidates:
   Voice Memos v2, Calendar v2, Iris Memory v3.

---

## Revision targets

- **Astrology Letter E ships:** First revision. Remove "draft" status
  if pattern held up. Add "Astrology-specific learnings" section.
- **Astrology Letter F ships:** Second revision. Promote to
  `status: active`.
- **Third sub-system ships Letter A:** Third revision. Validate the
  "universal" claim.

---

*End of draft. See `SYSTEM_FINANCE.md` for the Finance v2 exemplar,*
*`SYSTEM_ASTROLOGY.md` for the first test implementation.*
