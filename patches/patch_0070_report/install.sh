#!/bin/bash
# Patch 0070: Monthly Financial Report Generator
set -e
MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Patch 0070: Financial Report Generator ==="

cp "$PATCH_DIR/opt/mythos/finance/report_template.html" "$MYTHOS_ROOT/finance/report_template.html"
cp "$PATCH_DIR/opt/mythos/finance/report_generator.py" "$MYTHOS_ROOT/finance/report_generator.py"
chmod +x "$MYTHOS_ROOT/finance/report_generator.py"
mkdir -p "$MYTHOS_ROOT/finance/reports"

echo "  ✓ Report generator installed"
echo ""
echo "Generate report:"
echo "  cd /opt/mythos/finance && /opt/mythos/.venv/bin/python3 report_generator.py"
echo ""
echo "Options:"
echo "  --months 3     Last 3 months only"
echo "  --output /path  Custom output path"
