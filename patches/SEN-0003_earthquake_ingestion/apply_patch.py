import sys
import os
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=3,
    description='Earthquake & seismic monitoring ingestion',
    patch_type='MAJOR',
)
patch.begin()

# Ensure observatory directory structure
os.makedirs('/opt/mythos/observatory/ingest', exist_ok=True)
for d in ['/opt/mythos/observatory', '/opt/mythos/observatory/ingest']:
    init = os.path.join(d, '__init__.py')
    if not os.path.exists(init):
        with open(init, 'w') as f:
            f.write('')

# Deploy files
patch.deploy_file(
    'opt/mythos/observatory/ingest/seismic_ingest.py',
    '/opt/mythos/observatory/ingest/seismic_ingest.py'
)
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/quakes_handler.py',
    '/opt/mythos/telegram_bot/handlers/quakes_handler.py'
)
patch.deploy_file(
    'opt/mythos/services/mythos-seismic-ingest.service',
    '/opt/mythos/services/mythos-seismic-ingest.service'
)

# Run SQL migration
patch.run_sql('opt/mythos/migrations/sen_0003_earthquake_tables.sql')

# Install and start service
subprocess.run([
    'sudo', 'cp',
    '/opt/mythos/services/mythos-seismic-ingest.service',
    '/etc/systemd/system/mythos-seismic-ingest.service'
], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-seismic-ingest.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'mythos-seismic-ingest.service'], check=True)

# Register handler
init_path = '/opt/mythos/telegram_bot/handlers/__init__.py'
with open(init_path, 'r') as f:
    content = f.read()

if 'quakes_handler' not in content:
    lines = content.split('\n')
    insert_idx = None
    for i, line in enumerate(lines):
        if '.register(app)' in line or 'add_handler' in line:
            insert_idx = i
    if insert_idx is not None:
        indent = '    '
        lines.insert(insert_idx + 1,
            f'{indent}from telegram_bot.handlers import quakes_handler')
        lines.insert(insert_idx + 2,
            f'{indent}quakes_handler.register(app)')
        content = '\n'.join(lines)

    with open(init_path, 'w') as f:
        f.write(content)

patch.restart_service('mythos-bot.service')

patch.finish()
print("✅ SEN-0003: Earthquake ingestion deployed")
print("   Service: mythos-seismic-ingest.service (polling every 10 min)")
print("   Command: /quakes — seismic activity summary")
print("   Tables: earthquakes, seismic_clusters, antipodal_pairs")
print("   Features: cluster detection, antipodal pairing, auto-antipode trigger")
