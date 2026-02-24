#!/bin/bash
# ============================================================
# Patch 0121: /diag command — Comprehensive system diagnostics
# Version: 1.19.0
# ============================================================
set -e

MYTHOS=/opt/mythos
BOT_DIR=$MYTHOS/telegram_bot
HANDLERS=$BOT_DIR/handlers
BOT_PY=$BOT_DIR/mythos_bot.py
VERSION="1.19.0"

echo "=== Installing patch 0121: System Diagnostics Command ==="

# 1. Deploy diag_handler.py
echo "Deploying diag_handler.py..."
cp opt/mythos/telegram_bot/handlers/diag_handler.py "$HANDLERS/diag_handler.py"
chown adge:adge "$HANDLERS/diag_handler.py"
chmod 644 "$HANDLERS/diag_handler.py"
echo "✓ diag_handler.py deployed"

# 2. Wire into bot if not already wired
echo "Checking bot wiring..."

# Check if already imported
if grep -q "diag_handler" "$BOT_PY"; then
    echo "· diag_handler already referenced in bot — skipping wiring"
else
    echo "Wiring /diag into bot..."

    # Backup
    cp "$BOT_PY" "$BOT_PY.bak.0121"

    # Add import — find last handler import line and add after it
    # We look for the last "from handlers." import line
    LAST_HANDLER_IMPORT=$(grep -n "^from handlers\.\|^from telegram_bot.handlers\." "$BOT_PY" | tail -1 | cut -d: -f1)

    if [ -z "$LAST_HANDLER_IMPORT" ]; then
        echo "⚠ Could not find handler imports — manual wiring needed"
        echo "  Add: from handlers.diag_handler import handle_diag"
        echo "  Add: application.add_handler(CommandHandler('diag', handle_diag))"
    else
        # Insert import after the last handler import
        sed -i "${LAST_HANDLER_IMPORT}a\\from handlers.diag_handler import handle_diag" "$BOT_PY"
        echo "✓ Added import"

        # Add command handler — find the weather handler registration (last known command)
        # and add after it
        WEATHER_LINE=$(grep -n "cmd_weather" "$BOT_PY" | grep "add_handler" | tail -1 | cut -d: -f1)

        if [ -n "$WEATHER_LINE" ]; then
            NEXT_LINE=$((WEATHER_LINE + 1))
            sed -i "${WEATHER_LINE}a\\\\n    # --- Diagnostics ---\\n    application.add_handler(CommandHandler('diag', handle_diag))" "$BOT_PY"
            echo "✓ Added CommandHandler for /diag"
        else
            # Fallback: find any add_handler line near the end and append after
            LAST_HANDLER=$(grep -n "add_handler(CommandHandler" "$BOT_PY" | tail -1 | cut -d: -f1)
            if [ -n "$LAST_HANDLER" ]; then
                sed -i "${LAST_HANDLER}a\\\\n    # --- Diagnostics ---\\n    application.add_handler(CommandHandler('diag', handle_diag))" "$BOT_PY"
                echo "✓ Added CommandHandler for /diag (after last handler)"
            else
                echo "⚠ Could not find handler registration block — manual wiring needed"
                echo "  Add: application.add_handler(CommandHandler('diag', handle_diag))"
            fi
        fi
    fi
fi

# 3. Update version
echo "$VERSION" > "$MYTHOS/.version"
echo "✓ Version set to $VERSION"

# 4. Restart bot
echo "Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

# 5. Verify
BOT_STATUS=$(systemctl is-active mythos-bot.service)
echo "Bot status: $BOT_STATUS"

if [ "$BOT_STATUS" = "active" ]; then
    echo "✓ Bot running"
else
    echo "❌ Bot failed to start — check logs:"
    echo "  journalctl -u mythos-bot.service -n 30 --no-pager"
    echo ""
    echo "To rollback:"
    echo "  cp $BOT_PY.bak.0121 $BOT_PY"
    echo "  sudo systemctl restart mythos-bot.service"
    exit 1
fi

echo ""
echo "=== Patch 0121 installed successfully ==="
echo ""
echo "Commands:"
echo "  /diag          — Full system diagnostic (as file)"
echo "  /diag hw       — Hardware only"
echo "  /diag bot db   — Combine blocks"
echo "  /diag help     — Show all blocks"
echo ""
echo "Blocks: hw, services, workers, bot, api, db, docker, ollama, redis, net, patches"
