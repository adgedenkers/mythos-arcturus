---
title: "SYSTEM: Astrology v2"
category: system
status: active
stream: SEN
location: docs
tags: [astrology, swisseph, transits, natal, system-doc]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# SYSTEM: Astrology v2

> **Workflow:** see `docs/WORKFLOW.md`
> **Design plan:** see `docs/ASTROLOGY_V2.md`
> **Pattern:** see `docs/SUB-SYSTEMS.md`
> **This doc:** canonical current state of Astrology v2. Updated after
> every patch lands. Read this before starting any astrology conversation.

---

## Status

- **Build phase:** COMPLETE — A→F shipped 2026-04-21
- **Last shipped patch:** F (SEN-0010) — 2026-04-21
- **Active work:** None. Post-v2 work tracked in REQUESTS.md.
- **Design plan:** `docs/ASTROLOGY_V2.md` (locked)

---

## Architecture Summary

Astrology v2 is a **Swiss Ephemeris–backed chart and transit engine**
living primarily in the SEN stream at `/opt/mythos/astrology/`. It
produces two things: **natal charts** (static per-person snapshots stored
Postgres-first with JSON artifacts) and **daily transit reports** (how
the current sky activates a natal chart, with Ollama-powered Iris-voiced
interpretations).

The engine uses `pyswisseph` directly via the **Master Ephemeris
Provider** (`astrology/ephemeris.py`). Kerykeion is retained for SVG
chart rendering only, and is configured to use the same ephemeris path.

All planetary position data flows through `ephemeris.py`. All natal
chart reads flow through `natal_generator.load_natal()`. All transit
computations flow through `transit_pressure.py` + `transit_interpreter.py`.

Ephemeris files live at `/opt/mythos/astrology/ephe/` (canonical).
The old `/opt/mythos/ephemeris/` path is archived at
`/opt/mythos/archive/ephemeris_pre_astro_v2/`.

---

## Patch Ledger

| Letter | Scope | Patch # | Shipped |
|--------|-------|---------|---------|
| A | Anchor — docs, `SYSTEM_ASTROLOGY.md`, `ASTROLOGY_V2.md`, `SUB-SYSTEMS.md` (draft), golden fixture harness with 5 verified aspect tests | SEN-0004 | 2026-04-21 |
| B | Ephemeris Provider — `ephemeris.py` (514 lines), `SE_EPHE_PATH` env var, `astrology/__init__.py` | SEN-0005 | 2026-04-21 |
| C | Consolidation — shadow-copy ephemeris files, fix 5 hardcoded paths, service stop/start, Kerykeion parity test, archive old ephemeris dir | SEN-0006 | 2026-04-21 |
| C.1 | Cleanup — archive `adriaan_harold_denkers/` chart dir + stale YAML, simplify `astro_position.py` candidate list, fix PATCH_HISTORY duplicate | SEN-0007 | 2026-04-21 |
| D | Natal State — `natal_generator.py` (load_natal, write_chart_artifact, generate_natal, self_check), generate `charts/ka.json` + `charts/seraphe.json` from Postgres | SEN-0008 | 2026-04-21 |
| E | Daily Transits — `transit_handler.py` (/transits Telegram command), wire natal_generator into transit_pressure.py, restart bot | SEN-0009 | 2026-04-21 |
| F | Integration — `daily-transits` CLI, update SYSTEM_ASTROLOGY.md, promote SUB-SYSTEMS.md to N=2 | SEN-0010 | 2026-04-21 |

---

## Current Disk State (post-SEN-0010)

### Key modules

| File | Purpose |
|---|---|
| `astrology/__init__.py` | Package marker (SEN-0005) |
| `astrology/ephemeris.py` | Master Ephemeris Provider — all swe calls go here |
| `astrology/natal_generator.py` | Postgres read/write interface for natal charts |
| `astrology/spiral/transit_pressure.py` | Daily transit computation + persistence |
| `astrology/spiral/transit_interpreter.py` | Ollama-powered Iris-voiced interpretations |
| `telegram_bot/handlers/transit_handler.py` | /transits Telegram command |
| `bin/daily-transits` | Shell CLI for transit reports |
| `astrology/tests/check_accuracy.py` | Golden fixture harness (5 test cases) |
| `astrology/tests/fixtures/expected_aspects.json` | Golden fixture data |

