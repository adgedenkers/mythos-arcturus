import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=8,
    description='context_engine',
    patch_type='MINOR',
)
patch.begin()

# Deploy context engine module
patch.deploy_file(
    'opt/mythos/iris/core/src/context_engine.py',
    '/opt/mythos/iris/core/src/context_engine.py',
)

# Deploy access policy config
patch.deploy_file(
    'opt/mythos/config/context_access_policy.yaml',
    '/opt/mythos/config/context_access_policy.yaml',
)

# Deploy CLI tool
patch.deploy_file(
    'opt/mythos/bin/iris-context',
    '/opt/mythos/bin/iris-context',
)

# Make CLI executable
import os, stat
cli_path = '/opt/mythos/bin/iris-context'
st = os.stat(cli_path)
os.chmod(cli_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# Ensure PyYAML is available in venv (for access policy loading)
import subprocess
subprocess.run(
    ['/opt/mythos/.venv/bin/pip', 'install', '--quiet', 'pyyaml'],
    check=False,
)

# Validate Python files compile
import py_compile
py_compile.compile('/opt/mythos/iris/core/src/context_engine.py', doraise=True)
py_compile.compile('/opt/mythos/bin/iris-context', doraise=True)

patch.finish()
