#!/bin/bash
# Patch 0104: Weather Service and /weather Command
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "🌤 Installing Patch 0104: Weather Service"
echo "======================================================"

# 1. Copy core files (NO sudo - adge owns /opt/mythos)
echo "Step 1/4: Installing weather service..."
cp "$PATCH_DIR/opt/mythos/core/weather_service.py" "$MYTHOS_ROOT/core/"
echo "  ✓ core/weather_service.py installed"

# 2. Copy handler
echo "Step 2/4: Installing weather handler..."
cp "$PATCH_DIR/opt/mythos/telegram_bot/handlers/weather_handler.py" "$MYTHOS_ROOT/telegram_bot/handlers/"
echo "  ✓ weather_handler.py installed"

# 3. Update analyst to use shared weather service
echo "Step 3/4: Updating analyst to use weather service..."
cd "$MYTHOS_ROOT"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/update_analyst.py"
echo "  ✓ Analyst updated"

# 4. Restart bot
echo "Step 4/4: Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 2

if systemctl is-active --quiet mythos-bot.service; then
    echo "  ✓ Bot running"
else
    echo "  ✗ Bot failed to start!"
    sudo journalctl -u mythos-bot.service -n 10 --no-pager
    exit 1
fi

echo ""
echo "======================================================"
echo "✅ Patch 0104 installed"
echo ""
echo "⚠️  WIRING REQUIRED:"
echo "  Add to mythos_bot.py imports:"
echo "    from telegram_bot.handlers.weather_handler import cmd_weather"
echo ""
echo "  Add command handler (after calendar line):"
echo "    application.add_handler(CommandHandler('weather', cmd_weather))"
echo ""
echo "  Then restart: sudo systemctl restart mythos-bot.service"
echo ""
echo "Commands:"
echo "  /weather              → Oxford, NY (default)"
echo "  /weather 13827        → By zip code"
echo "  /weather Denver, CO   → By city/state"
echo "======================================================"
