#!/bin/bash
# Patch 0053: Sudoers configuration for Mythos patch automation
# 
# This patch adds passwordless sudo for specific commands needed by
# the patch monitor service and install scripts.
#
# IMPORTANT: This patch must be run manually with sudo the first time,
# since we need sudo access to install the sudoers file!

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_NUM="0053"

echo "=== Patch ${PATCH_NUM}: Sudoers Configuration ==="

# ============================================================
# 1. VALIDATE SUDOERS FILE SYNTAX
# ============================================================
echo "Validating sudoers syntax..."

# visudo -c -f can check syntax without installing
if ! visudo -c -f "$PATCH_DIR/mythos-sudoers" >/dev/null 2>&1; then
    echo "❌ ERROR: Invalid sudoers syntax!"
    echo "Run: visudo -c -f $PATCH_DIR/mythos-sudoers"
    exit 1
fi

echo "  ✓ Syntax valid"

# ============================================================
# 2. INSTALL SUDOERS FILE
# ============================================================
echo "Installing sudoers file..."

# Must use sudo to write to /etc/sudoers.d/
sudo cp "$PATCH_DIR/mythos-sudoers" /etc/sudoers.d/mythos
sudo chmod 0440 /etc/sudoers.d/mythos
sudo chown root:root /etc/sudoers.d/mythos

echo "  ✓ Installed to /etc/sudoers.d/mythos"

# ============================================================
# 3. VERIFY INSTALLATION
# ============================================================
echo "Verifying installation..."

# Test that we can now run systemctl without password prompt
if sudo -n systemctl is-active mythos-bot.service >/dev/null 2>&1; then
    echo "  ✓ systemctl works without password"
else
    echo "  ⚠ systemctl may still require password"
fi

# Test postgres access
if sudo -n -u postgres psql -d mythos -c "SELECT 1;" >/dev/null 2>&1; then
    echo "  ✓ PostgreSQL access works without password"
else
    echo "  ⚠ PostgreSQL access may still require password"
fi

# ============================================================
# 4. SUMMARY
# ============================================================
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "The following commands now work without password prompts:"
echo "  - sudo systemctl restart mythos-*"
echo "  - sudo -u postgres psql -d mythos ..."
echo "  - sudo journalctl -u mythos-*"
echo ""
echo "Future patches will auto-deploy correctly."
echo ""
echo "To test:"
echo "  sudo -n systemctl status mythos-bot.service"
echo "  sudo -n -u postgres psql -d mythos -c 'SELECT 1;'"
