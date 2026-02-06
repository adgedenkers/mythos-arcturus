#!/bin/bash
# Patch 0067: Fix patch monitor bugs
# - Fix UnboundLocalError in finally blocks (referenced 'e' outside except scope)
# - Add missing notify_finance_import() method
# - Add send_notification.py for Telegram notifications
# - Fix finally blocks to properly clean up self.processing
# - Rename methods to _private convention for internal methods

set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Patch 0067: Fix Patch Monitor Bugs ==="

# 1. Install fixed patch monitor
echo "Installing fixed mythos_patch_monitor.py..."
cp "$PATCH_DIR/opt/mythos/mythos_patch_monitor.py" "$MYTHOS_ROOT/mythos_patch_monitor.py"
echo "  ✓ Patch monitor updated"

# 2. Install send_notification.py
echo "Installing send_notification.py..."
cp "$PATCH_DIR/opt/mythos/telegram_bot/send_notification.py" "$MYTHOS_ROOT/telegram_bot/send_notification.py"
chmod +x "$MYTHOS_ROOT/telegram_bot/send_notification.py"
echo "  ✓ Notification script installed"

# 3. Check if TELEGRAM_ADMIN_CHAT_ID is set in .env
if grep -q "TELEGRAM_ADMIN_CHAT_ID" "$MYTHOS_ROOT/.env" 2>/dev/null; then
    echo "  ✓ TELEGRAM_ADMIN_CHAT_ID already in .env"
else
    echo ""
    echo "  ⚠️  TELEGRAM_ADMIN_CHAT_ID not found in .env"
    echo "  To enable notifications, add to /opt/mythos/.env:"
    echo "    TELEGRAM_ADMIN_CHAT_ID=<your_telegram_chat_id>"
    echo ""
fi

# 4. Restart patch monitor
echo "Restarting patch monitor..."
sudo systemctl restart mythos-patch-monitor.service
sleep 2

# Check if it started OK
if systemctl is-active --quiet mythos-patch-monitor.service; then
    echo "  ✓ Patch monitor running"
else
    echo "  ✗ Patch monitor failed to start!"
    sudo journalctl -u mythos-patch-monitor.service --no-pager -n 10
    exit 1
fi

echo ""
echo "=== Patch 0067 Complete ==="
echo ""
echo "Fixes applied:"
echo "  1. Fixed UnboundLocalError in all finally blocks"
echo "  2. Added _notify_finance_import() method"
echo "  3. Added send_notification.py for Telegram alerts"
echo "  4. Fixed self.processing cleanup in finally blocks"
echo ""
echo "To test auto-import:"
echo "  cp ~/Downloads/financial_temp/sunmark*.CSV ~/Downloads/"
echo "  sudo tail -f /var/log/mythos_patch_monitor.log"
