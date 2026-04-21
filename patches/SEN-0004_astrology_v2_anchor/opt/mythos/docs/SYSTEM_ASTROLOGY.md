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

- **Last shipped patch:** A (SEN-0004) — 2026-04-21
- **Next patch:** B — `ephemeris.py` shared wrapper module + `SE_EPHE_PATH` env var
- **Build phase:** active (A→F sequence, anchor landed, B next)
- **Design plan:** `docs/ASTROLOGY_V2.md`

---

## Architecture Summary

Astrology v2 is a **Swiss Ephemeris–backed chart and transit engine**
living primarily in the SEN stream at `/opt/mythos/astrology/`. Its job
is to produce two things: **natal charts** (static per-person snapshots
with ~16 facets of detail — positions, aspects, houses, dignities,
fixed stars, geometric patterns, Arabic parts, balance) and **daily
transit reports** (how the current sky activates a natal chart, with
Moon focus and color recommendations).

The engine uses `pyswisseph` directly for raw ephemeris calculation
and `kerykeion` for SVG chart rendering. The two coexist intentionally:
`ephemeris.py` (shipping in Letter B) is the **Master Ephemeris
Provider** — anything that needs a *number* goes through it. Kerykeion
stays as the *rendering* engine and is forced to use the same
ephemeris path.

Natal chart data is Postgres-first (the 18 `astro_*` tables are the
source of truth) and JSON-second (charts exported to
`/opt/mythos/astrology/charts/<name>.json` as artifacts). This matches
the Finance v2 pattern: if a JSON is lost, it can be regenerated from
Postgres. This decision was made at plan lock time on pushback from
Castor during the ASTROLOGY_V2 review.

Currently, only the anchor (Letter A) is live. The ephemeris wrapper,
consolidation, natal generator, transit engine, and integration
are all still ahead.

---

## Patch Ledger

| Letter | Scope | Patch # | Shipped | Notes |
|--------|-------|---------|---------|-------|
| A | Anchor — `SUB-SYSTEMS.md` (draft), `SYSTEM_ASTROLOGY.md`, `ASTROLOGY_V2.md`, `NEXT_PATCH_SPEC.md`, golden fixture harness with 5 verified aspect tests, ARCHITECTURE.md pointer | SEN-0004 | 2026-04-21 | Docs + validation only. No code moves. |
| B | Ephemeris Provider — `ephemeris.py` as thin Swiss Ephemeris wrapper; sets `swe.set_ephe_path()` at import; exports PLANETS, SIGNS, ASPECT_DEFS, lon_to_sign, calc_aspect, etc.; adds `SE_EPHE_PATH=/opt/mythos/astrology/ephe` to `/opt/mythos/.env` | — | — | **Next up — will be SEN-0005** |
| C | Consolidation + Legacy Alignment — move ephemeris files from `/opt/mythos/ephemeris/` to `/opt/mythos/astrology/ephe/`; archive duplicate chart dirs; fix 5 hardcoded ephemeris paths in legacy scripts; align 3+ scripts to import constants from `ephemeris.py`; force Kerykeion to use external path | — | — | **High blast-radius — requires Castor review** |
| D | Natal State (Postgres-first) — `natal_generator.py` writes to `astro_*` Postgres tables, exports JSON artifact to `charts/<name>.json`; regenerate `ka.json` + `seraphe.json` from corrected YAML; snake_case schema with `house_system` + `zodiac_type` as top-level keys | — | — | |
| E | Daily Transits — refactor uploaded `daily_transits.py` to import from `ephemeris.py`, load natal via `natal_generator.load_natal()`; CLI flags `--person`, `--date`, `--from`/`--to`, `--json`, `--output`; revise `SUB-SYSTEMS.md` with lessons | — | — | First functional user-facing logic |
| F | Integration — `daily-transits` CLI symlink at `/opt/mythos/bin/`; Telegram `/transits` handler (SYS companion patch for registration); final `SUB-SYSTEMS.md` revision | — | — | Final letter |

**Letter sequence is locked.** Re-lettering is not happening.

---

