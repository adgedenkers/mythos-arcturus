#!/bin/bash
# Patch 0018: Sunmark Description Cleanup
# Improves Sunmark transaction descriptions by:
# - Stripping generic prefixes like "Point Of Sale Withdrawal"
# - Extracting clean merchant names and locations
# - Adding transaction type tags like (POS), (ATM), (EXT)

set -e

echo "Installing patch 0018: Sunmark Description Cleanup"

# Copy updated parser
cp opt/mythos/finance/parsers.py /opt/mythos/finance/parsers.py
echo "✓ Updated parsers.py"

# Copy update script
cp opt/mythos/finance/update_sunmark_descriptions.py /opt/mythos/finance/update_sunmark_descriptions.py
chmod +x /opt/mythos/finance/update_sunmark_descriptions.py
echo "✓ Added update_sunmark_descriptions.py"

# Run dry-run first to show what will change
echo ""
echo "=== Preview of changes ==="
cd /opt/mythos/finance
/opt/mythos/.venv/bin/python3 update_sunmark_descriptions.py --dry-run

echo ""
read -p "Apply these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    /opt/mythos/.venv/bin/python3 update_sunmark_descriptions.py
    echo "✓ Patch 0018 complete"
else
    echo "Skipped database update. Run manually with:"
    echo "  cd /opt/mythos/finance && /opt/mythos/.venv/bin/python3 update_sunmark_descriptions.py"
fi
