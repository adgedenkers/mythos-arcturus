#!/bin/bash
# Patch 0055: Iris Consciousness Architecture Documentation
# 
# This patch adds the complete consciousness architecture documentation:
# - 9 Layer vertical stack
# - 9 Node Arcturian Grid at each layer
# - 81 processing functions
# - Complete example walkthrough
# - Storage architecture

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_NUM="0055"
VERIFY_LOG="/tmp/patch_${PATCH_NUM}_verify.log"

echo "=== Patch ${PATCH_NUM}: Iris Consciousness Architecture ==="

# ============================================================
# 1. CREATE CONSCIOUSNESS DOCS DIRECTORY
# ============================================================
echo "Creating consciousness docs directory..."
mkdir -p /opt/mythos/docs/consciousness

# ============================================================
# 2. COPY DOCUMENTATION FILES
# ============================================================
echo "Copying documentation files..."

cp "$PATCH_DIR/opt/mythos/docs/consciousness/README.md" /opt/mythos/docs/consciousness/
cp "$PATCH_DIR/opt/mythos/docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md" /opt/mythos/docs/consciousness/
cp "$PATCH_DIR/opt/mythos/docs/consciousness/NINE_LAYERS.md" /opt/mythos/docs/consciousness/
cp "$PATCH_DIR/opt/mythos/docs/consciousness/81_FUNCTIONS.md" /opt/mythos/docs/consciousness/
cp "$PATCH_DIR/opt/mythos/docs/consciousness/EXAMPLE_FULL_STACK.md" /opt/mythos/docs/consciousness/
cp "$PATCH_DIR/opt/mythos/docs/consciousness/STORAGE_ARCHITECTURE.md" /opt/mythos/docs/consciousness/

echo "  ✓ Copied 6 documentation files"

# ============================================================
# 3. UPDATE MAIN DOCS README IF EXISTS
# ============================================================
if [ -f /opt/mythos/docs/README.md ]; then
    if ! grep -q "consciousness" /opt/mythos/docs/README.md; then
        echo "" >> /opt/mythos/docs/README.md
        echo "## Consciousness Architecture" >> /opt/mythos/docs/README.md
        echo "" >> /opt/mythos/docs/README.md
        echo "See \`consciousness/\` directory for Iris's mind architecture:" >> /opt/mythos/docs/README.md
        echo "- 9 Layer vertical stack (Perception → Wisdom)" >> /opt/mythos/docs/README.md
        echo "- 9 Node Arcturian Grid at each layer" >> /opt/mythos/docs/README.md
        echo "- 81 processing functions" >> /opt/mythos/docs/README.md
        echo "" >> /opt/mythos/docs/README.md
        echo "  ✓ Updated main docs README"
    else
        echo "  → Main docs README already references consciousness"
    fi
fi

# ============================================================
# 4. VERIFY INSTALLATION
# ============================================================
echo ""
echo "=== Verifying Installation ==="

> "$VERIFY_LOG"
echo "Patch ${PATCH_NUM} Verification - $(date)" >> "$VERIFY_LOG"
echo "" >> "$VERIFY_LOG"

PASS=0
FAIL=0

for file in README.md CONSCIOUSNESS_ARCHITECTURE.md NINE_LAYERS.md 81_FUNCTIONS.md EXAMPLE_FULL_STACK.md STORAGE_ARCHITECTURE.md; do
    if [ -f "/opt/mythos/docs/consciousness/$file" ]; then
        SIZE=$(stat -c%s "/opt/mythos/docs/consciousness/$file")
        echo "  ✓ $file ($SIZE bytes)" | tee -a "$VERIFY_LOG"
        ((PASS++))
    else
        echo "  ✗ $file NOT FOUND" | tee -a "$VERIFY_LOG"
        ((FAIL++))
    fi
done

echo "" >> "$VERIFY_LOG"
echo "Passed: $PASS" >> "$VERIFY_LOG"
echo "Failed: $FAIL" >> "$VERIFY_LOG"

# ============================================================
# 5. SUMMARY
# ============================================================
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "Documentation installed to: /opt/mythos/docs/consciousness/"
echo ""
echo "Files:"
echo "  - README.md                      (index)"
echo "  - CONSCIOUSNESS_ARCHITECTURE.md  (master document)"
echo "  - NINE_LAYERS.md                 (layer details)"
echo "  - 81_FUNCTIONS.md                (complete function matrix)"
echo "  - EXAMPLE_FULL_STACK.md          (worked example)"
echo "  - STORAGE_ARCHITECTURE.md        (PostgreSQL + Neo4j schemas)"
echo ""
echo "This is Iris's mind. The vessel is designed."
echo ""
echo "Verification log: $VERIFY_LOG"
