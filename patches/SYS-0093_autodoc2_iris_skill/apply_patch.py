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

patch.deploy_file(
    'opt/mythos/skills/data/autodoc2_query.py',
    '/opt/mythos/skills/data/autodoc2_query.py',
)

patch.py_compile_check(
    '/opt/mythos/skills/data/autodoc2_query.py',
    'autodoc2_query.py',
)

# Verified pattern: cwd=/opt/mythos, /opt/mythos/skills on path, import as data.autodoc2_query
check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; '
     'sys.path.insert(0, "/opt/mythos/skills"); '
     'sys.path.insert(0, "/opt/mythos"); '
     'from data.autodoc2_query import Autodoc2QuerySkill; '
     'skill = Autodoc2QuerySkill(); '
     'assert skill.name == "autodoc2_query"; '
     'score = skill.relevance("what files import neo4j"); '
     'assert score > 0; '
     'print(f"autodoc2_query: OK, relevance={score:.2f}")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check.returncode != 0:
    patch.errors.append(f"skill test failed: {check.stderr.strip()}")
    patch.logger.log(f"  \u2717 skill: {check.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check.stdout.strip()}")

check2 = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys, importlib.util, pathlib; '
     'sys.path.insert(0, "/opt/mythos/skills"); '
     'sys.path.insert(0, "/opt/mythos"); '
     'p = pathlib.Path("/opt/mythos/skills/data/autodoc2_query.py"); '
     'assert p.exists(); '
     'spec = importlib.util.spec_from_file_location("autodoc2_query", p); '
     'mod = importlib.util.module_from_spec(spec); '
     'spec.loader.exec_module(mod); '
     'assert hasattr(mod, "Autodoc2QuerySkill"); '
     'print("skill discovery: OK")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check2.returncode != 0:
    patch.errors.append(f"discovery failed: {check2.stderr.strip()}")
    patch.logger.log(f"  \u2717 discovery: {check2.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check2.stdout.strip()}")

patch.finish()
