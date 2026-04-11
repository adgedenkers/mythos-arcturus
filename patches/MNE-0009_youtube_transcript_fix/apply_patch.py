import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=9,
    description='youtube transcript fix',
    patch_type='MINOR',
)
patch.begin()

patch.deploy_file(
    'opt/mythos/skills/data/youtube_intake.py',
    '/opt/mythos/skills/data/youtube_intake.py',
)
patch.deploy_file(
    'opt/mythos/workers/youtube_queue_consumer.py',
    '/opt/mythos/workers/youtube_queue_consumer.py',
)
patch.deploy_file(
    'opt/mythos/workers/youtube_channel_monitor.py',
    '/opt/mythos/workers/youtube_channel_monitor.py',
)

# Restart the queue consumer service if it exists standalone, otherwise the bot
import subprocess
result = subprocess.run(
    ['systemctl', 'is-active', '--quiet', 'mythos-youtube-consumer.service'],
    capture_output=True
)
if result.returncode == 0:
    patch.restart_service('mythos-youtube-consumer.service')
else:
    patch.restart_service('mythos-bot.service')

patch.finish()
