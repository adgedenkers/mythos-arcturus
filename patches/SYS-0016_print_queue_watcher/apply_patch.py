import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=16,
    description='print queue watcher',
    patch_type='MINOR',
)
patch.begin()

# Create watch directories
home = os.path.expanduser('~adge')
watch_dir = os.path.join(home, 'print-queue')
done_dir = os.path.join(watch_dir, 'done')
os.makedirs(watch_dir, exist_ok=True)
os.makedirs(done_dir, exist_ok=True)
print(f"  ✓ Created {watch_dir} and {done_dir}")

# Ensure inotify-tools is installed
result = subprocess.run(['dpkg', '-l', 'inotify-tools'], capture_output=True, text=True)
if 'ii' not in result.stdout:
    print("  → Installing inotify-tools...")
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'inotify-tools'], check=True)
    print("  ✓ inotify-tools installed")
else:
    print("  ✓ inotify-tools already installed")

# Deploy the watcher script
patch.deploy_file('opt/mythos/bin/print-watcher.sh', '/opt/mythos/bin/print-watcher.sh')
os.chmod('/opt/mythos/bin/print-watcher.sh', 0o755)
print("  ✓ Deployed print-watcher.sh")

# Deploy service file to /opt/mythos/services/ first, then sudo copy to systemd
patch.deploy_file(
    'opt/mythos/services/mythos-print-watcher.service',
    '/opt/mythos/services/mythos-print-watcher.service'
)
svc_src = '/opt/mythos/services/mythos-print-watcher.service'
svc_dest = '/etc/systemd/system/mythos-print-watcher.service'
if os.path.exists(svc_src):
    subprocess.run(['sudo', 'cp', svc_src, svc_dest], check=True)
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-print-watcher.service'], check=True)
    patch.restart_service('mythos-print-watcher.service')
    print("  ✓ Service deployed, enabled, and started")
else:
    print("  ✓ [dry-run] Skipped systemd deployment")

patch.finish()
