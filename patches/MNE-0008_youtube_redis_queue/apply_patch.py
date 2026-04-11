import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=8,
    description='YouTube Redis queue — priority-based ingestion with full channel backfill via yt-dlp',
    patch_type='MAJOR',
)
patch.begin()

# ── 1. Deploy queue consumer ──
print("[1/5] Deploying queue consumer...")
patch.deploy_file(
    'opt/mythos/workers/youtube_queue_consumer.py',
    '/opt/mythos/workers/youtube_queue_consumer.py'
)
print("  ✓ youtube_queue_consumer.py deployed")

# ── 2. Update channel monitor (v2 — queue-based) ──
print("[2/5] Updating channel monitor to v2 (queue-based)...")
patch.deploy_file(
    'opt/mythos/workers/youtube_channel_monitor.py',
    '/opt/mythos/workers/youtube_channel_monitor.py'
)
print("  ✓ youtube_channel_monitor.py updated to v2")

# ── 3. Update channel skill (v2 — queue status) ──
print("[3/5] Updating channel skill with queue status...")
patch.deploy_file(
    'opt/mythos/skills/data/youtube_channel.py',
    '/opt/mythos/skills/data/youtube_channel.py'
)
print("  ✓ youtube_channel.py updated to v2")

# ── 4. Install queue consumer service ──
print("[4/5] Installing queue consumer service...")
service_src = os.path.join(os.path.dirname(__file__), 'mythos-youtube-queue.service')
service_dst = '/etc/systemd/system/mythos-youtube-queue.service'
subprocess.run(['sudo', 'cp', service_src, service_dst], check=True)
subprocess.run(['sudo', 'chmod', '644', service_dst], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-youtube-queue.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'mythos-youtube-queue.service'], check=True)
print("  ✓ mythos-youtube-queue.service installed and started")

# ── 5. Restart monitor and API ──
print("[5/5] Restarting monitor and API...")
subprocess.run(['sudo', 'systemctl', 'restart', 'mythos-youtube-monitor.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'restart', 'mythos-api.service'], check=True)

import time
time.sleep(2)

for svc in ['mythos-youtube-queue', 'mythos-youtube-monitor', 'mythos-api']:
    result = subprocess.run(['sudo', 'systemctl', 'is-active', f'{svc}.service'],
                           capture_output=True, text=True)
    status = '✓' if 'active' in result.stdout else '⚠'
    print(f"  {status} {svc}.service")

print()
print("=" * 60)
print("  MNE-0008 Complete — YouTube Redis Queue")
print("=" * 60)
print()
print("  Architecture:")
print("    Channel Monitor → finds new videos → pushes to Redis queue")
print("    Queue Consumer  → pulls from queue → ingests one at a time")
print("    YouTube Skill   → manages subs + reports queue status")
print()
print("  Priority levels:")
print("    HIGH (0)   — Manual URL from Iris (jumps the line)")
print("    NORMAL (1) — New video from RSS (processed promptly)")
print("    LOW (2)    — Backfill from yt-dlp (processed leisurely)")
print()
print("  Delays between ingestions:")
print("    HIGH: 5s  |  NORMAL: 30s  |  LOW: 60s")
print()
print("  New commands for Iris:")
print('    "how is the youtube queue?"')
print('    "what videos are pending?"')
print('    "youtube queue status"')
print()
print("  When you subscribe a new channel, yt-dlp scrapes ALL video IDs")
print("  and queues them at LOW priority. They'll trickle in over hours.")
print()

patch.finish()
