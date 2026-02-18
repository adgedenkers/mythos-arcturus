#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== Patch: Calendar CRUD ==="
sudo chown adge:adge /opt/mythos/core/message_extractor.py /opt/mythos/core/action_executor.py
/opt/mythos/.venv/bin/python3 "$SCRIPT_DIR/patch_calendar_crud.py"
sudo systemctl restart mythos-api.service
sleep 2
echo "✅ Done. Test with Iris."
