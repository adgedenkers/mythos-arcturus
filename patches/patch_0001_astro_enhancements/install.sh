#!/bin/bash
# ============================================================================
# Patch 0001: Astrology Engine v2.1 Enhancements
#
# Changes:
#   1. Fixed Star Conjunctions — built-in catalog of 29 major stars with
#      J2000 positions and precession correction. No CSV dependency.
#   2. Tiered Aspect Orb Filtering — aspects now carry "tier" field
#      (major/minor/harmonic) with enforced per-tier orb limits.
#   3. Dispositor Chain — circular loop detection via DFS cycle-finding.
#   4. Mutual Reception — classical (sign) + modern (sign+house) detection.
#
# Files modified:
#   /opt/mythos/astrology/astrochart_cli_engine.py
#
# Backward compatible: all existing keys preserved, new fields additive.
# ============================================================================

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="/opt/mythos/astrology"

echo "=== Patch 0001: Astrology Engine v2.1 Enhancements ==="

# Backup current engine
if [ -f "$TARGET/astrochart_cli_engine.py" ]; then
    cp "$TARGET/astrochart_cli_engine.py" "$TARGET/astrochart_cli_engine.py.bak.$(date +%Y%m%d%H%M%S)"
    echo "  ✓ Backed up existing engine"
fi

# Install updated engine
cp "$PATCH_DIR/opt/mythos/astrology/astrochart_cli_engine.py" "$TARGET/astrochart_cli_engine.py"
echo "  ✓ Installed astrochart_cli_engine.py v2.1"

# Verify
if python3 -c "import sys; sys.path.insert(0,'$TARGET'); import astrochart_cli_engine; print(f'  ✓ Engine loads OK')" 2>/dev/null; then
    echo "  ✓ Import verification passed"
else
    echo "  ⚠ Import check failed — may need dependencies"
fi

echo ""
echo "=== Patch 0001 complete ==="
echo ""
echo "What changed:"
echo "  • Fixed Star Conjunctions: 29-star built-in catalog (Regulus, Algol, Spica, etc.)"
echo "    - Precession-corrected from J2000 to birth year"
echo "    - CSV still used if present (fallback to built-in)"
echo "    - Configurable orb (default 1°)"
echo "  • Tiered Aspect Orbs: 'tier' field added to each aspect"
echo "    - major (conj/opp/tri/sq/sex): up to 8°"
echo "    - minor (semi-sextile/quincunx/semi-sq/sesqui): up to 2-3°"
echo "    - harmonic (quintile/septile/decile families): up to 1-2°"
echo "  • Dispositor Chain: circular loops detected and labeled"
echo "    - New field: 'Circular Loops' (list of planet sequences)"
echo "  • Mutual Receptions: classical + modern detection"
echo "    - New fields: 'Classical Mutual Receptions', 'Modern Mutual Receptions'"
echo "    - Backward-compatible 'Mutual Receptions' field preserved"
echo ""
echo "Engine version: 2.1"
