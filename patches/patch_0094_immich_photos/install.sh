#!/usr/bin/env bash
# Patch 0094 - Immich Photo Management System
# Version: v1.16.0
# Installs Immich as the sovereign family photo archive on Arcturus

set -euo pipefail

PATCH="0094"
VERSION="v1.16.0"
PHOTOS_DIR="/opt/photos"
IMMICH_CONFIG="/opt/mythos/photos"

echo "╔══════════════════════════════════════════════════╗"
echo "║  Patch ${PATCH} - Immich Photo Archive - ${VERSION}  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 1. Create directory structure ────────────────────────────────────────────
echo "▶ Creating directory structure..."
mkdir -p "${PHOTOS_DIR}/library"
mkdir -p "${PHOTOS_DIR}/pgdata"
mkdir -p "${IMMICH_CONFIG}"
mkdir -p /opt/photos/import/google
mkdir -p /opt/photos/import/icloud
mkdir -p /opt/photos/import/amazon
mkdir -p /opt/photos/import/staging
echo "  ✓ Directories created"
echo "    Library:  ${PHOTOS_DIR}/library"
echo "    Database: ${PHOTOS_DIR}/pgdata"
echo "    Import staging areas ready"

# ── 2. Set permissions ────────────────────────────────────────────────────────
echo ""
echo "▶ Setting permissions..."
chmod 755 "${PHOTOS_DIR}"
chmod 755 "${PHOTOS_DIR}/library"
chmod 700 "${PHOTOS_DIR}/pgdata"
echo "  ✓ Permissions set"

# ── 3. Install docker-compose.yml and .env ───────────────────────────────────
echo ""
echo "▶ Installing Immich configuration..."
cp opt/mythos/photos/docker-compose.yml "${IMMICH_CONFIG}/docker-compose.yml"

# Only install .env if it doesn't already exist (don't overwrite custom passwords)
if [ ! -f "${IMMICH_CONFIG}/.env" ]; then
    cp opt/mythos/photos/.env "${IMMICH_CONFIG}/.env"
    echo "  ✓ .env installed — IMPORTANT: Edit password in ${IMMICH_CONFIG}/.env before first run"
else
    echo "  ℹ  .env already exists — skipping (keeping existing config)"
fi

# ── 4. Install systemd service ────────────────────────────────────────────────
echo ""
echo "▶ Installing systemd service..."
cp etc/systemd/system/mythos-photos.service /etc/systemd/system/mythos-photos.service
systemctl daemon-reload
systemctl enable mythos-photos.service
echo "  ✓ mythos-photos.service installed and enabled"

# ── 5. Pull Docker images ─────────────────────────────────────────────────────
echo ""
echo "▶ Pulling Immich Docker images (this will take a few minutes)..."
cd "${IMMICH_CONFIG}"
docker compose pull
echo "  ✓ Images pulled"

# ── 6. Start Immich ───────────────────────────────────────────────────────────
echo ""
echo "▶ Starting Immich..."
docker compose up -d
echo "  ✓ Immich stack started"

# ── 7. Wait for health ────────────────────────────────────────────────────────
echo ""
echo "▶ Waiting for Immich to become healthy (up to 60s)..."
ATTEMPTS=0
until curl -sf http://localhost:2283/api/server-info/ping > /dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ $ATTEMPTS -ge 30 ]; then
        echo "  ⚠  Immich not responding yet — may still be initializing."
        echo "     Check: docker logs immich_server"
        echo "     Then:  curl http://localhost:2283/api/server-info/ping"
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

if curl -sf http://localhost:2283/api/server-info/ping > /dev/null 2>&1; then
    echo "  ✓ Immich is up and responding"
fi

# ── 8. Update TODO.md ─────────────────────────────────────────────────────────
echo ""
echo "▶ Updating TODO.md..."
TODO="/opt/mythos/docs/TODO.md"
if [ -f "$TODO" ]; then
    # Add completed entry
    sed -i "s/> \*\*Last Updated:\*\*.*/> **Last Updated:** $(date '+%Y-%m-%d %H:%M %Z')/" "$TODO"
    echo "  ✓ TODO.md timestamp updated"
fi

# ── 9. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   INSTALLATION COMPLETE                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  Immich Web UI:  http://arcturus.local:2283                  ║"
echo "║  (Also:          http://$(hostname -I | awk '{print $1}'):2283)                   ║"
echo "║                                                              ║"
echo "║  FIRST RUN STEPS:                                            ║"
echo "║  1. Open the URL above in your browser                       ║"
echo "║  2. Create your admin account                                ║"
echo "║  3. Install mobile app — point to http://arcturus.local:2283 ║"
echo "║                                                              ║"
echo "║  IMPORT STAGING AREAS (for ingestion patches):               ║"
echo "║  Google:  /opt/photos/import/google/                         ║"
echo "║  iCloud:  /opt/photos/import/icloud/                         ║"
echo "║  Amazon:  /opt/photos/import/amazon/                         ║"
echo "║                                                              ║"
echo "║  SERVICE COMMANDS:                                            ║"
echo "║  sudo systemctl start|stop|restart mythos-photos             ║"
echo "║  docker logs immich_server -f                                ║"
echo "║  docker logs immich_machine_learning -f                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Patch ${PATCH} ${VERSION} complete."
