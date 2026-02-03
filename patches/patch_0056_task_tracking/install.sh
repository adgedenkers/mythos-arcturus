#!/bin/bash
# Patch 0056: Task Tracking System
# Adds /task and /tasks commands using existing idea_backlog table

set -e

echo "📦 Installing Patch 0056: Task Tracking..."

# Copy task handler
cp opt/mythos/telegram_bot/handlers/task_handler.py /opt/mythos/telegram_bot/handlers/

# Update handlers __init__.py to include task_handler exports
if ! grep -q "task_handler" /opt/mythos/telegram_bot/handlers/__init__.py; then
    echo "" >> /opt/mythos/telegram_bot/handlers/__init__.py
    echo "# Task tracking" >> /opt/mythos/telegram_bot/handlers/__init__.py
    echo "from .task_handler import task_command, tasks_command" >> /opt/mythos/telegram_bot/handlers/__init__.py
fi

# Add imports to mythos_bot.py if not present
if ! grep -q "task_command" /opt/mythos/telegram_bot/mythos_bot.py; then
    # Add import after iris_handler import
    sed -i '/from handlers.iris_handler import/a\
\
# Task tracking commands\
from handlers.task_handler import task_command, tasks_command' /opt/mythos/telegram_bot/mythos_bot.py
fi

# Add command handlers before "# Message handlers" line
if ! grep -q 'CommandHandler("task"' /opt/mythos/telegram_bot/mythos_bot.py; then
    sed -i '/# Message handlers/i\
    # Task tracking commands\
    application.add_handler(CommandHandler("task", task_command))\
    application.add_handler(CommandHandler("tasks", tasks_command))\
' /opt/mythos/telegram_bot/mythos_bot.py
fi

# Update help text to include task commands
# Find the SYSTEM section in help and add task commands before it
if ! grep -q "/task" /opt/mythos/telegram_bot/mythos_bot.py; then
    sed -i '/\*\*SYSTEM\*\*/i\
━━━━━━━━━━━━━━━━━━━━━━━━\
**TASKS**\
━━━━━━━━━━━━━━━━━━━━━━━━\
`/task add Do something` - Add task\
`/task add -h Urgent!` - High priority\
`/tasks` - List open tasks\
`/task done 1` - Complete task #1\
`/task drop 1` - Remove task #1\
' /opt/mythos/telegram_bot/mythos_bot.py
fi

# Restart bot service
echo "🔄 Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

# Wait and check
sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✅ Patch 0056 installed successfully!"
    echo ""
    echo "New commands available:"
    echo "  /task add Buy groceries"
    echo "  /task add -h Urgent thing"
    echo "  /tasks (or /task list)"
    echo "  /task done 1"
    echo "  /task drop 1"
else
    echo "❌ Bot service failed to start!"
    journalctl -u mythos-bot.service -n 20
    exit 1
fi
