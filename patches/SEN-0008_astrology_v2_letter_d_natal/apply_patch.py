#!/usr/bin/env python3
"""
SEN-0008 (Letter D): Astrology v2 Natal State — Postgres-first

What this patch changes:
- Deploys /opt/mythos/astrology/natal_generator.py
  Provides: load_natal(name), write_chart_artifact(chart, path),
  generate_natal(...), self_check()
- Generates charts/ka.json by calling load_natal('Adge') against
  existing Postgres data (chart_id=9, already populated)
- Generates charts/seraphe.json by calling load_natal('Becky Denkers')
  against existing Postgres data (chart_id=11, already populated)
- Rewrites NEXT_PATCH_SPEC.md for Letter E (Daily Transits)

No SQL migration: astro_natal_charts already has house_system and
zodiac_type columns with correct defaults. 7 charts already in DB
including Adge (chart_id=9, correct 1977 DOB) and Seraphe (chart_id=11,
correct 1978 DOB, 14:02 birth time from becky.yaml).

Diag finding: The existing pipeline (astrochart_cli_engine → astro_loader)
already generates and persists charts. natal_generator.py is a clean
read interface that Letter E (Daily Transits) will consume, plus a
generate_natal() path using astrology.ephemeris for any future charts.

Tables touched: none (reads only for artifact generation)
Services restarted: none
Blast radius: LOW
Gating:
  - natal_generator.py imports cleanly (both styles)
  - self_check() reports db_reachable=True, adge_chart=True, seraphe_chart=True
  - ka.json and seraphe.json written and non-empty
  - ka.json planet count >= 10
  - all 5 golden fixtures pass
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


NATAL_GENERATOR_PATH = Path('/opt/mythos/astrology/natal_generator.py')
KA_JSON_PATH         = Path('/opt/mythos/astrology/charts/ka.json')
SERAPHE_JSON_PATH    = Path('/opt/mythos/astrology/charts/seraphe.json')
NEXT_PATCH_SPEC_PATH = Path('/opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md')
CHECK_ACCURACY_PATH  = '/opt/mythos/astrology/tests/check_accuracy.py'


def log(patch, msg):
    patch.logger.log(msg)


def verify_module_imports(patch) -> bool:
    """Verify natal_generator imports cleanly both as direct and package style."""

    # Test 1: direct import
    cmd1 = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos/astrology"); '
        'import natal_generator as ng; '
        'import json; print(json.dumps(ng.self_check(), default=str))',
    ]
    # Test 2: package import
    cmd2 = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from astrology import natal_generator as ng; '
        'import json; print(json.dumps(ng.self_check(), default=str))',
    ]

    for label, cmd in [('direct', cmd1), ('package', cmd2)]:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if out.returncode != 0:
                patch.errors.append(
                    f"natal_generator {label} import failed: {out.stderr.strip()}"
                )
                log(patch, f"  ✗ {label} import FAILED")
                log(patch, f"    {out.stderr.strip()[:300]}")
                return False
            log(patch, f"  ✓ {label} import ok")
        except Exception as e:
            patch.errors.append(f"natal_generator {label} import error: {e}")
            return False

    # Parse self_check from last cmd2 run
    try:
        result = json.loads(out.stdout.strip())
        log(patch, f"  — self_check —")
        for k, v in result.items():
            log(patch, f"    {k}: {v}")

        if not result.get('db_reachable'):
            patch.errors.append("natal_generator: DB not reachable")
            log(patch, "  ✗ DB not reachable")
            return False
        if not result.get('adge_chart'):
            patch.errors.append("natal_generator: Adge chart not found in DB")
            log(patch, "  ✗ Adge chart missing from DB")
            return False
        if not result.get('seraphe_chart'):
            patch.errors.append("natal_generator: Seraphe chart not found in DB")
            log(patch, "  ✗ Seraphe chart missing from DB")
            return False

        log(patch, f"  ✓ self_check PASS (DB reachable, both charts present)")
        return True
    except Exception as e:
        patch.errors.append(f"self_check parse error: {e}")
        return False


def generate_artifacts(patch) -> bool:
    """Call load_natal for Adge and Seraphe, write JSON artifacts."""

    script = '''
import sys, json
sys.path.insert(0, "/opt/mythos")
from astrology.natal_generator import load_natal, write_chart_artifact
from pathlib import Path

results = {}

# Adge
adge = load_natal("Adge")
if adge:
    write_chart_artifact(adge, Path("/opt/mythos/astrology/charts/ka.json"))
    results["adge"] = {
        "ok": True,
        "planet_count": len(adge.get("chart_objects", {})),
        "aspect_count": len(adge.get("chart_aspects", [])),
        "house_count": len(adge.get("house_cusps", {})),
        "size_bytes": Path("/opt/mythos/astrology/charts/ka.json").stat().st_size,
    }
else:
    results["adge"] = {"ok": False, "error": "load_natal returned None"}

# Seraphe (stored as 'Becky Denkers')
seraphe = load_natal("Becky Denkers")
if seraphe:
    write_chart_artifact(seraphe, Path("/opt/mythos/astrology/charts/seraphe.json"))
    results["seraphe"] = {
        "ok": True,
        "planet_count": len(seraphe.get("chart_objects", {})),
        "aspect_count": len(seraphe.get("chart_aspects", [])),
        "house_count": len(seraphe.get("house_cusps", {})),
        "size_bytes": Path("/opt/mythos/astrology/charts/seraphe.json").stat().st_size,
    }
else:
    results["seraphe"] = {"ok": False, "error": "load_natal returned None"}

print(json.dumps(results, default=str))
'''

    try:
        out = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', '-c', script],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode != 0:
            patch.errors.append(f"artifact generation failed: {out.stderr.strip()}")
            log(patch, f"  ✗ artifact generation FAILED")
            log(patch, f"    {out.stderr.strip()[:400]}")
            return False

        results = json.loads(out.stdout.strip())

        for person, data in results.items():
            if not data.get('ok'):
                patch.errors.append(
                    f"{person} artifact generation failed: {data.get('error')}"
                )
                log(patch, f"  ✗ {person}: {data.get('error')}")
                return False
            log(patch, f"  ✓ {person}:")
            log(patch, f"    planets: {data['planet_count']}")
            log(patch, f"    aspects: {data['aspect_count']}")
            log(patch, f"    houses:  {data['house_count']}")
            log(patch, f"    size:    {data['size_bytes']:,} bytes")

            # Gate: must have at least 10 planets
            if data['planet_count'] < 10:
                patch.errors.append(
                    f"{person} chart has only {data['planet_count']} objects — too few"
                )
                log(patch, f"  ✗ {person}: only {data['planet_count']} objects")
                return False

        if hasattr(patch, 'files_deployed'):
            patch.files_deployed.append(str(KA_JSON_PATH))
            patch.files_deployed.append(str(SERAPHE_JSON_PATH))

        return True
    except Exception as e:
        patch.errors.append(f"artifact generation error: {e}")
        log(patch, f"  ✗ error: {e}")
        return False


def run_golden_fixtures(patch) -> bool:
    """Run check_accuracy.py. Must pass all 5."""
    try:
        result = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY_PATH],
            capture_output=True, text=True, timeout=60,
        )
        log(patch, "  — golden fixture output —")
        for line in result.stdout.splitlines():
            log(patch, f"    {line}")
        if result.returncode == 0:
            log(patch, "  ✓ all 5 golden fixtures PASS")
            return True
        patch.errors.append(f"golden fixtures failed (exit {result.returncode})")
        log(patch, "  ✗ golden fixtures FAILED")
        return False
    except Exception as e:
        patch.errors.append(f"golden fixture error: {e}")
        return False


def rewrite_next_patch_spec(patch) -> bool:
    """Rewrite NEXT_PATCH_SPEC.md for Letter E."""
    new_spec = '''---
title: "Astrology Next Patch Spec — Letter E"
category: spec
status: active
stream: SEN
location: docs/astrology
tags: [astrology, spec, next-patch]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Astrology Next Patch Spec — Letter E (Daily Transits Refactor)

> **This file is rewritten wholesale at the end of every feature patch.**
> It describes exactly one patch ahead of the current state.
>
> **Current state:** Letter D (SEN-0008) shipped — natal_generator.py
> deployed, charts/ka.json and charts/seraphe.json generated from
> Postgres, Adge (chart_id=9) and Seraphe (chart_id=11) both confirmed
> present with correct birth data.
>
> **This spec covers:** Letter E — Daily Transits Refactor.
> **Expected patch number:** SEN-0009 (verify via `mythos-diag streams`).

---

## Scope

Refactor the existing daily_transits.py to use:
- `astrology.ephemeris` for all calculations (replacing inline swisseph calls)
- `astrology.natal_generator.load_natal()` for natal chart data
  (no birth data re-entry, reads from Postgres)
- Proper applying/separating detection (was broken in original due to
  the flags=0 footgun fixed in SEN-0005)

The existing `daily_transits.py` (uploaded 2026-04-21, 357 lines)
serves as the reference for feature parity. It computes:
  - All transiting planet positions for a given date
  - Aspects between transiting planets and natal positions
  - Orb values, applying/separating, transit quality

### Target interface

```python
from astrology.transit_engine import compute_transits, format_transit_report

# Compute transits for Adge on a date
transits = compute_transits(
    natal_name='Adge',       # loads from natal_generator
    transit_date='2026-04-28',
    tz_str='America/New_York',
)

# Format for Telegram or console
report = format_transit_report(transits, style='telegram')
```

---

## Files created

| File | Purpose |
|---|---|
| `/opt/mythos/astrology/transit_engine.py` | Daily transits computation module |

---

## Files modified

None. Pure addition patch.

---

## SQL

None.

---

## Services restarted

None.

---

## Verification

1. **Import smoke test** on transit_engine.py
2. **Compute Adge transits for 2026-04-28** — must match the golden
   fixtures (Uranus opp Sun at 0.0017° orb, etc.) to within 0.005°
3. **Applying/separating is non-null** — all aspects must have
   applying field set (True or False), not None
4. **All 5 existing golden fixtures still pass**

---

## Blast radius

**Low.** New module, no existing code touched, no services restarted,
no schema changes.

---

## After Letter E ships

- Rewrite this file to describe Letter F (Integration — CLI + Telegram)
- Update SYSTEM_ASTROLOGY.md to mark E shipped
- Letter F will wire transit_engine into the Telegram /transits command

---

*End of Letter E spec.*
'''

    if NEXT_PATCH_SPEC_PATH.exists():
        backup = NEXT_PATCH_SPEC_PATH.with_suffix('.md.sen0008.bak')
        backup.write_text(NEXT_PATCH_SPEC_PATH.read_text())
        log(patch, f"  ✓ backed up prior NEXT_PATCH_SPEC to {backup.name}")

    NEXT_PATCH_SPEC_PATH.write_text(new_spec)
    log(patch, "  ✓ NEXT_PATCH_SPEC.md rewritten for Letter E")

    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(NEXT_PATCH_SPEC_PATH))
    return True


# ═══════════════════════════════════════════════════════════════════════
# Main flow
# ═══════════════════════════════════════════════════════════════════════

patch = PatchBase(
    stream='SEN',
    number=8,
    description='astrology v2 letter D — natal state postgres-first',
    patch_type='MINOR',
)
patch.begin()

print("\n" + "=" * 70)
print("SEN-0008 — Astrology v2 Letter D (Natal State — Postgres-first)")
print("Slim scope: existing charts in Postgres, module wraps them cleanly")
print("=" * 70 + "\n")

# ─── PHASE 1: Deploy natal_generator.py ─────────────────────────
print("PHASE 1: Deploy natal_generator.py")
print("-" * 70)
patch.deploy_file(
    'opt/mythos/astrology/natal_generator.py',
    str(NATAL_GENERATOR_PATH),
)
log(patch, f"  ✓ natal_generator.py deployed ({NATAL_GENERATOR_PATH.stat().st_size:,} bytes)")

if patch.errors:
    print("\n✗ Phase 1 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 2: Verify imports and self_check ──────────────────────
print("\nPHASE 2: Verify natal_generator imports and self_check")
print("-" * 70)
import_ok = verify_module_imports(patch)

if not import_ok:
    print("\n✗ Phase 2 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 3: Generate canonical chart artifacts ─────────────────
print("\nPHASE 3: Generate charts/ka.json and charts/seraphe.json from Postgres")
print("-" * 70)
artifacts_ok = generate_artifacts(patch)

if not artifacts_ok:
    print("\n✗ Phase 3 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 4: Golden fixture regression gate ─────────────────────
print("\nPHASE 4: Golden fixture regression check")
print("-" * 70)
fixtures_ok = run_golden_fixtures(patch)

if not fixtures_ok:
    print("\n✗ Phase 4 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 5: Rewrite NEXT_PATCH_SPEC.md for Letter E ────────────
print("\nPHASE 5: Rewriting NEXT_PATCH_SPEC.md for Letter E")
print("-" * 70)
rewrite_next_patch_spec(patch)

# ─── Done ─────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("✓ SEN-0008 complete — natal state module live, artifacts generated")
print("=" * 70 + "\n")

patch.finish()
