#!/bin/bash
# Patch 0091: Transaction Editor UI
set -e

echo "=== Patch 0091: Transaction Editor UI ==="

echo "[1] Deploying finance API routes..."
cp "$(dirname "$0")/opt/mythos/api/routes/finance.py" /opt/mythos/api/routes/finance.py
echo "    ✓ finance.py deployed (added PATCH /transactions/{id} and /categories)"

echo "[2] Deploying dashboard template..."
cp "$(dirname "$0")/opt/mythos/web/templates/dashboard.html" /opt/mythos/web/templates/dashboard.html
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
echo "=== Patch 0091 complete ==="
echo ""
echo "Visit https://mythos-api.denkers.co/app/finance/ to see the transaction editor."
echo ""
echo "New features:"
echo "  • Transaction table with filters (month, account, category, search)"
echo "  • Click 'Edit' on any row to edit description and category inline"
echo "  • PATCH /api/finance/transactions/{id} endpoint"
echo "  • GET /api/finance/categories endpoint"
