#!/usr/bin/env python3
"""
MNE-0001: Backlog cleanup and /backlog command
- Marks completed backlog items as done
- Archives duplicate entries
- Tags personal vs dev vs doc items with domain
- Assigns priority_order to unordered rows
- Deploys /backlog Telegram command (separate from /task)
"""
import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=1,
    description='Backlog cleanup and /backlog command',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy backlog handler ────────────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/telegram_bot/handlers/backlog_handler.py',
    '/opt/mythos/telegram_bot/handlers/backlog_handler.py'
)

# ── 2. Run SQL migration ─────────────────────────────────────────────────────
patch.run_sql('opt/mythos/migrations/mne_0001_backlog_cleanup.sql')

# ── 3. Register /backlog command in route_handler.py ──────────────────────────
route_handler_path = '/opt/mythos/telegram_bot/handlers/route_handler.py'

with open(route_handler_path, 'r') as f:
    content = f.read()

# Add import for backlog_handler
import_line = 'from .backlog_handler import backlog_command'
if import_line not in content:
    # Find the last 'from .' import line and add after it
    lines = content.split('\n')
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('from .') and 'import' in line:
            last_import_idx = i

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_line)
        content = '\n'.join(lines)
        print(f"  ✓ Added import: {import_line}")
    else:
        patch.errors.append("Could not find import insertion point in route_handler.py")

# Add command registration for /backlog
# Look for where commands are registered — typically CommandHandler additions
backlog_registration = "backlog_command"
if backlog_registration not in content:
    # Look for task-related registration to add nearby
    # Common patterns: app.add_handler(CommandHandler("task", ...))
    # or a dict/list of commands
    #
    # We'll search for 'task_command' or 'tasks_command' registration
    # and add the backlog one right after

    # Strategy: find "task" command registration line and add after it
    lines = content.split('\n')
    inserted = False
    for i, line in enumerate(lines):
        if 'task' in line.lower() and 'commandhandler' in line.lower():
            # Found task registration — add backlog after it
            # Determine indentation
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            new_line = f'{indent_str}app.add_handler(CommandHandler("backlog", backlog_command))'
            lines.insert(i + 1, new_line)
            content = '\n'.join(lines)
            print(f"  ✓ Registered /backlog command (after task handler)")
            inserted = True
            break

    if not inserted:
        # Fallback: search for any CommandHandler pattern
        for i, line in enumerate(lines):
            if 'CommandHandler' in line and 'add_handler' in line:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                new_line = f'{indent_str}app.add_handler(CommandHandler("backlog", backlog_command))'
                lines.insert(i + 1, new_line)
                content = '\n'.join(lines)
                print(f"  ✓ Registered /backlog command (after first CommandHandler)")
                inserted = True
                break

    if not inserted:
        patch.errors.append("Could not find command registration point in route_handler.py — register /backlog manually")

# Write updated route_handler
with open(route_handler_path, 'w') as f:
    f.write(content)
print(f"  ✓ Updated {route_handler_path}")

# ── 4. Restart bot ───────────────────────────────────────────────────────────
patch.restart_service('mythos-bot.service')

patch.finish()
