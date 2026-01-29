#!/bin/bash
# patch_0031_finance_bot_commands - Add /balance, /finance, /spending to Telegram bot
#
# New commands:
#   /balance  - Show current account balances
#   /finance  - Full financial summary (balances + month activity + recent)
#   /spending - Spending by category this month

set -e

echo "=== patch_0031_finance_bot_commands ==="

# Copy the finance handler
cp opt/mythos/telegram_bot/handlers/finance_handler.py /opt/mythos/telegram_bot/handlers/
echo "✓ Installed finance_handler.py"

# Backup the bot
cp /opt/mythos/telegram_bot/mythos_bot.py /opt/mythos/telegram_bot/mythos_bot.py.bak.$(date +%Y%m%d_%H%M%S)
echo "✓ Backed up mythos_bot.py"

# Add import for finance handlers (after the patch_handlers import)
if ! grep -q "finance_handler" /opt/mythos/telegram_bot/mythos_bot.py; then
    sed -i '/from handlers.patch_handlers import/a\
\
# Finance commands\
from handlers.finance_handler import (\
    balance_command,\
    finance_command,\
    spending_command\
)' /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Added finance handler imports"
else
    echo "• Finance imports already present"
fi

# Add command handlers (after patch management commands section)
if ! grep -q 'CommandHandler("balance"' /opt/mythos/telegram_bot/mythos_bot.py; then
    sed -i '/application.add_handler(CommandHandler("patch_rollback_confirm"/a\
    \
    # Finance commands\
    application.add_handler(CommandHandler("balance", balance_command))\
    application.add_handler(CommandHandler("finance", finance_command))\
    application.add_handler(CommandHandler("spending", spending_command))' /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Added finance command handlers"
else
    echo "• Finance commands already registered"
fi

# Restart the bot service
sudo systemctl restart mythos-bot.service
echo "✓ Restarted mythos-bot service"

# Verify it's running
sleep 2
if systemctl is-active --quiet mythos-bot.service; then
    echo "✓ Bot service is running"
else
    echo "⚠ Bot service may not have started correctly"
    sudo systemctl status mythos-bot.service --no-pager
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "New Telegram commands:"
echo "  /balance  - Current account balances"
echo "  /finance  - Full financial summary"
echo "  /spending - Category breakdown"
