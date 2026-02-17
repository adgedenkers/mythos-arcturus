#!/bin/bash
# Patch 0093: Bill persistence + Forecast view
# Version: 1.15.8
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Patch 0093: Bill Persistence + Forecast v1.15.8 ==="

echo "[1] Running database migration..."
sudo -u postgres psql -d mythos -f "$SCRIPT_DIR/migrate.sql"
echo "    ✓ bill_overrides table created"

echo "[2] Deploying finance API routes..."
sudo cp "$SCRIPT_DIR/opt/mythos/api/routes/finance.py" /opt/mythos/api/routes/finance.py
echo "    ✓ finance.py deployed"

echo "[3] Deploying dashboard template..."
sudo cp "$SCRIPT_DIR/opt/mythos/web/templates/dashboard.html" /opt/mythos/web/templates/dashboard.html
echo "    ✓ dashboard.html deployed"

echo "[4] Verifying bill_overrides table..."
COUNT=$(sudo -u postgres psql -d mythos -tAc "SELECT COUNT(*) FROM bill_overrides;" 2>/dev/null || echo "ERROR")
if [ "$COUNT" = "ERROR" ]; then
    echo "    ✗ Migration may have failed — check DB manually"
    exit 1
fi
echo "    ✓ bill_overrides table ready ($COUNT rows)"

echo "[5] Restarting API service..."
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
echo "=== Patch 0093 complete ==="
echo ""
echo "New features:"
echo "  • Bill overrides now persist to DB (bill_overrides table)"
echo "  • Reset button clears override, reverts to auto-match"
echo "  • Forecast section in sidebar with day-by-day timeline"
echo "  • Forecast: USAA+SUN combined or per-account, 14/30/45/60 days"
echo "  • Alert banner for overdraft risk or low balance"
