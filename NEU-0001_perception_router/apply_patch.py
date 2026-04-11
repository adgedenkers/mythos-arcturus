import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')

from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=1,
    description='global perception router',
    patch_type='FOUNDATION',
)

patch.begin()

patch.deploy_file(
    'opt/mythos/neuro/perception_router.py',
    '/opt/mythos/neuro/perception_router.py'
)

patch.deploy_file(
    'opt/mythos/neuro/perception_event_types.py',
    '/opt/mythos/neuro/perception_event_types.py'
)

patch.finish()
