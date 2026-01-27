#!/bin/bash
# patch_0021_help_and_chat_mode install script
# Adds /help improvements and implements /mode chat with Ollama

set -e

echo "📦 Installing patch_0021: Help & Chat Mode"

# Copy files
cp -v opt/mythos/telegram_bot/mythos_bot.py /opt/mythos/telegram_bot/mythos_bot.py
cp -v opt/mythos/telegram_bot/handlers/__init__.py /opt/mythos/telegram_bot/handlers/__init__.py
cp -v opt/mythos/telegram_bot/handlers/chat_mode.py /opt/mythos/telegram_bot/handlers/chat_mode.py

# Set permissions
chmod +x /opt/mythos/telegram_bot/mythos_bot.py
chmod 644 /opt/mythos/telegram_bot/handlers/chat_mode.py
chmod 644 /opt/mythos/telegram_bot/handlers/__init__.py

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
echo "✅ patch_0021 installed successfully!"
echo ""
echo "New features:"
echo "  - /help now shows organized command reference"
echo "  - /mode chat connects directly to Ollama (qwen2.5:32b)"
echo "  - Chat maintains conversation context across messages"
echo "  - /clear resets chat conversation"
echo "  - /model fast uses llama3.2:3b for quick responses"
