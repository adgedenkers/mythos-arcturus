#!/bin/bash
# print-watcher.sh — Watches ~/print-queue for PDFs and prints them
# Pattern: *-[13-digit-timestamp].pdf  (e.g. MyNote-1772666957951.pdf)
# After printing, moves file to ~/print-queue/done/

set -euo pipefail

WATCH_DIR="${HOME}/print-queue"
DONE_DIR="${WATCH_DIR}/done"
LOG_TAG="print-watcher"

# Ensure directories exist
mkdir -p "$WATCH_DIR" "$DONE_DIR"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [$LOG_TAG] $*"
  logger -t "$LOG_TAG" "$*"
}

log "Watching ${WATCH_DIR} for printable PDFs..."

inotifywait -m -e close_write -e moved_to --format '%f' "$WATCH_DIR" | while read -r FILE; do
  # Match: anything, dash, 13 digits, .pdf
  if [[ "$FILE" =~ ^.+-[0-9]{13}\.pdf$ ]]; then
    FILEPATH="${WATCH_DIR}/${FILE}"

    # Brief pause to ensure file is fully written
    sleep 1

    if [ -f "$FILEPATH" ]; then
      log "Printing: ${FILE}"

      if lp "$FILEPATH" 2>&1; then
        log "Sent to printer: ${FILE}"
        mv "$FILEPATH" "${DONE_DIR}/${FILE}"
        log "Archived to done/: ${FILE}"
      else
        log "ERROR: Failed to print ${FILE}"
      fi
    fi
  fi
done
