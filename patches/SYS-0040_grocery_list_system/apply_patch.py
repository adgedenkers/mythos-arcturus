import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=40,
    description='grocery_telegram_skill',
    patch_type='MINOR',
)
patch.begin()

# Deploy the skill
patch.deploy_file('opt/mythos/skills/data/grocery_skill.py', '/opt/mythos/skills/data/grocery_skill.py')

# Drop the orphaned grocery_* tables from the first attempt
patch.run_sql('opt/mythos/migrations/drop_grocery_tables.sql')

# Restart bot so skill engine picks it up
patch.restart_service('mythos-bot.service')

patch.finish()
