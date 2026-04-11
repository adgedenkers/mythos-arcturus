#!/bin/bash
# Daily integrity scan + telemetry regeneration
# Biological System: iris-immune
# Installed by: Patch 0172
# Cron: 3:00 AM daily via /etc/cron.d/mythos-integrity
#
# Runs: full integrity scan, then regenerates live telemetry docs.

set -euo pipefail

VENV="/opt/mythos/.venv/bin/python3"
MYTHOS_ROOT="/opt/mythos"
LOG="/opt/mythos/docs/live/integrity-cron.log"

export MYTHOS_ROOT

echo "=== Integrity Scan: $(date) ===" >> "$LOG"

# Run full integrity scan
cd "$MYTHOS_ROOT"
$VENV -m integrity scan >> "$LOG" 2>&1

# Regenerate live telemetry docs
$VENV /opt/mythos/tools/generate_system_state.py >> "$LOG" 2>&1

echo "=== Complete: $(date) ===" >> "$LOG"
echo "" >> "$LOG"

# Keep log from growing forever — keep last 500 lines
tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
