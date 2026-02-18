#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Patch 0100: Knowledge Map Auto-Rebuild ==="

# Run migration (triggers)
echo "Creating DB triggers..."
sudo -u postgres psql -d mythos -f "$SCRIPT_DIR/opt/mythos/core/migration_0100_triggers.sql"

# Copy builder
echo "Installing knowledge_map_builder.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/knowledge_map_builder.py" /opt/mythos/core/knowledge_map_builder.py

# Install service
echo "Installing systemd service..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/mythos-knowledge-map.service" /etc/systemd/system/mythos-knowledge-map.service
sudo systemctl daemon-reload
sudo systemctl enable mythos-knowledge-map.service
sudo systemctl start mythos-knowledge-map.service

# Do initial rebuild
echo "Running initial knowledge map rebuild..."
/opt/mythos/.venv/bin/python3 /opt/mythos/core/knowledge_map_builder.py

sleep 2
echo ""

# Verify
systemctl status mythos-knowledge-map.service --no-pager | head -5

echo ""
echo "=== Done ==="
echo ""
echo "How it works:"
echo "  1. You add/edit/delete a bill, account, or routine in PostgreSQL"
echo "  2. DB trigger fires pg_notify"
echo "  3. Listener catches it, rebuilds KNOWLEDGE_MAP.md from DB"
echo "  4. Extractor picks up new map on next message (file mtime check)"
echo ""
echo "Test: add a fake bill, check the map, delete the fake bill"
echo "  sudo -u postgres psql -d mythos -c \"INSERT INTO recurring_bills (merchant_name, expected_amount, expected_day, is_active) VALUES ('Test Bill', 99.99, 1, true);\""
echo "  sleep 2 && grep 'Test Bill' /opt/mythos/docs/KNOWLEDGE_MAP.md"
echo "  sudo -u postgres psql -d mythos -c \"DELETE FROM recurring_bills WHERE merchant_name = 'Test Bill';\""
