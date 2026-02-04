#!/bin/bash
# Patch 0065: Finance Importer v2
# Clean import system with proper bank-specific parsing

set -e

echo "=== Installing Patch 0065: Finance Importer v2 ==="

# Backup old importer if it exists
if [ -f /opt/mythos/finance/import_transactions.py ]; then
    cp /opt/mythos/finance/import_transactions.py /opt/mythos/finance/import_transactions.py.bak.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backed up old importer"
fi

# Install new importer
cp opt/mythos/finance/importer.py /opt/mythos/finance/
chmod +x /opt/mythos/finance/importer.py
echo "✓ Installed new importer"

# Install documentation
mkdir -p /opt/mythos/docs/finance
cp opt/mythos/docs/finance/IMPORT_SYSTEM.md /opt/mythos/docs/finance/
echo "✓ Installed documentation"

# Create symlink for convenience
ln -sf /opt/mythos/finance/importer.py /opt/mythos/bin/finance-import 2>/dev/null || true

echo ""
echo "=== Patch 0065 Complete ==="
echo ""
echo "Usage:"
echo "  # Sunmark (balance comes from CSV):"
echo "  python /opt/mythos/finance/importer.py sunmark /path/to/download.CSV --verbose"
echo ""
echo "  # USAA (must provide current balance):"
echo "  python /opt/mythos/finance/importer.py usaa /path/to/bk_download.csv --balance 1243.19 --verbose"
echo ""
echo "  # Dry run (test without importing):"
echo "  python /opt/mythos/finance/importer.py sunmark /path/to/file.CSV --dry-run --verbose"
echo ""
echo "Documentation: /opt/mythos/docs/finance/IMPORT_SYSTEM.md"
