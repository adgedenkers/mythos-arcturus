#!/bin/bash
# patch_0024_architecture_update install script
# Updates ARCHITECTURE.md with core design principles

set -e

echo "📦 Installing patch_0024: Architecture Documentation Update"

# Copy files
cp -v opt/mythos/docs/ARCHITECTURE.md /opt/mythos/docs/ARCHITECTURE.md

# Set permissions
chmod 644 /opt/mythos/docs/ARCHITECTURE.md

echo ""
echo "✅ patch_0024 installed successfully!"
echo ""
echo "Changes to ARCHITECTURE.md:"
echo "  - Added 'Core Design Principles' section"
echo "  - Principle 1: Everything Goes Through the API Gateway"
echo "  - Principle 2: Assistants Are Stateless Classes"
echo "  - Principle 3: Workers Handle Async/Heavy Tasks"
echo "  - Updated system diagram with API as central hub"
echo "  - Added 'Message Flow (Critical Path)' section"
echo "  - Added 'Adding a New Assistant' guide"
echo "  - Updated to reflect ChatAssistant addition"
