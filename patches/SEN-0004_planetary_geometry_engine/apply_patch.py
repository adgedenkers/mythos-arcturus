import sys
import os
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=4,
    description='Planetary geometry engine — positions, aspects, alignments, forcing vectors',
    patch_type='MAJOR',
)
patch.begin()

# Ensure observatory directory structure
os.makedirs('/opt/mythos/observatory/geometry', exist_ok=True)
for d in ['/opt/mythos/observatory', '/opt/mythos/observatory/geometry']:
    init = os.path.join(d, '__init__.py')
    if not os.path.exists(init):
        with open(init, 'w') as f:
            f.write('')

# Verify pyswisseph is installed
try:
    import swisseph
    print(f"  ✓ pyswisseph {swisseph.version} available")
except ImportError:
    print("  ⚠ Installing pyswisseph...")
    subprocess.run([
        '/opt/mythos/.venv/bin/pip', 'install', 'pyswisseph'
    ], check=True)

# Deploy files
patch.deploy_file(
    'opt/mythos/observatory/geometry/planetary_engine.py',
    '/opt/mythos/observatory/geometry/planetary_engine.py'
)
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/planets_handler.py',
    '/opt/mythos/telegram_bot/handlers/planets_handler.py'
)
patch.deploy_file(
    'opt/mythos/services/mythos-planetary-engine.service',
    '/opt/mythos/services/mythos-planetary-engine.service'
)

# Run SQL migration
patch.run_sql('opt/mythos/migrations/sen_0004_planetary_geometry.sql')

# Install and start service
subprocess.run([
    'sudo', 'cp',
    '/opt/mythos/services/mythos-planetary-engine.service',
    '/etc/systemd/system/mythos-planetary-engine.service'
], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-planetary-engine.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'mythos-planetary-engine.service'], check=True)

# Register handler
init_path = '/opt/mythos/telegram_bot/handlers/__init__.py'
with open(init_path, 'r') as f:
    content = f.read()

if 'planets_handler' not in content:
    lines = content.split('\n')
    insert_idx = None
    for i, line in enumerate(lines):
        if '.register(app)' in line or 'add_handler' in line:
            insert_idx = i
    if insert_idx is not None:
        indent = '    '
        lines.insert(insert_idx + 1,
            f'{indent}from telegram_bot.handlers import planets_handler')
        lines.insert(insert_idx + 2,
            f'{indent}planets_handler.register(app)')
        content = '\n'.join(lines)

    with open(init_path, 'w') as f:
        f.write(content)

patch.restart_service('mythos-bot.service')

patch.finish()
print("✅ SEN-0004: Planetary Geometry Engine deployed")
print("   Service: mythos-planetary-engine.service (computing hourly)")
print("   Command: /planets — current planetary positions & geometry")
print("   Tables: planetary_positions, planetary_aspects,")
print("           planetary_alignments, planetary_forcing")
print("   Features: Swiss Ephemeris positions, Gaussian aspect strength,")
print("             gravitational forcing vectors, alignment detection,")
print("             7-day backfill on first run")
