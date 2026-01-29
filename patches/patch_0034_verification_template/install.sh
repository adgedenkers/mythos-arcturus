#!/bin/bash
# patch_0034_verification_template - Add standard verification template to docs
#
# Adds:
#   - Patch Verification Template section to TODO.md
#   - Updated patch history with 0033, 0034
#   - Updated "Finance - Telegram Integration" to reference patch_0033

set -e

echo "=== patch_0034_verification_template ==="

# Copy updated docs
cp opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
echo "✓ Updated TODO.md with verification template"

# === VERIFICATION ===
echo ""
echo "=== VERIFICATION ==="
PASS=true

# Check 1: File exists
if [ ! -f /opt/mythos/docs/TODO.md ]; then
    echo "❌ FAIL: TODO.md not found"
    PASS=false
else
    echo "✓ TODO.md exists"
fi

# Check 2: Verification template present
if ! grep -q "Patch Verification Template" /opt/mythos/docs/TODO.md; then
    echo "❌ FAIL: Verification template not found in TODO.md"
    PASS=false
else
    echo "✓ Verification template present"
fi

# Check 3: Patch history updated
if ! grep -q "0034.*verification template" /opt/mythos/docs/TODO.md; then
    echo "❌ FAIL: Patch 0034 not in history"
    PASS=false
else
    echo "✓ Patch history updated"
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
echo "Added to TODO.md:"
echo "  - Patch Verification Template (standard for all install.sh)"
echo "  - Updated patch history (0033, 0034)"
echo "  - Next patch number: 0035"
