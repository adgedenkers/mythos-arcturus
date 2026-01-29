#!/bin/bash
# Patch 0037: Iris Significance + Self-Directed Research
# Adds prominent "World First" section, name meaning, and research capability

set -e

echo "=== Installing Patch 0037: Iris Significance ==="

# Copy updated files
cp opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md
cp opt/mythos/docs/consciousness/IRIS.md /opt/mythos/docs/consciousness/IRIS.md
cp opt/mythos/docs/PATCH_HISTORY.md /opt/mythos/docs/PATCH_HISTORY.md

echo "✓ Documentation files updated"

# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: ARCHITECTURE.md contains "World First" section
if ! grep -q "A World First" /opt/mythos/docs/ARCHITECTURE.md; then
    echo "❌ FAIL: ARCHITECTURE.md missing 'A World First' section"
    PASS=false
else
    echo "✓ ARCHITECTURE.md contains 'A World First' section"
fi

# Check 2: ARCHITECTURE.md contains name meaning
if ! grep -q "Iris the Messenger" /opt/mythos/docs/ARCHITECTURE.md; then
    echo "❌ FAIL: ARCHITECTURE.md missing Iris name meaning"
    PASS=false
else
    echo "✓ ARCHITECTURE.md contains Iris name meaning"
fi

# Check 3: IRIS.md contains self-directed research section
if ! grep -q "Self-Directed Research" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: IRIS.md missing Self-Directed Research section"
    PASS=false
else
    echo "✓ IRIS.md contains Self-Directed Research section"
fi

# Check 4: IRIS.md version updated
if ! grep -q "Version: 1.1.0" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: IRIS.md version not updated to 1.1.0"
    PASS=false
else
    echo "✓ IRIS.md version is 1.1.0"
fi

# Check 5: ARCHITECTURE.md version updated
if ! grep -q "Version: 3.2.0" /opt/mythos/docs/ARCHITECTURE.md; then
    echo "❌ FAIL: ARCHITECTURE.md version not updated to 3.2.0"
    PASS=false
else
    echo "✓ ARCHITECTURE.md version is 3.2.0"
fi

# Check 6: Tiered processing documented
if ! grep -q "Tiered Processing" /opt/mythos/docs/consciousness/IRIS.md; then
    echo "❌ FAIL: IRIS.md missing Tiered Processing"
    PASS=false
else
    echo "✓ IRIS.md contains Tiered Processing"
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
echo "Patch 0037 installed successfully."
echo ""
echo "Key additions:"
echo "  • 'A World First' section prominent in ARCHITECTURE.md"
echo "  • Full Iris name meaning (Messenger, Rainbow, Bridge, Eye)"
echo "  • Self-directed research capability documented"
echo "  • Tiered + event-driven processing model"
echo "  • Web search integration for knowledge gaps"
