#!/bin/bash
# patch_0022_default_chat_status install script
# - Makes chat the default mode
# - Enhanced /status with activity log and topic tracking

set -e

echo "📦 Installing patch_0022: Default Chat Mode + Enhanced Status"

# Copy files
cp -v opt/mythos/telegram_bot/mythos_bot.py /opt/mythos/telegram_bot/mythos_bot.py
cp -v opt/mythos/telegram_bot/handlers/chat_mode.py /opt/mythos/telegram_bot/handlers/chat_mode.py

# Set permissions
chmod +x /opt/mythos/telegram_bot/mythos_bot.py
chmod 644 /opt/mythos/telegram_bot/handlers/chat_mode.py

# Restart the bot service
echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

# Wait a moment and check status
sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ mythos-bot.service is running"
else
    echo "❌ mythos-bot.service failed to start"
    journalctl -u mythos-bot.service -n 20 --no-pager
    exit 1
fi

echo ""
echo "✅ patch_0022 installed successfully!"
echo ""
echo "Changes:"
echo "  - Default mode is now 'chat' (was 'db')"
echo "  - /status shows:"
echo "      • Current mode and model"
echo "      • Chat message count and recent topics"
echo "      • Activity log (last 5 actions)"
echo "  - Topics auto-extracted from your questions"
echo "  - Activity logging for mode switches, queries, etc."
