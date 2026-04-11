import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=7,
    description='Trigger engine — standalone autonomic scheduler service',
    patch_type='MAJOR',
)
patch.begin()

# Deploy trigger engine
patch.deploy_file(
    'opt/mythos/iris/core/src/trigger_engine.py',
    '/opt/mythos/iris/core/src/trigger_engine.py'
)

# Deploy standalone runner
patch.deploy_file(
    'opt/mythos/iris/core/src/trigger_runner.py',
    '/opt/mythos/iris/core/src/trigger_runner.py'
)

# Deploy systemd service unit
patch.deploy_file(
    'opt/mythos/services/mythos-trigger.service',
    '/opt/mythos/services/mythos-trigger.service'
)

# Symlink service unit into systemd
try:
    subprocess.run([
        'sudo', 'ln', '-sf',
        '/opt/mythos/services/mythos-trigger.service',
        '/etc/systemd/system/mythos-trigger.service',
    ], check=True, capture_output=True, text=True)
    patch.logger.log("  ✓ symlinked mythos-trigger.service")
except Exception as e:
    patch.errors.append(f"symlink service: {e}")
    patch.logger.log(f"  ✗ symlink service: {e}")

# Reload systemd
try:
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'],
                   check=True, capture_output=True, text=True)
    patch.logger.log("  ✓ systemctl daemon-reload")
except Exception as e:
    patch.errors.append(f"daemon-reload: {e}")
    patch.logger.log(f"  ✗ daemon-reload: {e}")

# Enable the service
try:
    subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-trigger.service'],
                   check=True, capture_output=True, text=True)
    patch.logger.log("  ✓ enabled mythos-trigger.service")
except Exception as e:
    patch.errors.append(f"enable service: {e}")
    patch.logger.log(f"  ✗ enable service: {e}")

# Start the service
patch.restart_service('mythos-trigger.service')

# Verify it's running
import time
time.sleep(2)
try:
    result = subprocess.run(
        ['systemctl', 'is-active', 'mythos-trigger.service'],
        capture_output=True, text=True,
    )
    if result.stdout.strip() == 'active':
        patch.logger.log("  ✓ mythos-trigger.service is active")
        patch.validations.append("service running")
    else:
        patch.errors.append(f"service not active: {result.stdout.strip()}")
        patch.logger.log(f"  ⚠ service status: {result.stdout.strip()}")
        # Show journal for debugging
        journal = subprocess.run(
            ['journalctl', '-u', 'mythos-trigger.service', '-n', '15', '--no-pager'],
            capture_output=True, text=True,
        )
        patch.logger.log(f"  Journal:\n{journal.stdout}")
except Exception as e:
    patch.errors.append(f"verify service: {e}")

patch.finish()
