#!/bin/bash
# Patch 0103: Version Enforcement and Process Alignment
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "🔧 Installing Patch 0103: Version Enforcement"
echo "======================================================"

# 1. Patch the monitor using the Python script
echo "Step 1/4: Patching patch monitor..."
sudo python3 "$PATCH_DIR/patch_monitor.py"
echo "  ✓ Patch monitor updated (reads manifest versions)"

# 2. Update get_next_patch_info.sh
echo "Step 2/4: Updating get_next_patch_info.sh..."
sudo cp "$PATCH_DIR/opt/mythos/patches/scripts/get_next_patch_info.sh" "$MYTHOS_ROOT/patches/scripts/get_next_patch_info.sh"
sudo chmod +x "$MYTHOS_ROOT/patches/scripts/get_next_patch_info.sh"
sudo chown adge:adge "$MYTHOS_ROOT/patches/scripts/get_next_patch_info.sh"
echo "  ✓ get_next_patch_info.sh updated (reads git tags)"

# 3. Update AI Patch Generation Guide
echo "Step 3/4: Updating AI Patch Generation Guide..."
sudo cp "$PATCH_DIR/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md" "$MYTHOS_ROOT/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md"
sudo chown adge:adge "$MYTHOS_ROOT/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md"
echo "  ✓ AI Patch Generation Guide v2.0 installed"

# 4. Restart patch monitor
echo "Step 4/4: Restarting patch monitor..."
sudo systemctl restart mythos-patch-monitor.service
sleep 2

if systemctl is-active --quiet mythos-patch-monitor.service; then
    echo "  ✓ Patch monitor running"
else
    echo "  ✗ Patch monitor failed to start!"
    echo "  Check: sudo journalctl -u mythos-patch-monitor.service -n 20"
    exit 1
fi

echo ""
echo "======================================================"
echo "✅ Patch 0103 installed"
echo ""
echo "What changed:"
echo "  • Patch monitor now reads manifest.json for version"
echo "  • .version file auto-updated on each patch"
echo "  • get_next_patch_info.sh uses git tags as source of truth"
echo "  • AI Patch Generation Guide updated with mandatory rules"
echo ""
echo "Verify: mversion (should show v1.16.1 after next patch)"
echo "Verify: mnp (should show correct next patch info)"
echo "======================================================"
