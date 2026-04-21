#!/usr/bin/env python3
"""
SEN-0007 (Letter C.1 — Cleanup): Astrology v2 Narrow Cleanup

What this patch changes:
- Archives /opt/mythos/astrology/charts/adriaan_harold_denkers/
  (wrong birth year 1978 vs correct 1977, no full_chart preservation needed)
- Archives /opt/mythos/astrology/user_input/adriaan_harold_denkers.yaml
  (wrong birth year AND wrong coordinates — redundant with adge.yaml)
- Deletes the originals AFTER archive succeeds
- Simplifies /opt/mythos/astrology/astro_position.py's _EPHE_CANDIDATES
  block (8 fallback paths → single SE_EPHE_PATH env read matching the
  pattern of the 4 files updated in SEN-0006)
- Renames the legacy PATCH_HISTORY.md SEN-0004 entry (planetary geometry
  engine, shipped 2026-03-13) to "SEN-0004-LEGACY" so the current
  astrology v2 anchor entry stands clean
- Rewrites /opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md for Letter D

NARROWED FROM ORIGINAL SPEC:
Per preflight diagnostic 2026-04-21, the original Letter C.1 spec was
too broad in two ways:

1. Chart directory archiving — the original spec named 3 dirs to archive
   (adge/, adriaan_harold_denkers/, becky/). The diag revealed 7 chart
   directories exist, including charts for Brandi Carlile, Riley Green,
   Fitz, Carl Jung, and test data. Only adriaan_harold_denkers/ is
   genuinely stale. The other 6 are live/intentional data and are left
   untouched.

2. Constant alignment — the original spec called for migrating local
   PLANETS/SIGNS/ASPECTS constants to import from astrology.ephemeris.
   The diag revealed per-file shape differences (astro_position.py has
   a custom `dict[str, tuple[str, int | None]]` PLANETS shape that
   doesn't match ephemeris.py's `dict[str, int]`). Forcing this into
   C.1 would make the patch too risky. Deferred into the already-filed
   "Comprehensive astrology tool audit + dedup" REQUESTS.md entry, which
   has capacity for the per-file migration work this actually needs.

Tables touched: none
Services restarted: none
Blast radius: LOW
Gating: py_compile on edited file + all 5 golden fixtures pass

Companion patch: (deferred) constant alignment will happen as part of
the astrology audit request after A→F completes.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

# Archive destination for all pre-v2 cleanup work
ARCHIVE_DIR = Path('/opt/mythos/astrology/archive/charts_pre_astro_v2')

# Stale chart dir — wrong birth year source (1978 vs correct 1977)
STALE_CHART_DIR = Path('/opt/mythos/astrology/charts/adriaan_harold_denkers')
STALE_CHART_ARCHIVE = ARCHIVE_DIR / 'charts_adriaan_harold_denkers'

# Stale YAML — wrong birth year AND wrong coordinates
STALE_YAML = Path('/opt/mythos/astrology/user_input/adriaan_harold_denkers.yaml')
STALE_YAML_ARCHIVE = ARCHIVE_DIR / 'adriaan_harold_denkers.yaml'

# The file with the candidate-list fallback to simplify
ASTRO_POSITION = Path('/opt/mythos/astrology/astro_position.py')

# The current candidate-list block (verified via diag 2026-04-21)
ASTRO_POSITION_OLD_BLOCK = '''_EPHE_CANDIDATES = [
    _os.environ.get("SWISSEPH_PATH", ""),
    "/opt/mythos/astrology/ephe",
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ephe"),
    "/dev/astrology/swisseph/ephe",
    "/home/adge/dev/astrology/swisseph/ephe",
    "/opt/swisseph/ephe",
    "/usr/share/swisseph/ephe",
    "/usr/share/ephe",
]
_EPHE_PATH_SET = None
for _p in _EPHE_CANDIDATES:
    if _p and _os.path.isdir(_p):
        swe.set_ephe_path(_p)
        _EPHE_PATH_SET = _p
        break'''

# Simplified replacement — matches the pattern of the 4 files updated in SEN-0006
ASTRO_POSITION_NEW_BLOCK = '''# SEN-0007: simplified from 8-entry candidate list to SE_EPHE_PATH env read
# matching the pattern of the 4 files updated in SEN-0006 (Letter C).
_EPHE_PATH_SET = _os.environ.get("SE_EPHE_PATH", "/opt/mythos/astrology/ephe")
if _os.path.isdir(_EPHE_PATH_SET):
    swe.set_ephe_path(_EPHE_PATH_SET)
else:
    _EPHE_PATH_SET = None'''

# PATCH_HISTORY.md — rename legacy entry
PATCH_HISTORY = Path('/opt/mythos/docs/PATCH_HISTORY.md')
PATCH_HISTORY_OLD_HEADER = '### SEN-0004: Planetary geometry engine — positions, aspects, alignments, forcing vectors'
PATCH_HISTORY_NEW_HEADER = '### SEN-0004-LEGACY: Planetary geometry engine — positions, aspects, alignments, forcing vectors (pre-stream-tracking, number collision resolved 2026-04-21 by SEN-0007)'

# Golden fixture harness
CHECK_ACCURACY_PATH = '/opt/mythos/astrology/tests/check_accuracy.py'

# NEXT_PATCH_SPEC.md target
NEXT_PATCH_SPEC_PATH = Path('/opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md')


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def log(patch, msg):
    patch.logger.log(msg)


def archive_path(patch, src: Path, dest: Path, kind: str) -> bool:
    """Archive src to dest, preserving src until archive verified.

    Shadow-copy pattern: copy first, verify, then delete original.
    """
    if not src.exists():
        log(patch, f"  ⚠ {kind} {src} does not exist — nothing to archive")
        return True  # idempotent — treat as already done

    dest.parent.mkdir(parents=True, exist_ok=True)

    # If archive target already exists (patch re-run), remove prior
    if dest.exists():
        log(patch, f"  ⚠ archive target exists, removing prior: {dest}")
        if dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    try:
        # Copy first (preserve original)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

        # Verify: archive should exist and (for dirs) have same file count
        if not dest.exists():
            patch.errors.append(f"{kind} archive verify failed: {dest} does not exist after copy")
            log(patch, f"  ✗ {kind} archive verify failed")
            return False

        if src.is_dir():
            src_count = sum(1 for _ in src.rglob('*') if _.is_file())
            dest_count = sum(1 for _ in dest.rglob('*') if _.is_file())
            if src_count != dest_count:
                patch.errors.append(
                    f"{kind} archive verify failed: "
                    f"src has {src_count} files, archive has {dest_count}"
                )
                log(patch, f"  ✗ {kind} archive file count mismatch")
                return False
        else:
            if src.stat().st_size != dest.stat().st_size:
                patch.errors.append(f"{kind} archive size mismatch")
                log(patch, f"  ✗ {kind} archive size mismatch")
                return False

        log(patch, f"  ✓ {kind} archived: {src.name} → {dest}")

        # Now safe to delete original
        if src.is_dir():
            shutil.rmtree(src)
        else:
            src.unlink()
        log(patch, f"  ✓ {kind} original removed: {src}")

        if hasattr(patch, 'files_deployed'):
            patch.files_deployed.append(str(dest))

        return True

    except Exception as e:
        patch.errors.append(f"{kind} archive failed: {e}")
        log(patch, f"  ✗ {kind} archive failed: {e}")
        return False


def edit_file_block(patch, path: Path, old_block: str, new_block: str, label: str) -> bool:
    """SYS-0077 pattern: anchor uniqueness + backup + post-verify + py_compile."""
    if not path.exists():
        patch.errors.append(f"{label} target missing: {path}")
        log(patch, f"  ✗ {label} file missing")
        return False

    current = path.read_text()

    # Idempotency
    if new_block in current:
        patch.validations.append(f"{label} already updated, skipping")
        log(patch, f"  ✓ {label} already updated (idempotent skip)")
        return True

    # Anchor uniqueness
    count = current.count(old_block)
    if count == 0:
        patch.errors.append(f"{label}: anchor block not found")
        log(patch, f"  ✗ {label}: anchor not found")
        return False
    if count > 1:
        patch.errors.append(f"{label}: anchor appears {count}x, ambiguous")
        log(patch, f"  ✗ {label}: anchor ambiguous ({count}x)")
        return False

    # Backup
    backup = path.with_suffix(path.suffix + '.sen0007.bak')
    backup.write_text(current)

    # Replace
    updated = current.replace(old_block, new_block, 1)
    path.write_text(updated)

    # Post-edit verify
    verify = path.read_text()
    if new_block not in verify or old_block in verify:
        patch.errors.append(f"{label}: post-edit verify failed, restoring backup")
        log(patch, f"  ✗ {label}: post-edit verify failed, restoring")
        path.write_text(current)
        return False

    # py_compile for .py files
    if str(path).endswith('.py'):
        import py_compile
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as e:
            patch.errors.append(f"{label}: py_compile failed: {e}")
            log(patch, f"  ✗ {label}: py_compile FAILED, restoring")
            path.write_text(current)
            return False

    log(patch, f"  ✓ {label} updated")
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(path))
    return True


def edit_patch_history_header(patch) -> bool:
    """Rename the legacy SEN-0004 entry in PATCH_HISTORY.md.

    Per diag, there are TWO lines starting with '### SEN-0004':
      Line 1315: "### SEN-0004: Planetary geometry engine..." (the legacy one)
      Line 2152: "### SEN-0004: astrology v2 anchor" (the current one)

    We rename only the first one. The anchor is the full header text
    which is unique to the legacy entry.
    """
    if not PATCH_HISTORY.exists():
        patch.errors.append(f"PATCH_HISTORY.md missing at {PATCH_HISTORY}")
        log(patch, f"  ✗ PATCH_HISTORY.md missing")
        return False

    current = PATCH_HISTORY.read_text()

    # Idempotency
    if PATCH_HISTORY_NEW_HEADER in current:
        patch.validations.append("PATCH_HISTORY legacy entry already renamed")
        log(patch, f"  ✓ PATCH_HISTORY legacy SEN-0004 already renamed (idempotent)")
        return True

    # Anchor uniqueness
    count = current.count(PATCH_HISTORY_OLD_HEADER)
    if count == 0:
        patch.errors.append("PATCH_HISTORY: legacy SEN-0004 header not found")
        log(patch, f"  ✗ PATCH_HISTORY: legacy header not found")
        return False
    if count > 1:
        patch.errors.append(f"PATCH_HISTORY: legacy header appears {count}x, ambiguous")
        log(patch, f"  ✗ PATCH_HISTORY: legacy header ambiguous")
        return False

    # Backup
    backup = PATCH_HISTORY.with_suffix('.md.sen0007.bak')
    backup.write_text(current)

    # Replace
    updated = current.replace(PATCH_HISTORY_OLD_HEADER, PATCH_HISTORY_NEW_HEADER, 1)
    PATCH_HISTORY.write_text(updated)

    # Verify
    verify = PATCH_HISTORY.read_text()
    if PATCH_HISTORY_NEW_HEADER not in verify or PATCH_HISTORY_OLD_HEADER in verify:
        patch.errors.append("PATCH_HISTORY: post-edit verify failed")
        log(patch, f"  ✗ PATCH_HISTORY: post-edit verify failed, restoring")
        PATCH_HISTORY.write_text(current)
        return False

    # Confirm only ONE SEN-0004 header remains (the v2 anchor one)
    remaining = verify.count('### SEN-0004:')
    if remaining != 1:
        patch.errors.append(
            f"PATCH_HISTORY: expected 1 remaining SEN-0004 header, found {remaining}"
        )
        log(patch, f"  ✗ PATCH_HISTORY: unexpected header count {remaining}")
        PATCH_HISTORY.write_text(current)
        return False

    log(patch, f"  ✓ PATCH_HISTORY.md legacy SEN-0004 renamed to SEN-0004-LEGACY")
    log(patch, f"    — exactly 1 remaining '### SEN-0004:' header (the v2 anchor)")

    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(PATCH_HISTORY))
    return True


def run_golden_fixtures(patch) -> bool:
    """Run check_accuracy.py. Must pass all 5."""
    if not os.path.isfile(CHECK_ACCURACY_PATH):
        patch.errors.append(f"check_accuracy.py missing at {CHECK_ACCURACY_PATH}")
        log(patch, f"  ✗ check_accuracy.py missing")
        return False

    try:
        result = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY_PATH],
            capture_output=True, text=True, timeout=60,
        )
        log(patch, f"  — golden fixture output —")
        for line in result.stdout.splitlines():
            log(patch, f"    {line}")
        if result.returncode == 0:
            log(patch, f"  ✓ all 5 golden fixtures PASS")
            return True
        patch.errors.append(
            f"golden fixture check failed (exit {result.returncode})"
        )
        log(patch, f"  ✗ golden fixtures FAILED")
        return False
    except Exception as e:
        patch.errors.append(f"golden fixture run error: {e}")
        log(patch, f"  ✗ golden fixture error: {e}")
        return False


def rewrite_next_patch_spec(patch) -> bool:
    """Rewrite NEXT_PATCH_SPEC.md to describe Letter D."""
    new_spec = '''---
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
'''

    if not NEXT_PATCH_SPEC_PATH.parent.exists():
        NEXT_PATCH_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing
    if NEXT_PATCH_SPEC_PATH.exists():
        backup = NEXT_PATCH_SPEC_PATH.with_suffix('.md.sen0007.bak')
        backup.write_text(NEXT_PATCH_SPEC_PATH.read_text())
        log(patch, f"  ✓ backed up prior NEXT_PATCH_SPEC to {backup.name}")

    NEXT_PATCH_SPEC_PATH.write_text(new_spec)
    log(patch, f"  ✓ NEXT_PATCH_SPEC.md rewritten for Letter D")

    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(NEXT_PATCH_SPEC_PATH))
    return True


# ═══════════════════════════════════════════════════════════════════════
# Main flow
# ═══════════════════════════════════════════════════════════════════════

patch = PatchBase(
    stream='SEN',
    number=7,
    description='astrology v2 letter C.1 cleanup',
    patch_type='MINOR',
)
patch.begin()

print("\n" + "=" * 70)
print("SEN-0007 — Astrology v2 Letter C.1 (Cleanup)")
print("Narrowed scope after preflight diag 2026-04-21")
print("=" * 70 + "\n")

# ─── PHASE 1: Archive stale chart directory ─────────────────────
print("PHASE 1: Archive stale chart directory (adriaan_harold_denkers)")
print("-" * 70)
archive_path(patch, STALE_CHART_DIR, STALE_CHART_ARCHIVE, 'chart dir')

if patch.errors:
    print("\n✗ Phase 1 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 2: Archive stale YAML ────────────────────────────────
print("\nPHASE 2: Archive stale YAML (adriaan_harold_denkers.yaml)")
print("-" * 70)
archive_path(patch, STALE_YAML, STALE_YAML_ARCHIVE, 'yaml')

if patch.errors:
    print("\n✗ Phase 2 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 3: Simplify astro_position.py candidate list ─────────
print("\nPHASE 3: Simplify astro_position.py candidate-list fallback")
print("-" * 70)
edit_file_block(
    patch,
    ASTRO_POSITION,
    ASTRO_POSITION_OLD_BLOCK,
    ASTRO_POSITION_NEW_BLOCK,
    'astro_position.py',
)

if patch.errors:
    print("\n✗ Phase 3 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 4: Rename legacy PATCH_HISTORY.md SEN-0004 entry ────
print("\nPHASE 4: Rename legacy PATCH_HISTORY SEN-0004 entry")
print("-" * 70)
edit_patch_history_header(patch)

if patch.errors:
    print("\n✗ Phase 4 FAILED — aborting")
    patch.finish()
    sys.exit(1)

# ─── PHASE 5: Golden fixtures (regression gate) ─────────────────
print("\nPHASE 5: Golden fixture regression check")
print("-" * 70)
fixtures_ok = run_golden_fixtures(patch)

if not fixtures_ok:
    print("\n✗ Phase 5 FAILED — fixtures broke after cleanup")
    patch.finish()
    sys.exit(1)

# ─── PHASE 6: Rewrite NEXT_PATCH_SPEC.md for Letter D ──────────
print("\nPHASE 6: Rewriting NEXT_PATCH_SPEC.md for Letter D")
print("-" * 70)
rewrite_next_patch_spec(patch)

# ─── Done ───────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("✓ SEN-0007 complete — cleanup successful")
print("=" * 70 + "\n")

patch.finish()
