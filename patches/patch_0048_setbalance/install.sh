#!/bin/bash
# Patch 0048: Add /setbalance command and live /report
# - /setbalance USAA 1431.65 - Set account balance manually
# - /report now pulls live from database

set -e

echo "Installing setbalance command..."

# Backup existing finance_handler.py
if [ -f /opt/mythos/telegram_bot/handlers/finance_handler.py ]; then
    cp /opt/mythos/telegram_bot/handlers/finance_handler.py \
       /opt/mythos/telegram_bot/handlers/finance_handler.py.bak.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backed up existing finance_handler.py"
fi

# Copy updated finance_handler.py
cp -v opt/mythos/telegram_bot/handlers/finance_handler.py \
      /opt/mythos/telegram_bot/handlers/finance_handler.py

# Add setbalance_command to the import line in mythos_bot.py
if ! grep -q "setbalance_command" /opt/mythos/telegram_bot/mythos_bot.py; then
    echo "Adding setbalance_command to imports..."
    sed -i 's/from handlers.finance_handler import (/from handlers.finance_handler import (\n    setbalance_command,/' \
        /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Added import"
else
    echo "✓ setbalance_command already imported"
fi

# Add handler registration after report_command (or spending_command if report not there)
if ! grep -q '"setbalance"' /opt/mythos/telegram_bot/mythos_bot.py; then
    echo "Adding /setbalance handler registration..."
    if grep -q '"report"' /opt/mythos/telegram_bot/mythos_bot.py; then
        sed -i '/CommandHandler("report", report_command)/a\    application.add_handler(CommandHandler("setbalance", setbalance_command))' \
            /opt/mythos/telegram_bot/mythos_bot.py
    else
        sed -i '/CommandHandler("spending", spending_command)/a\    application.add_handler(CommandHandler("setbalance", setbalance_command))' \
            /opt/mythos/telegram_bot/mythos_bot.py
    fi
    echo "✓ Added handler"
else
    echo "✓ /setbalance handler already registered"
fi

# Restart the bot
echo "Restarting mythos-bot service..."
sudo systemctl restart mythos-bot.service

sleep 2

# Check status
if systemctl is-active --quiet mythos-bot.service; then
    echo "✓ mythos-bot service is running"
else
    echo "⚠️ mythos-bot service may have issues, check: sudo systemctl status mythos-bot.service"
fi

echo ""
echo "✓ Patch 0048 installed successfully"
echo ""
echo "New commands:"
echo "  /setbalance <ACCT> <amount> - Set account balance"
echo "    Examples:"
echo "      /setbalance USAA 1431.65"
echo "      /setbalance SUN 976.47"
echo ""
echo "  /report - Now pulls LIVE data from database"
