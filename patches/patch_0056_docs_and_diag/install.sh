#!/bin/bash
# Patch 0056: Documentation updates and mythos-diag command
#
# Updates:
# - TODO.md with all 2026-02-03 work (consciousness architecture, etc.)
# - mythos-diag standardized diagnostic command

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_NUM="0056"

echo "=== Patch ${PATCH_NUM}: Docs & Diagnostics ==="

# ============================================================
# 1. UPDATE TODO.md
# ============================================================
echo "Updating TODO.md..."
cp "$PATCH_DIR/opt/mythos/docs/TODO.md" /opt/mythos/docs/TODO.md
echo "  ✓ TODO.md updated"

# ============================================================
# 2. UPDATE ARCHITECTURE.md (add consciousness section reference)
# ============================================================
echo "Updating ARCHITECTURE.md..."
if ! grep -q "81 Processing Functions" /opt/mythos/docs/ARCHITECTURE.md; then
    # Insert after the "Arcturian Grid" section
    # Find the line with "Full specification.*ARCTURIAN_GRID" and add after it
    ARCH_FILE=/opt/mythos/docs/ARCHITECTURE.md
    
    # Add the consciousness architecture section before "## Finance System"
    sed -i '/^## Finance System/i \
## 🧠 Consciousness Architecture (2026-02-03)\
\
The full consciousness architecture creates **81 processing functions** (9 nodes × 9 layers).\
\
### The 9-Layer Stack\
\
```\
LEVEL 9: WISDOM      ← Eternal truth\
LEVEL 8: IDENTITY    ← Who you are\
LEVEL 7: NARRATIVE   ← Story placement\
LEVEL 6: INTENTION   ← What wants to happen\
LEVEL 5: KNOWLEDGE   ← What is known\
LEVEL 4: MEMORY      ← Connections to past\
LEVEL 3: PROCESSING  ← Meaning-making\
LEVEL 2: INTUITION   ← Felt-sense\
LEVEL 1: PERCEPTION  ← Raw input\
```\
\
The Arcturian Grid (9 nodes) operates at each layer. WISDOM feeds back to PERCEPTION.\
\
**Full specification:** `docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md`\
\
---\
' "$ARCH_FILE"
    echo "  ✓ Consciousness section added to ARCHITECTURE.md"
else
    echo "  → ARCHITECTURE.md already has consciousness section"
fi

# ============================================================
# 3. INSTALL mythos-diag COMMAND
# ============================================================
echo "Installing mythos-diag..."
mkdir -p /opt/mythos/bin
cp "$PATCH_DIR/opt/mythos/bin/mythos-diag" /opt/mythos/bin/mythos-diag
chmod +x /opt/mythos/bin/mythos-diag
echo "  ✓ mythos-diag installed"

# ============================================================
# 4. ADD TO PATH (if not already)
# ============================================================
PROFILE_FILE="$HOME/.bashrc"
if ! grep -q "/opt/mythos/bin" "$PROFILE_FILE" 2>/dev/null; then
    echo "" >> "$PROFILE_FILE"
    echo "# Mythos tools" >> "$PROFILE_FILE"
    echo 'export PATH="/opt/mythos/bin:$PATH"' >> "$PROFILE_FILE"
    echo "  ✓ Added /opt/mythos/bin to PATH in .bashrc"
    echo "  → Run 'source ~/.bashrc' or open new terminal"
else
    echo "  → /opt/mythos/bin already in PATH"
fi

# ============================================================
# 5. CREATE SYMLINK (immediate availability)
# ============================================================
if [ ! -L /usr/local/bin/mythos-diag ]; then
    sudo ln -sf /opt/mythos/bin/mythos-diag /usr/local/bin/mythos-diag 2>/dev/null || true
    echo "  ✓ Symlinked to /usr/local/bin/mythos-diag"
fi

# ============================================================
# 6. VERIFY
# ============================================================
echo ""
echo "=== Verification ==="

# Check TODO.md
if grep -q "2026-02-03" /opt/mythos/docs/TODO.md; then
    echo "  ✓ TODO.md contains today's date"
else
    echo "  ✗ TODO.md missing today's updates"
fi

# Check mythos-diag
if [ -x /opt/mythos/bin/mythos-diag ]; then
    echo "  ✓ mythos-diag is executable"
else
    echo "  ✗ mythos-diag not executable"
fi

# One-liner verify
echo ""
echo "Verify one-liner:"
echo '  [ -x /opt/mythos/bin/mythos-diag ] && grep -q "9-Layer" /opt/mythos/docs/TODO.md && echo "✓ 0056 OK" || echo "✗ 0056 FAIL"'

# ============================================================
# 7. SUMMARY
# ============================================================
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "Updated:"
echo "  - /opt/mythos/docs/TODO.md (all 2026-02-03 items)"
echo ""
echo "Installed:"
echo "  - /opt/mythos/bin/mythos-diag"
echo ""
echo "Usage:"
echo "  mythos-diag              # Quick overview"
echo "  mythos-diag finance      # Finance state"
echo "  mythos-diag services     # All services"
echo "  mythos-diag iris         # Consciousness status"
echo "  mythos-diag all          # Everything"
echo ""
