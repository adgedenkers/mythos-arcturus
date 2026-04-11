import sys
import os
import subprocess
import shutil
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=17,
    description='pdf open wrapper for print queue',
    patch_type='MINOR',
)
patch.begin()

# Deploy the wrapper script
patch.deploy_file('opt/mythos/bin/pdf-open-wrapper.sh', '/opt/mythos/bin/pdf-open-wrapper.sh')
os.chmod('/opt/mythos/bin/pdf-open-wrapper.sh', 0o755)
print("  ✓ Deployed pdf-open-wrapper.sh")

# Deploy the .desktop file to user's local applications
desktop_src = os.path.join(patch.patch_dir, 'opt/mythos/bin/pdf-smart-open.desktop')
desktop_dest_dir = os.path.expanduser('~adge/.local/share/applications')
desktop_dest = os.path.join(desktop_dest_dir, 'pdf-smart-open.desktop')
os.makedirs(desktop_dest_dir, exist_ok=True)

if os.path.exists(desktop_src):
    shutil.copy2(desktop_src, desktop_dest)
    print(f"  ✓ Installed desktop file to {desktop_dest}")

    # Set as default PDF handler
    subprocess.run([
        'xdg-mime', 'default', 'pdf-smart-open.desktop', 'application/pdf'
    ], check=True)
    print("  ✓ Set pdf-smart-open as default PDF handler")
else:
    print("  ✓ [dry-run] Skipped desktop file install")

# Also keep a copy in /opt/mythos/bin/ for reference
patch.deploy_file('opt/mythos/bin/pdf-smart-open.desktop', '/opt/mythos/bin/pdf-smart-open.desktop')
print("  ✓ Stored desktop file copy in /opt/mythos/bin/")

patch.finish()
