#!/bin/bash
# Patch 0075 — Documentation Update
# Updates TODO.md and ARCHITECTURE.md to reflect 2026-02-09 session work
set -e

echo "=========================================="
echo "Patch 0075 — Documentation Update"
echo "=========================================="

MYTHOS=/opt/mythos

echo ""
echo "Step 1: Updating TODO.md..."
cp "$(dirname "$0")/opt/mythos/docs/TODO.md" "$MYTHOS/docs/TODO.md"
chown adge:adge "$MYTHOS/docs/TODO.md"
echo "  ✅ TODO.md updated"

echo ""
echo "Step 2: Updating ARCHITECTURE.md..."
cp "$(dirname "$0")/opt/mythos/docs/ARCHITECTURE.md" "$MYTHOS/docs/ARCHITECTURE.md"
chown adge:adge "$MYTHOS/docs/ARCHITECTURE.md"
echo "  ✅ ARCHITECTURE.md updated (v3.5.0 → v4.0.0)"

echo ""
echo "=========================================="
echo "✅ Patch 0075 installed"
echo "=========================================="
echo ""
echo "Changes documented:"
echo "  • Patches 0068-0074 recorded"
echo "  • Iris prompt architecture section added"
echo "  • Iris memory system section added"
echo "  • Ollama model management section added"
echo "  • Web dashboard documented"
echo "  • Three-tier model system documented"
echo "  • Builder mode added to backlog"
echo "  • Seraphe mode added to backlog"
echo "  • Memory poisoning insight documented"
echo "  • Model selection findings documented"
