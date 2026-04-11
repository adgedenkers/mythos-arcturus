import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=5,
    description='SDIP graph builder - Neo4j document/topic/system/chunk nodes',
    patch_type='MINOR',
)
patch.begin()

# Deploy graph builder
patch.deploy_file('opt/mythos/sdip/sdip_graph.py', '/opt/mythos/sdip/sdip_graph.py')

target_path = '/opt/mythos/sdip/sdip_graph.py'
if os.path.exists(target_path):
    os.chmod(target_path, 0o755)

    link_path = '/opt/mythos/bin/sdip-graph'
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(target_path, link_path)
    print(f"  Symlinked {link_path} → {target_path}")

patch.finish()
