#!/bin/bash
# Rollback Script for Patch 0009
# Removes Qdrant collections and related files

set -e

MYTHOS_BASE="/opt/mythos"
QDRANT_URL="http://localhost:6333"
AUTO_MODE=false

# Check for auto mode (called from install.sh on failure)
if [ "$1" = "--auto" ]; then
    AUTO_MODE=true
fi

echo "=========================================="
echo "Rolling Back Patch 0009: Qdrant Collections"
echo "=========================================="
echo ""

# Function to prompt (skip in auto mode)
confirm() {
    if [ "$AUTO_MODE" = true ]; then
        return 0  # Auto-confirm
    fi
    read -p "$1 (y/N) " -n 1 -r
    echo ""
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Delete collections from Qdrant
echo "Checking Qdrant collections..."

if curl -s "${QDRANT_URL}/healthz" | grep -q "passed"; then
    echo "  Qdrant is accessible"
    
    if confirm "Delete Qdrant collections (mythos_messages, mythos_photos, mythos_entities)?"; then
        for coll in mythos_messages mythos_photos mythos_entities; do
            echo -n "  Deleting $coll... "
            response=$(curl -s -X DELETE "${QDRANT_URL}/collections/${coll}")
            if echo "$response" | grep -q "true\|not found"; then
                echo "✓"
            else
                echo "⚠️  (may not have existed)"
            fi
        done
    else
        echo "  Skipping collection deletion"
    fi
else
    echo "  ⚠️  Qdrant not accessible, skipping collection deletion"
fi

echo ""

# Remove Python module
echo "Removing Python module..."
if confirm "Remove /opt/mythos/qdrant/ directory?"; then
    rm -rf "${MYTHOS_BASE}/qdrant"
    echo "  ✓ Removed /opt/mythos/qdrant/"
else
    echo "  Skipping directory removal"
fi

# Remove config file
echo ""
echo "Removing configuration..."
if confirm "Remove /opt/mythos/config/qdrant_config.yaml?"; then
    rm -f "${MYTHOS_BASE}/config/qdrant_config.yaml"
    echo "  ✓ Removed qdrant_config.yaml"
else
    echo "  Skipping config removal"
fi

echo ""
echo "=========================================="
echo "Rollback Complete"
echo "=========================================="
echo ""
echo "Patch 0009 has been rolled back."
echo ""
echo "To reinstall, run:"
echo "  cd /opt/mythos/patches/patch_0009_build"
echo "  ./install.sh"
echo ""
