#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Patch 0096: Routines Engine & Checkin System ==="

# Run database migration
echo "Running database migration..."
sudo -u postgres psql -d mythos -f "$SCRIPT_DIR/opt/mythos/core/migration_0096_routines.sql"

# Copy core engine
echo "Installing routines_engine.py..."
sudo mkdir -p /opt/mythos/core
sudo cp "$SCRIPT_DIR/opt/mythos/core/routines_engine.py" /opt/mythos/core/routines_engine.py
sudo cp "$SCRIPT_DIR/opt/mythos/core/migration_0096_routines.sql" /opt/mythos/core/migration_0096_routines.sql

# Copy Telegram handler
echo "Installing checkin_handler.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/telegram_bot/handlers/checkin_handler.py" /opt/mythos/telegram_bot/handlers/checkin_handler.py

echo ""
echo "=== MANUAL STEPS REQUIRED ==="
echo ""
echo "1. Add to /opt/mythos/telegram_bot/mythos_bot.py imports:"
echo "   from handlers.checkin_handler import handle_checkin, handle_routines, handle_rdone, handle_rskip, handle_routine_add"
echo ""
echo "2. Add command registrations (before the MessageHandler lines):"
echo "   application.add_handler(CommandHandler('checkin', handle_checkin))"
echo "   application.add_handler(CommandHandler('routines', handle_routines))"
echo "   application.add_handler(CommandHandler('rdone', handle_rdone))"
echo "   application.add_handler(CommandHandler('rskip', handle_rskip))"
echo "   application.add_handler(CommandHandler('routine_add', handle_routine_add))"
echo ""
echo "3. Restart the bot:"
echo "   sudo systemctl restart mythos-bot.service"
echo ""
echo "4. Test:"
echo "   /checkin  — morning briefing"
echo "   /routines — today's routine list"
echo "   /rdone 1  — complete first routine"
echo "   /rskip 2  — skip second routine"
echo ""
echo "=== Patch 0096 installed ==="
