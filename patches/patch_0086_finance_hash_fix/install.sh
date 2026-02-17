#!/bin/bash
# Patch 0086: Finance Hash Fix
# Fixes non-deterministic USAA hash, removes duplicates, rehashes all transactions

set -e
PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="/opt/mythos/.venv/bin/python3"
FINANCE_DIR="/opt/mythos/finance"

echo "=== Patch 0086: Finance Hash Fix ==="
echo ""

# 1. Deploy updated importer.py
echo "[1] Deploying importer.py v4..."
cp "$PATCH_DIR/opt/mythos/finance/importer.py" "$FINANCE_DIR/importer.py"
echo "    ✓ importer.py deployed"

# 2. Deploy rehash script
echo "[2] Deploying rehash script..."
mkdir -p "$FINANCE_DIR/scripts"
cp "$PATCH_DIR/opt/mythos/finance/scripts/rehash_transactions.py" "$FINANCE_DIR/scripts/rehash_transactions.py"
chmod +x "$FINANCE_DIR/scripts/rehash_transactions.py"
echo "    ✓ rehash_transactions.py deployed"

# 3. Run dry-run first so you can see what will change
echo ""
echo "[3] Running DRY RUN of rehash (no changes yet)..."
echo "----------------------------------------"
cd "$FINANCE_DIR"
$VENV_PYTHON "$FINANCE_DIR/scripts/rehash_transactions.py" --dry-run
echo "----------------------------------------"
echo ""

# 4. Run live rehash
echo "[4] Running LIVE rehash..."
echo "----------------------------------------"
$VENV_PYTHON "$FINANCE_DIR/scripts/rehash_transactions.py"
echo "----------------------------------------"
echo ""

echo "=== Patch 0086 complete ==="
echo ""
echo "Next steps:"
echo "  - Re-import your latest CSVs to verify no duplicates are created"
echo "  - Test: python importer.py usaa /path/to/file.csv --balance XXXX --dry-run"