### Ephemeris

| Path | Status |
|---|---|
| `/opt/mythos/astrology/ephe/` | **Canonical** — full asteroid set (ast5/7/10/50/90/136 + planets/moon) |
| `/opt/mythos/archive/ephemeris_pre_astro_v2/` | Archived old location |
| `SE_EPHE_PATH=/opt/mythos/astrology/ephe` | Set in `/opt/mythos/.env` |

### Charts

| Path | Contents |
|---|---|
| `astrology/charts/ka.json` | Adge's canonical chart artifact (from Postgres) |
| `astrology/charts/seraphe.json` | Seraphe's canonical chart artifact (from Postgres) |
| `astrology/charts/adge/` | Original Feb 16 generation, preserved for regression diff |
| `astrology/charts/becky/` | Seraphe original, preserved |
| `astrology/charts/brandi/`, `fitz/`, `riley/`, `carl_jung/`, `test_person/` | Live charts |
| `astrology/archive/charts_pre_astro_v2/` | `adriaan_harold_denkers/` (wrong birth year) |

### YAML birth data

| File | Person | Status |
|---|---|---|
| `user_input/adge.yaml` | Adge — DOB 1977-11-22, Albany NY | Canonical ✓ |
| `user_input/becky.yaml` | Seraphe — DOB 1978-08-19 14:02, Norwich NY | Canonical ✓ |
| `user_input/brandi.yaml` | Brandi Carlile | Live |
| `user_input/fitz.yaml` | Fitz | Live |
| `user_input/riley.yaml` | Riley Green | Live |
| `user_input/carl_jung.yaml` | Carl Jung | Live |
| `user_input/test_person.yaml` | Test fixture | Live |

---

## Database State

### astro_natal_charts (7 rows)

| chart_id | name | birth_date | birth_time |
|---|---|---|---|
| 9 | Adge | 1977-11-22 | 08:30 |
| 10 | Fitz | 2010-09-08 | 14:39 |
| 11 | Becky Denkers | 1978-08-19 | 14:02 |
| 12 | Riley Green | 1988-10-18 | 14:45 |
| 13 | Brandi Carlile | 1981-06-01 | 15:45 |
| 16 | Test Person | 1990-03-15 | 15:30 |
| 17 | Adriaan Harold Denkers | 1978-11-22 | 08:30 ⚠ wrong year |

Chart 17 (`Adriaan Harold Denkers`) has wrong birth year 1978. Source
YAML was archived in SEN-0007. The DB row remains for historical record
but should not be used for calculations.

### Child tables

14 child tables all FK-linked to `astro_natal_charts.chart_id` with
`ON DELETE CASCADE`: `astro_chart_objects` (109 rows), `astro_natal_aspects`
(749 rows), `astro_natal_house_cusps` (84 rows), `astro_dignities`,
`astro_retrogrades`, `astro_sect`, `astro_balance`, `astro_arabic_parts`,
`astro_fixed_star_conjunctions`, `astro_chart_ruler`, `astro_dispositors`,
`astro_geometric_patterns`, `astro_chart_points`, `astro_geometry_audit`.

### Transit tables

| Table | Purpose |
|---|---|
| `spiral_transit_pressure` | Daily transit aspects, orbs, applying/separating, threshold levels |
| `astro_events` | Sky events (ingresses, stations, eclipses, lunations) |

---

## How to use

### Daily transits (Telegram)

```
/transits              — today, Adge, full Ollama interpretations
/transits seraphe      — today, Seraphe
/transits brief        — today, Adge, no LLM (fast)
/transits date 2026-04-28  — specific date
```

