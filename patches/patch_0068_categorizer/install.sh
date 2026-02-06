#!/bin/bash
# Patch 0068: Inline transaction categorization
# - New categorizer.py module (loads category_mappings, applies to transactions)
# - Updated importer.py v3 with inline categorization
# - Retroactively categorizes existing uncategorized transactions

set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$MYTHOS_ROOT/.venv/bin/python3"

echo "=== Patch 0068: Inline Transaction Categorization ==="

# 1. Install categorizer
echo "Installing categorizer.py..."
cp "$PATCH_DIR/opt/mythos/finance/categorizer.py" "$MYTHOS_ROOT/finance/categorizer.py"
echo "  ✓ Categorizer installed"

# 2. Install updated importer
echo "Installing importer.py v3..."
cp "$PATCH_DIR/opt/mythos/finance/importer.py" "$MYTHOS_ROOT/finance/importer.py"
echo "  ✓ Importer updated"

# 3. Retroactively categorize existing transactions
echo ""
echo "Categorizing existing transactions..."
cd "$MYTHOS_ROOT/finance"
$VENV_PY categorizer.py --verbose 2>&1 | tail -25
echo "  ✓ Retroactive categorization complete"

# 4. Restart patch monitor (it calls importer.py)
echo ""
echo "Restarting patch monitor..."
sudo systemctl restart mythos-patch-monitor.service
sleep 2

if systemctl is-active --quiet mythos-patch-monitor.service; then
    echo "  ✓ Patch monitor running"
else
    echo "  ✗ Patch monitor failed to start!"
    sudo journalctl -u mythos-patch-monitor.service --no-pager -n 10
fi

echo ""
echo "=== Patch 0068 Complete ==="
echo ""
echo "What's new:"
echo "  1. Transactions are categorized inline during import"
echo "  2. category_mappings table applied to description + original_description"
echo "  3. merchant_name populated from mappings"
echo "  4. Run 'python /opt/mythos/finance/categorizer.py' anytime to re-categorize"
echo "  5. Use --all flag to re-categorize everything (including already categorized)"
