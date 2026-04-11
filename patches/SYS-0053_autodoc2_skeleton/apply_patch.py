#!/usr/bin/env python3
"""
SYS-0053_autodoc2_skeleton

Builds AutoDoc2 from scratch as a clean, multi-language replacement for the
legacy /opt/mythos/tools/autodoc.py. Phase 1: skeleton + Python walker via
tree-sitter. Future phases add JS, TS, SQL, PHP, Go, Bash, YAML walkers
without touching the dispatch core.

This patch:
  1. Installs tree-sitter + tree-sitter-languages into /opt/mythos/.venv
  2. Deploys the autodoc2 package to /opt/mythos/tools/autodoc2/
  3. Symlinks /opt/mythos/bin/autodoc2 -> /opt/mythos/tools/autodoc2/cli.py
  4. Marks cli.py executable

No service restart. autodoc2 is a CLI tool, not a service.

Validation after install:
  cd /tmp && git clone --depth 1 https://github.com/psf/requests.git
  autodoc2 /tmp/requests --env-file /opt/mythos/.env.demo-live
  Then check demo-live Neo4j browser at http://localhost:7475 for nodes.
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=53,
    description='autodoc2_skeleton',
    patch_type='MINOR',
)
patch.begin()

# ---------------------------------------------------------------------------
# 1. Install tree-sitter dependencies into the venv
# ---------------------------------------------------------------------------
print("[autodoc2] Installing tree-sitter and tree-sitter-languages into venv...")
venv_pip = '/opt/mythos/.venv/bin/pip'
try:
    subprocess.run(
        [venv_pip, 'install', '--upgrade', 'tree-sitter', 'tree-sitter-languages'],
        check=True,
    )
    print("[autodoc2] tree-sitter packages installed.")
except subprocess.CalledProcessError as e:
    print(f"[autodoc2] WARNING: pip install failed: {e}")
    print("[autodoc2] You may need to install manually:")
    print("           /opt/mythos/.venv/bin/pip install tree-sitter tree-sitter-languages")

# ---------------------------------------------------------------------------
# 2. Deploy package files
# ---------------------------------------------------------------------------
files_to_deploy = [
    'opt/mythos/tools/autodoc2/__init__.py',
    'opt/mythos/tools/autodoc2/cli.py',
    'opt/mythos/tools/autodoc2/config.py',
    'opt/mythos/tools/autodoc2/filters.py',
    'opt/mythos/tools/autodoc2/walker.py',
    'opt/mythos/tools/autodoc2/engine.py',
    'opt/mythos/tools/autodoc2/neo4j_writer.py',
    'opt/mythos/tools/autodoc2/markdown_writer.py',
    'opt/mythos/tools/autodoc2/llm_client.py',
    'opt/mythos/tools/autodoc2/walkers/__init__.py',
    'opt/mythos/tools/autodoc2/walkers/python_walker.py',
]

for relpath in files_to_deploy:
    target = '/' + relpath
    patch.deploy_file(relpath, target)

# ---------------------------------------------------------------------------
# 3. Make cli.py executable
# ---------------------------------------------------------------------------
cli_path = '/opt/mythos/tools/autodoc2/cli.py'
os.chmod(cli_path, 0o755)
print(f"[autodoc2] chmod +x {cli_path}")

# ---------------------------------------------------------------------------
# 4. Symlink into /opt/mythos/bin/
# ---------------------------------------------------------------------------
bin_dir = Path('/opt/mythos/bin')
bin_dir.mkdir(parents=True, exist_ok=True)
symlink_path = bin_dir / 'autodoc2'
if symlink_path.exists() or symlink_path.is_symlink():
    symlink_path.unlink()
symlink_path.symlink_to(cli_path)
print(f"[autodoc2] symlink: {symlink_path} -> {cli_path}")

# ---------------------------------------------------------------------------
# 5. Verify import works
# ---------------------------------------------------------------------------
print("[autodoc2] Verifying tree-sitter import...")
try:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         'import tree_sitter; import tree_sitter_languages; '
         'p = tree_sitter_languages.get_parser("python"); '
         'print("tree-sitter OK, python grammar loaded")'],
        check=True, capture_output=True, text=True,
    )
    print(f"[autodoc2] {result.stdout.strip()}")
except subprocess.CalledProcessError as e:
    print(f"[autodoc2] WARNING: tree-sitter verification failed:")
    print(f"           stdout: {e.stdout}")
    print(f"           stderr: {e.stderr}")

patch.finish()
