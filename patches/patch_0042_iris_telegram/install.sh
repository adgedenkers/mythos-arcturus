#!/bin/bash
# Patch 0042: Iris Telegram Integration
# Adds /iris, /iris_test, /iris_run, /iris_task commands

set -e

echo "=== Installing Patch 0042: Iris Telegram Integration ==="

# Copy Iris handler
cp -v opt/mythos/telegram_bot/handlers/iris_handler.py /opt/mythos/telegram_bot/handlers/

# Copy updated health.py to Iris
cp -v opt/mythos/iris/core/src/health.py /opt/mythos/iris/core/src/

# Add imports and handlers to mythos_bot.py
BOTFILE="/opt/mythos/telegram_bot/mythos_bot.py"

# Check if already patched
if grep -q "iris_handler" "$BOTFILE"; then
    echo "Bot already has Iris imports, skipping..."
else
    echo "Adding Iris imports to bot..."
    
    # Add import after other handler imports (after finance_handler import)
    sed -i '/from handlers.finance_handler import/a\
\
# Iris consciousness commands\
from handlers.iris_handler import (\
    iris_command,\
    iris_test_command,\
    iris_run_command,\
    iris_task_command\
)' "$BOTFILE"
    
    echo "Import added"
fi

# Check if command handlers already added
if grep -q 'CommandHandler("iris"' "$BOTFILE"; then
    echo "Command handlers already added, skipping..."
else
    echo "Adding command handlers..."
    
    # Add handlers after the spending command handler
    sed -i '/CommandHandler("spending", spending_command)/a\
\
    # Iris consciousness commands\
    application.add_handler(CommandHandler("iris", iris_command))\
    application.add_handler(CommandHandler("iris_test", iris_test_command))\
    application.add_handler(CommandHandler("iris_run", iris_run_command))\
    application.add_handler(CommandHandler("iris_task", iris_task_command))' "$BOTFILE"
    
    echo "Command handlers added"
fi

# Rebuild and restart Iris with new health.py
echo "=== Rebuilding Iris ==="
cd /opt/mythos/docker
docker compose -f docker-compose.iris.yml build iris-core
docker compose -f docker-compose.iris.yml down
docker compose -f docker-compose.iris.yml up -d

# Restart Telegram bot
echo "=== Restarting Telegram Bot ==="
sudo systemctl restart mythos-bot.service

# Wait and verify
echo "=== Waiting for services ==="
sleep 5

echo "=== Iris Status ==="
curl -s http://localhost:8100/status | head -c 200 && echo ""

echo "=== Bot Status ==="
sudo systemctl status mythos-bot.service --no-pager | head -10

echo ""
echo "=== Patch 0042 Complete ==="
echo ""
echo "Test with Telegram:"
echo "  /iris - Show Iris status"
echo "  /iris_test - Test sandbox execution"
echo "  /iris_run print('hello') - Run code"
