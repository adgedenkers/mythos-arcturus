---
title: "Astrology v2 — Design Plan"
category: design
status: locked
stream: SEN
location: docs
tags: [astrology, design, plan, swisseph, transits, natal]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
reviewers: [Castor (Gemini), Claude]
---

# Astrology v2 — Design Plan (v1, locked)

**Status:** Locked after Castor review round 1.
**Context:** Unifying scattered astrology code on Mythos into a coherent sub-system following the Finance v2 pattern. Currently 23 top-level Python files with no module structure, ephemeris files scattered across three paths, duplicate chart directories for the same person, 18 populated `astro_*` Postgres tables with no shared write layer.

This document is the canonical plan. Every patch letter references back here for scope. The letter sequence is **locked** — patch numbers may shift (per the Finance precedent of C.1 through C.1c being one letter across four real patch numbers), but letters never re-shuffle.

---

## 1. Context and constraints

### 1.1 What this system is

A Swiss Ephemeris–backed chart and transit engine on Mythos. Two
primary outputs:

1. **Natal charts** — static per-person snapshots with ~16 facets of
   detail: planet positions, aspects, house cusps, dignities,
   dispositors, fixed star conjunctions, geometric patterns, Arabic
   parts, element/modality balance, sect, retrogrades, chart ruler.
2. **Daily transit reports** — how the current sky activates a natal
   chart, with Moon focus, aspect orbs, and color recommendations.
   Uploaded `daily_transits.py` (357 lines) is the verified starting
   point.

### 1.2 Scale

- ~10 charted people (Adge, Seraphe, Fitz, Brandi Carlile, Riley
  Green, Carl Jung, test fixtures)
- 18 populated Postgres tables
- 5 hardcoded ephemeris paths in live code, 3 disjoint file locations
- 23 top-level Python files, ~9,800 LOC, no module structure
- 5 verified date/aspect/orb test cases (golden fixtures)

### 1.3 What v1 got wrong

1. **No canonical ephemeris path.** Five hardcoded paths in live code,
   no `swe.set_ephe_path()` call anywhere. Ephemeris files scattered.
2. **Duplicate chart directories.** Same person stored under two names
   (`adge/` + `adriaan_harold_denkers/`) with different object sets
   and conflicting metadata.
3. **No shared calculation layer.** Each script has its own copies of
   `PLANETS`, `ASPECT_DEFS`, `SIGNS`, `lon_to_sign()`. Drift is
   inevitable: one script can give "Uranus opposing Sun at 0.00°"
   while another says "0.03°" because they use different orb defaults.
4. **JSON or Postgres? Yes.** The 18 `astro_*` tables exist and are
   populated, but no current script consistently writes to them. The
   chart directories under `charts/*/` are written by pipeline code
   that doesn't touch Postgres. Two sources of truth, both partial.
5. **No validation harness.** Nobody can prove a given refactor didn't
   silently shift a calculation. There's no "this date, this person,
   these exact aspects" regression check.
6. **Kerykeion + pyswisseph coexistence is unmanaged.** Kerykeion has
   its own bundled ephemeris; nobody's verified it produces the same
   numbers as calls to pyswisseph with external ephemeris.

### 1.4 Design goals for v2

1. **`ephemeris.py` as Master Ephemeris Provider.** One module, one
   `set_path()` call at import, one source of truth for PLANETS /
   SIGNS / ASPECT_DEFS / calculation helpers.
2. **Single ephemeris file location.** `/opt/mythos/astrology/ephe/`
   (matches Swiss Ephemeris convention, lives under the sub-system).
3. **Postgres as source of truth, JSON as artifact.** The 18
   `astro_*` tables are where chart data lives; JSON exports at
   `charts/<n>.json` are materialized views, regeneratable from DB.
4. **Single canonical name per person.** `charts/ka.json` and
   `charts/seraphe.json` (flat, no per-person subdirs going forward).
