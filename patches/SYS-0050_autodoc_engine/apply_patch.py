import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
import os
import subprocess

patch = PatchBase(
    stream='SYS',
    number=50,
    description='autodoc_engine',
    patch_type='MINOR',
)

patch.begin()

# Deploy the autodoc engine
patch.deploy_file(
    'opt/mythos/tools/autodoc.py',
    '/opt/mythos/tools/autodoc.py'
)

# Make executable
os.chmod('/opt/mythos/tools/autodoc.py', 0o755)

# Create symlink in /opt/mythos/bin/
symlink_path = '/opt/mythos/bin/autodoc'
target_path = '/opt/mythos/tools/autodoc.py'
if os.path.exists(symlink_path) or os.path.islink(symlink_path):
    os.remove(symlink_path)
os.symlink(target_path, symlink_path)

# Ensure neo4j python driver is installed
subprocess.run(
    ['/opt/mythos/.venv/bin/pip', 'install', 'neo4j', '--quiet'],
    check=True
)

# Create output directories
os.makedirs('/opt/mythos/docs/autodoc', exist_ok=True)
os.makedirs('/opt/mythos/docs/autodoc/modules', exist_ok=True)
os.makedirs('/opt/mythos/docs/autodoc/streams', exist_ok=True)
os.makedirs('/opt/mythos/docs/autodoc/files', exist_ok=True)

patch.finish()
