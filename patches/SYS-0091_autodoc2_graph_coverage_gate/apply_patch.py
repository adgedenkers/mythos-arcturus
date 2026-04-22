import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=91,
    description='autodoc2 graph coverage gate — post-patch Neo4j verification',
    patch_type='MINOR',
)
patch.begin()

# Deploy the complete replacement post_install.py
# (full-file replacement is safer than str_replace for multi-anchor edits)
patch.deploy_file(
    'opt/mythos/patches/scripts/post_install.py',
    '/opt/mythos/patches/scripts/post_install.py',
)

# Smoke test: verify the new function is present and importable
check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; sys.path.insert(0, "/opt/mythos/patches/scripts"); '
     'import post_install; '
     'assert hasattr(post_install, "step_verify_graph_coverage"), "function missing"; '
     'import inspect; '
     'sig = inspect.signature(post_install.step_verify_graph_coverage); '
     'assert "files_deployed" in sig.parameters, "wrong signature"; '
     'src = inspect.getsource(post_install.run_pipeline); '
     'assert "step_verify_graph_coverage" in src, "not wired into run_pipeline"; '
     'assert "graph_coverage" in src, "result key missing"; '
     'print("post_install.py: step_verify_graph_coverage present and wired")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check.returncode != 0:
    patch.errors.append(f"smoke test failed: {check.stderr.strip()}")
    patch.logger.log(f"  \u2717 smoke test: {check.stderr.strip()}")
else:
    patch.logger.log(f"  \u2713 {check.stdout.strip()}")

patch.finish()
