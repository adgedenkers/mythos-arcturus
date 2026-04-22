#!/usr/bin/env python3
"""
SEN-0010 (Letter F): Astrology v2 Integration + Completion

What this patch changes:
- Deploys /opt/mythos/bin/daily-transits CLI script (executable)
- Deploys updated /opt/mythos/docs/SYSTEM_ASTROLOGY.md (A→F complete)
- Deploys updated /opt/mythos/docs/SUB-SYSTEMS.md (promoted DRAFT→ACTIVE,
  N=2, Astrology v2 learnings section added)
- Rewrites NEXT_PATCH_SPEC.md to mark arc complete

Tables touched: none
Services restarted: none
Blast radius: LOW — pure file addition + doc updates
Gating: CLI syntax valid + all 5 golden fixtures pass
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

DAILY_TRANSITS_PATH    = Path('/opt/mythos/bin/daily-transits')
SYSTEM_ASTRO_PATH      = Path('/opt/mythos/docs/SYSTEM_ASTROLOGY.md')
SUB_SYSTEMS_PATH       = Path('/opt/mythos/docs/SUB-SYSTEMS.md')
NEXT_PATCH_SPEC_PATH   = Path('/opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md')
CHECK_ACCURACY_PATH    = '/opt/mythos/astrology/tests/check_accuracy.py'


def log(patch, msg):
    patch.logger.log(msg)


def verify_cli_script(patch) -> bool:
    """Verify daily-transits is executable and syntax-valid."""
    if not DAILY_TRANSITS_PATH.exists():
        patch.errors.append(f"daily-transits missing at {DAILY_TRANSITS_PATH}")
        return False

    # Check executable bit
    import stat
    mode = DAILY_TRANSITS_PATH.stat().st_mode
    if not (mode & stat.S_IXUSR):
        patch.errors.append("daily-transits is not executable")
        log(patch, "  ✗ daily-transits not executable")
        return False

    # Syntax check
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-m', 'py_compile',
         str(DAILY_TRANSITS_PATH)],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        patch.errors.append(f"daily-transits py_compile failed: {result.stderr.strip()}")
        log(patch, f"  ✗ py_compile failed: {result.stderr.strip()[:200]}")
        return False

    # Smoke test: --help exits 0
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', str(DAILY_TRANSITS_PATH), '--help'],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        patch.errors.append(f"daily-transits --help failed: {result.stderr.strip()}")
        log(patch, f"  ✗ --help failed")
        return False

    log(patch, f"  ✓ daily-transits: executable, syntax valid, --help ok")
    return True


def run_golden_fixtures(patch) -> bool:
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
    return False


def rewrite_next_patch_spec(patch) -> bool:
    new_spec = '''---
title: "Astrology Next Patch Spec — POST v2"
category: spec
status: complete
stream: SEN
location: docs/astrology
updated: 2026-04-21
---

# Astrology v2 — Complete

Astrology v2 (A→F) shipped 2026-04-21 across 7 patches (SEN-0004
through SEN-0010). There is no Letter G.

## Post-v2 work

Three items are filed in `/opt/mythos/docs/REQUESTS.md`:

1. **SYS: Full graph coverage + post-patch verification gate**
   — every deployed tool mapped in Neo4j, post-scan gate on patch-install

2. **SYS: PatchBase microtool kit with Ollama integration**
   — `ollama-analyze` microtool callable from apply_patch.py

3. **SEN: Comprehensive astrology tool audit + dedup**
   — inventory all 23+ astrology .py files, unify around ephemeris.py,
     dedup one-offs, fold unique features into canonical modules

## Starting the next astrology conversation

Run the standard session-start diagnostic:

```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"; cat /opt/mythos/docs/TODO.md >> "$D"
echo "\\n\\n=== ARCHITECTURE ===" >> "$D"; cat /opt/mythos/docs/ARCHITECTURE.md >> "$D"
echo "\\n\\n=== STREAMS ===" >> "$D"; cat /opt/mythos/docs/STREAMS.md >> "$D"
cat "$D" | xclip -selection clipboard && echo "✓"
```

Then share `SYSTEM_ASTROLOGY.md` for astrology-specific context.

*End — arc complete.*
'''
    if NEXT_PATCH_SPEC_PATH.exists():
        backup = NEXT_PATCH_SPEC_PATH.with_suffix('.md.sen0010.bak')
        backup.write_text(NEXT_PATCH_SPEC_PATH.read_text())
        log(patch, "  ✓ backed up prior NEXT_PATCH_SPEC")
    NEXT_PATCH_SPEC_PATH.write_text(new_spec)
    log(patch, "  ✓ NEXT_PATCH_SPEC.md updated — arc complete")
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(NEXT_PATCH_SPEC_PATH))
    return True


# ═══════════════════════════════════════════════════════════════════════
patch = PatchBase(
    stream='SEN',
    number=10,
    description='astrology v2 letter F — integration + completion',
    patch_type='MINOR',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0010 — Astrology v2 Letter F (Integration + Completion)')
print('Final letter. A→F done.')
print('=' * 70 + '\n')

# ─── PHASE 1: Deploy daily-transits CLI ─────────────────────────
print('PHASE 1: Deploy daily-transits CLI')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/bin/daily-transits',
    str(DAILY_TRANSITS_PATH),
)
# Ensure executable bit (deploy_file preserves mode from source)
import os, stat
DAILY_TRANSITS_PATH.chmod(
    DAILY_TRANSITS_PATH.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP
)
log(patch, f'  ✓ daily-transits deployed and marked executable')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 2: Verify CLI ─────────────────────────────────────────
print('\nPHASE 2: Verify daily-transits CLI')
print('-' * 70)
if not verify_cli_script(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 3: Deploy SYSTEM_ASTROLOGY.md ────────────────────────
print('\nPHASE 3: Deploy updated SYSTEM_ASTROLOGY.md')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/docs/SYSTEM_ASTROLOGY.md',
    str(SYSTEM_ASTRO_PATH),
)
log(patch, f'  ✓ SYSTEM_ASTROLOGY.md updated (A→F complete, full current state)')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 4: Deploy SUB-SYSTEMS.md ─────────────────────────────
print('\nPHASE 4: Deploy updated SUB-SYSTEMS.md')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/docs/SUB-SYSTEMS.md',
    str(SUB_SYSTEMS_PATH),
)
log(patch, f'  ✓ SUB-SYSTEMS.md promoted DRAFT→ACTIVE (N=2), learnings added')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 5: Golden fixtures ───────────────────────────────────
print('\nPHASE 5: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 6: Rewrite NEXT_PATCH_SPEC.md — arc complete ─────────
print('\nPHASE 6: Mark arc complete in NEXT_PATCH_SPEC.md')
print('-' * 70)
rewrite_next_patch_spec(patch)

print('\n' + '=' * 70)
print('✓ SEN-0010 complete — Astrology v2 A→F finished')
print('  Seven patches. One day. The sky is now queryable.')
print('=' * 70 + '\n')

patch.finish()
