import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=7,
    description='SDIP console - Textual TUI for browsing documents and sensitivity',
    patch_type='MINOR',
)
patch.begin()

# Deploy console
patch.deploy_file('opt/mythos/sdip/sdip_console.py', '/opt/mythos/sdip/sdip_console.py')

target_path = '/opt/mythos/sdip/sdip_console.py'
if os.path.exists(target_path):
    os.chmod(target_path, 0o755)

    link_path = '/opt/mythos/bin/sdip-console'
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(target_path, link_path)
    print(f"  Symlinked {link_path} → {target_path}")

patch.finish()
