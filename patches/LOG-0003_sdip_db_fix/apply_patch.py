import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=3,
    description='SDIP DB connection fix - Unix socket matching Mythos convention',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file('opt/mythos/sdip/config.py', '/opt/mythos/sdip/config.py')
patch.deploy_file('opt/mythos/sdip/sdip_ingest.py', '/opt/mythos/sdip/sdip_ingest.py')

os.chmod('/opt/mythos/sdip/sdip_ingest.py', 0o755)

patch.finish()
