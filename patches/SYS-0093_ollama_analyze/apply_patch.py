#!/usr/bin/env python3
"""
SYS-0093: ollama-analyze microtool

Adds LLM-powered code/SQL analysis callable from patch builds:

1. Deploy /opt/mythos/tools/ollama_analyze.py
   - CLI: ollama-analyze --task sql-drift --files migration.sql
   - Tasks: sql-drift, py-signatures, review, sql-analyze
   - Default model: qwen3:30b-a3b (overridable via OLLAMA_ANALYZE_MODEL)
   - Dry-run aware: returns stub when MYTHOS_PATCH_DRY_RUN=1
   - Strips <think> blocks from qwen3 thinking mode output
   - Always returns parsed JSON dict or None on failure

2. Symlink /opt/mythos/bin/ollama-analyze -> ollama_analyze.py

3. Add PatchBase.ollama_analyze() method to patch_base.py
   - patch.ollama_analyze(prompt, files=[], task=None, model=None, timeout=120)
   - Returns dict | None
   - Dry-run aware, logs result summary

4. Register MythosTool node via patchbase-methods --register

Tables: none. Services: none. Blast radius: LOW.
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TOOL_PATH    = '/opt/mythos/tools/ollama_analyze.py'
SYMLINK_PATH = '/opt/mythos/bin/ollama-analyze'
PATCHBASE    = '/opt/mythos/patches/scripts/patch_base.py'
VENV         = '/opt/mythos/.venv/bin/python3'

patch = PatchBase(
    stream='SYS',
    number=93,
    description='ollama-analyze microtool + PatchBase.ollama_analyze()',
    patch_type='MINOR',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0093 -- ollama-analyze microtool')
print('=' * 70 + '\n')

# ── PHASE 1: Deploy ollama_analyze.py ────────────────────────────
print('PHASE 1: Deploy ollama_analyze.py')
print('-' * 70)

patch.deploy_file(
    'opt/mythos/tools/ollama_analyze.py',
    TOOL_PATH,
)
if patch.errors:
    patch.finish(); sys.exit(1)

# Make executable
try:
    os.chmod(TOOL_PATH, 0o755)
    patch.logger.log('  ✓ chmod 755 ollama_analyze.py')
except Exception as e:
    patch.errors.append(f'chmod failed: {e}')
    patch.finish(); sys.exit(1)

# py_compile check
if not patch.py_compile_check(TOOL_PATH, 'ollama_analyze.py'):
    patch.finish(); sys.exit(1)

# ── PHASE 2: Symlink ─────────────────────────────────────────────
print('\nPHASE 2: Symlink /opt/mythos/bin/ollama-analyze')
print('-' * 70)

try:
    p = Path(SYMLINK_PATH)
    if p.exists() or p.is_symlink():
        p.unlink()
    p.symlink_to(TOOL_PATH)
    patch.logger.log(f'  ✓ symlink: {SYMLINK_PATH} -> {TOOL_PATH}')
except Exception as e:
    patch.errors.append(f'symlink failed: {e}')
    patch.logger.log(f'  ✗ symlink failed: {e}')
    patch.finish(); sys.exit(1)

# ── PHASE 3: Add ollama_analyze to PatchBase ─────────────────────
print('\nPHASE 3: Add PatchBase.ollama_analyze()')
print('-' * 70)

if not patch.assert_file_exists(PATCHBASE, 'patch_base.py'):
    patch.finish(); sys.exit(1)

NEW_METHOD = '''
    def ollama_analyze(self, prompt: str, files: list = None,
                       task: str = None, model: str = None,
                       timeout: int = 120) -> dict | None:
        """Run LLM analysis on a prompt + optional file contents.

        SYS-0093: Wraps /opt/mythos/tools/ollama_analyze.py for use
        inside apply_patch.py. Returns parsed JSON dict or None on failure.
        Dry-run aware -- returns a stub dict without calling Ollama.

        Args:
            prompt:  Analysis prompt.
            files:   List of absolute file paths to include as context.
            task:    Preset task: sql-drift, py-signatures, review, sql-analyze.
            model:   Ollama model override (default: qwen3:30b-a3b).
            timeout: Seconds before giving up (default: 120).

        Returns:
            dict on success, None on failure.

        Example:
            result = patch.ollama_analyze(
                prompt="Check for missing indexes",
                files=["/opt/mythos/migrations/SYS-0093_schema.sql"],
                task="sql-drift",
            )
            if result and result.get("issues"):
                patch.errors.append(f"SQL issues: {result['issues']}")
        """
        import json as _json
        tool = '/opt/mythos/tools/ollama_analyze.py'
        if not os.path.isfile(tool):
            msg = f"ollama_analyze: tool not found: {tool}"
            self.errors.append(msg)
            self.logger.log(f"  ✗ {msg}")
            return None

        if self.dry_run:
            self.validations.append("ollama_analyze: skipped (dry run)")
            self.logger.log("  ✓ [validate] ollama_analyze: skipped in dry run")
            return {'dry_run': True, 'summary': 'Dry run -- no analysis performed',
                    'safe': True, 'issues': [], 'warnings': []}

        cmd = ['/opt/mythos/.venv/bin/python3', tool, '--json']
        if task:
            cmd += ['--task', task]
        if prompt:
            cmd += ['--prompt', prompt]
        if files:
            cmd += ['--files'] + [str(f) for f in files]
        if model:
            cmd += ['--model', model]
        cmd += ['--timeout', str(timeout)]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 10,
            )
        except subprocess.TimeoutExpired:
            msg = f"ollama_analyze: timed out after {timeout}s"
            self.errors.append(msg)
            self.logger.log(f"  ✗ {msg}")
            return None
        except Exception as e:
            msg = f"ollama_analyze: subprocess error: {e}"
            self.errors.append(msg)
            self.logger.log(f"  ✗ {msg}")
            return None

        if result.returncode != 0:
            stderr = (result.stderr or '').strip()[:200]
            msg = f"ollama_analyze: failed (exit {result.returncode}): {stderr}"
            self.errors.append(msg)
            self.logger.log(f"  ✗ ollama_analyze: FAILED")
            return None

        try:
            parsed = _json.loads(result.stdout.strip())
            summary = parsed.get('summary', parsed.get('raw', '')[:80])
            self.logger.log(f"  ✓ ollama_analyze: {summary}")
            return parsed
        except _json.JSONDecodeError as e:
            msg = f"ollama_analyze: JSON parse failed: {e}"
            self.errors.append(msg)
            self.logger.log(f"  ✗ {msg}")
            return None

'''

# Anchor: the line that opens the private ledger section
patch.str_replace(
    PATCHBASE,
    old='    def _bump_streams_json(self):',
    new=NEW_METHOD + '    def _bump_streams_json(self):',
    label='add ollama_analyze method',
)
if patch.errors:
    patch.finish(); sys.exit(1)

# ── PHASE 4: Smoke test CLI ───────────────────────────────────────
print('\nPHASE 4: Smoke test CLI')
print('-' * 70)

patch.run_python_check(
    code=(
        "import subprocess, json\n"
        "r = subprocess.run(\n"
        "    ['/opt/mythos/.venv/bin/python3', '/opt/mythos/tools/ollama_analyze.py', '--list-tasks'],\n"
        "    capture_output=True, text=True, timeout=10\n"
        ")\n"
        "assert r.returncode == 0, f'exit {r.returncode}: {r.stderr}'\n"
        "assert 'sql-drift' in r.stdout, f'sql-drift not in output: {r.stdout}'\n"
        "print(r.stdout.strip())\n"
    ),
    label='ollama-analyze --list-tasks',
    timeout=15,
)
if patch.errors:
    patch.finish(); sys.exit(1)

# Smoke test dry-run mode
patch.run_python_check(
    code=(
        "import subprocess, json, os\n"
        "env = {**os.environ, 'MYTHOS_PATCH_DRY_RUN': '1'}\n"
        "r = subprocess.run(\n"
        "    ['/opt/mythos/.venv/bin/python3', '/opt/mythos/tools/ollama_analyze.py',\n"
        "     '--task', 'sql-drift', '--json'],\n"
        "    capture_output=True, text=True, timeout=10, env=env\n"
        ")\n"
        "assert r.returncode == 0, f'exit {r.returncode}: {r.stderr}'\n"
        "result = json.loads(r.stdout)\n"
        "assert result.get('dry_run') is True, f'expected dry_run=True: {result}'\n"
        "print('dry_run stub:', result)\n"
    ),
    label='ollama-analyze dry-run stub',
    timeout=15,
)
if patch.errors:
    patch.finish(); sys.exit(1)

# ── PHASE 5: Register to Neo4j ────────────────────────────────────
print('\nPHASE 5: Register PatchBase methods to Neo4j')
print('-' * 70)

patch.run_python_check(
    code=(
        "import subprocess\n"
        "r = subprocess.run(\n"
        "    ['/opt/mythos/.venv/bin/python3',\n"
        "     '/opt/mythos/tools/patchbase_register.py', '--register'],\n"
        "    capture_output=True, text=True, timeout=30\n"
        ")\n"
        "print(r.stdout.strip())\n"
        "assert r.returncode == 0, f'register failed: {r.stderr}'\n"
    ),
    label='patchbase-methods --register',
    timeout=35,
)
if patch.errors:
    patch.finish(); sys.exit(1)

# ── Done ──────────────────────────────────────────────────────────
print('\n' + '=' * 70)
print('✓ SYS-0093 complete -- ollama-analyze microtool deployed')
print('  /opt/mythos/tools/ollama_analyze.py')
print('  /opt/mythos/bin/ollama-analyze (symlink)')
print('  PatchBase.ollama_analyze() -- LLM analysis from patch builds')
print('  Tasks: sql-drift, py-signatures, review, sql-analyze')
print('=' * 70 + '\n')

patch.finish()
