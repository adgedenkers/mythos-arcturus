#!/bin/bash
# ============================================================
# SYS-0001: Stream Development System
# 
# Enables parallel development across named streams:
#   NEU (NEURO), LOG (LOGOS), MNE (MNEMOS), SEN (SENSUS), SYS (SYSTEM)
#
# Changes:
#   1. Updates patch monitor to recognize stream-prefixed patches
#   2. Deploys STREAMS.md, STREAMS.json, REQUESTS.md
#   3. Deploys stream_status.sh diagnostic script
#   4. Preserves all existing patch_NNNN_ functionality
# ============================================================
set -e

MYTHOS="/opt/mythos"
DOCS="$MYTHOS/docs"
STREAMS_DIR="$DOCS/streams"
PATCH_MONITOR="$MYTHOS/mythos_patch_monitor.py"
BACKUP_SUFFIX=".bak_SYS0001"

echo "============================================================"
echo "  SYS-0001: Stream Development System"
echo "============================================================"

# ── 1. Backup patch monitor ──
echo ""
echo "[1/4] Backing up patch monitor..."
if [ -f "$PATCH_MONITOR" ]; then
    cp -v "$PATCH_MONITOR" "${PATCH_MONITOR}${BACKUP_SUFFIX}"
    echo "  ✓ Backed up"
else
    echo "  ERROR: Patch monitor not found at $PATCH_MONITOR"
    exit 1
fi

# ── 2. Update patch monitor regex ──
echo ""
echo "[2/4] Updating patch monitor to recognize stream prefixes..."

# The old pattern only matches: patch_0001_foo.zip
# The new pattern also matches: NEU-0001_foo.zip, LOG-0023_bar.zip, SYS-0001_baz.zip
# We use python to do the replacement safely

/opt/mythos/.venv/bin/python3 << 'PYEOF'
import re
from pathlib import Path

monitor = Path("/opt/mythos/mythos_patch_monitor.py")
content = monitor.read_text()

old_pattern = r'"patch": re.compile(r"^\^patch_\\d\{4\}_\.\*\\\.zip\$")'

# More robust: find the exact line
old_line = '    "patch": re.compile(r"^patch_\\d{4}_.*\\.zip$"),'
new_line = '    "patch": re.compile(r"^(patch_\\d{4}|[A-Z]{3}-\\d{4})_.*\\.zip$"),'

if old_line in content:
    content = content.replace(old_line, new_line)
    monitor.write_text(content)
    print("  ✓ Patch pattern updated")
    print(f"    Old: {old_line.strip()}")
    print(f"    New: {new_line.strip()}")
else:
    # Try a regex-based find in case whitespace differs
    pattern = re.compile(r'(\s*"patch":\s*re\.compile\(r"\^patch_\\d\{4\}_\.\*\\\.zip\$"\))')
    match = pattern.search(content)
    if match:
        indent = match.group(1).split('"')[0]
        replacement = f'{indent}"patch": re.compile(r"^(patch_\\d{{4}}|[A-Z]{{3}}-\\d{{4}})_.*\\.zip$"),'
        content = content[:match.start()] + replacement + content[match.end():]
        monitor.write_text(content)
        print("  ✓ Patch pattern updated (regex match)")
    else:
        print("  WARNING: Could not find patch pattern to update")
        print("  You may need to update manually.")
        print("  Looking for: ^patch_\\d{4}_.*\\.zip$")
        # Don't exit — rest of patch is still valuable
PYEOF

# Verify the change
echo ""
echo "  Verifying patch monitor syntax..."
/opt/mythos/.venv/bin/python3 -c "
import py_compile
py_compile.compile('/opt/mythos/mythos_patch_monitor.py', doraise=True)
print('  ✓ Syntax OK')
" || {
    echo "  ERROR: Syntax check failed — restoring backup"
    cp "${PATCH_MONITOR}${BACKUP_SUFFIX}" "$PATCH_MONITOR"
    exit 1
}

# ── 3. Deploy stream coordination files ──
echo ""
echo "[3/4] Deploying stream coordination files..."

mkdir -p "$STREAMS_DIR"

cp -v opt/mythos/docs/STREAMS.md "$DOCS/STREAMS.md"
cp -v opt/mythos/docs/STREAMS.json "$DOCS/STREAMS.json"
cp -v opt/mythos/docs/REQUESTS.md "$DOCS/REQUESTS.md"
cp -v opt/mythos/docs/streams/stream_status.sh "$STREAMS_DIR/stream_status.sh"

chmod +x "$STREAMS_DIR/stream_status.sh"

echo "  ✓ Stream files deployed"

# ── 4. Restart patch monitor ──
echo ""
echo "[4/4] Restarting patch monitor..."
sudo systemctl restart mythos-patch-monitor.service
sleep 2

STATUS=$(sudo systemctl is-active mythos-patch-monitor.service)
if [ "$STATUS" = "active" ]; then
    echo "  ✓ mythos-patch-monitor — active"
else
    echo "  WARNING: mythos-patch-monitor — $STATUS"
    echo "  Check: journalctl -u mythos-patch-monitor.service -n 20"
    echo "  Backup at: ${PATCH_MONITOR}${BACKUP_SUFFIX}"
fi

echo ""
echo "============================================================"
echo "  SYS-0001 Installed"
echo ""
echo "  Stream prefixes now recognized:"
echo "    NEU-NNNN_*.zip  (NEURO)"
echo "    LOG-NNNN_*.zip  (LOGOS)"
echo "    MNE-NNNN_*.zip  (MNEMOS)"
echo "    SEN-NNNN_*.zip  (SENSUS)"
echo "    SYS-NNNN_*.zip  (SYSTEM)"
echo "    patch_NNNN_*.zip (legacy — still works)"
echo ""
echo "  Files deployed:"
echo "    $DOCS/STREAMS.md"
echo "    $DOCS/STREAMS.json"
echo "    $DOCS/REQUESTS.md"
echo "    $STREAMS_DIR/stream_status.sh"
echo ""
echo "  Next step:"
echo "    Run the inventory session to assign existing"
echo "    infrastructure to streams."
echo ""
echo "  Quick test:"
echo "    bash $STREAMS_DIR/stream_status.sh"
echo "    bash $STREAMS_DIR/stream_status.sh NEU"
echo "============================================================"
