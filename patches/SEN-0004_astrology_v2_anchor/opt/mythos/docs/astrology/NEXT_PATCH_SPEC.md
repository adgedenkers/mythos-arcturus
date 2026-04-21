---
title: "Astrology Next Patch Spec — Letter B"
category: spec
status: active
stream: SEN
location: docs/astrology
tags: [astrology, spec, next-patch]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Astrology Next Patch Spec — Letter B

> **This file is rewritten wholesale at the end of every feature patch.**
> It describes exactly one patch ahead of the current state.
>
> **Current state:** Letter A (SEN-0004) shipped 2026-04-21.
> **This spec covers:** Letter B — Ephemeris Provider.
> **Expected patch number:** SEN-0005 (verify via `mythos-diag streams` at build time).

---

## Scope

Ship `/opt/mythos/astrology/ephemeris.py` as the Master Ephemeris
Provider for all astrology calculation on Mythos. Add
`SE_EPHE_PATH=/opt/mythos/astrology/ephe` to `/opt/mythos/.env` so
the module has a canonical path even on fresh environments. Verify
the module produces correct positions for the 5 golden fixtures.

**No file moves.** No consolidation. No legacy script changes. This
patch is a pure addition — `ephemeris.py` exists after, didn't before.

**No services restarted.** The module is imported on demand.

---

## Files created

### `/opt/mythos/astrology/ephemeris.py`

Full shared wrapper around `pyswisseph`. Exports:

**Constants**

```python
PLANETS: dict[str, int]        # {'Sun': swe.SUN, 'Moon': swe.MOON, ...}
LILITH_ID: int                 # swe.MEAN_APOG
ASTEROIDS: dict[str, int]      # {'Chiron': 15, 'Ceres': ..., 'Pallas': ..., 'Juno': ..., 'Vesta': ...}
SIGNS: list[str]               # ['Aries', 'Taurus', ...]
SIGN_GLYPHS: dict[str, str]    # Unicode glyphs per sign
PLANET_GLYPHS: dict[str, str]  # Unicode glyphs per planet
ELEMENTS: dict[str, str]       # sign → element
MODALITIES: dict[str, str]     # sign → modality (Cardinal/Fixed/Mutable)
POLARITIES: dict[str, str]     # sign → polarity (masculine/feminine)
TRAD_RULERS: dict[str, str]    # sign → traditional ruler
MOD_RULERS: dict[str, str]     # sign → modern ruler
ASPECT_DEFS: dict[str, dict]   # aspect name → {ang, orb, major}
ASPECT_WORDS: dict[str, str]   # human-friendly aspect names
```

**Helpers**

```python
def lon_to_sign(lon: float) -> tuple[str, float]
def fmt_pos(lon: float) -> str                    # "0d08mSagittarius"
def ang_dist(a: float, b: float) -> float
def calc_aspect(l1, l2, s1=None, s2=None) -> dict | None
def det_sect(sun_lon: float, asc_lon: float) -> str
def calc_planets(jd: float, flags: int = 0) -> dict
def calc_houses(jd: float, lat: float, lon: float, system: str = 'P') -> dict
def calc_natal_full(year, month, day, hour, minute, lat, lon, tz_offset, name: str = "") -> dict
def date_to_jd(year, month, day, hour, minute, tz_offset) -> float
```

**Path initialization**

At module import time:

```python
import os
import swisseph as swe
SE_EPHE_PATH = os.environ.get('SE_EPHE_PATH', '/opt/mythos/astrology/ephe')
swe.set_ephe_path(SE_EPHE_PATH)
```

The fallback default matches the canonical path Letter C will establish,
so even if `.env` isn't loaded (e.g., in a one-off REPL session),
`ephemeris.py` still uses the right path.

### `/opt/mythos/migrations/SEN-0005_env_ephemeris_path.sh`

(Shell script, not SQL.) Appends `SE_EPHE_PATH=/opt/mythos/astrology/ephe`
to `/opt/mythos/.env` if not already present. Idempotent.

---

## Files modified

None. This patch is pure addition.

---

## SQL

None.

---

## Services restarted

None.

---

## Verification

At end of `apply_patch.py`:

1. **Import smoke test**
   ```bash
   /opt/mythos/.venv/bin/python3 -c "from astrology import ephemeris; print(ephemeris.SE_EPHE_PATH); print(len(ephemeris.PLANETS))"
   ```
   Expect: `/opt/mythos/astrology/ephe` and `11` (or whatever the
   planet count turns out to be).

2. **Env var set**
   ```bash
   grep -q '^SE_EPHE_PATH=' /opt/mythos/.env
   ```
   Expect: exit 0.

3. **Known-value calculation test**
   Calculate Sun's longitude for 2026-04-28 12:00 UT. Expected value
   is derived from the uploaded `daily_transits.py` output and locked
   in the fixture.

4. **Golden fixture harness**
   ```bash
   /opt/mythos/.venv/bin/python3 /opt/mythos/astrology/tests/check_accuracy.py
   ```
   Expect: all 5 fixtures PASS (within 0.1° orb tolerance). If any
   fail, `apply_patch.py` calls `patch.fail()` and rolls back.

---

## Rollback

`PatchBase` auto-rollback handles this:

1. Delete `/opt/mythos/astrology/ephemeris.py`
2. Remove `SE_EPHE_PATH=...` line from `/opt/mythos/.env`

Since no service was restarted and no SQL ran, rollback is trivial.

---

## Blast radius

**Low.** Pure addition, no existing code touched, no service restart.
The only risk is `ephemeris.py` producing wrong values, which the
golden fixtures catch.

**No Castor review required** (blast radius < medium per
WORKFLOW.md Phase 2.5).

---

## Open questions for Letter B

1. **Asteroid IDs.** The uploaded `daily_transits.py` uses `Chiron: 15`
   only. Ceres/Pallas/Juno/Vesta are in the wider swisseph world as
   IDs 17/18/19/20, but need verification against the installed
   `ast5/` ephemeris files. Confirm during B build via a smoke test.
2. **House system default.** Placidus is the existing default; lock
   as module-level constant `DEFAULT_HOUSE_SYSTEM = 'P'`.
3. **Lilith variant.** Current uses `MEAN_APOG` (mean Black Moon
   Lilith). True Lilith (`OSCU_APOG`) gives different positions.
   Ship `LILITH_ID = swe.MEAN_APOG` as the default; add optional
   `TRUE_LILITH_ID = swe.OSCU_APOG` for completeness.

---

## After Letter B ships

- Update `SYSTEM_ASTROLOGY.md` — mark B as shipped with date and
  patch number; mark C as next.
- Rewrite this file (`NEXT_PATCH_SPEC.md`) to describe Letter C.
- Golden fixture status should now be "all 5 pass against
  ephemeris.py" — that becomes Letter C's starting state.

---

*End of Letter B spec.*
