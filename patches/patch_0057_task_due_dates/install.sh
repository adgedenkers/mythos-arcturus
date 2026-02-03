#!/bin/bash
# Patch 0057: Task Due Dates
# Adds due date support to task tracking

set -e

echo "📦 Installing Patch 0057: Task Due Dates..."

# Copy updated task handler
cp opt/mythos/telegram_bot/handlers/task_handler.py /opt/mythos/telegram_bot/handlers/

# Restart bot service
echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

# Wait and check
sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ Patch 0057 installed successfully!"
    echo ""
    echo "Due date formats now supported:"
    echo "  /task add -d today Urgent thing"
    echo "  /task add -d tomorrow Call mom"
    echo "  /task add -d friday Weekly review"
    echo "  /task add -d 10th Pay rent"
    echo "  /task add -d 2/14 Valentine's day"
    echo ""
    echo "New command:"
    echo "  /task due - Show tasks sorted by due date"
else
    echo "❌ Bot service failed to start!"
    journalctl -u mythos-bot.service -n 20
    exit 1
fi
