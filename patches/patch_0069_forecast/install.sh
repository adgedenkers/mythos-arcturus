#!/bin/bash
# Patch 0069: Balance Forecast & Projection Commands
# New commands: /forecast, /projection, /bills, /income
set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Patch 0069: Balance Forecast ==="

# 1. Install forecast handler
echo "Installing forecast_handler.py..."
cp "$PATCH_DIR/opt/mythos/telegram_bot/handlers/forecast_handler.py" \
   "$MYTHOS_ROOT/telegram_bot/handlers/forecast_handler.py"
echo "  ✓ Forecast handler installed"

# 2. Register commands in bot
BOT_FILE="$MYTHOS_ROOT/telegram_bot/mythos_bot.py"

# Check if already registered
if grep -q "forecast_handler" "$BOT_FILE"; then
    echo "  ✓ Commands already registered in bot"
else
    echo "Registering commands in bot..."
    
    # Add import
    sed -i '/^from handlers.finance_handler/a from handlers.forecast_handler import forecast_command, projection_command, bills_command, income_command' "$BOT_FILE"
    
    # Add command handlers - find the last CommandHandler line and add after it
    # We need to add before the line that starts the bot (app.run_polling or similar)
    sed -i '/app.add_handler.*CommandHandler.*"report"/a\    app.add_handler(CommandHandler("forecast", forecast_command))\n    app.add_handler(CommandHandler("projection", projection_command))\n    app.add_handler(CommandHandler("bills", bills_command))\n    app.add_handler(CommandHandler("income", income_command))' "$BOT_FILE"
    
    echo "  ✓ Commands registered"
fi

# 3. Check accounts have account_type set
echo "Checking account types..."
sudo -u postgres psql -d mythos -c "
-- Ensure checking accounts are marked
UPDATE accounts SET account_type = 'checking' 
WHERE abbreviation IN ('USAA', 'SUN', 'SID', 'DVA', 'NBT') AND (account_type IS NULL OR account_type = '');

-- Credit cards
UPDATE accounts SET account_type = 'credit' 
WHERE abbreviation IN ('AMEX', 'TJX', 'LLBEAN', 'TSC', 'OLDNAVY') AND (account_type IS NULL OR account_type = '');

-- Loan
UPDATE accounts SET account_type = 'loan'
WHERE abbreviation = 'USAALOAN' AND (account_type IS NULL OR account_type = '');
" 2>&1 | grep -v "^$"
echo "  ✓ Account types verified"

# 4. Restart bot
echo "Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

if systemctl is-active --quiet mythos-bot.service; then
    echo "  ✓ Bot running"
else
    echo "  ✗ Bot failed to start!"
    sudo journalctl -u mythos-bot.service --no-pager -n 15
    exit 1
fi

echo ""
echo "=== Patch 0069 Complete ==="
echo ""
echo "New commands:"
echo "  /forecast    - Day-by-day balance projection (30 days)"
echo "  /projection  - Quick financial outlook summary"
echo "  /bills       - Upcoming bills (14 days)"
echo "  /income      - Expected income (30 days)"
