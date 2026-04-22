#!/usr/bin/env python3
"""
SEN-0012: transit_handler.py — compute+persist before reading cache

Root cause: transit_handler.py called get_todays_pressure() which only
reads the spiral_transit_pressure DB cache. No rows existed for the
requested date, so it returned empty. The compute step was never called.

Fix: replace the get_todays_pressure() call with a helper that:
  1. Calls run_daily_pressure() (compute + persist) — idempotent via
     unique constraint on (chart_id, computed_date, planet, point, aspect)
  2. Returns the computed aspects directly (skips the re-read)

run_daily_pressure() is already the designed entry point ("Call this
once per day from morning brief or cron"). Using get_todays_pressure()
alone only works if something else has already run the daily pipeline.
The /transits command IS the pipeline entry point, so it must compute.

Services restarted: mythos-bot.service
Blast radius: LOW
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TRANSIT_HANDLER_PATH = Path('/opt/mythos/telegram_bot/handlers/transit_handler.py')
CHECK_ACCURACY_PATH  = '/opt/mythos/astrology/tests/check_accuracy.py'

# The import block to fix
OLD_IMPORTS = '''        from astrology.spiral.transit_pressure import (
            get_todays_pressure,
            format_pressure_brief,
        )
        from astrology.spiral.transit_interpreter import (
            interpret_transits,
            format_pressure_brief_with_interp,
        )

        # Get transit aspects (computes if not cached, persists to DB)
        aspects = get_todays_pressure(chart_id, target_date=target_date)'''

NEW_IMPORTS = '''        from astrology.spiral.transit_pressure import (
            run_daily_pressure,
            get_todays_pressure,
            format_pressure_brief,
        )
        from astrology.spiral.transit_interpreter import (
            interpret_transits,
            format_pressure_brief_with_interp,
        )

        # SEN-0012: run_daily_pressure computes + persists, then returns aspects.
        # get_todays_pressure alone only reads the cache — if nothing has run
        # the daily pipeline yet, it returns empty. run_daily_pressure is the
        # correct entry point (idempotent via unique constraint on the table).
        aspects = run_daily_pressure(chart_id, target_date=target_date)
        if not aspects:
            # Fallback: try reading existing cache (e.g. already computed today)
            aspects = get_todays_pressure(chart_id, target_date=target_date)'''


def log(patch, msg):
    patch.logger.log(msg)


def fix_transit_handler(patch) -> bool:
    if not TRANSIT_HANDLER_PATH.exists():
        patch.errors.append(f"transit_handler.py missing at {TRANSIT_HANDLER_PATH}")
        return False

    current = TRANSIT_HANDLER_PATH.read_text()

    # Idempotency
    if 'run_daily_pressure' in current:
        patch.validations.append("transit_handler.py: already using run_daily_pressure")
        log(patch, "  ✓ already fixed (idempotent)")
        return True

    count = current.count(OLD_IMPORTS)
    if count == 0:
        patch.errors.append("transit_handler.py: anchor not found")
        log(patch, "  ✗ anchor not found")
        return False
    if count > 1:
        patch.errors.append(f"transit_handler.py: anchor ambiguous ({count}x)")
        return False

    backup = TRANSIT_HANDLER_PATH.with_suffix('.py.sen0012.bak')
    backup.write_text(current)

    updated = current.replace(OLD_IMPORTS, NEW_IMPORTS, 1)
    TRANSIT_HANDLER_PATH.write_text(updated)

    verify = TRANSIT_HANDLER_PATH.read_text()
    if 'run_daily_pressure' not in verify:
        TRANSIT_HANDLER_PATH.write_text(current)
        patch.errors.append("transit_handler.py: post-edit verify failed")
        return False

    import py_compile
    try:
        py_compile.compile(str(TRANSIT_HANDLER_PATH), doraise=True)
    except py_compile.PyCompileError as e:
        TRANSIT_HANDLER_PATH.write_text(current)
        patch.errors.append(f"transit_handler.py: py_compile failed: {e}")
        return False

    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(TRANSIT_HANDLER_PATH))
    log(patch, "  ✓ transit_handler.py: now uses run_daily_pressure")
    return True


def verify_live_compute(patch) -> bool:
    """Confirm run_daily_pressure returns aspects for 2026-04-28."""
    cmd = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from datetime import date; '
        'from astrology.spiral.transit_pressure import run_daily_pressure; '
        'aspects = run_daily_pressure(chart_id=9, target_date=date(2026, 4, 28)); '
        'print(f"aspects: {len(aspects)}"); '
        'assert len(aspects) > 0; '
        '[print(f"  {a[\'transiting_planet\']} {a[\'aspect_type\']} natal {a[\'natal_point\']} {a[\'orb\']:.3f}°") for a in aspects[:4]]',
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        patch.errors.append(f"live compute failed: {out.stderr.strip()[:300]}")
        log(patch, f"  ✗ {out.stderr.strip()[:200]}")
        return False
    for line in out.stdout.strip().splitlines():
        log(patch, f"  {line}")
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


# ═══════════════════════════════════════════════════════════════════════
patch = PatchBase(
    stream='SEN',
    number=12,
    description='transit_handler fix — compute+persist not just cache read',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0012 — transit_handler.py: use run_daily_pressure not get_todays_pressure')
print('=' * 70 + '\n')

# ─── PHASE 0: Allowlist bot ──────────────────────────────────────
print('PHASE 0: Allowlist mythos-bot.service')
print('-' * 70)
try:
    patch.allowlist_append_unit('mythos-bot.service')
    log(patch, '  ✓ allowlisted')
except Exception as e:
    patch.errors.append(f'allowlist failed: {e}')
if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 1: Fix transit_handler.py ────────────────────────────
print('\nPHASE 1: Fix transit_handler.py')
print('-' * 70)
if not fix_transit_handler(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 2: Verify run_daily_pressure returns data ─────────────
print('\nPHASE 2: Verify run_daily_pressure returns aspects')
print('-' * 70)
if not verify_live_compute(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 3: Restart bot ───────────────────────────────────────
print('\nPHASE 3: Restart mythos-bot.service')
print('-' * 70)
try:
    patch.stop_service('mythos-bot.service')
    log(patch, '  ✓ stopped')
    patch.start_service('mythos-bot.service')
    if patch.is_service_active('mythos-bot.service'):
        log(patch, '  ✓ active')
    else:
        patch.errors.append('bot not active after restart')
except Exception as e:
    patch.errors.append(f'bot restart failed: {e}')
if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 4: Golden fixtures ────────────────────────────────────
print('\nPHASE 4: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SEN-0012 complete — /transits will now compute and return data')
print('=' * 70 + '\n')

patch.finish()
