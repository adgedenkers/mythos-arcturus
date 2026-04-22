---
title: "Mythos Sub-Systems Pattern"
category: architecture
status: active
stream: null
location: docs
tags: [architecture, pattern, sub-system, finance, astrology]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
reviewed_at: 2026-04-21
---

# Mythos Sub-Systems Pattern

> **Status: ACTIVE.** This pattern is now validated against two
> sub-systems: Finance v2 (original) and Astrology v2 (completed
> 2026-04-21). The pattern held. Promoted from DRAFT.
>
> Next revision target: when a third sub-system ships Letter A.

---

## What a sub-system is

A **sub-system** is a coherent feature domain on Mythos that has its own
data model, its own state evolution, and its own long-lived build arc
spanning many patches. Examples:

- **Finance v2** — double-entry ledger on Postgres (A→L, 12 letters)
- **Astrology v2** — chart calculation + transit engine on Swiss Ephemeris (A→F, 7 patches)
- Future candidates: **Voice Memos v2**, **Iris Memory v3**, **Calendar v2**

A sub-system is bigger than a feature and smaller than a stream. A
stream (NEU, LOG, MNE, SEN, SYS) is the ownership boundary; a sub-system
is a build arc within a stream.

---

## What this pattern is not

**This is not a design pattern.** Design patterns are single-purpose
reusable techniques. A sub-system is an assembly that uses multiple
patterns.

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

**Exemplars:** Finance v2 (`SYSTEM_FINANCE.md`) and Astrology v2 (`SYSTEM_ASTROLOGY.md`).

### 2. Locked letter sequence

Each sub-system has a **letter sequence** describing its logical build
order: A, B, C, D, E, F, ... Letters are chosen when the design plan is
locked and **never change** — even when a single letter requires multiple
patch numbers (Finance's Letter C.1 was four real patches; Astrology's
Letter C.1 was one additional cleanup patch).

**Common letter patterns:**

| Letter | Typical Scope |
|---|---|
| A | Anchor — docs, design plan, validation harness |
| B | First code — shared libraries, wrappers, infrastructure |
| C | Consolidation — migrate legacy state to new architecture |
| D | Core feature — primary domain logic |
| E | Integration — wire into Mythos (CLI, API, Telegram) |
| F+ | Refinement, completion, docs update |

### 3. SYSTEM_<NAME>.md structure

Eight sections in order:

```
1. Frontmatter (YAML)
2. Status — last patch letter, next patch, build phase
3. Architecture Summary — 2–4 paragraphs
4. Patch Ledger — letters, patch numbers, dates, scope
5. Current State — disk layout, DB state, service state
6. How to use — quick reference for common operations
7. Known issues / debt — honest accounting of what's left
8. Incoming Notes — append-only, date-stamped
```

### 4. NEXT_PATCH_SPEC.md structure

Exactly one patch ahead. Sections:

- Patch letter + proposed stream + patch number
- Scope — what files change, what SQL runs, what services restart
- Verification criteria — how we know it worked
- Rollback — how we undo it if it didn't
- Blast radius — low / medium / high

### 5. Golden fixture validation (non-negotiable)

Every sub-system ships a validation harness in Letter A before any
refactoring. The harness runs known inputs through the current system
and compares against known-good expected outputs.

Every subsequent patch runs the harness as the last gating step of
`apply_patch.py` and rolls back on failure.

**Astrology v2 result:** 5 aspect test cases ran at the end of every
patch (A through F — 9 patch runs total). Deltas were identical to 4
decimal places across all runs, confirming no calculation regression
across the entire build arc.

### 6. MANIFEST.yaml per patch

```yaml
stream: SEN
number: 10
letter: F
subsystem: astrology
description: "..."
patch_type: MINOR
services_restarted: []
tables_touched: []
blast_radius: low
review_link: null  # URL to external review if blast_radius >= medium
```

Blast radius ≥ medium triggers an external review before shipping
(Castor/Gemini for Astrology v2).

### 7. Service stop/start — Phase 0 allowlist

**Learned from Astrology v2 (SEN-0006 v1 failure):** Before calling
`patch.stop_service()` on any unit, register it with the allowlist:

```python
# Phase 0 — always before Phase 1 (stop services)
for svc in SERVICES_TO_MANAGE:
    patch.allowlist_append_unit(svc)
```

