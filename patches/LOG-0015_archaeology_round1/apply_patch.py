import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=15,
    description='archaeology round1 - fix false positives',
    patch_type='MINOR',
)
patch.begin()

# Deploy updated mission.yaml with live row counts and files_with_main query
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/mission.yaml',
    '/opt/mythos/mission/missions/system_archaeology/mission.yaml'
)

# Deploy updated dead_code.md prompt with expanded classification rules
patch.deploy_file(
    'opt/mythos/mission/missions/system_archaeology/prompts/dead_code.md',
    '/opt/mythos/mission/missions/system_archaeology/prompts/dead_code.md'
)

patch.finish()
