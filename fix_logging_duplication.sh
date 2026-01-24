#!/usr/bin/env bash
set -euo pipefail

TARGET="/opt/mythos/sales_ingestion/ingest_sales_zip.py"
BACKUP_DIR="/opt/mythos/_upgrade_backups/logging_fix_$(date +%Y%m%d_%H%M%S)"

echo "============================================================"
echo "Mythos Logging Duplication Fix"
echo "============================================================"

if [[ ! -f "$TARGET" ]]; then
  echo "❌ Target file not found: $TARGET"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
cp -a "$TARGET" "$BACKUP_DIR/ingest_sales_zip.py.bak"

echo "✓ Backup created at:"
echo "  $BACKUP_DIR/ingest_sales_zip.py.bak"
echo ""

echo "---- Removing logging.basicConfig from ingest_sales_zip.py ----"

# Remove the entire logging.basicConfig(...) block
# This safely deletes from 'logging.basicConfig(' up to the matching ')'
python3 <<'PY'
from pathlib import Path
import re

path = Path("/opt/mythos/sales_ingestion/ingest_sales_zip.py")
text = path.read_text()

pattern = re.compile(
    r"logging\.basicConfig\s*\(\s*.*?\)\s*",
    re.DOTALL
)

new_text, count = pattern.subn("", text)

if count == 0:
    print("No logging.basicConfig block found — nothing to remove.")
else:
    print(f"Removed {count} logging.basicConfig block(s).")

path.write_text(new_text)
PY

echo ""
echo "---- Verifying logger remains ----"
grep -n "getLogger" "$TARGET" || {
  echo "❌ getLogger not found — aborting"
  exit 1
}

echo ""
echo "✓ Logging configuration cleaned successfully."
echo ""
echo "Next steps:"
echo "  sudo systemctl restart mythos-patch-monitor.service"
echo "  tail -f /var/log/mythos_patch_monitor.log"
echo "============================================================"