### Daily transits (CLI)

```bash
daily-transits                    # today, Adge, full
daily-transits seraphe            # today, Seraphe
daily-transits adge 2026-04-28   # specific date
daily-transits brief              # fast, no Ollama
```

### Load a natal chart programmatically

```python
from astrology.natal_generator import load_natal
chart = load_natal('Adge')  # reads from Postgres
planets = chart['chart_objects']
sun_lon = planets['Sun']['longitude']
```

### Compute transits programmatically

```python
from astrology.spiral.transit_pressure import get_todays_pressure
aspects = get_todays_pressure(chart_id=9)  # Adge
```

---

## Libraries

| Library | Use |
|---|---|
| `pyswisseph` 20230604 | All ephemeris calculations (via `ephemeris.py`) |
| `kerykeion` 5.x | SVG chart rendering only |

---

## Known issues / debt

1. **Chart 17 wrong birth year** — `Adriaan Harold Denkers` in DB has
   1978 birth year (should be 1977 = same as Adge). Source YAML deleted
   in SEN-0007. DB row left for audit trail. Do not use for calculations.

2. **`weekly_report.py` uses Kerykeion directly** — not migrated to use
   `ephemeris.py`. Covered by the "Comprehensive astrology tool audit"
   REQUESTS.md entry scheduled for post-A→F.

3. **`astrochart_cli_engine.py` monolith** — 1500 LOC with its own
   copies of ELEMENTS/MODALITIES constants. Also covered by audit request.

4. **`transit_pressure.py` uses narrow orbs** — 3° maximum for all
   aspects, tighter than `ephemeris.py`'s default ASPECT_DEFS. This is
   intentional (spiral time context) but worth noting for comparison
   with `/transits` output.

5. **`integrity.graph` crash loop** — `mythos-obs-graph.service` is in
   auto-restart. Unrelated to astrology v2 but noted since it causes
   `⊘ Graph: integrity.graph not available` in every post-install pipeline.

---

## Post-v2 work (REQUESTS.md)

Three requests filed for after A→F:

1. **SYS: Full graph coverage + post-patch verification gate**
2. **SYS: PatchBase microtool kit with Ollama integration**
3. **SEN: Comprehensive astrology tool audit + dedup**

These are now unblocked. Schedule in SYS/SEN capacity planning.

---

## Incoming Notes

> Append-only, date-stamped, never edit. Review when astrology work resumes.

**2026-04-21** (SEN-0004): Castor (Gemini) reviewed ASTROLOGY_V2 plan,
round 1. Six critiques accepted. Full review in `ASTROLOGY_V2.md` §16.

**2026-04-21** (SEN-0004): `charts/adge/full_chart_adge.json` preserved
in `archive/charts_pre_astro_v2/` for regression diff after Letter D
regenerates `ka.json`. Diff to surface any Moshier→Swiss precision shift.

**2026-04-21** (SEN-0005): Swiss Ephemeris footgun documented — `flags=0`
silently returns speed=0.0 for all bodies. `DEFAULT_CALC_FLAGS = FLG_SWIEPH | FLG_SPEED`
(=258) is the correct default. Set in `ephemeris.py`.

**2026-04-21** (SEN-0006): Two scripts (`lunar_calendar_worker.py` and
`seraphe_lunar_generator.py`) were silently using Moshier approximation
because their isdir() guards on `/opt/mythos/ephemeris/ephe/` (non-existent
path) silently failed. Letter C upgraded them to full Swiss Ephemeris.
Expected position shifts: sub-arcsecond inner planets, up to ~0.1° outer.

**2026-04-21** (SEN-0009): `transit_pressure.py` now wired to
`natal_generator` via `_load_natal_positions_via_generator()`. Falls
back to raw Postgres if natal_generator is unavailable.

**2026-04-21** (SEN-0010): Astrology v2 A→F complete.

---

*Seven patches. One day. The sky is now queryable.*
