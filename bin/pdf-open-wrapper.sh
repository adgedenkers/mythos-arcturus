#!/bin/bash
# pdf-open-wrapper.sh — Smart PDF opener
# Suppresses auto-open for files in ~/print-queue/
# Opens normally with Evince for everything else

PRINT_QUEUE="${HOME}/print-queue"
REAL_VIEWER="/usr/bin/evince"

for FILE in "$@"; do
  # Resolve to absolute path
  ABS_PATH="$(realpath "$FILE" 2>/dev/null || echo "$FILE")"

  if [[ "$ABS_PATH" == "${PRINT_QUEUE}/"* ]]; then
    # Silently skip — the print watcher handles these
    logger -t pdf-open-wrapper "Suppressed open for print-queue file: $FILE"
  else
    # Open normally
    "$REAL_VIEWER" "$FILE" &
  fi
done
