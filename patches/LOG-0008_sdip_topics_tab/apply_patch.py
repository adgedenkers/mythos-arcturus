import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=8,
    description='SDIP console topics tab - Neo4j topic browser with drilldown',
    patch_type='PATCH',
)
patch.begin()

patch.deploy_file('opt/mythos/sdip/sdip_console.py', '/opt/mythos/sdip/sdip_console.py')

target_path = '/opt/mythos/sdip/sdip_console.py'
if os.path.exists(target_path):
    os.chmod(target_path, 0o755)

patch.finish()
