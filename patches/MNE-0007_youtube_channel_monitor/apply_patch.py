import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=7,
    description='YouTube channel monitor — auto-ingest transcripts from subscribed channels',
    patch_type='MAJOR',
)
patch.begin()

# ── 1. Run SQL migration ──
print("[1/5] Creating youtube_channel_subscriptions table...")
patch.run_sql('opt/mythos/migrations/mne_0007_youtube_channels.sql')
print("  ✓ Table created")

# ── 2. Deploy worker ──
print("[2/5] Deploying channel monitor worker...")
patch.deploy_file(
    'opt/mythos/workers/youtube_channel_monitor.py',
    '/opt/mythos/workers/youtube_channel_monitor.py'
)
print("  ✓ youtube_channel_monitor.py deployed")

# ── 3. Deploy skill ──
print("[3/5] Deploying channel subscription skill...")
patch.deploy_file(
    'opt/mythos/skills/data/youtube_channel.py',
    '/opt/mythos/skills/data/youtube_channel.py'
)
print("  ✓ youtube_channel.py skill deployed")

# ── 4. Install systemd service ──
print("[4/5] Installing systemd service...")
service_src = os.path.join(os.path.dirname(__file__), 'mythos-youtube-monitor.service')
service_dst = '/etc/systemd/system/mythos-youtube-monitor.service'
subprocess.run(['sudo', 'cp', service_src, service_dst], check=True)
subprocess.run(['sudo', 'chmod', '644', service_dst], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-youtube-monitor.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'mythos-youtube-monitor.service'], check=True)
print("  ✓ mythos-youtube-monitor.service installed and started")

# ── 5. Restart API to pick up new skill ──
print("[5/5] Restarting API service...")
subprocess.run(['sudo', 'systemctl', 'restart', 'mythos-api.service'], check=True)

import time
time.sleep(2)

result = subprocess.run(['sudo', 'systemctl', 'is-active', 'mythos-youtube-monitor.service'],
                       capture_output=True, text=True)
if 'active' in result.stdout:
    print("  ✓ Monitor service running")
else:
    print("  ⚠ Monitor may not be running")

result = subprocess.run(['sudo', 'systemctl', 'is-active', 'mythos-api.service'],
                       capture_output=True, text=True)
if 'active' in result.stdout:
    print("  ✓ API service running")
else:
    print("  ⚠ API may not be running")

print()
print("=" * 60)
print("  MNE-0007 Complete — YouTube Channel Monitor")
print("=" * 60)
print()
print("  Components:")
print("    • youtube_channel_subscriptions table (Postgres)")
print("    • youtube_channel_monitor.py worker (polls RSS feeds)")
print("    • youtube_channel.py skill (natural language management)")
print("    • mythos-youtube-monitor.service (systemd)")
print()
print("  How to use (tell Iris):")
print('    "track @stefanburns on youtube"')
print('    "follow Pam Gregory on youtube"')
print('    "who am I tracking on youtube?"')
print('    "stop tracking TEDx Talks"')
print()
print("  The monitor checks every 2 hours (configurable per channel).")
print("  New videos are auto-ingested and you get a Telegram notification.")
print()

patch.finish()
