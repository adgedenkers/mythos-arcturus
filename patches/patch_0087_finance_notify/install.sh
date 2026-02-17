#!/bin/bash
# Patch 0087: Finance Import Notification Fix
# Always sends Telegram notification after CSV import (not just when imported > 0)

set -e
VENV_PYTHON="/opt/mythos/.venv/bin/python3"

echo "=== Patch 0087: Finance Import Notification Fix ==="

echo "[1] Applying patch to patch monitor..."
$VENV_PYTHON "$(dirname "$0")/opt/mythos/apply_patch.py"

echo "[2] Restarting patch monitor service..."
sudo systemctl restart mythos-patch-monitor.service
sleep 2

STATUS=$(sudo systemctl is-active mythos-patch-monitor.service)
if [ "$STATUS" = "active" ]; then
    echo "    ✓ mythos-patch-monitor.service is active"
else
    echo "    ✗ Service status: $STATUS"
    exit 1
fi

echo ""
echo "=== Patch 0087 complete ==="
echo ""
echo "Drop a bank CSV in ~/Downloads to verify you get a Telegram notification."
echo "All-skipped imports will now send: ℹ️ Finance Import — Up to Date"
echo "New transaction imports will send: ✅ Finance Import Complete"
