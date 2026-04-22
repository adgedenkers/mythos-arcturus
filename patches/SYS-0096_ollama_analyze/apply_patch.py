#!/usr/bin/env python3
"""
SYS-0096: ollama-analyze microtool deployment

Deploys the ollama-analyze CLI tool and registers PatchBase methods
to Neo4j. PatchBase.ollama_analyze() was added manually to patch_base.py
before this patch ran.

1. Deploy /opt/mythos/tools/ollama_analyze.py
2. Symlink /opt/mythos/bin/ollama-analyze
3. Smoke test CLI (--list-tasks + dry-run)
4. Register all PatchBase methods to Neo4j via patchbase-methods --register

Tables: none. Services: none. Blast radius: LOW.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TOOL_PATH    = '/opt/mythos/tools/ollama_analyze.py'
SYMLINK_PATH = '/opt/mythos/bin/ollama-analyze'

patch = PatchBase(
    stream='SYS',
    number=96,
    description='ollama-analyze microtool + Neo4j registration',
    patch_type='MINOR',
)
patch.begin()

print('\n' + '=' * 70)
print('SYS-0096 -- ollama-analyze microtool')
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

try:
    os.chmod(TOOL_PATH, 0o755)
    patch.logger.log('  ✓ chmod 755 ollama_analyze.py')
except Exception as e:
    patch.errors.append(f'chmod failed: {e}')
    patch.finish(); sys.exit(1)

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

# ── PHASE 3: Smoke tests ──────────────────────────────────────────
print('\nPHASE 3: Smoke tests')
print('-' * 70)

patch.run_python_check(
    code=(
        "import subprocess\n"
        "r = subprocess.run(\n"
        "    ['/opt/mythos/.venv/bin/python3', '/opt/mythos/tools/ollama_analyze.py', '--list-tasks'],\n"
        "    capture_output=True, text=True, timeout=10\n"
        ")\n"
        "assert r.returncode == 0, f'exit {r.returncode}: {r.stderr}'\n"
        "assert 'sql-drift' in r.stdout\n"
        "print(r.stdout.strip())\n"
    ),
    label='--list-tasks',
    timeout=15,
)
if patch.errors:
    patch.finish(); sys.exit(1)

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
        "assert result.get('dry_run') is True\n"
        "print('dry_run stub OK:', result.get('summary'))\n"
    ),
    label='dry-run stub',
    timeout=15,
)
if patch.errors:
    patch.finish(); sys.exit(1)

# ── PHASE 4: Verify PatchBase.ollama_analyze exists ──────────────
print('\nPHASE 4: Verify PatchBase.ollama_analyze()')
print('-' * 70)

patch.run_python_check(
    code=(
        "import sys\n"
        "sys.path.insert(0, '/opt/mythos/patches/scripts')\n"
        "from patch_base import PatchBase\n"
        "assert hasattr(PatchBase, 'ollama_analyze'), 'method missing'\n"
        "print('  PatchBase.ollama_analyze: present')\n"
    ),
    label='PatchBase.ollama_analyze present',
    timeout=10,
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

print('\n' + '=' * 70)
print('✓ SYS-0096 complete -- ollama-analyze microtool deployed')
print('  /opt/mythos/tools/ollama_analyze.py')
print('  /opt/mythos/bin/ollama-analyze (symlink)')
print('  PatchBase.ollama_analyze() -- already in patch_base.py')
print('  Tasks: sql-drift, py-signatures, review, sql-analyze')
print('=' * 70 + '\n')

patch.finish()
