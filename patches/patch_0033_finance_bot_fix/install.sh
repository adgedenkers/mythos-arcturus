#!/bin/bash
# patch_0033_finance_bot_fix - Fix finance bot commands (replaces broken patch_0031)
#
# This patch:
#   1. Restores bot from backup if corrupted
#   2. Properly adds finance handler imports and command registrations
#
# Commands added:
#   /balance  - Current account balances
#   /finance  - Full financial summary
#   /spending - Category breakdown

set -e

echo "=== patch_0033_finance_bot_fix ==="

BOT_FILE="/opt/mythos/telegram_bot/mythos_bot.py"
BACKUP_FILE="/opt/mythos/telegram_bot/mythos_bot.py.bak.20260129_063826"

# Check if current bot file is broken
if ! /opt/mythos/.venv/bin/python3 -m py_compile "$BOT_FILE" 2>/dev/null; then
    echo "⚠ Bot file has syntax errors, restoring from backup..."
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$BOT_FILE"
        echo "✓ Restored from backup"
    else
        echo "❌ No backup found at $BACKUP_FILE"
        exit 1
    fi
fi

# Copy the finance handler
cp opt/mythos/telegram_bot/handlers/finance_handler.py /opt/mythos/telegram_bot/handlers/
echo "✓ Installed finance_handler.py"

# Check if finance imports already exist (clean)
if grep -q "from handlers.finance_handler import" "$BOT_FILE"; then
    echo "• Finance imports already present"
else
    # Add finance import AFTER the patch_handlers import block (after the closing paren)
    # Find line number of the closing ) for patch_handlers import
    PATCH_END=$(grep -n "patch_rollback_confirm_command" "$BOT_FILE" | head -1 | cut -d: -f1)
    PATCH_END=$((PATCH_END + 1))  # The line with closing )
    
    # Insert after that line
    sed -i "${PATCH_END}a\\
\\
# Finance commands\\
from handlers.finance_handler import (\\
    balance_command,\\
    finance_command,\\
    spending_command\\
)" "$BOT_FILE"
    echo "✓ Added finance handler imports"
fi

# Check if finance command handlers already registered
if grep -q 'CommandHandler("balance"' "$BOT_FILE"; then
    echo "• Finance commands already registered"
else
    # Find line where patch commands end and add after
    HANDLER_LINE=$(grep -n 'CommandHandler("patch_rollback_confirm"' "$BOT_FILE" | head -1 | cut -d: -f1)
    
    sed -i "${HANDLER_LINE}a\\
    \\
    # Finance commands\\
    application.add_handler(CommandHandler(\"balance\", balance_command))\\
    application.add_handler(CommandHandler(\"finance\", finance_command))\\
    application.add_handler(CommandHandler(\"spending\", spending_command))" "$BOT_FILE"
    echo "✓ Added finance command handlers"
fi

# Verify syntax is still valid
if /opt/mythos/.venv/bin/python3 -m py_compile "$BOT_FILE" 2>/dev/null; then
    echo "✓ Syntax check passed"
else
    echo "❌ Syntax error after patching!"
    echo "Restoring backup..."
    cp "$BACKUP_FILE" "$BOT_FILE"
    exit 1
fi

# Restart the bot service
sudo systemctl restart mythos-bot.service
echo "✓ Restarted mythos-bot service"

# Verify it's running
sleep 3
if systemctl is-active --quiet mythos-bot.service; then
    echo "✓ Bot service is running"
else
    echo "⚠ Bot service may not have started correctly"
    sudo systemctl status mythos-bot.service --no-pager | head -20
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Telegram commands available:"
echo "  /balance  - Current account balances"
echo "  /finance  - Full financial summary"
echo "  /spending - Category breakdown"
