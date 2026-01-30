#!/bin/bash
# Patch 0047: Finance Telegram Report
# Adds /report command for full financial status report (HTML formatted)

set -e

echo "Installing finance telegram report..."

# Backup existing finance_handler.py
if [ -f /opt/mythos/telegram_bot/handlers/finance_handler.py ]; then
    cp /opt/mythos/telegram_bot/handlers/finance_handler.py \
       /opt/mythos/telegram_bot/handlers/finance_handler.py.bak.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backed up existing finance_handler.py"
fi

# Copy updated finance_handler.py
cp -v opt/mythos/telegram_bot/handlers/finance_handler.py \
      /opt/mythos/telegram_bot/handlers/finance_handler.py

# Add report_command to the import line in mythos_bot.py
if ! grep -q "report_command" /opt/mythos/telegram_bot/mythos_bot.py; then
    echo "Adding report_command to imports..."
    sed -i 's/from handlers.finance_handler import (/from handlers.finance_handler import (\n    report_command,/' \
        /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Added import"
else
    echo "✓ report_command already imported"
fi

# Add handler registration after spending_command
if ! grep -q '"report"' /opt/mythos/telegram_bot/mythos_bot.py; then
    echo "Adding /report handler registration..."
    sed -i '/CommandHandler("spending", spending_command)/a\    application.add_handler(CommandHandler("report", report_command))' \
        /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Added handler"
else
    echo "✓ /report handler already registered"
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
echo "✓ Patch 0047 installed successfully"
echo "  Command: /report"
echo "  Shows: Full financial status report with projections"
