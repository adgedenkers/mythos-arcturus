#!/usr/bin/env bash
# icloudpd sync wrapper for Mythos Photos
# Patch 0096
# Runs as a systemd service, continuously syncing iCloud photos to Arcturus

set -euo pipefail

ICLOUD_DIR="/opt/photos/import/icloud"
LOG_FILE="/opt/photos/import/icloud/sync.log"
COOKIE_DIR="/opt/photos/import/icloud/.cookies"
READY_DIR="/opt/photos/import/icloud/ready"

# Load config
CONFIG="/opt/mythos/photos/icloud.conf"
if [ ! -f "$CONFIG" ]; then
    echo "ERROR: Config not found at $CONFIG"
    echo "Create it with:"
    echo "  ICLOUD_USERNAME=your@apple.id"
    exit 1
fi
source "$CONFIG"

mkdir -p "$ICLOUD_DIR" "$COOKIE_DIR" "$READY_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting iCloud sync for $ICLOUD_USERNAME"
log "Destination: $READY_DIR"

/opt/mythos/.venv/bin/icloudpd \
    --directory "$READY_DIR" \
    --username "$ICLOUD_USERNAME" \
    --cookie-directory "$COOKIE_DIR" \
    --folder-structure "{:%Y/%Y-%m-%d}" \
    --recent 0 \
    --auto-delete \
    --until-found 50 \
    --log-level info \
    2>&1 | tee -a "$LOG_FILE"

log "Sync complete"
