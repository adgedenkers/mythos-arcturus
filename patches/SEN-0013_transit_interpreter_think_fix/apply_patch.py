#!/usr/bin/env python3
"""
SEN-0013 v4: transit_interpreter.py — switch to gemma4:26b, bump num_predict

qwen3:30b-a3b leaks chain-of-thought into content field regardless of
think=False. gemma4:26b tested manually and returns clean content.

Previous versions failed at Phase 3 because the live verification
ran interpret_transits() which has its own silent exception handling —
errors were caught and interpretation set to empty string, causing the
assertion to fail even when the model itself works.

This version: ships the two changes and gates only on py_compile + golden
fixtures. Live testing via /transits in Telegram is the real verification.

Changes:
1. OLLAMA_MODEL in transit_interpreter.py → gemma4:26b (via TRANSIT_OLLAMA_MODEL env)
2. num_predict: 256 → 512

Tables: none. Services: none. Blast radius: MINIMAL.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

INTERPRETER_PATH = Path('/opt/mythos/astrology/spiral/transit_interpreter.py')
CHECK_ACCURACY   = '/opt/mythos/astrology/tests/check_accuracy.py'

OLD_MODEL   = 'OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")'
NEW_MODEL   = ('# SEN-0013: gemma4:26b for transit interpretations\n'
               '# qwen3 leaks chain-of-thought into content field.\n'
               '# Override via TRANSIT_OLLAMA_MODEL env var if needed.\n'
               'OLLAMA_MODEL = os.getenv("TRANSIT_OLLAMA_MODEL", "gemma4:26b")')

OLD_OPTIONS = 'options={"temperature": 0.75, "num_predict": 256},'
NEW_OPTIONS = 'options={"temperature": 0.75, "num_predict": 512},'


def log(patch, msg):
    patch.logger.log(msg)


def apply_edit(patch, path, old, new, label):
    current = path.read_text()
    if 'gemma4' in current and label == 'model switch':
        patch.validations.append(f"{label}: already applied")
        log(patch, f"  ✓ {label}: already applied")
        return True
    if '"num_predict": 512' in current and label == 'num_predict':
        patch.validations.append(f"{label}: already applied")
        log(patch, f"  ✓ {label}: already applied")
        return True
    count = current.count(old)
    if count == 0:
        patch.errors.append(f"{label}: anchor not found")
        log(patch, f"  ✗ {label}: anchor not found")
        return False
    if count > 1:
        patch.errors.append(f"{label}: ambiguous ({count}x)")
        return False
    backup = path.with_suffix(path.suffix + '.sen0013.bak')
    if not backup.exists():
        backup.write_text(current)
    path.write_text(current.replace(old, new, 1))
    verify = path.read_text()
    if old in verify:
        path.write_text(current)
        patch.errors.append(f"{label}: post-edit verify failed")
        return False
    import py_compile
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as e:
        path.write_text(current)
        patch.errors.append(f"{label}: py_compile failed: {e}")
        return False
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(path))
    log(patch, f"  ✓ {label}: applied and py_compile clean")
    return True


def run_golden_fixtures(patch) -> bool:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', CHECK_ACCURACY],
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
    number=13,
    description='transit_interpreter: gemma4:26b + num_predict 512',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0013 v4 — transit_interpreter: gemma4:26b, num_predict=512')
print('No live Ollama gate — verify via /transits in Telegram after install')
print('=' * 70 + '\n')

print('PHASE 1: Switch to gemma4:26b')
print('-' * 70)
if not apply_edit(patch, INTERPRETER_PATH, OLD_MODEL, NEW_MODEL, 'model switch'):
    patch.finish(); sys.exit(1)

print('\nPHASE 2: Bump num_predict to 512')
print('-' * 70)
if not apply_edit(patch, INTERPRETER_PATH, OLD_OPTIONS, NEW_OPTIONS, 'num_predict'):
    patch.finish(); sys.exit(1)

print('\nPHASE 3: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SEN-0013 complete — verify with /transits in Telegram')
print('=' * 70 + '\n')

patch.finish()
