#!/bin/bash
# Patch 0051: Seraphe Report - Simple financial snapshot
# 
# Adds:
# - Credit card accounts to database
# - current_balance column to accounts table
# - /snapshot command (the Seraphe Report)
# - /setbal quick balance update

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Patch 0051: Seraphe Report ==="

# Copy files first
echo "Copying files..."
cp "$PATCH_DIR/opt/mythos/finance/migration_0051_credit_cards.sql" /opt/mythos/finance/
cp "$PATCH_DIR/opt/mythos/telegram_bot/handlers/snapshot_handler.py" /opt/mythos/telegram_bot/handlers/

# Run database migration
echo "Running database migration..."
sudo -u postgres psql -d mythos -f /opt/mythos/finance/migration_0051_credit_cards.sql

# Update bot to include new commands
echo "Updating bot with new commands..."

# Check if snapshot commands already registered
if ! grep -q "snapshot_command" /opt/mythos/telegram_bot/mythos_bot.py; then
    # Add import after finance_handler import
    sed -i '/from handlers.finance_handler import/a from handlers.snapshot_handler import snapshot_command, setbal_command' /opt/mythos/telegram_bot/mythos_bot.py
    
    # Add command handlers after setbalance
    sed -i '/CommandHandler("setbalance", setbalance_command)/a\    application.add_handler(CommandHandler("snapshot", snapshot_command))\n    application.add_handler(CommandHandler("setbal", setbal_command))' /opt/mythos/telegram_bot/mythos_bot.py
    
    echo "Bot commands registered"
else
    echo "Snapshot commands already registered"
fi

# Restart bot
echo "Restarting Telegram bot..."
sudo systemctl restart mythos-bot.service

# Wait and check status
sleep 2
if sudo systemctl is-active --quiet mythos-bot.service; then
    echo "✓ Bot restarted successfully"
else
    echo "⚠ Bot may have issues - check with: sudo journalctl -u mythos-bot.service -n 50"
fi

echo ""
echo "=== Patch 0051 Complete ==="
echo ""
echo "New commands:"
echo "  /snapshot  - The Seraphe Report (full financial snapshot)"
echo "  /setbal    - Quick balance update (e.g., /setbal USAA 1431.65)"
echo ""
echo "New accounts added:"
echo "  LLBEAN, TSC, OLDNAVY, TJX, AMEX (credit cards)"
echo "  USAALOAN (loan)"
echo ""
