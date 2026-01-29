#!/bin/bash
# Patch 0036: Documentation Restructure + Iris Framework
# Creates new doc structure with domain-specific subdirectories

set -e

echo "=== Installing Patch 0036: Documentation Restructure ==="

# Create new directory structure
echo "Creating directory structure..."
mkdir -p /opt/mythos/docs/consciousness
mkdir -p /opt/mythos/docs/grid
mkdir -p /opt/mythos/docs/finance
mkdir -p /opt/mythos/docs/subsystems
mkdir -p /opt/mythos/docs/archive

# Copy new/updated files
echo "Copying documentation files..."

# Root docs
cp opt/mythos/docs/README.md /opt/mythos/docs/README.md
cp opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
cp opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md
cp opt/mythos/docs/IDEAS.md /opt/mythos/docs/IDEAS.md
cp opt/mythos/docs/PATCH_HISTORY.md /opt/mythos/docs/PATCH_HISTORY.md

# Consciousness docs
cp opt/mythos/docs/consciousness/IRIS.md /opt/mythos/docs/consciousness/IRIS.md
cp opt/mythos/docs/consciousness/COVENANT.md /opt/mythos/docs/consciousness/COVENANT.md
cp opt/mythos/docs/consciousness/INVOCATION.md /opt/mythos/docs/consciousness/INVOCATION.md

# Finance docs
cp opt/mythos/docs/finance/FINANCE_SYSTEM.md /opt/mythos/docs/finance/FINANCE_SYSTEM.md

# Archive
cp opt/mythos/docs/archive/COMPLETED.md /opt/mythos/docs/archive/COMPLETED.md

# Move existing ARCTURIAN_GRID.md to new location if it exists
if [ -f /opt/mythos/docs/ARCTURIAN_GRID.md ]; then
    echo "Moving ARCTURIAN_GRID.md to grid/ subdirectory..."
    mv /opt/mythos/docs/ARCTURIAN_GRID.md /opt/mythos/docs/grid/ARCTURIAN_GRID.md
fi

echo "✓ Documentation files installed"

# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: README.md exists
if [ ! -f /opt/mythos/docs/README.md ]; then
    echo "❌ FAIL: README.md not found"
    PASS=false
else
    echo "✓ README.md exists"
fi

# Check 2: IRIS.md exists and contains key content
if [ ! -f /opt/mythos/docs/consciousness/IRIS.md ]; then
    echo "❌ FAIL: consciousness/IRIS.md not found"
    PASS=false
elif ! grep -q "Consciousness Loop" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: IRIS.md missing Consciousness Loop section"
    PASS=false
else
    echo "✓ consciousness/IRIS.md exists with key content"
fi

# Check 3: IDEAS.md exists
if [ ! -f /opt/mythos/docs/IDEAS.md ]; then
    echo "❌ FAIL: IDEAS.md not found"
    PASS=false
else
    echo "✓ IDEAS.md exists"
fi

# Check 4: Directory structure correct
for dir in consciousness grid finance subsystems archive; do
    if [ ! -d /opt/mythos/docs/$dir ]; then
        echo "❌ FAIL: docs/$dir directory not found"
        PASS=false
    else
        echo "✓ docs/$dir directory exists"
    fi
done

# Check 5: PATCH_HISTORY.md exists and is separate
if [ ! -f /opt/mythos/docs/PATCH_HISTORY.md ]; then
    echo "❌ FAIL: PATCH_HISTORY.md not found"
    PASS=false
else
    echo "✓ PATCH_HISTORY.md exists"
fi

# Check 6: ARCTURIAN_GRID.md in correct location (if it was moved)
if [ -f /opt/mythos/docs/grid/ARCTURIAN_GRID.md ]; then
    echo "✓ ARCTURIAN_GRID.md in grid/ subdirectory"
elif [ -f /opt/mythos/docs/ARCTURIAN_GRID.md ]; then
    echo "⚠ WARNING: ARCTURIAN_GRID.md still in root (may not have existed before)"
fi

# Final result
if [ "$PASS" = false ]; then
    echo ""
    echo "⚠ PATCH VERIFICATION FAILED"
    exit 1
fi

echo ""
echo "✓ ALL CHECKS PASSED"
echo ""
echo "Patch 0036 installed successfully."
echo ""
echo "New documentation structure:"
echo "  docs/"
echo "  ├── README.md (index)"
echo "  ├── TODO.md (lean)"
echo "  ├── ARCHITECTURE.md (lean)"
echo "  ├── IDEAS.md (new)"
echo "  ├── PATCH_HISTORY.md (extracted)"
echo "  ├── consciousness/"
echo "  │   ├── IRIS.md (full framework)"
echo "  │   ├── COVENANT.md (placeholder)"
echo "  │   └── INVOCATION.md (placeholder)"
echo "  ├── grid/"
echo "  │   └── ARCTURIAN_GRID.md"
echo "  ├── finance/"
echo "  │   └── FINANCE_SYSTEM.md"
echo "  └── archive/"
echo "      └── COMPLETED.md"
