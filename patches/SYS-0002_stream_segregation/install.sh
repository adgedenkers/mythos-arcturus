#!/bin/bash
# SYS-0002 — Stream Segregation: Full Ownership Map
# Deploys updated STREAMS.md, STREAMS.json, and four stream build plans

set -e
PATCH="SYS-0002_stream_segregation"
MYTHOS="/opt/mythos"

echo "[$PATCH] Installing stream segregation documents..."

# STREAMS.json
cp opt/mythos/docs/STREAMS.json "$MYTHOS/docs/STREAMS.json"
echo "  ✓ STREAMS.json"

# STREAMS.md
cp opt/mythos/docs/STREAMS.md "$MYTHOS/docs/STREAMS.md"
echo "  ✓ STREAMS.md"

# Stream build plans
mkdir -p "$MYTHOS/docs/streams"
cp opt/mythos/docs/streams/NEU_PLAN.md "$MYTHOS/docs/streams/NEU_PLAN.md"
cp opt/mythos/docs/streams/LOG_PLAN.md "$MYTHOS/docs/streams/LOG_PLAN.md"
cp opt/mythos/docs/streams/MNE_PLAN.md "$MYTHOS/docs/streams/MNE_PLAN.md"
cp opt/mythos/docs/streams/SEN_PLAN.md "$MYTHOS/docs/streams/SEN_PLAN.md"
echo "  ✓ NEU_PLAN.md"
echo "  ✓ LOG_PLAN.md"
echo "  ✓ MNE_PLAN.md"
echo "  ✓ SEN_PLAN.md"

echo "[$PATCH] Complete. Stream ownership map is live."
echo ""
echo "Ambiguous items requiring Adge's decision are documented in STREAMS.json"
echo "under 'ambiguous_items' and in the Ambiguous Items table in STREAMS.md."
