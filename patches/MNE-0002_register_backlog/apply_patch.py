#!/usr/bin/env python3
"""
MNE-0001a: Register /backlog command in mythos_bot.py
Hotfix — MNE-0001 deployed the handler but couldn't auto-patch the registration.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=2,
    description='Register /backlog command in bot',
    patch_type='PATCH',
)
patch.begin()

bot_path = '/opt/mythos/telegram_bot/mythos_bot.py'

with open(bot_path, 'r') as f:
    content = f.read()

# ── 1. Add import ─────────────────────────────────────────────────────────────
import_line = 'from telegram_bot.handlers.backlog_handler import backlog_command'
anchor_import = 'from telegram_bot.handlers.integrity_handler import handle_integrity'

if import_line not in content:
    content = content.replace(
        anchor_import,
        anchor_import + '\n' + import_line
    )
    print(f'  ✓ Added import for backlog_command')
else:
    print(f'  · Import already present')

# ── 2. Add command registration ───────────────────────────────────────────────
registration = '    application.add_handler(CommandHandler("backlog", backlog_command))'
anchor_reg = '    application.add_handler(CommandHandler("tasks", tasks_command))'

if 'backlog_command' not in content.split('add_handler')[0:] and '"backlog"' not in content:
    content = content.replace(
        anchor_reg,
        anchor_reg + '\n' + registration
    )
    print(f'  ✓ Registered /backlog command')
else:
    print(f'  · Registration already present')

with open(bot_path, 'w') as f:
    f.write(content)

# ── 3. Restart bot ────────────────────────────────────────────────────────────
patch.restart_service('mythos-bot.service')

patch.finish()