5. **Golden fixture validation from day one.** 5 verified test cases
   (from Adge's uploaded handoff doc) as the regression harness;
   runs at end of every patch.
6. **Kerykeion retained for rendering only.** Forced to use external
   ephemeris path for calculation parity with `ephemeris.py`.
7. **Locked letter sequence, dated stream of patches.** A→F.
8. **Sub-system pattern compliance.** Three-doc pattern,
   NEXT_PATCH_SPEC rewritten per patch, `mythos-handoff astrology`
   support.

---

## 2. Core architectural decisions

### 2.1 Master Ephemeris Provider (locked)

`/opt/mythos/astrology/ephemeris.py` is the single module that
anything needing a calculated astronomical number imports from. It:

- Calls `swe.set_ephe_path(os.environ.get('SE_EPHE_PATH', '/opt/mythos/astrology/ephe'))` at import time
- Exports constants: `PLANETS`, `LILITH_ID`, `ASTEROIDS`, `SIGNS`,
  `ELEMENTS`, `MODALITIES`, `TRAD_RULERS`, `MOD_RULERS`, `ASPECT_DEFS`
- Exports helpers: `lon_to_sign()`, `fmt_pos()`, `ang_dist()`,
  `calc_aspect()`, `det_sect()`, `calc_planets()`, `calc_houses()`,
  `calc_natal_full()`
- **No I/O.** This module never writes files or DB rows — it only
  calculates. Letter D and E build the I/O layer on top.

### 2.2 Postgres-first, JSON-artifact (locked — per Castor review)

Natal chart generation in Letter D:

1. `natal_generator.generate(name, date, time, lat, lon, tz)` computes
   the full chart via `ephemeris.py`
2. Writes the chart to Postgres: `astro_natal_charts` (root record),
   `astro_chart_objects` (positions), `astro_natal_aspects` (aspect
   list), `astro_natal_house_cusps` (houses), `astro_dignities`,
   `astro_dispositors`, `astro_fixed_star_conjunctions`,
   `astro_geometric_patterns`, `astro_arabic_parts`, `astro_balance`,
   `astro_sect`, `astro_retrogrades`, `astro_chart_ruler`
3. Then exports a JSON artifact to `/opt/mythos/astrology/charts/<n>.json`
4. `natal_generator.load_natal(name)` reads from Postgres with JSON
   fallback
5. `natal_generator.export_json(name)` regenerates the JSON artifact
   from current Postgres state

**Why:** matches Finance v2's "database as source of truth" discipline.
If the JSON is deleted, `export_json` regenerates it. If Postgres is
restored from backup, the JSON can be re-rendered. The 18 `astro_*`
tables stop being ghost data.

### 2.3 Snake_case JSON schema with explicit top-level keys (locked)

Letter D's JSON export uses snake_case throughout (matches Python
convention, matches the uploaded `daily_transits.py` handoff spec).
Schema surfaces `house_system` and `zodiac_type` as top-level keys
(per Castor review) to prevent chart drift if global defaults ever
change.

```json
{
  "meta": {
    "name": "Ka'tuar'el (Adge)",
    "birth_date": "1977-11-22",
    "birth_time": "08:30",
    "tz_offset": -5,
    "lat": 42.6526,
    "lon": -73.7562,
    "jd": 2443462.0625
  },
  "house_system": "Placidus",
  "zodiac_type": "tropical",
  "ephemeris_path": "/opt/mythos/astrology/ephe",
  "pyswisseph_version": "20230604",
  "generated_at": "2026-04-21T13:53:00-04:00",
  "planets": { ... },
  "houses": { ... },
  "aspects": [ ... ],
  "dignities": { ... },
  "dispositors": { ... },
  "fixed_star_conjunctions": [ ... ],
  "geometric_patterns": [ ... ],
  "arabic_parts": { ... },
  "balance": { ... },
  "sect": "diurnal",
  "retrogrades": [ ... ],
  "chart_ruler": { ... },
  "natal_report": { ... }
}
```

