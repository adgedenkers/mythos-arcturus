#!/bin/bash
# Patch 0052: Fix snapshot handler registration + Add verify pattern
# 
# Fixes:
# - Properly registers snapshot_handler import
# - Adds /snapshot and /setbal commands to bot
#
# New:
# - Introduces verify_install.sh pattern for post-install checks

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_NUM="0052"
VERIFY_LOG="/tmp/patch_${PATCH_NUM}_verify.log"

echo "=== Patch ${PATCH_NUM}: Snapshot Handler Fix ==="

# ============================================================
# 1. ADD IMPORT FOR SNAPSHOT_HANDLER
# ============================================================
echo "Adding snapshot_handler import..."

BOT_FILE="/opt/mythos/telegram_bot/mythos_bot.py"

# Check if already imported
if grep -q "from handlers.snapshot_handler import" "$BOT_FILE"; then
    echo "  → snapshot_handler already imported"
else
    # Add import after the finance_handler import block
    # Find the line with "from handlers.finance_handler import" and add after the closing paren
    sed -i '/from handlers.finance_handler import/,/)/{
        /)/{
            a\
from handlers.snapshot_handler import (\
    snapshot_command,\
    setbal_command\
)
        }
    }' "$BOT_FILE"
    echo "  → Added snapshot_handler import"
fi

# ============================================================
# 2. REGISTER COMMAND HANDLERS
# ============================================================
echo "Registering command handlers..."

# Check if snapshot command already registered
if grep -q 'CommandHandler("snapshot"' "$BOT_FILE"; then
    echo "  → /snapshot already registered"
else
    # Add after setbalance command
    sed -i '/CommandHandler("setbalance", setbalance_command)/a\    application.add_handler(CommandHandler("snapshot", snapshot_command))\n    application.add_handler(CommandHandler("setbal", setbal_command))' "$BOT_FILE"
    echo "  → Added /snapshot and /setbal commands"
fi

# ============================================================
# 3. INSTALL VERIFY SCRIPT (NEW PATTERN)
# ============================================================
echo "Installing verify script..."
cp "$PATCH_DIR/opt/mythos/patches/scripts/verify_install.sh" /opt/mythos/patches/scripts/
chmod +x /opt/mythos/patches/scripts/verify_install.sh

# ============================================================
# 4. RESTART BOT
# ============================================================
echo "Restarting Telegram bot..."
sudo systemctl restart mythos-bot.service

# Wait for startup
sleep 3

# ============================================================
# 5. RUN VERIFICATION
# ============================================================
echo "Running verification..."
/opt/mythos/patches/scripts/verify_install.sh "$PATCH_NUM" > "$VERIFY_LOG" 2>&1

# Show summary
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "Verification log: $VERIFY_LOG"
echo ""
echo "Quick check:"
tail -20 "$VERIFY_LOG"
echo ""
echo "Full results: cat $VERIFY_LOG"
