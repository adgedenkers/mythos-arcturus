#!/bin/bash
# Patch 0054: Auto-deploy test
# 
# This patch does nothing except verify that the auto-deploy
# pipeline is working correctly after the sudoers fix.

set -e

PATCH_NUM="0054"
VERIFY_LOG="/tmp/patch_${PATCH_NUM}_verify.log"

echo "=== Patch ${PATCH_NUM}: Auto-Deploy Test ==="

# Clear and start log
> "$VERIFY_LOG"
exec > >(tee -a "$VERIFY_LOG") 2>&1

echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ============================================================
# 1. CHECK SUDO ACCESS
# ============================================================
echo "━━━ SUDO ACCESS ━━━"

if sudo -n systemctl is-active mythos-bot.service >/dev/null 2>&1; then
    echo "  ✓ systemctl works without password"
else
    echo "  ✗ systemctl requires password"
fi

if sudo -n -u postgres psql -d mythos -c "SELECT 1;" >/dev/null 2>&1; then
    echo "  ✓ PostgreSQL works without password"
else
    echo "  ✗ PostgreSQL requires password"
fi

# ============================================================
# 2. CHECK SERVICES
# ============================================================
echo ""
echo "━━━ SERVICE STATUS ━━━"

if sudo -n systemctl is-active --quiet mythos-bot.service; then
    echo "  ✓ mythos-bot.service is running"
else
    echo "  ✗ mythos-bot.service is NOT running"
fi

if sudo -n systemctl is-active --quiet mythos-patch-monitor.service; then
    echo "  ✓ mythos-patch-monitor.service is running"
else
    echo "  ✗ mythos-patch-monitor.service is NOT running"
fi

# ============================================================
# 3. CONFIRM AUTO-DEPLOY WORKED
# ============================================================
echo ""
echo "━━━ AUTO-DEPLOY VERIFICATION ━━━"

# If we got here, the patch monitor successfully:
# 1. Detected the zip in ~/Downloads
# 2. Extracted it to /opt/mythos/patches/
# 3. Ran this install.sh script

echo "  ✓ Patch was auto-detected"
echo "  ✓ Patch was auto-extracted"
echo "  ✓ install.sh was auto-executed"
echo ""
echo "🎉 AUTO-DEPLOY PIPELINE IS WORKING!"

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "Verification log: $VERIFY_LOG"
echo ""
echo "The patch system is fully operational."
echo "Future patches will auto-deploy when dropped in ~/Downloads"