## Current Disk State (as of SEN-0004)

### Directories

```
/opt/mythos/astrology/
├── archive/                          # Older versions, zipped backups
├── charts/                           # Per-person chart output
│   ├── adge/                         # Feb 16 gen, Moshier fallback, has full_chart_adge.json ✓
│   ├── adriaan_harold_denkers/       # Mar 27 gen, wrong birth year 1978 in metadata
│   ├── becky/                        # Feb 16 gen, has full_chart_seraphe.json
│   ├── brandi/ fitz/ riley/ carl_jung/ test_person/
│   └── chart.svg
├── ephe/                             # PARTIAL — needs consolidation in Letter C
│   ├── ast136/s136199s.se1
│   ├── seas_18.se1
│   ├── semo_18.se1
│   └── sepl_18.se1
├── spiral/                           # Consciousness-time engine (separate subsystem)
├── tools/seraphe-moon-calcs/         # Seraphe lunar transit tools
├── scripts/                          # Aggregation scripts
├── user_input/                       # YAML birth data per person
├── reports/                          # Generated reports
├── tests/                            # ← NEW in SEN-0004
│   ├── check_accuracy.py             # Golden fixture harness
│   └── fixtures/expected_aspects.json
└── [23 top-level .py files — no module structure]
```

### Duplicate ephemeris locations (Letter C fixes)

| Path | Status |
|---|---|
| `/opt/mythos/ephemeris/` | Most complete set — asteroids 5, 7, 10, 50, 90, 136 + planets + moon. **Needs to move to `/opt/mythos/astrology/ephe/`.** |
| `/opt/mythos/astrology/ephe/` | Partial duplicate (target of consolidation) |
| `/opt/mythos/.venv/lib/python3.12/site-packages/kerykeion/sweph/` | Kerykeion's bundled copy — pip-managed, leave alone |

### Hardcoded ephemeris paths in live code (Letter C fixes)

| File | Path |
|---|---|
| `/opt/mythos/workers/lunar_calendar_worker.py` | `/opt/mythos/ephemeris/ephe` |
| `/opt/mythos/observatory/geometry/planetary_engine.py` | `/opt/mythos/ephemeris` |
| `/opt/mythos/astrology/seraphe_lunar_generator.py` | `/opt/mythos/ephemeris/ephe` |
| `/opt/mythos/astrology/spiral/transit_pressure.py` | `/opt/mythos/astrology/ephe` |
| `/opt/mythos/astrology/astro_position.py` | `/opt/mythos/astrology/ephe` |

No script currently calls `swe.set_ephe_path()`. Swiss Ephemeris is
falling back to its compiled-in default path. This is the likely root
cause of the scatter.

---

## Current Database State

**Schema:** `public` (astrology tables are not yet in their own schema)

**`astro_*` tables — all present, populated for Adge, Seraphe, Fitz,
Brandi Carlile, Riley Green, and others:**

| Table | Purpose |
|---|---|
| `astro_natal_charts` | Natal chart records |
| `astro_natal_aspects` | Natal aspects |
| `astro_natal_house_cusps` | House cusp data |
| `astro_chart_points` | Chart point objects |
| `astro_chart_objects` | Chart body objects |
| `astro_chart_ruler` | Chart rulers |
| `astro_dignities` | Dignity scores |
| `astro_dispositors` | Dispositor chains |
| `astro_events` | Astrological event log |
| `astro_fixed_star_conjunctions` | Fixed star hits |
| `astro_geometric_patterns` | Chart geometry patterns |
| `astro_geometry_audit` | Geometry audit log |
| `astro_retrogrades` | Retrograde tracking |
| `astro_sect` | Day/night sect data |
| `astro_arabic_parts` | Arabic parts |
| `astro_balance` | Element/modality balance |
| `astrological_events` | Broader astro event log |
| `message_astrological_context` | Astro context per message |

**What does NOT exist yet:**

- A `natal_generator.py` that writes to these tables as its primary
  output (Letter D will build this)
- A snake_case JSON schema with `house_system` / `zodiac_type` as
  top-level keys (Letter D)
