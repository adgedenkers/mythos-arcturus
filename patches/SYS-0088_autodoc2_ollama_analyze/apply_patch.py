import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
from pathlib import Path
import py_compile
import tempfile
import shutil

patch = PatchBase(
    stream='SYS',
    number=88,
    description='autodoc2 ollama-analyze microtool (gemma4:26b)',
    patch_type='MINOR',
)
patch.begin()


def syntax_check(src_path: str, label: str):
    """Compile-check a Python file before deploying. Abort patch on failure."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            tmp_path = tmp.name
        shutil.copy2(src_path, tmp_path)
        py_compile.compile(tmp_path, doraise=True)
        os.unlink(tmp_path)
        patch.logger.log(f"  ✓ syntax OK: {label}")
    except py_compile.PyCompileError as e:
        patch.errors.append(f"syntax error in {label}: {e}")
        patch.logger.log(f"  ✗ syntax error: {label}: {e}")
    except Exception as e:
        patch.errors.append(f"syntax check failed for {label}: {e}")
        patch.logger.log(f"  ✗ syntax check failed: {label}: {e}")


# ── Syntax check all modified Python files before deploying anything ─────────

patch_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))

files_to_check = [
    ('opt/mythos/tools/autodoc2/analyzer.py',     'analyzer.py'),
    ('opt/mythos/tools/autodoc2/config.py',       'config.py'),
    ('opt/mythos/tools/autodoc2/cli.py',          'cli.py'),
    ('opt/mythos/tools/autodoc2/engine.py',       'engine.py'),
    ('opt/mythos/tools/autodoc2/neo4j_writer.py', 'neo4j_writer.py'),
]

for rel, label in files_to_check:
    syntax_check(str(patch_dir / rel), label)

# Abort if any syntax errors — deploy nothing
if patch.errors:
    patch.finish()
    sys.exit(1)

# ── Deploy files ──────────────────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/tools/autodoc2/analyzer.py',
    '/opt/mythos/tools/autodoc2/analyzer.py',
)

patch.deploy_file(
    'opt/mythos/tools/autodoc2/config.py',
    '/opt/mythos/tools/autodoc2/config.py',
)

patch.deploy_file(
    'opt/mythos/tools/autodoc2/cli.py',
    '/opt/mythos/tools/autodoc2/cli.py',
)

patch.deploy_file(
    'opt/mythos/tools/autodoc2/engine.py',
    '/opt/mythos/tools/autodoc2/engine.py',
)

patch.deploy_file(
    'opt/mythos/tools/autodoc2/neo4j_writer.py',
    '/opt/mythos/tools/autodoc2/neo4j_writer.py',
)

# ── Smoke test: import the package and verify Analyzer is accessible ──────────

try:
    import subprocess
    check = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         'import sys; sys.path.insert(0, "/opt/mythos/tools"); '
         'from autodoc2.analyzer import Analyzer, AnalysisResult, ANALYSIS_MODEL; '
         'assert ANALYSIS_MODEL == "gemma4:26b", f"Wrong model: {ANALYSIS_MODEL}"; '
         'a = Analyzer(); '
         'print(f"Analyzer OK — model: {ANALYSIS_MODEL}")'],
        capture_output=True, text=True, timeout=30,
    )
    if check.returncode != 0:
        patch.errors.append(f"import smoke test failed: {check.stderr.strip()}")
        patch.logger.log(f"  ✗ import smoke test: {check.stderr.strip()}")
    else:
        patch.logger.log(f"  ✓ {check.stdout.strip()}")
except Exception as e:
    patch.errors.append(f"smoke test exception: {e}")
    patch.logger.log(f"  ✗ smoke test exception: {e}")

# ── Verify --analyze flag is recognised by CLI ────────────────────────────────

try:
    check2 = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         'import sys; sys.path.insert(0, "/opt/mythos/tools"); '
         'from autodoc2.cli import build_parser; '
         'p = build_parser(); '
         'args = p.parse_args(["--analyze", "--status"]); '
         'assert args.analyze is True; '
         'print("--analyze flag OK")'],
        capture_output=True, text=True, timeout=15,
    )
    if check2.returncode != 0:
        patch.errors.append(f"CLI flag test failed: {check2.stderr.strip()}")
        patch.logger.log(f"  ✗ CLI flag test: {check2.stderr.strip()}")
    else:
        patch.logger.log(f"  ✓ {check2.stdout.strip()}")
except Exception as e:
    patch.errors.append(f"CLI flag test exception: {e}")
    patch.logger.log(f"  ✗ CLI flag test exception: {e}")

patch.finish()
