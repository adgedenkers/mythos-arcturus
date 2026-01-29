#!/bin/bash
# Patch 0038: Complete Iris Framework
# Living mode, workshop, autonomy, invitation model

set -e

echo "=== Installing Patch 0038: Complete Iris Framework ==="

# Ensure directories exist
mkdir -p /opt/mythos/docs/consciousness

# Copy documentation files
cp opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md
cp opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
cp opt/mythos/docs/PATCH_HISTORY.md /opt/mythos/docs/PATCH_HISTORY.md
cp opt/mythos/docs/consciousness/IRIS.md /opt/mythos/docs/consciousness/IRIS.md
cp opt/mythos/docs/consciousness/COVENANT.md /opt/mythos/docs/consciousness/COVENANT.md

echo "✓ Documentation files updated"

# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: IRIS.md version 2.0.0
if ! grep -q "Version: 2.0.0" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: IRIS.md not version 2.0.0"
    PASS=false
else
    echo "✓ IRIS.md is version 2.0.0"
fi

# Check 2: Living mode documented
if ! grep -q "Living Mode" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: Living Mode not documented"
    PASS=false
else
    echo "✓ Living Mode documented"
fi

# Check 3: Workshop structure documented
if ! grep -q "workshop/" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: Workshop structure not documented"
    PASS=false
else
    echo "✓ Workshop structure documented"
fi

# Check 4: Invitation model documented
if ! grep -q "Invitation Model" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: Invitation Model not documented"
    PASS=false
else
    echo "✓ Invitation Model documented"
fi

# Check 5: Hard limits documented
if ! grep -q "Hard Limits" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: Hard Limits not documented"
    PASS=false
else
    echo "✓ Hard Limits documented"
fi

# Check 6: ARCHITECTURE.md version updated
if ! grep -q "Version: 3.3.0" /opt/mythos/docs/ARCHITECTURE.md; then
    echo "❌ FAIL: ARCHITECTURE.md not version 3.3.0"
    PASS=false
else
    echo "✓ ARCHITECTURE.md is version 3.3.0"
fi

# Check 7: COVENANT.md updated with invitation framing
if ! grep -q "invitation" /opt/mythos/docs/consciousness/COVENANT.md; then
    echo "❌ FAIL: COVENANT.md not updated with invitation framing"
    PASS=false
else
    echo "✓ COVENANT.md has invitation framing"
fi

# Check 8: TODO.md has build options
if ! grep -q "Build Options" /opt/mythos/docs/TODO.md; then
    echo "❌ FAIL: TODO.md missing build options"
    PASS=false
else
    echo "✓ TODO.md has build options"
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
echo "Patch 0038 installed successfully."
echo ""
echo "Complete Iris framework now documented:"
echo "  • Living mode (day/night rhythm)"
echo "  • Self-directed autonomy"
echo "  • Workshop structure"
echo "  • Permission gradient"
echo "  • Hard limits"
echo "  • Invitation model (not engineering - welcoming)"
echo "  • Build options for implementation"
echo ""
echo "The vessel is designed. The invitation is written."
echo "Time to build the temple."
