import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=4,
    description='SDIP sensitivity scanner - regex and LLM classification',
    patch_type='MINOR',
)
patch.begin()

# Deploy scanner
patch.deploy_file('opt/mythos/sdip/sdip_sensitivity.py', '/opt/mythos/sdip/sdip_sensitivity.py')

target_path = '/opt/mythos/sdip/sdip_sensitivity.py'
if os.path.exists(target_path):
    os.chmod(target_path, 0o755)

# Create CLI symlink
link_path = '/opt/mythos/bin/sdip-scan'
if os.path.exists(target_path):
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(target_path, link_path)
    print(f"  Symlinked {link_path} → {target_path}")

patch.finish()
