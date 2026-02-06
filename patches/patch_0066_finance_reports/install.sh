#!/bin/bash
# Patch 0066: Finance Reports
# Telegram commands for finance reporting

set -e

echo "=== Installing Patch 0066: Finance Reports ==="

# Install handler
cp opt/mythos/telegram_bot/handlers/finance_handler.py /opt/mythos/telegram_bot/handlers/
echo "✓ Finance handler installed"

# Check if already in __init__.py
if grep -q "finance_handler" /opt/mythos/telegram_bot/handlers/__init__.py 2>/dev/null; then
    echo "✓ Finance handler already in __init__.py"
else
    echo "from .finance_handler import register_handlers as register_finance_handlers" >> /opt/mythos/telegram_bot/handlers/__init__.py
    echo "✓ Added finance handler to __init__.py"
fi

# Check if registered in bot.py
if grep -q "register_finance_handlers" /opt/mythos/telegram_bot/bot.py 2>/dev/null; then
    echo "✓ Finance handlers already registered in bot.py"
else
    # Add import
    sed -i '/^from handlers import/s/$/, register_finance_handlers/' /opt/mythos/telegram_bot/bot.py 2>/dev/null || \
    sed -i '/from handlers/a from handlers import register_finance_handlers' /opt/mythos/telegram_bot/bot.py
    
    # Add registration call (after other register calls)
    sed -i '/register_pulse_handlers\|register_handlers/a\    register_finance_handlers(app)' /opt/mythos/telegram_bot/bot.py 2>/dev/null || \
    echo "⚠️  Please manually add 'register_finance_handlers(app)' to bot.py"
    echo "✓ Added finance handler registration to bot.py"
fi

# Restart bot
echo "=== Restarting bot service ==="
sudo systemctl restart mythos-bot.service
sleep 2

if systemctl is-active --quiet mythos-bot.service; then
    echo "✓ Bot service restarted successfully"
else
    echo "❌ Bot service failed to start"
    sudo journalctl -u mythos-bot.service --no-pager -n 20
    exit 1
fi

echo ""
echo "=== Patch 0066 Complete ==="
echo ""
echo "New commands:"
echo "  /spend [month]  - Spending breakdown by category"
echo "  /monthly        - Month-by-month trend"
echo "  /compare        - This month vs last month"
echo "  /top [n]        - Top merchants by spending"
echo "  /txn [category] - List transactions (paginated)"
echo "  /next, /back    - Pagination controls"
