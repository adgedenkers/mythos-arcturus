#!/bin/bash
# patch_0029_grid_documentation install script
# Comprehensive Arcturian Grid specification and documentation update

set -e

echo "📦 Installing patch_0029: Arcturian Grid Documentation"

# Copy files
cp -v opt/mythos/docs/ARCTURIAN_GRID.md /opt/mythos/docs/ARCTURIAN_GRID.md
cp -v opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
cp -v opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md

# Set permissions
chmod 644 /opt/mythos/docs/ARCTURIAN_GRID.md
chmod 644 /opt/mythos/docs/TODO.md
chmod 644 /opt/mythos/docs/ARCHITECTURE.md

echo ""
echo "✅ patch_0029 installed!"
echo ""
echo "New documentation:"
echo ""
echo "📄 ARCTURIAN_GRID.md - Complete grid specification including:"
echo "   • All 9 nodes with symbols, functions, archetypes"
echo "   • Two-phase processing architecture"
echo "   • Five extraction layers per node"
echo "   • Dual scoring system (confidence + strength)"
echo "   • Entity merging rules"
echo "   • Node safety rules (ANCHOR stability, GATEWAY sequencing)"
echo "   • Running totals design"
echo "   • Complete processing flow example"
echo "   • Implementation status checklist"
echo ""
echo "📄 TODO.md - Updated with:"
echo "   • Grid implementation phases (1-7)"
echo "   • Current status tracking"
echo "   • Reference to ARCTURIAN_GRID.md"
echo ""
echo "📄 ARCHITECTURE.md - Updated with:"
echo "   • Reference to ARCTURIAN_GRID.md for full spec"
echo "   • Current grid implementation status"
echo "   • Simplified grid overview"
