---
title: "Astrology Next Patch Spec — Letter D"
category: spec
status: active
stream: SEN
location: docs/astrology
tags: [astrology, spec, next-patch]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Astrology Next Patch Spec — Letter D (Natal State — Postgres-first)

> **This file is rewritten wholesale at the end of every feature patch.**
> It describes exactly one patch ahead of the current state.
>
> **Current state:** Letter C.1 Cleanup (SEN-0007) shipped —
> `adriaan_harold_denkers/` chart dir archived and removed, stale YAML
> archived and removed, astro_position.py candidate-list fallback
> simplified, PATCH_HISTORY legacy SEN-0004 renamed to SEN-0004-LEGACY.
> Constant alignment was deliberately deferred to the
> "Comprehensive astrology tool audit + dedup" REQUESTS.md entry —
> per-file PLANETS/SIGNS/ASPECT_DEFS shape differences need dedicated
> migration work that doesn't belong in a cleanup patch.
>
> **This spec covers:** Letter D — Natal State (Postgres-first).
> **Expected patch number:** SEN-0008 (verify via `mythos-diag streams`).

---

## Scope

Per Castor round 1 review: Postgres-first, with JSON as rendering
artifact. Matches the Finance v2 pattern — the database is the source
of truth, and JSON outputs are generated on demand from the database.

1. **Schema: `astro_natal_charts` canonical shape**
   - Verify/extend the existing `astro_natal_charts` table (18 astro_*
     tables already exist per SEN-0006 integrity scan)
   - Explicit top-level keys: `house_system` (default 'Placidus'),
     `zodiac_type` (default 'tropical')
   - snake_case columns throughout
   - Foreign key to `people` table for person_id

2. **Generate canonical charts for Adge and Seraphe**
   - From `user_input/adge.yaml` (verified correct)
   - From `user_input/becky.yaml` (Seraphe's canonical YAML)
   - Write rows to `astro_natal_charts` with full planet positions,
     house cusps, angles, dispositors, dignities, fixed star conjunctions
   - Produce `charts/ka.json` and `charts/seraphe.json` as rendering
     artifacts from the DB rows (not the other way around)

3. **`natal_generator.py` module**
   - New file: `/opt/mythos/astrology/natal_generator.py`
   - `generate_natal(person_id: int) -> dict` — reads YAML, calculates
     via `astrology.ephemeris`, writes to `astro_natal_charts`,
     writes JSON artifact
   - `load_natal(person_id: int) -> dict` — reads from Postgres,
     optionally regenerates JSON if stale
   - Both use the canonical `astrology.ephemeris` module exclusively

4. **Golden fixture extension**
   - Add regression fixtures for natal-chart-level data (sun sign,
     moon sign, ASC, specific aspects)
   - Must match pre-v2 chart data to within existing tolerances

---

## Files created

| File | Purpose |
|---|---|
| `/opt/mythos/astrology/natal_generator.py` | Natal state engine (Postgres-first) |
| `/opt/mythos/migrations/sen_0008_natal_charts_schema.sql` | Schema extensions if needed |

---

## Files modified

None. This is a pure addition patch (like Letter B was).

---

## Files created as DB-sourced artifacts

| File | Source |
|---|---|
| `/opt/mythos/astrology/charts/ka.json` | Generated from `astro_natal_charts` row for Adge |
| `/opt/mythos/astrology/charts/seraphe.json` | Generated from `astro_natal_charts` row for Seraphe |

These are produced by `natal_generator.generate_natal()`. They are
regeneratable at any time from the database.

---

## SQL

| File | Action |
|---|---|
| `sen_0008_natal_charts_schema.sql` | Add top-level `house_system`/`zodiac_type` columns if missing, verify FK to people |

---

## Services restarted

None (new module, not yet imported by any live service).

---

## Verification

1. **Import smoke test** on `natal_generator.py`
2. **py_compile** (automatic via SYS-0077 pattern if edits needed)
3. **Generate Adge's natal chart** — row must appear in `astro_natal_charts`,
   JSON artifact must write to `charts/ka.json`
4. **Generate Seraphe's natal chart** — same for `charts/seraphe.json`
5. **Diff-check against preserved `full_chart_adge.json`** — new generation
   must match the preserved April 2 chart to within 0.01° on all positions
6. **All 5 existing golden fixtures must still pass** (regression gate)

---

## Rollback

PatchBase auto-rollback handles:
- New files removed on failure
- SQL migration reversed via per-migration DOWN script (if needed)
- JSON artifacts are regeneratable — not protected specifically

Can reverse: true.

---

## Blast radius

**Medium.** New module, new SQL, new artifacts. No services restarted,
no existing code modified. Risk is contained to new surface area.

---

## After Letter D ships

- Update `SYSTEM_ASTROLOGY.md` — mark D shipped, natal state Postgres-first
- Rewrite this file to describe Letter E (Daily Transits refactor)
- Verify `natal_generator.load_natal()` is ready for Letter E to consume

---

*End of Letter D spec.*
