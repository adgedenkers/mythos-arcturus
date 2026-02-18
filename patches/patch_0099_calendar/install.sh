#!/bin/bash
set -e

echo "=== Installing Patch 0099: Calendar Display ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy formatter
echo "Installing calendar_formatter.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/calendar_formatter.py" /opt/mythos/core/calendar_formatter.py

# Copy handler
echo "Installing calendar_handler.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/telegram_bot/handlers/calendar_handler.py" /opt/mythos/telegram_bot/handlers/calendar_handler.py

# Register in bot if not already
if grep -q "calendar_handler" /opt/mythos/telegram_bot/mythos_bot.py; then
    echo "✓ Already registered in bot"
else
    echo "Registering /calendar command..."
    # Add import after checkin_handler import
    sudo sed -i '/from handlers.checkin_handler import/a from handlers.calendar_handler import handle_calendar' /opt/mythos/telegram_bot/mythos_bot.py
    # Add command handler after routine_add
    sudo sed -i "/CommandHandler('routine_add'/a\\    application.add_handler(CommandHandler('calendar', handle_calendar))" /opt/mythos/telegram_bot/mythos_bot.py
    echo "✓ Registered"
fi

# Restart bot
echo "Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 2
echo "✓ Bot restarted"

echo ""
echo "=== Done ==="
echo "Try:"
echo "  /calendar         — this week"
echo "  /calendar today   — just today"
echo "  /calendar month   — full month with bills"
echo "  /calendar add 2/20 2pm Dentist for Fitz"
