#!/bin/bash
# patch_0025_status_cleanup install script
# Cleaner /status output and tightened bot responses

set -e

echo "📦 Installing patch_0025: Status Cleanup"

cp -v opt/mythos/telegram_bot/mythos_bot.py /opt/mythos/telegram_bot/mythos_bot.py
chmod +x /opt/mythos/telegram_bot/mythos_bot.py

echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ mythos-bot.service is running"
else
    echo "❌ mythos-bot.service failed to start"
    journalctl -u mythos-bot.service -n 20 --no-pager
    exit 1
fi

echo ""
echo "✅ patch_0025 installed!"
echo ""
echo "Changes:"
echo "  - /status output simplified (no redundant soul line)"
echo "  - Tighter, cleaner bot responses throughout"
echo "  - Activity log shows last 3 items (was 5)"
echo "  - Chat topics shows last 3 (was 5)"
