import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=93,
    description='autodoc2 iris skill — natural language codebase queries',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy the skill ──────────────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/skills/data/autodoc2_query.py',
    '/opt/mythos/skills/data/autodoc2_query.py',
)

# ── Syntax check ──────────────────────────────────────────────────────────────

patch.py_compile_check(
    '/opt/mythos/skills/data/autodoc2_query.py',
    'autodoc2_query.py',
)

# ── Smoke test: import and instantiate the skill ──────────────────────────────

check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; '
     'sys.path.insert(0, "/opt/mythos/skills"); '
     'sys.path.insert(0, "/opt/mythos"); '
     'from data.autodoc2_query import Autodoc2QuerySkill; '
     'skill = Autodoc2QuerySkill(); '
     'assert skill.name == "autodoc2_query", f"wrong name: {skill.name}"; '
     'assert len(skill.triggers) > 5, "too few triggers"; '
     'msg = "what files import neo4j"; '
     'score = skill.relevance(msg); '
     'assert score > 0, f"zero relevance for: {msg}"; '
     'print(f"autodoc2_query skill: OK — relevance={score:.2f} for test query")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check.returncode != 0:
    patch.errors.append(f"skill smoke test failed: {check.stderr.strip()}")
    patch.logger.log(f"  \u2717 skill test: {check.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check.stdout.strip()}")

# ── Verify auto-discovery by skill engine ────────────────────────────────────

check2 = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; '
     'sys.path.insert(0, "/opt/mythos/skills"); '
     'sys.path.insert(0, "/opt/mythos"); '
     'import importlib, pathlib; '
     'skill_path = pathlib.Path("/opt/mythos/skills/data/autodoc2_query.py"); '
     'assert skill_path.exists(), "skill file not found"; '
     'spec = importlib.util.spec_from_file_location("autodoc2_query", skill_path); '
     'mod = importlib.util.module_from_spec(spec); '
     'spec.loader.exec_module(mod); '
     'assert hasattr(mod, "Autodoc2QuerySkill"), "class not found in module"; '
     'print("skill auto-discovery: OK")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check2.returncode != 0:
    patch.errors.append(f"discovery test failed: {check2.stderr.strip()}")
    patch.logger.log(f"  \u2717 discovery test: {check2.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check2.stdout.strip()}")

patch.finish()
