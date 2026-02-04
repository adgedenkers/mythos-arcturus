#!/bin/bash
# Test the finance importer with dry-run mode
# Run this BEFORE deploying the patch

echo "=== Testing Finance Importer v2 ==="
echo ""

IMPORTER="/home/claude/patch_0065_finance_importer/opt/mythos/finance/importer.py"
SUNMARK_FILE="/home/adge/finance/sunmark_20260204_151404.CSV"
USAA_FILE="/home/adge/finance/usaa_20260204_151550.csv"
USAA_BALANCE="1243.19"

# Activate venv
source /opt/mythos/.venv/bin/activate

echo "=== SUNMARK DRY RUN ==="
python "$IMPORTER" sunmark "$SUNMARK_FILE" --dry-run --verbose
echo ""

echo "=== USAA DRY RUN ==="
python "$IMPORTER" usaa "$USAA_FILE" --balance "$USAA_BALANCE" --dry-run --verbose
echo ""

echo "=== If the above looks correct, run the actual import: ==="
echo ""
echo "# Sunmark (has balance in CSV):"
echo "python $IMPORTER sunmark $SUNMARK_FILE --verbose"
echo ""
echo "# USAA (provide current balance):"
echo "python $IMPORTER usaa $USAA_FILE --balance $USAA_BALANCE --verbose"
