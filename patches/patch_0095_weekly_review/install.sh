#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Patch 0095: Weekly Financial Review ==="

# Copy finance review generator
echo "Installing weekly_review.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/finance/weekly_review.py" /opt/mythos/finance/weekly_review.py
sudo chmod +x /opt/mythos/finance/weekly_review.py

# Copy Telegram handler
echo "Installing review_handler.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/telegram_bot/handlers/review_handler.py" /opt/mythos/telegram_bot/handlers/review_handler.py

# Copy API route
echo "Installing review API route..."
sudo cp "$SCRIPT_DIR/opt/mythos/api/routes/review.py" /opt/mythos/api/routes/review.py

# Register Telegram command
# User needs to add to mythos_bot.py:
echo ""
echo "=== MANUAL STEPS REQUIRED ==="
echo ""
echo "1. Add to /opt/mythos/telegram_bot/mythos_bot.py imports:"
echo "   from handlers.review_handler import handle_review"
echo ""
echo "2. Add to the command registration section:"
echo "   application.add_handler(CommandHandler('review', handle_review))"
echo ""
echo "3. Add to /opt/mythos/api/main.py:"
echo "   from api.routes.review import router as review_router"
echo "   app.include_router(review_router, prefix='/api/finance', tags=['finance'])"
echo ""
echo "4. Restart services:"
echo "   sudo systemctl restart mythos-bot.service"
echo "   sudo systemctl restart mythos-api.service"
echo ""
echo "5. Test:"
echo "   /opt/mythos/.venv/bin/python3 /opt/mythos/finance/weekly_review.py"
echo "   /opt/mythos/.venv/bin/python3 /opt/mythos/finance/weekly_review.py --json"
echo ""
echo "=== Patch 0095 installed ==="
