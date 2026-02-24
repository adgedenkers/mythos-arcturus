#!/bin/bash
# Patch 0124: Comprehensive Help System Rewrite
# Covers ALL deployed features: inspect, diag, briefing, routines,
# forecast, weather, calendar, models, iris, personality, pulse, etc.
set -e

MYTHOS_ROOT="/opt/mythos"
HANDLER_DIR="$MYTHOS_ROOT/telegram_bot/handlers"

echo "📦 Installing patch 0124: Help System Rewrite"

# 1. Backup existing
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "  → Backing up help_handler.py"
cp "$HANDLER_DIR/help_handler.py" "$HANDLER_DIR/help_handler.py.bak.${TIMESTAMP}"

# 2. Install new handler
echo "  → Installing updated help_handler.py"
cp opt/mythos/telegram_bot/handlers/help_handler.py "$HANDLER_DIR/help_handler.py"

# 3. Restart bot
echo "  → Restarting mythos-bot service"
sudo systemctl restart mythos-bot.service
sleep 2

# 4. Verify
STATUS=$(systemctl is-active mythos-bot.service)
if [ "$STATUS" = "active" ]; then
    echo "✅ Patch 0124 installed. Bot is active."
    echo "   Try: /help or /help inspect or /help briefing"
else
    echo "⚠️  Bot may not have started cleanly."
    echo "   Check: journalctl -u mythos-bot -n 30"
    echo "   Restore: cp $HANDLER_DIR/help_handler.py.bak.${TIMESTAMP} $HANDLER_DIR/help_handler.py"
fi
