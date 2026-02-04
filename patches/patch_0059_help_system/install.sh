#!/bin/bash
# Patch 0059: Comprehensive Help System
# Adds topic-based help with examples for each subsystem

set -e

echo "📦 Installing Patch 0059: Comprehensive Help System..."

# Copy help handler
cp opt/mythos/telegram_bot/handlers/help_handler.py /opt/mythos/telegram_bot/handlers/

# Update handlers __init__.py to include help_handler
if ! grep -q "help_handler" /opt/mythos/telegram_bot/handlers/__init__.py; then
    echo "" >> /opt/mythos/telegram_bot/handlers/__init__.py
    echo "# Help system" >> /opt/mythos/telegram_bot/handlers/__init__.py
    echo "from .help_handler import help_command" >> /opt/mythos/telegram_bot/handlers/__init__.py
fi

# Replace the old help_command in mythos_bot.py with import from handler
# First, add the import if not present
if ! grep -q "from handlers.help_handler import" /opt/mythos/telegram_bot/mythos_bot.py; then
    sed -i '/from handlers.task_handler import/a\
\
# Help system\
from handlers.help_handler import help_command as help_command_handler' /opt/mythos/telegram_bot/mythos_bot.py
fi

# Update the help command registration to use the new handler
# Find and replace the help CommandHandler line
sed -i 's/CommandHandler("help", help_command)/CommandHandler("help", help_command_handler)/' /opt/mythos/telegram_bot/mythos_bot.py

# Restart bot service
echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

# Wait and check
sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ Patch 0059 installed successfully!"
    echo ""
    echo "New help system:"
    echo "  /help - Main overview"
    echo "  /help tasks - Task tracking with examples"
    echo "  /help finance - Finance system guide"
    echo "  /help sell - Selling workflow"
    echo "  /help chat - Chat mode tips"
    echo "  /help db - Database queries"
    echo "  /help system - Admin & patches"
else
    echo "❌ Bot service failed to start!"
    journalctl -u mythos-bot.service -n 20
    exit 1
fi
