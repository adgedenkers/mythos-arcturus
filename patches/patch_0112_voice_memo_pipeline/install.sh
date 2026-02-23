#!/bin/bash
# Patch 0112: Voice Memo Transcription Pipeline
# Syncthing watcher → Redis → GPU transcription → diarization → PostgreSQL → Telegram
set -e

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS=/opt/mythos

echo "=========================================="
echo "Patch 0112 — Voice Memo Pipeline"
echo "=========================================="

# ── Step 1: Database migration ────────────────────────────────────────────────
echo ""
echo "Step 1: Creating voice_memos tables..."
sudo -u postgres psql -d mythos -f "$PATCH_DIR/migration.sql"
echo "  ✓ Tables created"

# ── Step 2: Install services and workers ──────────────────────────────────────
echo ""
echo "Step 2: Installing Python files..."

cp "$PATCH_DIR/opt/mythos/services/diarized_transcription.py" "$MYTHOS/services/"
cp "$PATCH_DIR/opt/mythos/services/voice_watcher.py" "$MYTHOS/services/"
cp "$PATCH_DIR/opt/mythos/workers/transcription_worker.py" "$MYTHOS/workers/"

echo "  ✓ diarized_transcription.py installed"
echo "  ✓ voice_watcher.py installed"
echo "  ✓ transcription_worker.py installed"

# ── Step 3: Register transcription worker in worker.py ────────────────────────
echo ""
echo "Step 3: Registering transcription worker type..."

# Check if already registered
if grep -q '"transcription"' "$MYTHOS/workers/worker.py" 2>/dev/null; then
    echo "  ✓ Already registered"
else
    # Insert the transcription worker type into WORKER_TYPES dict
    # Find the closing brace of WORKER_TYPES and insert before it
    python3 << 'PYEOF'
import re

worker_file = "/opt/mythos/workers/worker.py"

with open(worker_file, "r") as f:
    content = f.read()

# The new worker type entry
new_entry = '''    "transcription": {
        "stream": "mythos:assignments:transcription",
        "group": "transcription_workers",
        "module": "transcription_worker",
        "function": "process_transcription"
    },'''

# Find the WORKER_TYPES dict and add before the closing brace
# Look for the last entry in the dict (ends with },\n})
# We'll insert after the last worker entry

# Find the "summary" entry (last one currently) and add after it
if '"summary"' in content and '"transcription"' not in content:
    # Find the end of the summary block
    # Pattern: "summary": { ... }  followed by the closing } of WORKER_TYPES
    # Insert our new entry after the summary block's closing }
    pattern = r'("summary"\s*:\s*\{[^}]+\})'
    match = re.search(pattern, content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + ',\n' + new_entry + content[insert_pos:]
        
        with open(worker_file, "w") as f:
            f.write(content)
        print("  ✓ Transcription worker registered in worker.py")
    else:
        print("  ⚠️  Could not find insertion point — add manually")
else:
    print("  ✓ Already present or summary entry not found")
PYEOF
fi

# ── Step 4: Ensure directories exist ─────────────────────────────────────────
echo ""
echo "Step 4: Ensuring directories..."
mkdir -p "$MYTHOS/voice_memos"/{incoming,processing,archive,wav_cache}
echo "  ✓ voice_memos directories ready"

# ── Step 5: Install systemd services ─────────────────────────────────────────
echo ""
echo "Step 5: Installing systemd services..."

sudo cp "$PATCH_DIR/mythos-voice-watcher.service" /etc/systemd/system/
sudo cp "$PATCH_DIR/mythos-transcription-worker.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mythos-voice-watcher.service
sudo systemctl enable mythos-transcription-worker.service

echo "  ✓ Services installed and enabled"

# ── Step 6: Start services ───────────────────────────────────────────────────
echo ""
echo "Step 6: Starting services..."

sudo systemctl start mythos-transcription-worker.service
sleep 2
sudo systemctl start mythos-voice-watcher.service
sleep 1

# Check status
if systemctl is-active --quiet mythos-transcription-worker.service; then
    echo "  ✓ Transcription worker running"
else
    echo "  ⚠️  Transcription worker failed — check: journalctl -u mythos-transcription-worker -n 20"
fi

if systemctl is-active --quiet mythos-voice-watcher.service; then
    echo "  ✓ Voice watcher running"
else
    echo "  ⚠️  Voice watcher failed — check: journalctl -u mythos-voice-watcher -n 20"
fi

echo ""
echo "=========================================="
echo "Patch 0112 Complete"
echo "=========================================="
echo ""
echo "Pipeline:"
echo "  1. Syncthing syncs .m4a → /opt/mythos/voice_memos/incoming/"
echo "  2. Watcher detects file → pushes to Redis stream"
echo "  3. Worker transcribes (GPU) + diarizes → stores in PostgreSQL"
echo "  4. Telegram notification with transcript preview"
echo ""
echo "Next steps:"
echo "  1. Configure Syncthing shared folder (see below)"
echo "  2. Install Möbius Sync on iPhone"
echo "  3. Set up HuggingFace token for diarization (optional)"
echo ""
echo "Syncthing Web UI: http://localhost:8384"
echo "  - Add shared folder pointing to: /opt/mythos/voice_memos/incoming"
echo "  - Set folder type: 'Receive Only'"
echo "  - Connect iPhone via Möbius Sync"
echo ""
echo "Syncthing Device ID (for pairing):"
syncthing -device-id 2>/dev/null || echo "  (run 'syncthing -device-id' to get it)"
echo ""
echo "Test manually:"
echo "  cp ~/some_recording.m4a /opt/mythos/voice_memos/incoming/"
echo "  journalctl -fu mythos-voice-watcher"
echo "  journalctl -fu mythos-transcription-worker"
