#!/bin/bash
# Patch 0102: Backlog Intelligence System
# - Schema migration: idea_backlog upgrade + backlog_analysis table
# - Core: backlog_analyst.py + morning_briefing.py
# - Handler: analyst_handler.py (Telegram commands)
# - Docs: TODO.md rebuilt

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧠 Installing Patch 0102: Backlog Intelligence System"
echo "======================================================"

# --- Database Migration ---
echo ""
echo "📊 Running database migration..."
sudo -u postgres psql -d mythos -f "$SCRIPT_DIR/migration.sql"
echo "✅ Database migration complete"

# --- Core Files ---
echo ""
echo "📦 Installing core files..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/backlog_analyst.py" /opt/mythos/core/backlog_analyst.py
sudo cp "$SCRIPT_DIR/opt/mythos/core/morning_briefing.py" /opt/mythos/core/morning_briefing.py
sudo chown root:root /opt/mythos/core/backlog_analyst.py /opt/mythos/core/morning_briefing.py
sudo chmod 644 /opt/mythos/core/backlog_analyst.py /opt/mythos/core/morning_briefing.py
echo "✅ Core files installed"

# --- Telegram Handler ---
echo ""
echo "📱 Installing Telegram handler..."
sudo cp "$SCRIPT_DIR/opt/mythos/telegram_bot/handlers/analyst_handler.py" /opt/mythos/telegram_bot/handlers/analyst_handler.py
sudo chown root:root /opt/mythos/telegram_bot/handlers/analyst_handler.py
sudo chmod 644 /opt/mythos/telegram_bot/handlers/analyst_handler.py
echo "✅ Handler installed"

# --- Documentation ---
echo ""
echo "📝 Updating TODO.md..."
sudo cp "$SCRIPT_DIR/opt/mythos/docs/TODO.md" /opt/mythos/docs/TODO.md
sudo chown root:root /opt/mythos/docs/TODO.md
sudo chmod 644 /opt/mythos/docs/TODO.md
echo "✅ TODO.md updated"

# --- Restart Services ---
echo ""
echo "🔄 Restarting services..."
sudo systemctl restart mythos-bot.service
sudo systemctl restart mythos-api.service
echo "✅ Services restarted"

echo ""
echo "======================================================"
echo "✅ Patch 0102 installed successfully!"
echo ""
echo "New Telegram commands:"
echo "  /briefing     — Run analysis now, get briefing"
echo "  /analyze      — Alias for /briefing"  
echo "  /priorities   — Show current priority queue"
echo "  /transfers    — Show transfer recommendations"
echo ""
echo "Morning briefing: 3:00 AM daily via Telegram"
echo "Evening review:   9:00 PM (only sends if urgent items)"
echo ""
echo "Test manually:"
echo "  /opt/mythos/.venv/bin/python3 /opt/mythos/core/backlog_analyst.py morning"
echo ""
echo "⚠️  IMPORTANT: You need to wire up the handlers in mythos_bot.py"
echo "  and start the morning briefing scheduler. See WIRING below."
echo ""
echo "=== WIRING INSTRUCTIONS ==="
echo ""
echo "1. In mythos_bot.py, add these imports:"
echo "   from telegram_bot.handlers.analyst_handler import cmd_briefing, cmd_priorities, cmd_transfers"
echo ""
echo "2. Add these command handlers:"
echo "   app.add_handler(CommandHandler('briefing', cmd_briefing))"
echo "   app.add_handler(CommandHandler('analyze', cmd_briefing))"
echo "   app.add_handler(CommandHandler('priorities', cmd_priorities))"
echo "   app.add_handler(CommandHandler('transfers', cmd_transfers))"
echo ""
echo "3. For the morning briefing scheduler, add after app is built:"
echo "   from core.morning_briefing import MorningBriefing"
echo "   morning = MorningBriefing(app)"
echo "   morning.start()"
echo ""
echo "Then restart: sudo systemctl restart mythos-bot.service"
echo "======================================================"
