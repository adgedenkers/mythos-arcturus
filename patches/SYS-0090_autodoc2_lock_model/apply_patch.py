import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
from pathlib import Path

patch = PatchBase(
    stream='SYS',
    number=90,
    description='autodoc2 lock qwen3-coder:30b analysis model',
    patch_type='PATCH',
)
patch.begin()

# ── 1. Lock model in analyzer.py (sed was applied to disk but not patched) ───

patch.str_replace(
    '/opt/mythos/tools/autodoc2/analyzer.py',
    old='ANALYSIS_MODEL = "gemma4:26b"',
    new='ANALYSIS_MODEL = "qwen3-coder:30b"',
)

# ── 2. Fix display string in engine.py — read from Analyzer, not hardcoded ───

patch.str_replace(
    '/opt/mythos/tools/autodoc2/engine.py',
    old='        print(f"[autodoc2] analyze:     {\'gemma4:26b\' if cfg.analyze else \'disabled\'}")',
    new='        from .analyzer import ANALYSIS_MODEL\n        print(f"[autodoc2] analyze:     {ANALYSIS_MODEL if cfg.analyze else \'disabled\'}")',
)

# ── 3. Fix cli.py executable bit after deploy_file ───────────────────────────
# deploy_file uses shutil.copy2 which preserves source permissions,
# but the source in the patch zip may lose +x. Explicitly set it here.

cli_path = Path('/opt/mythos/tools/autodoc2/cli.py')
if cli_path.exists():
    cli_path.chmod(0o755)
    patch.files_deployed.append(str(cli_path))
    patch.logger.log("  ✓ cli.py chmod 755")
else:
    patch.errors.append("cli.py not found at expected path")
    patch.logger.log("  ✗ cli.py not found")

# ── 4. Smoke test — verify model string is correct ───────────────────────────

check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; sys.path.insert(0, "/opt/mythos/tools"); '
     'from autodoc2.analyzer import ANALYSIS_MODEL; '
     'assert ANALYSIS_MODEL == "qwen3-coder:30b", f"Wrong: {ANALYSIS_MODEL}"; '
     'print(f"Model locked: {ANALYSIS_MODEL}")'],
    capture_output=True, text=True, timeout=15,
)
if check.returncode != 0:
    patch.errors.append(f"model lock check failed: {check.stderr.strip()}")
    patch.logger.log(f"  ✗ model lock: {check.stderr.strip()}")
else:
    patch.logger.log(f"  ✓ {check.stdout.strip()}")

patch.finish()
