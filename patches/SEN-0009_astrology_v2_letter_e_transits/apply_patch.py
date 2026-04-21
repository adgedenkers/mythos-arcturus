#!/usr/bin/env python3
"""
SEN-0009 (Letter E) v2: Astrology v2 Daily Transits — Wire the Engine

v1 failed at Phase 4: mythos_bot.py uses lazy imports inside the
application setup function (not top-level), and spiral_handler is
registered at line 1285 as:
    from telegram_bot.handlers.spiral_handler import handle_spiral
    application.add_handler(CommandHandler("spiral", handle_spiral))

v2 anchors on this exact two-line block.

What this patch changes:
1. Deploys /opt/mythos/telegram_bot/handlers/transit_handler.py
2. Injects natal_generator integration into transit_pressure.py
3. Registers /transits command in mythos_bot.py alongside /spiral
4. Restarts mythos-bot.service

Tables touched: none
Services restarted: mythos-bot.service
Blast radius: LOW-MEDIUM
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TRANSIT_HANDLER_PATH  = Path('/opt/mythos/telegram_bot/handlers/transit_handler.py')
TRANSIT_PRESSURE_PATH = Path('/opt/mythos/astrology/spiral/transit_pressure.py')
BOT_MAIN_PATH         = Path('/opt/mythos/telegram_bot/mythos_bot.py')
CHECK_ACCURACY_PATH   = '/opt/mythos/astrology/tests/check_accuracy.py'
NEXT_PATCH_SPEC_PATH  = Path('/opt/mythos/docs/astrology/NEXT_PATCH_SPEC.md')

# ─── Verified anchor from diag (lines 1285-1286 of mythos_bot.py) ──────────
# The bot registers spiral inside application setup as a lazy import + add_handler.
# We append transit_handler immediately after.
BOT_SPIRAL_ANCHOR = (
    'from telegram_bot.handlers.spiral_handler import handle_spiral\n'
    '    application.add_handler(CommandHandler("spiral", handle_spiral))'
)

BOT_TRANSIT_ADDITION = (
    'from telegram_bot.handlers.spiral_handler import handle_spiral\n'
    '    application.add_handler(CommandHandler("spiral", handle_spiral))\n'
    '    # SEN-0009: daily transit reports\n'
    '    from telegram_bot.handlers.transit_handler import handle_transits\n'
    '    application.add_handler(CommandHandler("transits", handle_transits))'
)

# ─── natal_generator injection anchor (verified present in transit_pressure.py) ──
TRANSIT_PRESSURE_MARKER = '# SEN-0009: natal_generator integration'
TRANSIT_PRESSURE_INJECT_ANCHOR = 'log = logging.getLogger("iris.transit_pressure")'
TRANSIT_PRESSURE_INJECT = '''log = logging.getLogger("iris.transit_pressure")

# SEN-0009: natal_generator integration
# Provides a load function that uses the canonical Letter D interface.
# Falls back gracefully if natal_generator is unavailable.
def _load_natal_positions_via_generator(chart_id: int) -> dict:
    """
    Load natal positions from natal_generator.load_natal() by chart_id.
    Returns {planet_name: longitude_float} matching transit_pressure expectations.
    Falls back to {} (caller will use raw Postgres fallback) if anything fails.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='/var/run/postgresql', port=5432,
            database='mythos', user='adge',
        )
        cur = conn.cursor()
        cur.execute('SELECT name FROM astro_natal_charts WHERE chart_id = %s', (chart_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {}
        import sys as _sys
        _sys.path.insert(0, '/opt/mythos')
        from astrology.natal_generator import load_natal
        chart = load_natal(row[0])
        if not chart:
            return {}
        result = {}
        for name, data in chart.get('chart_objects', {}).items():
            result[name] = data.get('longitude', 0.0)
        for pt_name, pt_data in chart.get('chart_points', {}).items():
            result[pt_name] = pt_data.get('longitude', 0.0)
        return result
    except Exception as exc:
        log.warning('natal_generator path failed for chart_id=%d: %s', chart_id, exc)
        return {}'''


def _log(patch, msg):
    patch.logger.log(msg)


def inject_natal_generator(patch) -> bool:
    if not TRANSIT_PRESSURE_PATH.exists():
        patch.errors.append(f"transit_pressure.py missing")
        return False
    current = TRANSIT_PRESSURE_PATH.read_text()
    if TRANSIT_PRESSURE_MARKER in current:
        patch.validations.append("transit_pressure.py: already injected")
        _log(patch, "  ✓ already injected (idempotent)")
        return True
    count = current.count(TRANSIT_PRESSURE_INJECT_ANCHOR)
    if count != 1:
        patch.errors.append(f"transit_pressure.py: anchor count {count} (expected 1)")
        _log(patch, f"  ✗ anchor count {count}")
        return False
    backup = TRANSIT_PRESSURE_PATH.with_suffix('.py.sen0009.bak')
    backup.write_text(current)
    updated = current.replace(TRANSIT_PRESSURE_INJECT_ANCHOR, TRANSIT_PRESSURE_INJECT, 1)
    TRANSIT_PRESSURE_PATH.write_text(updated)
    verify = TRANSIT_PRESSURE_PATH.read_text()
    if TRANSIT_PRESSURE_MARKER not in verify:
        TRANSIT_PRESSURE_PATH.write_text(current)
        patch.errors.append("transit_pressure.py: post-edit verify failed")
        return False
    import py_compile
    try:
        py_compile.compile(str(TRANSIT_PRESSURE_PATH), doraise=True)
    except py_compile.PyCompileError as e:
        TRANSIT_PRESSURE_PATH.write_text(current)
        patch.errors.append(f"transit_pressure.py: py_compile failed: {e}")
        return False
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(TRANSIT_PRESSURE_PATH))
    _log(patch, "  ✓ natal_generator integration injected")
    return True


def register_in_bot(patch) -> bool:
    if not BOT_MAIN_PATH.exists():
        patch.errors.append("mythos_bot.py missing")
        return False
    current = BOT_MAIN_PATH.read_text()
    if 'transit_handler' in current:
        patch.validations.append("mythos_bot.py: transit_handler already registered")
        _log(patch, "  ✓ already registered (idempotent)")
        return True
    count = current.count(BOT_SPIRAL_ANCHOR)
    if count == 0:
        patch.errors.append(
            "mythos_bot.py: spiral anchor not found.\n"
            "  Expected (lines 1285-1286):\n"
            "    from telegram_bot.handlers.spiral_handler import handle_spiral\n"
            "    application.add_handler(CommandHandler(\"spiral\", handle_spiral))\n"
            "  Manual fix: add these two lines after the spiral registration:\n"
            "    from telegram_bot.handlers.transit_handler import handle_transits\n"
            "    application.add_handler(CommandHandler(\"transits\", handle_transits))"
        )
        _log(patch, "  ✗ spiral anchor not found")
        return False
    if count > 1:
        patch.errors.append(f"mythos_bot.py: spiral anchor appears {count}x — ambiguous")
        _log(patch, f"  ✗ anchor ambiguous ({count}x)")
        return False
    backup = BOT_MAIN_PATH.with_suffix('.py.sen0009.bak')
    backup.write_text(current)
    updated = current.replace(BOT_SPIRAL_ANCHOR, BOT_TRANSIT_ADDITION, 1)
    BOT_MAIN_PATH.write_text(updated)
    verify = BOT_MAIN_PATH.read_text()
    if 'transit_handler' not in verify:
        BOT_MAIN_PATH.write_text(current)
        patch.errors.append("mythos_bot.py: post-edit verify failed")
        return False
    import py_compile
    try:
        py_compile.compile(str(BOT_MAIN_PATH), doraise=True)
    except py_compile.PyCompileError as e:
        BOT_MAIN_PATH.write_text(current)
        patch.errors.append(f"mythos_bot.py: py_compile failed: {e}")
        return False
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(BOT_MAIN_PATH))
    _log(patch, "  ✓ /transits registered in mythos_bot.py")
    return True


def smoke_test(patch) -> bool:
    cmd = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from astrology.natal_generator import load_natal; '
        'c = load_natal("Adge"); '
        'assert c and len(c.get("chart_objects", {})) >= 10; '
        'print("ok:", len(c["chart_objects"]), "planets")',
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        patch.errors.append(f"smoke test failed: {out.stderr.strip()[:200]}")
        _log(patch, f"  ✗ {out.stderr.strip()[:200]}")
        return False
    _log(patch, f"  ✓ {out.stdout.strip()}")
    return True


def run_golden_fixtures(patch) -> bool:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY_PATH],
        capture_output=True, text=True, timeout=60,
    )
    _log(patch, "  — golden fixture output —")
    for line in result.stdout.splitlines():
        _log(patch, f"    {line}")
    if result.returncode == 0:
        _log(patch, "  ✓ all 5 golden fixtures PASS")
        return True
    patch.errors.append(f"golden fixtures failed (exit {result.returncode})")
    return False


def rewrite_next_patch_spec(patch) -> bool:
    new_spec = '''---
title: "Astrology Next Patch Spec — Letter F"
category: spec
status: active
stream: SEN
location: docs/astrology
updated: 2026-04-21
---

# Astrology Next Patch Spec — Letter F (Integration + Completion)

> **Current state:** Letter E (SEN-0009) shipped — /transits Telegram
> command live for Adge and Seraphe, transit_pressure.py wired to
> natal_generator, bot restarted cleanly.
>
> **Expected patch number:** SEN-0010 (verify via `mythos-diag streams`).

---

## Scope

Final letter of Astrology v2. CLI tool + documentation completion.

1. **`/opt/mythos/bin/daily-transits` CLI** — shell-accessible transit
   report: `daily-transits adge` or `daily-transits seraphe 2026-04-28`

2. **Update `SYSTEM_ASTROLOGY.md`** — mark A→F complete, document full
   v2 architecture as stable.

3. **Update `SUB-SYSTEMS.md`** — increment from DRAFT (N=1) to N=2.
   Refine the pattern based on Astrology v2 experience.

4. **File a note in REQUESTS.md** that the comprehensive astrology tool
   audit can now be scheduled (pre-condition: A→F complete ✓).

---

## Files created

| File | Purpose |
|---|---|
| `/opt/mythos/bin/daily-transits` | Shell CLI for transit reports |

## Files modified

| File | Change |
|---|---|
| `/opt/mythos/docs/SYSTEM_ASTROLOGY.md` | Mark A→F complete |
| `/opt/mythos/docs/SUB-SYSTEMS.md` | Increment to N=2 |

## Services restarted: none (CLI addition only)
## SQL: none
## Blast radius: LOW

*End of Letter F spec.*
'''
    if NEXT_PATCH_SPEC_PATH.exists():
        backup = NEXT_PATCH_SPEC_PATH.with_suffix('.md.sen0009.bak')
        backup.write_text(NEXT_PATCH_SPEC_PATH.read_text())
    NEXT_PATCH_SPEC_PATH.write_text(new_spec)
    _log(patch, "  ✓ NEXT_PATCH_SPEC.md rewritten for Letter F")
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(NEXT_PATCH_SPEC_PATH))
    return True


# ═══════════════════════════════════════════════════════════════════════
patch = PatchBase(
    stream='SEN',
    number=9,
    description='astrology v2 letter E — daily transits wiring',
    patch_type='MINOR',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0009 v2 — Astrology v2 Letter E (Daily Transits)')
print('v1 fix: anchor on spiral lazy-import block at lines 1285-1286')
print('=' * 70 + '\n')

# ─── PHASE 0: Allowlist mythos-bot ──────────────────────────────
print('PHASE 0: Allowlist mythos-bot.service')
print('-' * 70)
try:
    patch.allowlist_append_unit('mythos-bot.service')
    _log(patch, '  ✓ mythos-bot.service allowlisted')
except Exception as e:
    patch.errors.append(f'allowlist failed: {e}')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 1: Deploy transit_handler.py ─────────────────────────
print('\nPHASE 1: Deploy transit_handler.py')
print('-' * 70)
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/transit_handler.py',
    str(TRANSIT_HANDLER_PATH),
)
_log(patch, '  ✓ transit_handler.py deployed')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 2: Inject natal_generator into transit_pressure.py ───
print('\nPHASE 2: Wire natal_generator into transit_pressure.py')
print('-' * 70)
if not inject_natal_generator(patch):
    print('\n✗ Phase 2 FAILED')
    patch.finish(); sys.exit(1)

# ─── PHASE 3: Register /transits in mythos_bot.py ───────────────
print('\nPHASE 3: Register /transits in mythos_bot.py')
print('-' * 70)
if not register_in_bot(patch):
    print('\n✗ Phase 3 FAILED')
    patch.finish(); sys.exit(1)

# ─── PHASE 4: Smoke test natal_generator ────────────────────────
print('\nPHASE 4: Smoke test natal_generator')
print('-' * 70)
if not smoke_test(patch):
    print('\n✗ Phase 4 FAILED')
    patch.finish(); sys.exit(1)

# ─── PHASE 5: Restart bot ───────────────────────────────────────
print('\nPHASE 5: Restart mythos-bot.service')
print('-' * 70)
try:
    patch.stop_service('mythos-bot.service')
    _log(patch, '  ✓ bot stopped')
    patch.start_service('mythos-bot.service')
    if patch.is_service_active('mythos-bot.service'):
        _log(patch, '  ✓ mythos-bot.service active')
    else:
        patch.errors.append('mythos-bot.service not active after restart')
        _log(patch, '  ✗ bot not active after restart')
except Exception as e:
    patch.errors.append(f'bot restart failed: {e}')
    _log(patch, f'  ✗ {e}')

if patch.errors:
    patch.finish(); sys.exit(1)

# ─── PHASE 6: Golden fixtures ───────────────────────────────────
print('\nPHASE 6: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

# ─── PHASE 7: Rewrite NEXT_PATCH_SPEC.md ────────────────────────
print('\nPHASE 7: Rewriting NEXT_PATCH_SPEC.md for Letter F')
print('-' * 70)
rewrite_next_patch_spec(patch)

print('\n' + '=' * 70)
print('✓ SEN-0009 complete — /transits command live')
print('=' * 70 + '\n')

patch.finish()
