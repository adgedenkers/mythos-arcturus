#!/bin/bash
# patch_0030_finance_auto_import - Add bank CSV auto-import to patch monitor
# 
# Adds support for auto-importing bank CSVs:
#   - USAA: bk_download.csv → auto-detected → account_id 2
#   - Sunmark: download.CSV → auto-detected → account_id 1
#
# Drop CSV files in ~/Downloads and they'll be:
#   1. Auto-detected by content (uses existing parsers)
#   2. Imported with deduplication
#   3. Archived to /opt/mythos/finance/archive/imports/

set -e

echo "=== patch_0030_finance_auto_import ==="

# Backup current monitor
if [ -f /opt/mythos/mythos_patch_monitor.py ]; then
    cp /opt/mythos/mythos_patch_monitor.py /opt/mythos/mythos_patch_monitor.py.bak
    echo "✓ Backed up existing monitor"
fi

# Copy new monitor
cp opt/mythos/mythos_patch_monitor.py /opt/mythos/mythos_patch_monitor.py
chmod +x /opt/mythos/mythos_patch_monitor.py
echo "✓ Installed updated patch monitor"

# Create archive directory for imports
mkdir -p /opt/mythos/finance/archive/imports
mkdir -p /opt/mythos/finance/archive/imports/errors
echo "✓ Created finance archive directories"

# Restart the service
sudo systemctl restart mythos-patch-monitor.service
echo "✓ Restarted mythos-patch-monitor service"

# Verify it's running
sleep 2
if systemctl is-active --quiet mythos-patch-monitor.service; then
    echo "✓ Service is running"
else
    echo "⚠ Service may not have started correctly"
    sudo systemctl status mythos-patch-monitor.service --no-pager
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Bank CSV auto-import is now active!"
echo ""
echo "Usage:"
echo "  1. Download CSV from your bank (no renaming needed!)"
echo "     - USAA downloads as: bk_download.csv"
echo "     - Sunmark downloads as: download.CSV"
echo "  2. File lands in ~/Downloads"
echo "  3. Monitor auto-detects bank from file content"
echo "  4. Imports with deduplication, archives when done"
echo ""
echo "Check logs: tail -f /var/log/mythos_patch_monitor.log"
