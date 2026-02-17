#!/bin/bash
# Patch 0089: Importer --allow-dupes flag
set -e

echo "=== Patch 0089: Importer --allow-dupes flag ==="

echo "[1] Deploying importer.py v5..."
cp "$(dirname "$0")/opt/mythos/finance/importer.py" /opt/mythos/finance/importer.py
echo "    ✓ importer.py deployed"

echo ""
echo "=== Patch 0089 complete ==="
echo ""
echo "New flag: --allow-dupes"
echo ""
echo "Usage:"
echo "  Normal import (skips true duplicates):"
echo "    python importer.py usaa file.csv --balance 3148.02"
echo ""
echo "  Force-import known duplicate transactions:"
echo "    python importer.py usaa file.csv --balance 3148.02 --allow-dupes"
echo ""
echo "Note: --allow-dupes uses row-index hashing. Re-importing the same"
echo "file with --allow-dupes is safe as long as the file hasn't changed."
