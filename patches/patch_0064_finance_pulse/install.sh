#!/bin/bash
# Patch 0064: Finance Pulse - Household Financial Visibility
# Adds /pulse command and weekly auto-send to Ka and Seraphe

set -e

echo "=== Installing Patch 0064: Finance Pulse ==="

# Copy pulse handler
cp opt/mythos/telegram_bot/handlers/pulse_handler.py /opt/mythos/telegram_bot/handlers/

echo "✓ Pulse handler installed"

# Update handlers __init__.py to export pulse_command
INIT_FILE="/opt/mythos/telegram_bot/handlers/__init__.py"

if ! grep -q "pulse_handler" "$INIT_FILE"; then
    echo "" >> "$INIT_FILE"
    echo "# Pulse handler (Patch 0064)" >> "$INIT_FILE"
    echo "from .pulse_handler import pulse_command, setup_pulse_scheduler" >> "$INIT_FILE"
    echo "✓ Added pulse exports to __init__.py"
else
    echo "✓ Pulse already in __init__.py"
fi

# Update main bot to register /pulse command and scheduler
BOT_FILE="/opt/mythos/telegram_bot/mythos_bot.py"

# Backup
cp "$BOT_FILE" "$BOT_FILE.bak.$(date +%Y%m%d_%H%M%S)"

# Add import if not present
if ! grep -q "pulse_command" "$BOT_FILE"; then
    # Find the line with help_handler import and add after it
    sed -i '/from handlers.help_handler import/a\
\
# Pulse handler (household finance visibility)\
from handlers.pulse_handler import pulse_command, setup_pulse_scheduler' "$BOT_FILE"
    echo "✓ Added pulse import to bot"
else
    echo "✓ Pulse import already present"
fi

# Add command handler registration if not present
if ! grep -q "pulse_command" "$BOT_FILE" || ! grep -q 'CommandHandler.*pulse' "$BOT_FILE"; then
    # Find where other finance commands are registered and add pulse
    # Look for the pattern of adding handlers
    sed -i '/application.add_handler(CommandHandler("snapshot"/a\
    application.add_handler(CommandHandler("pulse", pulse_command))' "$BOT_FILE"
    echo "✓ Added /pulse command handler"
else
    echo "✓ /pulse handler already registered"
fi

# Add scheduler setup before application.run_polling()
if ! grep -q "setup_pulse_scheduler" "$BOT_FILE"; then
    sed -i '/application.run_polling/i\
    # Set up weekly pulse scheduler\
    setup_pulse_scheduler(application)\
' "$BOT_FILE"
    echo "✓ Added pulse scheduler setup"
else
    echo "✓ Pulse scheduler already configured"
fi

echo ""
echo "=== Restarting bot service ==="
sudo systemctl restart mythos-bot.service
sleep 2

if systemctl is-active --quiet mythos-bot.service; then
    echo "✓ Bot service restarted successfully"
else
    echo "✗ Bot service failed to start - check logs:"
    echo "  journalctl -u mythos-bot.service -n 50"
    exit 1
fi

echo ""
echo "=== Patch 0064 Complete ==="
echo ""
echo "New command: /pulse"
echo "  - Shows current checking balances"
echo "  - Bills due next 14 days"
echo "  - Income expected next 14 days"
echo "  - 14-day projection with status"
echo ""
echo "Weekly auto-send: Sundays at 6:00 PM EST"
echo "  - Sends to TELEGRAM_ID_KA and TELEGRAM_ID_SERAPHE"
echo "  - Update .env with correct Seraphe ID when available"
echo ""
echo "Test with: /pulse"
