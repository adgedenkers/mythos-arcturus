#!/bin/bash
# Patch 0094: Documentation Update
# Version: 1.15.9
# Updates TODO.md and ARCHITECTURE.md to reflect patches 0082-0094
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Patch 0094: Documentation Update v1.15.9 ==="

echo "[1] Updating TODO.md..."
sudo cp "$SCRIPT_DIR/opt/mythos/docs/TODO.md" /opt/mythos/docs/TODO.md
echo "    ✓ TODO.md updated"

echo "[2] Updating ARCHITECTURE.md..."
sudo cp "$SCRIPT_DIR/opt/mythos/docs/ARCHITECTURE.md" /opt/mythos/docs/ARCHITECTURE.md
echo "    ✓ ARCHITECTURE.md updated"

echo "[3] Verifying..."
grep -q "2026-02-17" /opt/mythos/docs/TODO.md && echo "    ✓ TODO.md date correct" || echo "    ✗ TODO.md may not have updated"
grep -q "2026-02-17" /opt/mythos/docs/ARCHITECTURE.md && echo "    ✓ ARCHITECTURE.md date correct" || echo "    ✗ ARCHITECTURE.md may not have updated"
grep -q "bill_overrides" /opt/mythos/docs/ARCHITECTURE.md && echo "    ✓ bill_overrides documented" || echo "    ✗ bill_overrides missing"
grep -q "Finance Hub" /opt/mythos/docs/ARCHITECTURE.md && echo "    ✓ Finance Hub documented" || echo "    ✗ Finance Hub section missing"
grep -q "Forecast" /opt/mythos/docs/TODO.md && echo "    ✓ Forecast documented in TODO" || echo "    ✗ Forecast missing from TODO"

echo ""
echo "=== Patch 0094 complete ==="
echo ""
echo "Changes:"
echo "  TODO.md: Updated to 2026-02-17, reflects patches 0082-0094"
echo "    • Phase 1.6 Finance Hub section with full task status"
echo "    • Recently completed: 0086-0094"
echo "    • Backlog updated: credit card parsers, bill match tuning"
echo "    • Key insights: install script patterns, v4 hash strategy"
echo ""
echo "  ARCHITECTURE.md: Updated to v4.1.0 / 2026-02-17"
echo "    • Finance Hub section: sidebar nav, all API endpoints"
echo "    • Bill auto-match algorithm documented"
echo "    • bill_overrides table in DB section"
echo "    • Patch monitor deploy requirements"
echo "    • Updated directory structure (api/routes/, web/templates/)"
echo "    • Full finance Telegram commands (/forecast, /projection, /bills)"
echo "    • Common commands updated with finance queries"
