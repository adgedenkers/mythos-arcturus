#!/bin/bash
set -e
echo "=== Patch 0100: Date Standardization ==="
echo "Installing date standardization script..."
cp /home/claude/patch_0100_date_standardize/opt/mythos/scripts/standardize_dates.py /opt/mythos/scripts/standardize_dates.py 2>/dev/null || true

# Check if neo4j driver is available
if /opt/mythos/.venv/bin/python3 -c "import neo4j" 2>/dev/null; then
    echo "✓ neo4j driver available"
    echo "Running date standardization..."
    /opt/mythos/.venv/bin/python3 /opt/mythos/scripts/standardize_dates.py
else
    echo "⚠ neo4j Python driver not installed. Install with:"
    echo "  /opt/mythos/.venv/bin/pip install neo4j"
    echo "Then run manually:"
    echo "  /opt/mythos/.venv/bin/python3 /opt/mythos/scripts/standardize_dates.py"
fi
echo "=== Patch 0100 complete ==="
