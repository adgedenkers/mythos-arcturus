#!/bin/bash
# Patch 0060: Documentation Sync
# Ensures all documentation is current with patches 0056-0059

set -e

echo "📦 Installing Patch 0060: Documentation Sync..."

# Copy documentation files
cp opt/mythos/docs/TODO.md /opt/mythos/docs/
cp opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/
cp opt/mythos/docs/PATCH_HISTORY.md /opt/mythos/docs/

echo "✅ Patch 0060 installed successfully!"
echo ""
echo "Documentation now includes:"
echo "  - Task tracking system (0056-0057)"
echo "  - Comprehensive help system (0059)"
echo "  - Documentation rules added to TODO.md"
echo "  - Help System section in ARCHITECTURE.md"
echo "  - All patches 0056-0060 in PATCH_HISTORY.md"
echo ""
echo "📝 REMINDER: Every patch must update documentation!"
