#!/usr/bin/env python3
"""
MNE-0015: YouTube Queue Fix

Fixes:
  1. Pop-before-check bug — consumer now peeks before popping
  2. No throttle — 5-minute default between video processing
  3. Schema mismatch — INSERT now matches actual youtube_videos table
  4. Missing functions — subscribe_channel, unsubscribe_channel,
     list_subscriptions, get_queue_status now exist
  5. Permanent failures persist — monitor won't re-queue them

Also clears stale queue state (empty queue with inflated counters).
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=15,
    description='youtube_queue_fix',
    patch_type='MINOR',
)
patch.begin()

# Deploy fixed files
patch.deploy_file(
    'opt/mythos/workers/youtube_queue_consumer.py',
    '/opt/mythos/workers/youtube_queue_consumer.py',
)
patch.deploy_file(
    'opt/mythos/workers/youtube_channel_monitor.py',
    '/opt/mythos/workers/youtube_channel_monitor.py',
)

# Clear stale queue status counters (queue is empty, counters are misleading)
import subprocess
subprocess.run([
    'redis-cli', 'DEL',
    'mythos:youtube:queue:status',
], check=False)
print('  ✓ Cleared stale queue status counters')

# Restart both YouTube services
patch.restart_service('mythos-youtube-queue.service')
patch.restart_service('mythos-youtube-monitor.service')

patch.finish()

print()
print('MNE-0015 installed successfully.')
print()
print('What changed:')
print('  • Consumer now peeks before popping (no more lost videos)')
print('  • 5-minute throttle between videos (set YT_PROCESS_INTERVAL to change)')
print('  • INSERT matches actual youtube_videos schema')
print('  • subscribe_channel/unsubscribe/list/status functions now exist')
print('  • Permanently failed videos stay permanently failed')
print('  • Stale queue counters cleared')
print()
print('To re-subscribe channels:')
print('  Tell Iris: "track @channelhandle on YouTube"')
print('  Or: "track https://www.youtube.com/@channelhandle"')
print()
print('To check queue: "youtube queue status"')
