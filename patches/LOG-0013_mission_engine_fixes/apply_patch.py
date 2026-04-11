import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=13,
    description='Mission engine - Claude to Iris delegation pipeline',
    patch_type='MAJOR',
)
patch.begin()

# Deploy mission engine directory
patch.deploy_file('opt/mythos/mission/mission_runner.py', '/opt/mythos/mission/mission_runner.py')
patch.deploy_file('opt/mythos/mission/graph_bridge.py', '/opt/mythos/mission/graph_bridge.py')
patch.deploy_file('opt/mythos/mission/MISSION_SPEC.md', '/opt/mythos/mission/MISSION_SPEC.md')

# Deploy example templates
patch.deploy_file('opt/mythos/mission/templates/audit_handler.yaml', '/opt/mythos/mission/templates/audit_handler.yaml')
patch.deploy_file('opt/mythos/mission/templates/graph_snapshot.yaml', '/opt/mythos/mission/templates/graph_snapshot.yaml')

# Create logs directory
import os
os.makedirs('/opt/mythos/mission/logs', exist_ok=True)
os.makedirs('/tmp/mythos-mission', exist_ok=True)

# Make executables
os.chmod('/opt/mythos/mission/mission_runner.py', 0o755)
os.chmod('/opt/mythos/mission/graph_bridge.py', 0o755)

# Create CLI symlinks in /opt/mythos/bin/
for target, source in [
    ('/opt/mythos/bin/mythos-mission', '/opt/mythos/mission/mission_runner.py'),
    ('/opt/mythos/bin/graph-bridge', '/opt/mythos/mission/graph_bridge.py'),
]:
    if os.path.islink(target) or os.path.exists(target):
        os.remove(target)
    os.symlink(source, target)
    print(f"  Symlinked {target} -> {source}")

patch.finish()
