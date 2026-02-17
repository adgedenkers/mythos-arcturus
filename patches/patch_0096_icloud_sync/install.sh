#!/usr/bin/env bash
# Patch 0096 - iCloud Photo Sync Service
# Version: v1.16.2

set -euo pipefail

PATCH="0096"
VERSION="v1.16.2"

echo "╔════════════════════════════════════════════════════╗"
echo "║  Patch ${PATCH} - iCloud Photo Sync - ${VERSION}  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# ── 1. Install icloudpd ───────────────────────────────────────────────────────
echo "▶ Installing icloudpd..."
/opt/mythos/.venv/bin/pip install icloudpd --quiet
echo "  ✓ icloudpd installed: $(/opt/mythos/.venv/bin/icloudpd --version 2>&1 | head -1)"

# ── 2. Install sync script ────────────────────────────────────────────────────
echo ""
echo "▶ Installing sync script..."
cp opt/mythos/photos/icloud_sync.sh /opt/mythos/photos/icloud_sync.sh
chmod +x /opt/mythos/photos/icloud_sync.sh
echo "  ✓ Script installed at /opt/mythos/photos/icloud_sync.sh"

# ── 3. Install config template ────────────────────────────────────────────────
echo ""
echo "▶ Installing config template..."
if [ ! -f /opt/mythos/photos/icloud.conf ]; then
    cp opt/mythos/photos/icloud.conf.template /opt/mythos/photos/icloud.conf
    echo "  ✓ Config template installed at /opt/mythos/photos/icloud.conf"
    echo "  ⚠  Edit /opt/mythos/photos/icloud.conf with your Apple ID before first run"
else
    echo "  ℹ  icloud.conf already exists — skipping"
fi

# ── 4. Create directories ─────────────────────────────────────────────────────
echo ""
echo "▶ Creating directories..."
mkdir -p /opt/photos/import/icloud/{ready,.cookies}
echo "  ✓ Directories ready"

# ── 5. Install systemd service and timer ──────────────────────────────────────
echo ""
echo "▶ Installing systemd service and timer..."
cp etc/systemd/system/mythos-icloud-sync.service /etc/systemd/system/
cp etc/systemd/system/mythos-icloud-sync.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable mythos-icloud-sync.timer
echo "  ✓ mythos-icloud-sync.timer installed and enabled (runs every 6 hours)"
echo "  ℹ  Timer NOT started yet — complete first-run auth first"

# ── 6. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   INSTALLATION COMPLETE                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  FIRST RUN (authentication):                                 ║"
echo "║                                                              ║"
echo "║  1. Edit your Apple ID into the config:                      ║"
echo "║       nano /opt/mythos/photos/icloud.conf                    ║"
echo "║                                                              ║"
echo "║  2. Run first auth interactively (you'll need 2FA):          ║"
echo "║       /opt/mythos/.venv/bin/icloudpd \\                       ║"
echo "║         --directory /opt/photos/import/icloud/ready \\        ║"
echo "║         --username your@apple.id \\                           ║"
echo "║         --cookie-directory /opt/photos/import/icloud/.cookies"
echo "║                                                              ║"
echo "║  3. Complete 2FA when prompted                               ║"
echo "║                                                              ║"
echo "║  4. Once auth succeeds, start the timer:                     ║"
echo "║       sudo systemctl start mythos-icloud-sync.timer          ║"
echo "║                                                              ║"
echo "║  5. In Immich UI:                                            ║"
echo "║     Administration → Libraries → Create External Library     ║"
echo "║     Path: /opt/photos/import/icloud/ready                    ║"
echo "║                                                              ║"
echo "║  Log: /opt/photos/import/icloud/sync.log                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Patch ${PATCH} ${VERSION} complete."
