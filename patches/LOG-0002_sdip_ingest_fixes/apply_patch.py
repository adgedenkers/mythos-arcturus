import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=2,
    description='SDIP ingest fixes - skip .obsidian, remove phantom manifest import',
    patch_type='PATCH',
)
patch.begin()

# Deploy updated files
patch.deploy_file('opt/mythos/sdip/config.py', '/opt/mythos/sdip/config.py')
patch.deploy_file('opt/mythos/sdip/sdip_ingest.py', '/opt/mythos/sdip/sdip_ingest.py')

import os
os.chmod('/opt/mythos/sdip/sdip_ingest.py', 0o755)

patch.finish()
