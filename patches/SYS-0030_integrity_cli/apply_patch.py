import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=30,
    description='integrity CLI wrapper',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file('opt/mythos/bin/mythos-integrity', '/opt/mythos/bin/mythos-integrity')

import os
os.chmod('/opt/mythos/bin/mythos-integrity', 0o755)

patch.finish()
