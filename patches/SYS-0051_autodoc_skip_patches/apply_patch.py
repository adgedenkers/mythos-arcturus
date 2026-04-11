import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=51,
    description='autodoc_skip_patches_and_archive',
    patch_type='PATCH',
)

patch.begin()

patch.deploy_file(
    'opt/mythos/tools/autodoc.py',
    '/opt/mythos/tools/autodoc.py'
)

import os
os.chmod('/opt/mythos/tools/autodoc.py', 0o755)

patch.finish()
