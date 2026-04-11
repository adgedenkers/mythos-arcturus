#!/usr/bin/env python3
"""SYS-0052: Watchlist — streaming watchlist with deep links."""

import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=52,
    description='watchlist with streaming deep links',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy files ────────────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/migrations/sys_0052_watchlist.sql',
    '/opt/mythos/migrations/sys_0052_watchlist.sql'
)
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/watchlist_handler.py',
    '/opt/mythos/telegram_bot/handlers/watchlist_handler.py'
)

# ── Run migration ───────────────────────────────────────────────────────
patch.run_sql('opt/mythos/migrations/sys_0052_watchlist.sql')

# ── Wire handler into mythos_bot.py ─────────────────────────────────────
bot_file = '/opt/mythos/telegram_bot/mythos_bot.py'

with open(bot_file, 'r') as f:
    content = f.read()

# 1. Add import — find a nearby handler import as anchor
import_anchor = 'from telegram_bot.handlers.task_handler import'
if import_anchor not in content:
    # Try alternative import style
    import_anchor = 'from handlers.task_handler import'

import_line = '\nfrom telegram_bot.handlers.watchlist_handler import build_watch_handler'
alt_import_line = '\nfrom handlers.watchlist_handler import build_watch_handler'

if 'watchlist_handler' not in content:
    if import_anchor in content:
        # Find end of this import line
        idx = content.index(import_anchor)
        line_end = content.index('\n', idx)
        # Check which style the anchor uses
        if 'from telegram_bot.handlers.task_handler' in import_anchor:
            insert_line = import_line
        else:
            insert_line = alt_import_line
        content = content[:line_end] + content[line_end] + insert_line + content[line_end+1:]
        print(f"  ✓ Added import for watchlist_handler")
    else:
        print(f"  ⚠ Could not find import anchor '{import_anchor}' — manual import needed")

# 2. Add handler registration — ConversationHandler, not CommandHandler
#    Find a nearby add_handler call as anchor
reg_anchor = 'application.add_handler(CommandHandler("task"'
if reg_anchor not in content:
    reg_anchor = 'application.add_handler(CommandHandler("tasks"'

reg_line = '\n    application.add_handler(build_watch_handler())'

if 'build_watch_handler' not in content:
    if reg_anchor in content:
        idx = content.index(reg_anchor)
        # Find the end of this line (closing paren + newline)
        line_end = content.index('\n', idx)
        content = content[:line_end+1] + reg_line + content[line_end+1:]
        print(f"  ✓ Added handler registration for /watch")
    else:
        print(f"  ⚠ Could not find registration anchor — manual registration needed")

# Write back
with open(bot_file, 'w') as f:
    f.write(content)

# Verify syntax
import py_compile
py_compile.compile(bot_file, doraise=True)
print("  ✓ mythos_bot.py syntax OK")

py_compile.compile(
    '/opt/mythos/telegram_bot/handlers/watchlist_handler.py',
    doraise=True
)
print("  ✓ watchlist_handler.py syntax OK")

# ── Restart bot ─────────────────────────────────────────────────────────
patch.restart_service('mythos-bot.service')

patch.finish()
