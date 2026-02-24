#!/bin/bash
# Patch 0123: Mythos Filesystem Inspector (/inspect command)
# Adds /inspect command for browsing files, querying DBs, and checking services from Telegram
set -e

MYTHOS_ROOT="/opt/mythos"
BOT_DIR="$MYTHOS_ROOT/telegram_bot"
HANDLER_DIR="$BOT_DIR/handlers"

echo "📦 Installing patch 0123: Mythos Inspector"

# 1. Copy handler
echo "  → Installing inspect_handler.py"
cp opt/mythos/telegram_bot/handlers/inspect_handler.py "$HANDLER_DIR/inspect_handler.py"

# 2. Register in mythos_bot.py — add import after diag_handler import
if ! grep -q "inspect_handler" "$BOT_DIR/mythos_bot.py"; then
    echo "  → Adding import to mythos_bot.py"
    sed -i '/from handlers.diag_handler import handle_diag/a from handlers.inspect_handler import handle_inspect' "$BOT_DIR/mythos_bot.py"
else
    echo "  → Import already exists, skipping"
fi

# 3. Register command handler — add after diag handler registration
if ! grep -q "handle_inspect" "$BOT_DIR/mythos_bot.py"; then
    echo "  → Registering /inspect command handler"
    sed -i "/application.add_handler(CommandHandler('diag', handle_diag))/a\\    application.add_handler(CommandHandler('inspect', handle_inspect))" "$BOT_DIR/mythos_bot.py"
else
    echo "  → Handler already registered, skipping"
fi

# 4. Restart bot
echo "  → Restarting mythos-bot service"
sudo systemctl restart mythos-bot.service
sleep 2

# 5. Verify
STATUS=$(systemctl is-active mythos-bot.service)
if [ "$STATUS" = "active" ]; then
    echo "✅ Patch 0123 installed successfully. Bot is active."
    echo "   Try: /inspect or /inspect todo"
else
    echo "⚠️  Bot may not have started cleanly. Check: journalctl -u mythos-bot -n 30"
fi
