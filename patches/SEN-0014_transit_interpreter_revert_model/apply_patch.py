#!/usr/bin/env python3
"""
SEN-0014: transit_interpreter.py — revert to qwen3:30b-a3b, keep num_predict=512

Root cause (finally confirmed via direct testing):
  qwen3:30b-a3b with num_predict=256 was consuming all tokens on internal
  reasoning before producing any output, returning empty content.
  With num_predict=512 it works correctly — clean content, no leakage.

  gemma4:26b refuses all astrology prompts (safety filtering), returning
  empty content regardless of token budget.

  SEN-0013 switched to gemma4 which made things worse.
  This patch reverts the model back to qwen3:30b-a3b (the correct model)
  while keeping the num_predict=512 fix from SEN-0013.

  Verified: qwen3:30b-a3b with num_predict=512 returns proper content
  via both attr and dict access patterns.

Tables: none. Services: none. Blast radius: MINIMAL.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

INTERPRETER_PATH = Path('/opt/mythos/astrology/spiral/transit_interpreter.py')
CHECK_ACCURACY   = '/opt/mythos/astrology/tests/check_accuracy.py'

# SEN-0013 left this in place — revert it
OLD_MODEL = ('# SEN-0013: gemma4:26b for transit interpretations\n'
             '# qwen3 leaks chain-of-thought into content field.\n'
             '# Override via TRANSIT_OLLAMA_MODEL env var if needed.\n'
             'OLLAMA_MODEL = os.getenv("TRANSIT_OLLAMA_MODEL", "gemma4:26b")')
NEW_MODEL = 'OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")'


def log(patch, msg):
    patch.logger.log(msg)


def revert_model(patch) -> bool:
    if not INTERPRETER_PATH.exists():
        patch.errors.append("transit_interpreter.py missing")
        return False
    current = INTERPRETER_PATH.read_text()
    if 'qwen3:30b-a3b' in current and 'gemma4' not in current:
        patch.validations.append("model already reverted")
        log(patch, "  ✓ already on qwen3 (idempotent)")
        return True
    if OLD_MODEL not in current:
        patch.errors.append("SEN-0013 model block not found — check file state")
        log(patch, "  ✗ anchor not found")
        return False
    backup = INTERPRETER_PATH.with_suffix('.py.sen0014.bak')
    backup.write_text(current)
    updated = current.replace(OLD_MODEL, NEW_MODEL, 1)
    INTERPRETER_PATH.write_text(updated)
    verify = INTERPRETER_PATH.read_text()
    if 'gemma4' in verify or 'qwen3:30b-a3b' not in verify:
        INTERPRETER_PATH.write_text(current)
        patch.errors.append("post-edit verify failed")
        return False
    import py_compile
    try:
        py_compile.compile(str(INTERPRETER_PATH), doraise=True)
    except py_compile.PyCompileError as e:
        INTERPRETER_PATH.write_text(current)
        patch.errors.append(f"py_compile failed: {e}")
        return False
    if hasattr(patch, 'files_deployed'):
        patch.files_deployed.append(str(INTERPRETER_PATH))
    log(patch, "  ✓ reverted to qwen3:30b-a3b (num_predict=512 retained)")
    return True


def verify_qwen3_works(patch) -> bool:
    """Quick sanity check that qwen3+512 produces content."""
    cmd = [
        '/opt/mythos/.venv/bin/python3', '-c',
        'import sys; sys.path.insert(0, "/opt/mythos"); '
        'from ollama import Client; import os; '
        'c = Client(host=os.getenv("OLLAMA_HOST","http://localhost:11434")); '
        'r = c.chat(model="qwen3:30b-a3b", '
        'messages=[{"role":"user","content":"Mercury trine Mars 0.5 degrees. Two sentences."}], '
        'options={"temperature":0.75,"num_predict":512}); '
        'assert len(r.message.content) > 20, f"empty: {repr(r.message.content)}"; '
        'print("ok:", len(r.message.content), "chars")',
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if out.returncode != 0:
        patch.errors.append(f"qwen3 sanity check failed: {out.stderr.strip()[:200]}")
        log(patch, f"  ✗ {out.stderr.strip()[:150]}")
        return False
    log(patch, f"  ✓ {out.stdout.strip()}")
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
    number=14,
    description='transit_interpreter: revert to qwen3, keep num_predict=512',
    patch_type='PATCH',
)
patch.begin()

print('\n' + '=' * 70)
print('SEN-0014 — transit_interpreter: revert to qwen3:30b-a3b')
print('num_predict=512 (from SEN-0013) is the real fix, not the model switch')
print('=' * 70 + '\n')

print('PHASE 1: Revert model to qwen3:30b-a3b')
print('-' * 70)
if not revert_model(patch):
    patch.finish(); sys.exit(1)

print('\nPHASE 2: Sanity check qwen3 with 512 tokens')
print('-' * 70)
if not verify_qwen3_works(patch):
    patch.finish(); sys.exit(1)

print('\nPHASE 3: Golden fixture regression check')
print('-' * 70)
if not run_golden_fixtures(patch):
    patch.finish(); sys.exit(1)

print('\n' + '=' * 70)
print('✓ SEN-0014 complete — /transits should now produce Iris interpretations')
print('=' * 70 + '\n')

patch.finish()