`mythos-allowlist-append` is idempotent. Phase 0 is cheap. Skip it and
Phase 1 fails even though systemctl succeeds — PatchBase records the
error and the patch rolls back.

### 8. Shadow-copy pattern for file moves

Never `mv` ephemeris files or other large data during a patch. Use:

1. Copy to new location (preserve original)
2. Verify (byte-count / checksum)
3. Run all tests
4. Only after all gates pass: archive/delete the old location

If anything fails between steps 1-3, the old location is still live.
Rollback is trivial.

### 9. CLI tools go to `/opt/mythos/bin/`

Always. Never `/usr/local/bin/`. The `bin/` directory is `adge:adge`
owned and on PATH. `/usr/local/bin/` is root-owned and requires sudo.

---

## Build workflow

```
Plan → Review → Letter A → B → ... → F
  ↓       ↓          ↓
SYSTEM_ V2.md   NEXT_PATCH_SPEC.md (one patch ahead, always)
docs      &     Golden fixtures at end of every patch (gate, not info)
          External review (Castor) for blast_radius ≥ medium
```

---

## Astrology v2 learnings (N=2)

These are the lessons that Finance v2 (N=1) didn't teach us, surfaced
during Astrology v2 build:

### L1. Verify live schema before writing queries

Never assume column names from architecture docs or prior sessions.
Before writing any SQL against a table, run `\d tablename` and compare.
Three tables had wrong columns in SEN-0008 v1 (`astro_retrogrades`,
`astro_fixed_star_conjunctions`, `astro_chart_points`), causing a clean
rollback and a v2. Verified schema → correct queries, first time.

### L2. The flags=0 Swiss Ephemeris footgun

`swe.calc_ut()` with `flags=0` silently returns `speed=0.0` for all
bodies. This makes retrograde detection and applying/separating logic
wrong without any error. The correct default is:

```python
DEFAULT_CALC_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED  # = 258
```

This is documented in `ephemeris.py` and should be copied into any
future sub-system that uses Swiss Ephemeris directly.

### L3. Bot handler registration patterns vary

`mythos_bot.py` registers some handlers at module level (imports) and
others inside the application setup function as lazy imports. Before
writing any anchor for a bot registration edit, check the actual
registration pattern with `grep -n "handler\|register" mythos_bot.py`.
The `register()` function convention in individual handler files exists
but is not universally called from `mythos_bot.py`.

### L4. The diagnostic before the patch — always

Per the workflow rule established during Astrology v2: stop at the
diagnostic phase. Don't build a patch until live system state is
confirmed. Costs: 2 minutes of diag time. Saves: 1+ failed installs
(SEN-0008 v1, SEN-0009 v1 both failed at phases where better diag
would have caught the issue before building).

### L5. Scope narrowing is correct

The Letter C.1 original spec planned 5 tasks; diag revealed 2 were
wrong (archiving 3 chart dirs when only 1 was genuinely stale; constant
alignment that had per-file shape differences making it non-mechanical).
Narrowing scope mid-arc based on diag findings is not failure — it's
the right response. File the deferred work in REQUESTS.md. Ship the
narrowed patch. Continue.

### L6. Existing engines before new engines

Letter E (Daily Transits) was initially specced as "build a transit
engine using ephemeris.py." Diag revealed `transit_pressure.py` +
`transit_interpreter.py` already exist, are mature, and produce
Ollama-voiced interpretations. Letter E became "wire the existing engine"
instead. Before building a new module, run `find /opt/mythos -name "*transit*"`
and similar surveys.

---

## Known limitations

1. **N=2.** Finance is transactional (append-only ledger); Astrology
   is snapshot-based. A third sub-system with different characteristics
   (stochastic computation, real-time streaming, external API dependency)
   may reveal further pattern limitations.

2. **Golden fixtures assume deterministic computation.** Works for
   ephemeris (exact positions) and finance (balanced trial balance).
   Won't work for Ollama-output validation or anything stochastic.

3. **`integrity.graph` crash loop** means the graph update step in the
   post-install pipeline always shows `⊘`. This doesn't block patches
   but limits graph-based diag capability. Fix tracked separately.

---

## Revision targets

- **Third sub-system ships Letter A:** N=3 revision. Validate the
  "universal" claim. Add sub-system #3 learnings section.

---

*Finance v2 proved the pattern could work. Astrology v2 proved it does.*
*Seven patches. One day. One clean arc.*