- A Postgres → JSON export/import round-trip (Letter D)

---

## Libraries

| Library | Version | Use |
|---|---|---|
| `pyswisseph` | 20230604 | Direct ephemeris calculation (Master Provider in Letter B+) |
| `kerykeion` | 5.x | SVG chart rendering (retained, forced to use external ephe path) |

---

## Next Up

The full spec for the next patch lives in
[`docs/astrology/NEXT_PATCH_SPEC.md`](astrology/NEXT_PATCH_SPEC.md).
That file is rewritten wholesale at the end of every feature patch,
so it always describes exactly one patch ahead.

Run `mythos-handoff astrology` to assemble the full handoff payload
(this doc + ASTROLOGY_V2 + NEXT_PATCH_SPEC + live state + validations)
into your clipboard, ready to paste into a new conversation.

*Note: `mythos-handoff astrology` support ships in Letter A via a
config entry. If the tool reports "astrology not registered," the
patch didn't complete — re-check the install log.*

---

## Open Questions

1. **Kerykeion + external ephemeris parity.** Does Kerykeion respect
   an externally-set `swe.set_ephe_path()`, or does it reach for its
   own bundled `sweph/` directory internally? Letter C must verify
   this with a calculation parity test (same date → same planet
   position from both engines).
   *Resolution target: Letter C.*

2. **Snake_case vs PascalCase JSON schema migration.** The existing
   `full_chart_*.json` uses PascalCase keys (`Name`, `Birth`, `Date`).
   Letter D moves to snake_case. Old charts in
   `archive/charts_pre_astro_v2/` stay PascalCase as historical
   reference. Does any live code read the PascalCase charts and need
   updating too?
   *Resolution target: Letter D.*

3. **Object set standardization.** The `adge/` chart has 14 objects
   (no Ceres/Pallas/Juno/Vesta). The `adriaan_harold_denkers/` chart
   has 19. What's the canonical set for Letter D?
   *Resolution target: Letter D (proposal: 19-object standard set +
   configurable extras for specialty charts).*

4. **house_system default.** Currently Placidus everywhere. Should
   the natal generator support alternatives (Whole Sign, Equal,
   Koch) for Hellenistic / Vedic work, or stay Placidus-only?
   *Resolution target: Letter D (proposal: Placidus default,
   house_system arg supported but not UI-exposed).*

5. **Astro-to-spiritual framework bridge.** The Nine Day Sun framework,
   Seraphic Numerology, and Soul Stratigraphy all reference natal
   charts. Do they read JSON or Postgres? If JSON, the export format
   is their interface contract and changes break them.
   *Resolution target: Letter E review.*

---

## Incoming Notes

> **Rules:** append-only, date-stamped, never edit. Review when the
> next patch starts. Triage into "Next Up", defer to a later letter,
> or resolve inline. Never lose a note.

<!-- Add new notes below this line -->

**2026-04-21** (SEN-0004): Castor (Gemini) reviewed ASTROLOGY_V2 plan,
round 1. Six critiques accepted/incorporated. Key reshuffles: golden
fixtures moved from Letter I to Letter A; ephemeris.py + .env path
unified into Letter B; legacy script alignment pulled from Letter H
into Letter C; natal generator redesigned Postgres-first; SUB-SYSTEMS.md
shipped as draft, not active. Full review preserved in
`ASTROLOGY_V2.md` §16.

**2026-04-21** (SEN-0004): Old `charts/adge/full_chart_adge.json` is
preserved in `archive/charts_pre_astro_v2/` for diff-based regression
checking after Letter D regenerates `ka.json` from corrected YAML
via the new Postgres-first pipeline. Use this diff to surface any
calculation changes between the old Moshier-fallback engine and the
new full-ephemeris engine.

**2026-04-21** (SEN-0004): `user_input/adriaan_harold_denkers.yaml`
has **wrong birth year** (1978, should be 1977). `user_input/adge.yaml`
has the correct data. Letter C deletes the redundant YAML.

---

*Astrology v2 is a vessel for the sky's grammar.*
*One patch down. Five to go.*
