#!/bin/bash
# Patch 0092: Finance Hub — Sidebar nav, Bills tracker, Categories CRUD, Accounts balance update
# Version: 1.15.7
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Patch 0092: Finance Hub v1.15.7 ==="

echo "[1] Deploying finance API routes..."
sudo cp "$SCRIPT_DIR/opt/mythos/api/routes/finance.py" /opt/mythos/api/routes/finance.py
echo "    ✓ finance.py deployed"

echo "[2] Deploying dashboard template..."
sudo cp "$SCRIPT_DIR/opt/mythos/web/templates/dashboard.html" /opt/mythos/web/templates/dashboard.html
echo "    ✓ dashboard.html deployed"

echo "[3] Restarting API service..."
sudo systemctl restart mythos-api.service
sleep 2

STATUS=$(sudo systemctl is-active mythos-api.service)
if [ "$STATUS" = "active" ]; then
    echo "    ✓ mythos-api.service is active"
else
    echo "    ✗ Service status: $STATUS"
    exit 1
fi

echo ""
echo "=== Patch 0092 complete ==="
echo ""
echo "New features at https://mythos-api.denkers.co/app/finance/:"
echo "  • Sidebar nav: Overview | Transactions | Bills | Categories | Accounts"
echo "  • Overview: summary cards + mini bills + mini spending"
echo "  • Bills: auto-matched + manual override per bill"
echo "  • Categories: rename, merge, delete with transaction counts"
echo "  • Accounts: view all balances, update any account balance manually"
