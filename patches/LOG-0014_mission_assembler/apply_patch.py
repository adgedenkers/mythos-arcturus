import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=14,
    description='Mission assembler + modular system archaeology v2',
    patch_type='MINOR',
)
patch.begin()

# Deploy mission assembler
patch.deploy_file('opt/mythos/mission/mission_assembler.py', '/opt/mythos/mission/mission_assembler.py')

# Deploy modular archaeology mission
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/mission.yaml',
    '/opt/mythos/mission/missions/system_archaeology/mission.yaml',
)
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/prompts/dead_code.md',
    '/opt/mythos/mission/missions/system_archaeology/prompts/dead_code.md',
)
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/prompts/stress.md',
    '/opt/mythos/mission/missions/system_archaeology/prompts/stress.md',
)
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/prompts/synthesis.md',
    '/opt/mythos/mission/missions/system_archaeology/prompts/synthesis.md',
)

# Make assembler executable and symlink
import os
os.chmod('/opt/mythos/mission/mission_assembler.py', 0o755)

symlink_target = '/opt/mythos/bin/mythos-mission-assemble'
symlink_source = '/opt/mythos/mission/mission_assembler.py'
if os.path.islink(symlink_target) or os.path.exists(symlink_target):
    os.remove(symlink_target)
os.symlink(symlink_source, symlink_target)
print(f"  Symlinked {symlink_target} -> {symlink_source}")

# Ensure missions directory exists
os.makedirs('/opt/mythos/mission/missions', exist_ok=True)

patch.finish()
