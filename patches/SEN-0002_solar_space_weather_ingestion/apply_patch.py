import sys
import os
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=2,
    description='Solar & space weather ingestion service',
    patch_type='MAJOR',
)
patch.begin()

# Create observatory directories
os.makedirs('/opt/mythos/observatory/ingest', exist_ok=True)
os.makedirs('/opt/mythos/logs', exist_ok=True)

# Ensure __init__.py files exist for imports
for d in ['/opt/mythos/observatory', '/opt/mythos/observatory/ingest']:
    init = os.path.join(d, '__init__.py')
    if not os.path.exists(init):
        with open(init, 'w') as f:
            f.write('')

# Deploy files
patch.deploy_file(
    'opt/mythos/observatory/ingest/solar_ingest.py',
    '/opt/mythos/observatory/ingest/solar_ingest.py'
)
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/solar_handler.py',
    '/opt/mythos/telegram_bot/handlers/solar_handler.py'
)
patch.deploy_file(
    'opt/mythos/services/mythos-solar-ingest.service',
    '/opt/mythos/services/mythos-solar-ingest.service'
)

# Run SQL migration
patch.run_sql('opt/mythos/migrations/sen_0002_solar_space_weather.sql')

# Install and start service
subprocess.run([
    'sudo', 'cp',
    '/opt/mythos/services/mythos-solar-ingest.service',
    '/etc/systemd/system/mythos-solar-ingest.service'
], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-solar-ingest.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'mythos-solar-ingest.service'], check=True)

# Register handler — add import to handlers/__init__.py
init_path = '/opt/mythos/telegram_bot/handlers/__init__.py'
with open(init_path, 'r') as f:
    content = f.read()

if 'solar_handler' not in content:
    # Find the registration function and add our import + registration
    if 'def register_all' in content:
        old = 'def register_all(app):'
        new = ('def register_all(app):\n'
               '    from telegram_bot.handlers import solar_handler\n'
               '    solar_handler.register(app)')
        # Actually, safer to append at the end of the function
        # Find last line of register_all and append before it
        pass

    # Simpler: just append registration call
    # The handler self-registers when imported
    marker = '# === END HANDLER REGISTRATION ==='
    if marker in content:
        content = content.replace(
            marker,
            '    from telegram_bot.handlers import solar_handler\n'
            '    solar_handler.register(app)\n'
            f'    {marker}'
        )
    else:
        # Fallback: append to the function body
        # Look for the last register line and add after it
        lines = content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if '.register(app)' in line or 'add_handler' in line:
                insert_idx = i
        if insert_idx is not None:
            indent = '    '
            lines.insert(insert_idx + 1,
                f'{indent}from telegram_bot.handlers import solar_handler')
            lines.insert(insert_idx + 2,
                f'{indent}solar_handler.register(app)')
            content = '\n'.join(lines)

    with open(init_path, 'w') as f:
        f.write(content)

# Restart bot to pick up new handler
patch.restart_service('mythos-bot.service')

patch.finish()
print("✅ SEN-0002: Solar & space weather ingestion deployed")
print("   Service: mythos-solar-ingest.service (polling every 5 min)")
print("   Command: /solar — current conditions")
print("   Tables: solar_wind_readings, geomagnetic_indices, solar_flares,")
print("           cme_events, radiation_flux, solar_wind_events")
