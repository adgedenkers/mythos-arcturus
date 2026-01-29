#!/bin/bash
# patch_0032_docs_finance_update - Update documentation with finance system details
#
# Updates:
#   - ARCHITECTURE.md: Added complete Finance System section, Patch Monitor details
#   - TODO.md: Marked finance Telegram integration complete, updated patch history

set -e

echo "=== patch_0032_docs_finance_update ==="

# Copy updated docs
cp opt/mythos/docs/TODO.md /opt/mythos/docs/TODO.md
cp opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md

echo "✓ Updated TODO.md"
echo "✓ Updated ARCHITECTURE.md"

echo ""
echo "=== Documentation Updated ==="
echo ""
echo "Changes:"
echo "  - ARCHITECTURE.md v2.4.0: Added Finance System section"
echo "  - ARCHITECTURE.md: Added Patch Monitor artifact types"
echo "  - ARCHITECTURE.md: Added Principle 4 (docs updated with every patch)"
echo "  - TODO.md: Marked 'Finance - Telegram Integration' complete"
echo "  - TODO.md: Added patches 0030, 0031, 0032 to history"
echo "  - TODO.md: Next patch number is now 0033"