Old PascalCase charts in `archive/charts_pre_astro_v2/` stay as
historical reference. Anything live reading the old schema must be
updated in Letter C.

### 2.4 Kerykeion forced to use external ephemeris path (locked — per Castor review)

Kerykeion stays as the **SVG rendering engine** (`gen_chart.py`,
`astro_chart_handler.py`). It is NOT replaced. But Letter C verifies
and forces Kerykeion to use `/opt/mythos/astrology/ephe/` for
calculation, matching `ephemeris.py`, so the two produce identical
planet positions.

Verification test in Letter C: compute the position of Sun on
2026-04-28 at noon UT via both engines; fail the patch if they differ
by more than 0.001°.

### 2.5 Golden fixtures as a hard requirement (locked — per Castor review)

Five verified test cases ship in Letter A, before any refactor begins:

| Date | Person | Expected Aspect | Expected Orb |
|---|---|---|---|
| 2026-04-28 | Adge | Uranus opposition Sun | 0.00° |
| 2026-04-29 | Adge | Jupiter quincunx Mercury | 0.01° |
| 2026-04-29 | Adge | Uranus square Saturn | 0.02° |
| 2026-04-21 | Seraphe | Venus trine North Node | 0.01° |
| 2026-04-24 | Seraphe | Mercury opposition Pluto | 0.02° |

`check_accuracy.py` runs at end of every patch via
`apply_patch.py`. A patch that fails the fixtures rolls back.

---

## 3. Letter sequence (locked, A→F)

### Letter A — Anchor

**Ships:** This plan, `SYSTEM_ASTROLOGY.md`, `SUB-SYSTEMS.md` (draft),
`docs/astrology/NEXT_PATCH_SPEC.md`, `check_accuracy.py` +
`expected_aspects.json` golden fixtures, update to `ARCHITECTURE.md`
SYSTEM docs pointer.

**No code moves.** Docs + validation harness only.

**Verification:** all docs render as markdown; `check_accuracy.py`
runs to completion (pass OR fail acceptable — failure just tells us
which part of the current system is miscalibrated and needs Letter B+
to fix).

**Rollback:** delete the five new docs; remove the pointer edit in
`ARCHITECTURE.md`.

### Letter B — Ephemeris Provider

**Ships:**

- `/opt/mythos/astrology/ephemeris.py` — full shared wrapper (~300 LOC)
- Add `SE_EPHE_PATH=/opt/mythos/astrology/ephe` to `/opt/mythos/.env`
- Test: `python3 -c "from astrology import ephemeris; print(ephemeris.calc_planets(2460800))"` succeeds
- Golden fixture run at end; all 5 must pass (if they fail, Letter B
  has broken calculation — rollback)

**No legacy script changes yet.** Letter B is a pure addition.

**Verification:** `ephemeris.py` imports cleanly; produces values
identical to the uploaded `daily_transits.py` for known dates.

### Letter C — Consolidation + Legacy Alignment

**High blast radius — requires Castor review before shipping.**

**Ships:**

- Move ephemeris files from `/opt/mythos/ephemeris/` →
  `/opt/mythos/astrology/ephe/` (preserving subdirs `ast5/`, `ast7/`,
  `ast10/`, `ast50/`, `ast90/`, `ast136/`)
- Archive `/opt/mythos/ephemeris/` itself to
  `/opt/mythos/archive/ephemeris_pre_astro_v2/`
