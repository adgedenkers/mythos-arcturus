#!/bin/bash
# Patch 0076 — Voice Transcription
# Adds voice message handling with GPU-accelerated whisper transcription
set -e

echo "=========================================="
echo "Patch 0076 — Voice Transcription"
echo "=========================================="

MYTHOS=/opt/mythos

# ── Step 1: Install transcription service ────────────────────────────────────
echo ""
echo "Step 1: Installing transcription service..."
mkdir -p "$MYTHOS/services"

# Create __init__.py if missing
touch "$MYTHOS/services/__init__.py"

cp "$(dirname "$0")/opt/mythos/services/transcription.py" "$MYTHOS/services/transcription.py"
chown adge:adge "$MYTHOS/services/transcription.py" "$MYTHOS/services/__init__.py"
echo "  ✅ transcription.py installed"

# ── Step 2: Install voice handler ────────────────────────────────────────────
echo ""
echo "Step 2: Installing voice handler..."
cp "$(dirname "$0")/opt/mythos/telegram_bot/handlers/voice_handler.py" \
   "$MYTHOS/telegram_bot/handlers/voice_handler.py"
chown adge:adge "$MYTHOS/telegram_bot/handlers/voice_handler.py"
echo "  ✅ voice_handler.py installed"

# ── Step 3: Register voice handlers in bot ───────────────────────────────────
echo ""
echo "Step 3: Registering voice handlers in bot..."

BOT="$MYTHOS/telegram_bot/mythos_bot.py"
cp "$BOT" "$BOT.bak.$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('/opt/mythos/telegram_bot/mythos_bot.py', 'r') as f:
    content = f.read()

changes = 0

# Add import for voice handler
if 'from handlers.voice_handler import' not in content:
    # Add after the ollama_models import block
    content = content.replace(
        '# Task tracking commands',
        '# Voice transcription\n'
        'from handlers.voice_handler import handle_voice, handle_audio\n'
        '\n'
        '# Task tracking commands'
    )
    changes += 1
    print("  ✅ Added voice handler import")
else:
    print("  ⚠️  Voice handler import already present")

# Add VOICE and AUDIO message handlers (before the TEXT handler)
if 'filters.VOICE' not in content:
    content = content.replace(
        '    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))',
        '    application.add_handler(MessageHandler(filters.VOICE, handle_voice))\n'
        '    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))\n'
        '    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))'
    )
    changes += 1
    print("  ✅ Added VOICE and AUDIO message handlers")
else:
    print("  ⚠️  Voice handlers already registered")

# Add services to Python path (so bot can import services.transcription)
if "sys.path.insert(0, '/opt/mythos')" not in content:
    content = content.replace(
        "import sys\n",
        "import sys\nsys.path.insert(0, '/opt/mythos')\n",
        1
    )
    if "import sys" not in content:
        # Add sys import at top
        content = content.replace(
            "import os",
            "import os\nimport sys\nsys.path.insert(0, '/opt/mythos')",
            1
        )
    changes += 1
    print("  ✅ Added /opt/mythos to Python path")
else:
    print("  ⚠️  Python path already configured")

with open('/opt/mythos/telegram_bot/mythos_bot.py', 'w') as f:
    f.write(content)

print(f"\n  Total changes: {changes}")
PYEOF

# ── Step 4: Verify dependencies ─────────────────────────────────────────────
echo ""
echo "Step 4: Verifying dependencies..."

echo -n "  ffmpeg: "
which ffmpeg > /dev/null 2>&1 && echo "✅" || echo "❌ MISSING — run: sudo apt install ffmpeg"

echo -n "  faster-whisper: "
/opt/mythos/.venv/bin/python3 -c "from faster_whisper import WhisperModel; print('✅')" 2>&1 || echo "❌ MISSING"

echo -n "  torch CUDA: "
/opt/mythos/.venv/bin/python3 -c "import torch; print('✅' if torch.cuda.is_available() else '❌ NO CUDA')" 2>&1

# ── Step 5: Create media directories ────────────────────────────────────────
echo ""
echo "Step 5: Ensuring media directories..."
mkdir -p /opt/mythos/media
chown adge:adge /opt/mythos/media
echo "  ✅ /opt/mythos/media/ ready"

# ── Step 6: Restart bot ─────────────────────────────────────────────────────
echo ""
echo "Step 6: Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

BOT_STATUS=$(sudo systemctl is-active mythos-bot.service)
echo "  Bot: $BOT_STATUS"

if [ "$BOT_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0076 installed successfully!"
    echo "=========================================="
    echo ""
    echo "What's new:"
    echo "  • Voice messages → transcribed via faster-whisper (GPU)"
    echo "  • Audio files → transcribed and saved"
    echo "  • Transcripts sent to Iris for response"
    echo "  • All audio saved to /opt/mythos/media/{user}/"
    echo "  • Media records saved to media_files table"
    echo ""
    echo "Usage:"
    echo "  Send a voice message in Telegram → Iris transcribes and responds"
    echo ""
    echo "Note: First voice message will take ~15s extra to load the whisper model."
    echo "Subsequent messages transcribe much faster."
else
    echo ""
    echo "⚠️  Bot failed to start. Check:"
    echo "  journalctl -u mythos-bot.service -n 20 --no-pager"
fi
