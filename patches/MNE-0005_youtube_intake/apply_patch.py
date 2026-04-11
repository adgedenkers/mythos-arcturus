import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

import yaml
from pathlib import Path

patch_dir = Path(__file__).parent
with open(patch_dir / 'patch.yaml', 'r') as f:
    config = yaml.safe_load(f)

patch_number = config['number']
if patch_number == 'DRAFT':
    print("ERROR: Patch number is still DRAFT. Run mythos-diag streams and update patch.yaml")
    sys.exit(1)

patch = PatchBase(
    stream=config['stream'],
    number=int(patch_number),
    description=config['description'],
    patch_type=config.get('patch_type', 'MINOR'),
)
patch.begin()

# 1. Run SQL migration
patch.run_sql('opt/mythos/migrations/youtube_videos.sql')

# 2. Deploy skill
patch.deploy_file(
    'opt/mythos/skills/data/youtube_intake.py',
    '/opt/mythos/skills/data/youtube_intake.py'
)

# 3. Restart bot so skill engine picks it up
patch.restart_service('mythos-bot.service')

patch.finish()
