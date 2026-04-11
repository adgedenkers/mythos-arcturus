#!/bin/bash
# SYS-0003 — Stream Ownership Final: 6 decisions resolved, 2 deferred
set -e
PATCH="SYS-0003_stream_ownership_final"
MYTHOS="/opt/mythos"

echo "[$PATCH] Updating STREAMS.json with resolved ownership decisions..."
cp opt/mythos/docs/STREAMS.json "$MYTHOS/docs/STREAMS.json"
echo "  ✓ STREAMS.json"
echo ""
echo "Resolved:"
echo "  perception_log       → NEU"
echo "  orchestrator/        → LOG"
echo "  workers/             → SYS"
echo "  triad/               → LOG"
echo "  integrity/           → SYS"
echo "  spending_analytics   → SEN"
echo ""
echo "Deferred (default owners still in effect):"
echo "  checkin_handler.py   → SEN (pending review)"
echo "  overview.py          → SEN (pending review)"
echo ""
echo "[$PATCH] Complete."
