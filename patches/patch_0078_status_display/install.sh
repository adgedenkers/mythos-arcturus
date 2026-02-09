#!/bin/bash
# Patch 0078 — Patch Status Display Update
# Shows patch number alongside git tag version
set -e

echo "=========================================="
echo "Patch 0078 — Patch Status Display"
echo "=========================================="

HANDLER="/opt/mythos/telegram_bot/handlers/patch_handlers.py"
cp "$HANDLER" "$HANDLER.bak.$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('/opt/mythos/telegram_bot/handlers/patch_handlers.py', 'r') as f:
    content = f.read()

# Replace the patch_status_command function
old_func = '''async def patch_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_status - Show current version and recent patches
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    version = _get_current_version()
    tags = _get_recent_tags(5)
    logs = _get_recent_logs(3)
    
    # Check git remote
    has_remote, remote_url = _run_git("remote", "get-url", "origin")
    
    msg = f"📊 <b>Patch Status</b>\\n\\n"
    msg += f"<b>Current Version:</b> <code>{version}</code>\\n"
    msg += f"<b>GitHub:</b> {'✓ Connected' if has_remote else '✗ Not configured'}\\n\\n"
    
    msg += "<b>Recent Tags:</b>\\n"
    for t in tags[:5]:
        msg += f"• <code>{t['tag']}</code> ({t['date'][:10]})\\n"
    
    if logs:
        msg += "\\n<b>Recent Activity:</b>\\n"
        for log in logs[:3]:
            status = "✓" if log.get('status') == 'success' else "✗"
            patch_name = log.get('patch', log.get('target_tag', 'unknown'))
            msg += f"• {status} {patch_name}\\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')'''

new_func = '''async def patch_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_status - Show current version and recent patches
    """
    import re
    
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    version = _get_current_version()
    tags = _get_recent_tags(5)
    logs = _get_recent_logs(5)
    
    # Check git remote
    has_remote, remote_url = _run_git("remote", "get-url", "origin")
    
    # Extract latest patch number from recent activity
    latest_patch = "?"
    for log in (logs or []):
        patch_name = log.get('patch', log.get('target_tag', ''))
        m = re.search(r'patch_(\d{4})', str(patch_name))
        if m:
            latest_patch = m.group(1)
            break
    
    msg = f"📊 <b>Patch Status</b>\\n\\n"
    msg += f"<b>Latest Patch:</b> <code>#{latest_patch}</code>\\n"
    msg += f"<b>Git Tag:</b> <code>{version}</code>\\n"
    msg += f"<b>GitHub:</b> {'✓ Connected' if has_remote else '✗ Not configured'}\\n\\n"
    
    msg += "<b>Recent Patches:</b>\\n"
    for log in (logs or [])[:5]:
        status = "✓" if log.get('status') == 'success' else "✗"
        patch_name = log.get('patch', log.get('target_tag', 'unknown'))
        # Extract patch number and name
        m = re.search(r'patch_(\d{4})_(.+?)\.zip', str(patch_name))
        if m:
            num = m.group(1)
            name = m.group(2).replace('_', ' ')
            # Find matching git tag
            tag_match = ""
            for t in tags:
                if t['tag'] and t['date'][:10] == log.get('date', '')[:10]:
                    tag_match = f" → {t['tag']}"
                    break
            msg += f"  {status} <code>#{num}</code> {name}{tag_match}\\n"
        else:
            msg += f"  {status} {patch_name}\\n"
    
    if tags:
        msg += "\\n<b>Git Tags:</b>\\n"
        for t in tags[:5]:
            msg += f"  <code>{t['tag']}</code> ({t['date'][:10]})\\n"
    
    msg += f"\\n<i>Note: Patch numbers and git tags will be aligned in a future update.</i>"
    
    await update.message.reply_text(msg, parse_mode='HTML')'''

if old_func in content:
    content = content.replace(old_func, new_func)
    print("  ✅ Replaced patch_status_command")
else:
    print("  ⚠️  Could not find exact match for old function")
    print("      Attempting line-by-line replacement...")
    
    # Fallback: find and replace by function signature
    lines = content.split('\n')
    new_lines = []
    skip = False
    inserted = False
    
    for i, line in enumerate(lines):
        if 'async def patch_status_command' in line and not inserted:
            skip = True
            # Insert new function
            new_lines.append(new_func.replace('\\n', '\n'))
            inserted = True
            continue
        
        if skip:
            # Skip until next function definition
            if (line.startswith('async def ') or line.startswith('def ')) and 'patch_status' not in line:
                skip = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    if inserted:
        content = '\n'.join(new_lines)
        print("  ✅ Replaced via fallback method")
    else:
        print("  ❌ Failed to replace function")

with open('/opt/mythos/telegram_bot/handlers/patch_handlers.py', 'w') as f:
    f.write(content)
PYEOF

echo ""
echo "Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

BOT_STATUS=$(sudo systemctl is-active mythos-bot.service)
echo "  Bot: $BOT_STATUS"

if [ "$BOT_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0078 installed"
    echo "=========================================="
    echo ""
    echo "New /patch_status display:"
    echo "  • Shows latest patch number (#0078)"
    echo "  • Shows git tag separately"
    echo "  • Recent patches show number + name"
    echo "  • Note about future tag alignment"
else
    echo ""
    echo "⚠️  Bot failed to start. Check:"
    echo "  journalctl -u mythos-bot.service -n 20 --no-pager"
fi