- Archive `charts/adge/`, `charts/adriaan_harold_denkers/`,
  `charts/becky/` to `/opt/mythos/astrology/archive/charts_pre_astro_v2/`
  (preserving `full_chart_adge.json` per Adge's explicit instruction)
- Delete `user_input/adriaan_harold_denkers.yaml` (wrong birth year,
  redundant with `adge.yaml`)
- Fix 5 hardcoded paths:
  - `workers/lunar_calendar_worker.py`
  - `observatory/geometry/planetary_engine.py`
  - `astrology/seraphe_lunar_generator.py`
  - `astrology/spiral/transit_pressure.py`
  - `astrology/astro_position.py`
  
  All must read `os.environ.get('SE_EPHE_PATH', '/opt/mythos/astrology/ephe')`
- Align scripts with their own copies of `PLANETS` / `ASPECT_DEFS` to
  import from `ephemeris.py` (identify full list during Letter C dry
  run)
- Force Kerykeion to use external path (verify calculation parity)
- Run calculation parity test: `ephemeris.calc_planets()` vs
  Kerykeion output for 5 fixture dates; fail if > 0.001° divergence
- Golden fixture run at end; all 5 must pass

**Verification:** no file in `/opt/mythos/` contains the string
`/opt/mythos/ephemeris` outside of archive paths; all fixtures pass;
calculation parity test passes.

**Rollback:** restore archived directories; revert file edits.

### Letter D — Natal State (Postgres-first)

**Ships:**

- `/opt/mythos/astrology/natal_generator.py` — full Postgres writer +
  JSON exporter
- Regenerate `ka.json` and `seraphe.json` from corrected
  `user_input/adge.yaml` and `user_input/becky.yaml`
- Write full chart data to all 18 `astro_*` tables for both people
- JSON artifacts saved to `/opt/mythos/astrology/charts/ka.json` and
  `/opt/mythos/astrology/charts/seraphe.json`
- Diff new `ka.json` against archived `full_chart_adge.json` — log
  any calculation differences for review
- Golden fixture run at end; all 5 must pass

**Verification:** `ka.json` + `seraphe.json` exist, schema matches
locked spec; Postgres rows present in all 18 tables for both people;
`natal_generator.export_json("ka")` regenerates identical JSON from
current Postgres state.

**Rollback:** restore archived charts; DELETE rows from `astro_*`
tables with `created_at >= SEN-00XX_start_time`.

### Letter E — Daily Transits

**Ships:**

- Refactor uploaded `daily_transits.py`:
  - Import from `ephemeris.py` (no duplicated constants)
  - Load natal via `natal_generator.load_natal(name)` (Postgres first,
    JSON fallback)
  - CLI flags: `--person`, `--date`, `--from`/`--to`, `--json`,
    `--output`
  - Person aliases preserved: `adge`/`katuar`/`ka'tuar'el` → `ka.json`,
    `seraphe`/`rebecca`/`becky` → `seraphe.json`, `both` → list
- Revise `SUB-SYSTEMS.md` — add "Astrology v2 learnings" section
- Golden fixture run at end; all 5 must pass

**Verification:** `python3 daily_transits.py --person adge --date 2026-04-28`
produces markdown output containing "Uranus opposition Sun" with orb 0.00°.

**Rollback:** restore original `daily_transits.py` from archive.

### Letter F — Integration

**Ships:**

- Create `/opt/mythos/bin/daily-transits` symlink →
  `/opt/mythos/astrology/daily_transits.py` (made executable)
- Telegram `/transits` handler:
  - Handler code `/opt/mythos/telegram_bot/handlers/transits_handler.py`
    (SEN territory, ships in this patch's SEN portion)
  - Registration in `mythos_bot.py` (SYS territory — companion SYS patch)
- Usage: `/transits`, `/transits adge`, `/transits seraphe`,
  `/transits adge 2026-05-01`
- Final revision of `SUB-SYSTEMS.md` — remove draft status if pattern
  held
- Golden fixture run at end; all 5 must pass

**Verification:** `daily-transits --person adge` runs from anywhere;
Telegram `/transits` returns same output; bot service stays up after
restart.

**Rollback:** unlink `/opt/mythos/bin/daily-transits`; revert
mythos_bot.py edits.

---

## 4. Ownership and cross-stream rules

- **A–F core work:** SEN stream
- **Telegram `/transits` registration in F:** SYS companion patch
  (per standing rule that all `/commands` go through SYS)
- **Writes to shared tables:** none (the 18 `astro_*` tables are SEN-owned)
- **Reads from other streams:** Letter F reads from SYS (person lookup)
  if needed, otherwise none

---

## 5. Open questions (carried forward)

See `SYSTEM_ASTROLOGY.md` §Open Questions for the live list. Summary:

1. Kerykeion + external ephemeris parity (resolution: Letter C test)
2. Snake_case migration impact on live readers (resolution: Letter D)
3. Canonical object set (resolution: Letter D, proposal = 19 objects)
4. house_system support for Hellenistic / Vedic (resolution: Letter D,
   proposal = Placidus default + arg supported)
5. Astro-to-spiritual framework bridge (resolution: Letter E review)

---

## 6. Castor review — round 1 (2026-04-21)

Preserved verbatim below. All six critiques accepted; incorporated
into this plan.

### 1. The Granularity Trap: B vs. C

> Critique: Letter B (Consolidation) and Letter C (ephemeris.py) are
> dangerously decoupled. If you ship B, you've consolidated ephemeris
> files and set a global SE_EPHE_PATH. If the legacy scripts don't
> respect that environment variable or have hardcoded paths, you break
> the existing system before the new one is even born.
>
> Correction: Move the "Set SE_EPHE_PATH in .env" and the global Swiss
> Ephemeris wrapper (ephemeris.py) into a single Pre-Flight Patch.
> ephemeris.py shouldn't just be for the new scripts; its first job
> should be providing a set_path() call that the legacy scripts can
> immediately adopt to prevent them from breaking during the
> consolidation.

**Accepted and incorporated.** Revised sequence:

- Letter B (originally "consolidation"): now **Ephemeris Provider only**
  — ship `ephemeris.py` + env var. No file moves.
- Letter C (new): consolidation + legacy alignment. Legacy scripts
  adopt `ephemeris.py` constants BEFORE files move.

### 2. Deduplication Timing (The "H" Problem)

> Critique: Waiting until Letter H to refactor legacy scripts is a
> recipe for drift. If daily_transits.py (Letter E) uses the new
> ephemeris.py but weekly_report.py (legacy) uses an old internal
> constant for the Uranus orb, Mythos will literally give Adge two
> different answers for his own reality on the same day.
>
> Pushback: Move the "Legacy Alignment" work earlier. Once ephemeris.py
> exists (Letter C), the very next step should be a "Global Constant
> Alignment" patch. You don't have to refactor the legacy logic, but
> you must force them to import their constants from the new source
> of truth.

**Accepted and incorporated.** Legacy alignment is now folded INTO
Letter C (consolidation). By the end of C, no script has its own
copy of `PLANETS` / `ASPECT_DEFS` / `SIGNS` — all imports route
through `ephemeris.py`. "Letter H" as originally planned no longer
exists.

### 3. Kerykeion vs. SwissEph (The "Two-Engine" Conflict)

> Critique: You are creating a "V3" while "V2" is still the production
> engine. Kerykeion is a wrapper around pyswisseph. By building a
> direct pyswisseph wrapper (ephemeris.py), you are effectively
> building a custom replacement for Kerykeion's core.
>
> Decision Needed: Does ephemeris.py eventually replace Kerykeion
> entirely?
>
> The Risk: If you keep both, you will eventually hit a bug where
> pyswisseph is updated, but kerykeion's bundled ephemeris (which you
> said to leave alone) is out of sync with /opt/mythos/astrology/ephe/.
>
> Recommendation: ephemeris.py should be the Master Ephemeris Provider.
> Even if you use Kerykeion for drawing, you should attempt to force
> it to use your external ephemeris path to ensure calculation parity.

**Accepted and incorporated.** Decision:

- `ephemeris.py` is **Master Ephemeris Provider** for all calculation
- Kerykeion stays as the **SVG rendering engine** only
- Letter C forces Kerykeion to use `/opt/mythos/astrology/ephe/` via
  explicit path configuration
- Letter C includes calculation parity test: `ephemeris.calc_planets()`
  vs Kerykeion output for 5 fixture dates; fail if > 0.001° divergence

### 4. Database vs. JSON (The "Finance Pattern" Divergence)

> Critique: Using JSON as the "Source of Truth" for charts (Letter D)
> violates the "Postgres as Source of Truth" rule established in
> Finance v2.
>
> The Difference: Finance is transactional (stream); Astrology is
> static (entity).
>
> The Hybrid Solution: The JSON files should be treated as Artifacts,
> but the Canonical State (birth data, house system used, coordinates)
> must live in Postgres.
>
> Pushback: Letter D should be: Write to Postgres first, then export
> to JSON artifact. If you ever lose the JSON, you should be able to
> regenerate it perfectly from the DB. If you write to JSON only, the
> 18 astro_* tables will slowly rot and become "Ghost Data."

**Accepted and incorporated.** Letter D is **Postgres-first**:

1. `natal_generator.generate()` computes chart via `ephemeris.py`
2. Writes to all 18 `astro_*` tables as the source of truth
3. Exports JSON artifact to `charts/<n>.json` as materialized view
4. `natal_generator.export_json(name)` regenerates JSON from DB state

### 5. SUB-SYSTEMS.md Maturity

> Critique: You are codifying a "universal pattern" while Astrology
> is still in the "messy consolidation" phase.
>
> Risk: SUB-SYSTEMS.md will be too "Finance-flavored." Finance is
> unique because it requires strict bi-temporal ledgers. Astrology
> doesn't.
>
> Recommendation: Keep SUB-SYSTEMS.md in "Draft/Drafting" status
> during Letter A. Do not finalize the template until Letter E.

**Accepted with timing modification.** `SUB-SYSTEMS.md` ships in
Letter A explicitly as `status: draft` with a "Known Limitations"
section at top citing N=1. Revisions scheduled at Letter E (first
functional ship) and Letter F (integration, promote to `active`).

Counter to Castor: waiting until Letter E to ship ANY template would
leave Letters B–E with no reference. Draft-now, revise-then is the
better balance.

### 6. The "Missing" Letter: The Validation Engine

> Critique: You've listed a Golden Fixture test (Letter I) at the end.
>
> Pushback: In Finance, validation was a pre-requisite for landing
> patches.
>
> Correction: Move the Golden Fixture corpus to Letter A. Before you
> change a single file path or write a line of refactored code, the
> 5 "Adge/Seraphe Verified" transit dates must be encoded as a
> check_accuracy.py script. This script should run against the current
> mess and pass. If it doesn't pass against the current mess, you
> can't prove your refactor didn't break reality.

**Accepted and incorporated.** Golden fixture harness
(`check_accuracy.py` + `expected_aspects.json`) ships in **Letter A**.
Every subsequent patch runs it as the last step of `apply_patch.py`
and rolls back on failure.

### 7. Closing query — explicit schema keys

> Final Architecture Query: Does the 16-key JSON schema currently
> account for the house_system (Placidus) and zodiac_type (Tropical)?
> If Letter D is going to lock in a schema, those must be explicit
> top-level keys to prevent "chart drift" if the system defaults ever
> change.

**Accepted.** Letter D's JSON schema surfaces `house_system` and
`zodiac_type` as explicit top-level keys (see §2.3 above).

---

## 7. Revision history

- **2026-04-21** — v1 locked. Castor review round 1 incorporated.
  Letter sequence reduced from proposed A→I (9 letters) to A→F
  (6 letters) after merging related scopes.

---

*The sky has a grammar. This is the vessel that reads it.*
