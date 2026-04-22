import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
from pathlib import Path

patch = PatchBase(
    stream='SYS',
    number=92,
    description='autodoc2 patchbase microtool registration in Neo4j',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy patchbase_register.py ──────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/tools/patchbase_register.py',
    '/opt/mythos/tools/patchbase_register.py',
)

# Make it executable
Path('/opt/mythos/tools/patchbase_register.py').chmod(0o755)
patch.logger.log("  \u2713 patchbase_register.py chmod 755")

# ── Symlink to /opt/mythos/bin/patchbase-methods ──────────────────────────────

symlink = Path('/opt/mythos/bin/patchbase-methods')
target = Path('/opt/mythos/tools/patchbase_register.py')

if symlink.exists() or symlink.is_symlink():
    symlink.unlink()
symlink.symlink_to(target)
patch.files_deployed.append(str(symlink))
patch.logger.log("  \u2713 patchbase-methods symlink created")

# ── Syntax check ──────────────────────────────────────────────────────────────

patch.py_compile_check('/opt/mythos/tools/patchbase_register.py', 'patchbase_register.py')

# ── Smoke test: extract methods from live patch_base.py ───────────────────────

check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; sys.path.insert(0, "/opt/mythos/tools"); '
     'sys.path.insert(0, "/opt/mythos/patches/scripts"); '
     'from patchbase_register import extract_methods; '
     'from pathlib import Path; '
     'methods = extract_methods(Path("/opt/mythos/patches/scripts/patch_base.py")); '
     'names = [m["name"] for m in methods]; '
     'assert "deploy_file" in names, f"deploy_file missing: {names}"; '
     'assert "str_replace" in names, f"str_replace missing: {names}"; '
     'assert "restart_service" in names, f"restart_service missing: {names}"; '
     'print(f"Extracted {len(methods)} methods: " + ", ".join(names[:5]) + " ...")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check.returncode != 0:
    patch.errors.append(f"extract smoke test failed: {check.stderr.strip()}")
    patch.logger.log(f"  \u2717 extract test: {check.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check.stdout.strip()}")

# ── Register MythosTool nodes in Neo4j ───────────────────────────────────────

check2 = subprocess.run(
    ['/opt/mythos/.venv/bin/python3',
     '/opt/mythos/tools/patchbase_register.py', '--register'],
    capture_output=True, text=True, timeout=30,
    cwd='/opt/mythos',
)
if check2.returncode != 0:
    patch.errors.append(f"Neo4j registration failed: {check2.stderr.strip()}")
    patch.logger.log(f"  \u2717 Neo4j register: {check2.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check2.stdout.strip()}")

# ── Verify patchbase-methods CLI dumps output ─────────────────────────────────

check3 = subprocess.run(
    ['/opt/mythos/bin/patchbase-methods'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check3.returncode != 0:
    patch.errors.append(f"CLI dump failed: {check3.stderr.strip()}")
    patch.logger.log(f"  \u2717 patchbase-methods CLI: {check3.stderr.strip()}")
else:
    # Count method lines (lines starting with "patch.")
    method_lines = [l for l in check3.stdout.splitlines() if l.strip().startswith('patch.')]
    patch.logger.log(f"  \u2713 patchbase-methods CLI: {len(method_lines)} methods in output")

patch.finish()
