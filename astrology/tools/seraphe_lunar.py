#!/usr/bin/env bash
# seraphe-lunar — CLI wrapper for Seraphe's lunar calendar generator
# Usage:
#   seraphe-lunar                    # current cycle
#   seraphe-lunar --year 2026 --month 6
#   seraphe-lunar --skip-ollama      # fast/test mode, no Ollama calls
#   seraphe-lunar --list             # list all generated calendars
#   seraphe-lunar --status           # show worker status

set -e

GENERATOR="/opt/mythos/astrology/seraphe_lunar_generator.py"
VENV_PYTHON="/opt/mythos/.venv/bin/python3"
OUTPUT_DIR="/opt/mythos/outputs/lunar_calendars"

# Handle special flags before passing to Python
if [[ "$1" == "--list" || "$1" == "list" ]]; then
    echo ""
    echo "Seraphe Lunar Calendars — Generated"
    echo "─────────────────────────────────────"
    if ls "$OUTPUT_DIR"/*.pdf 2>/dev/null | head -20; then
        echo ""
    else
        echo "  No calendars generated yet."
        echo "  Run: seraphe-lunar"
    fi
    exit 0
fi

if [[ "$1" == "--status" || "$1" == "status" ]]; then
    echo ""
    echo "Lunar Calendar Worker Status"
    echo "─────────────────────────────"
    systemctl status mythos-worker-lunar.service --no-pager 2>/dev/null || \
        echo "  Worker service not running. Start with: sudo systemctl start mythos-worker-lunar"
    echo ""
    echo "Recent log:"
    tail -20 /opt/mythos/logs/lunar_calendar_worker.log 2>/dev/null || echo "  No log yet."
    exit 0
fi

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo ""
    echo "Usage: seraphe-lunar [options]"
    echo ""
    echo "Options:"
    echo "  --year YYYY         Year (default: current)"
    echo "  --month MM          Month 1-12 (default: current)"
    echo "  --skip-ollama       Fast mode — no Ollama calls, stub interpretations"
    echo "  --out PATH          Custom output path"
    echo "  --list              List all generated calendars"
    echo "  --status            Show worker service status"
    echo ""
    echo "Examples:"
    echo "  seraphe-lunar                        # generate current month"
    echo "  seraphe-lunar --year 2026 --month 6  # generate June 2026"
    echo "  seraphe-lunar --skip-ollama          # fast test (no AI interpretations)"
    echo ""
    exit 0
fi

# Pass all args to Python generator
exec "$VENV_PYTHON" "$GENERATOR" "$@"
