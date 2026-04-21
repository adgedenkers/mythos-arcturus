---
title: "Astrology Next Patch Spec — Letter C.1"
category: spec
status: active
stream: SEN
location: docs/astrology
tags: [astrology, spec, next-patch]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Astrology Next Patch Spec — Letter C.1 (Cleanup)

> **This file is rewritten wholesale at the end of every feature patch.**
> It describes exactly one patch ahead of the current state.
>
> **Current state:** Letter C Engine (SEN-0006) shipped — ephemeris files
> consolidated, 5 hardcoded paths fixed, services restarted cleanly,
> parity test passed, golden fixtures passed, old `/opt/mythos/ephemeris/`
> archived.
> **This spec covers:** Letter C.1 — Cleanup.
> **Expected patch number:** SEN-0007 (verify via `mythos-diag streams`).

---

## Scope

The "social" and "housekeeping" tasks that Castor split out from Letter C
so Letter C could focus purely on file-system and path-logic. All lower
blast-radius than C itself.

1. **Align scripts with duplicate constants** — identify scripts in
   `/opt/mythos/astrology/` that have their own copies of `PLANETS` /
   `SIGNS` / `ASPECT_DEFS` / `ELEMENTS` / `MODALITIES` and update them
   to import from `astrology.ephemeris` instead. Known candidates:
   `astrochart_cli_engine.py` (1,500 LOC monolith), `astrochart_cli_geometry.py`,
   `astro_position.py`, `astro_loader.py`. Preflight diagnostic will
   produce exhaustive list.

2. **Archive duplicate chart directories** —
   `charts/adge/`, `charts/adriaan_harold_denkers/`, `charts/becky/`
   all move to `/opt/mythos/astrology/archive/charts_pre_astro_v2/`.
   Preserves `full_chart_adge.json` per Adge's explicit instruction.
   New canonical charts (`ka.json`, `seraphe.json`) are produced in
   Letter D, not this patch.

3. **Delete stale YAML** — `user_input/adriaan_harold_denkers.yaml`
   has wrong birth year (1978 vs correct 1977) and is redundant with
   `user_input/adge.yaml`. Backed up to archive before delete.

4. **Fix PATCH_HISTORY.md duplicate SEN-0004 entry** — rename the
   legacy "Planetary geometry engine" entry to `SEN-0004-LEGACY` so
   the current "astrology v2 anchor" entry stands clean.

5. **Simplify `astro_position.py` candidate-list fallback** — it
   currently has a 6-entry candidate list with `SWISSEPH_PATH` env,
   relative paths, `/dev/...` paths, etc. Replace with a single line
   matching the pattern of the 4 files updated in Letter C.

---

## Files created

None.

---

## Files modified

| File | Change |
|---|---|
| `/opt/mythos/astrology/astrochart_cli_engine.py` | Remove local constants, `from astrology.ephemeris import *` |
| `/opt/mythos/astrology/astrochart_cli_geometry.py` | Same |
| `/opt/mythos/astrology/astro_position.py` | Replace candidate list, import constants |
| `/opt/mythos/astrology/astro_loader.py` | Same |
| `/opt/mythos/docs/PATCH_HISTORY.md` | Rename legacy SEN-0004 entry |

(Full list pending preflight diagnostic.)

---

## Files deleted

| File | Reason |
|---|---|
| `/opt/mythos/astrology/user_input/adriaan_harold_denkers.yaml` | Wrong birth year, redundant with `adge.yaml`. Backed up to archive first. |

---

## Files archived

| Source | Destination |
|---|---|
| `/opt/mythos/astrology/charts/adge/` | `/opt/mythos/astrology/archive/charts_pre_astro_v2/charts_adge_original/` |
| `/opt/mythos/astrology/charts/adriaan_harold_denkers/` | `/opt/mythos/astrology/archive/charts_pre_astro_v2/charts_adriaan_harold_denkers/` |
| `/opt/mythos/astrology/charts/becky/` | `/opt/mythos/astrology/archive/charts_pre_astro_v2/charts_becky_original/` |
| `/opt/mythos/astrology/user_input/adriaan_harold_denkers.yaml` | `/opt/mythos/astrology/archive/charts_pre_astro_v2/` |

Note: `full_chart_adge.json` is preserved intact via the `charts_adge_original/`
archive per Adge's explicit instruction.

---

## SQL

None.

---

## Services restarted

None (pure code + file organization changes).

---

## Verification

1. **Import smoke test** on each modified script — must import without error
2. **py_compile** on each modified script (automatic via PatchBase)
3. **Golden fixture harness** must pass all 5 (same as C)
4. **`grep -r "^PLANETS\s*=" /opt/mythos/astrology/`** should return only
   `ephemeris.py` (no duplicate definitions remain)

---

## Rollback

PatchBase auto-rollback handles file restorations via backup system.
Archive directories can be moved back manually if needed. Patch will
declare `can_reverse=true`.

---

## Blast radius

**Low-Medium.** Many files touched but each change is mechanical
(replace local constant with import). No service restarts, no schema
changes. Lower risk than C.

---

## After Letter C.1 ships

- Update `SYSTEM_ASTROLOGY.md` — mark C.1 shipped, C audit summary
- Rewrite this file to describe Letter D (Natal State Postgres-first)
- Run follow-up diagnostic for the comprehensive astrology audit
  request in `REQUESTS.md` — use the Letter C.1 post-state as baseline

---

*End of Letter C.1 spec.*
