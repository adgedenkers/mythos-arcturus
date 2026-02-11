#!/bin/bash
# Patch 0079 — Media Handlers (Photo Vision + Video Transcription)
# Photos → llava analysis → Iris
# Videos/Video notes → audio extraction → whisper → Iris
set -e

echo "=========================================="
echo "Patch 0079 — Media Handlers"
echo "=========================================="

MYTHOS=/opt/mythos
BOT="$MYTHOS/telegram_bot/mythos_bot.py"

# ── Step 1: Install media handler ────────────────────────────────────────────
echo ""
echo "Step 1: Installing media handler..."
cp "$(dirname "$0")/opt/mythos/telegram_bot/handlers/media_handler.py" \
   "$MYTHOS/telegram_bot/handlers/media_handler.py"
chown adge:adge "$MYTHOS/telegram_bot/handlers/media_handler.py"
echo "  ✅ media_handler.py installed"

# ── Step 2: Update bot to use new handlers ───────────────────────────────────
echo ""
echo "Step 2: Patching bot..."
cp "$BOT" "$BOT.bak.$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('/opt/mythos/telegram_bot/mythos_bot.py', 'r') as f:
    content = f.read()

changes = 0

# Add media handler import
if 'from handlers.media_handler import' not in content:
    content = content.replace(
        '# Voice transcription\nfrom handlers.voice_handler import handle_voice, handle_audio',
        '# Voice transcription\n'
        'from handlers.voice_handler import handle_voice, handle_audio\n'
        '\n'
        '# Media handlers (photo vision, video transcription)\n'
        'from handlers.media_handler import handle_photo_media, handle_video_media'
    )
    changes += 1
    print("  ✅ Added media handler imports")
else:
    print("  ⚠️  Media handler imports already present")

# Replace photo handler to route through media_handler in chat mode
# Find the existing handle_photo function and update it
old_photo_start = 'async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):'
if old_photo_start in content:
    # Find the full function and replace
    lines = content.split('\n')
    new_lines = []
    skip = False
    replaced = False
    
    for i, line in enumerate(lines):
        if old_photo_start in line and not replaced:
            skip = True
            replaced = True
            # Insert new version
            new_lines.append('async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):')
            new_lines.append('    """Handle photo messages - routes to sell mode or media handler"""')
            new_lines.append('    telegram_id = update.effective_user.id')
            new_lines.append('    session = get_or_create_session(telegram_id)')
            new_lines.append('    ')
            new_lines.append('    if not session:')
            new_lines.append('        await update.message.reply_text("❌ Not registered. Use /start")')
            new_lines.append('        return')
            new_lines.append('    ')
            new_lines.append('    if is_sell_mode(session):')
            new_lines.append('        if update.message.photo:')
            new_lines.append('            await handle_sell_photos(update, context, session)')
            new_lines.append('        elif update.message.document and update.message.document.mime_type.startswith("image/"):')
            new_lines.append('            await handle_sell_photos(update, context, session)')
            new_lines.append('        return')
            new_lines.append('    ')
            new_lines.append('    # Chat mode — use vision analysis')
            new_lines.append('    await handle_photo_media(update, context)')
            continue
        
        if skip:
            # Skip until next function def at same indentation
            if (line.startswith('async def ') or line.startswith('def ')) and old_photo_start not in line:
                skip = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    changes += 1
    print("  ✅ Replaced handle_photo to use media handler in chat mode")
else:
    print("  ⚠️  Could not find handle_photo function")

# Add VIDEO and VIDEO_NOTE handlers
if 'filters.VIDEO' not in content:
    content = content.replace(
        '    application.add_handler(MessageHandler(filters.VOICE, handle_voice))',
        '    application.add_handler(MessageHandler(filters.VIDEO, handle_video_media))\n'
        '    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_media))\n'
        '    application.add_handler(MessageHandler(filters.VOICE, handle_voice))'
    )
    changes += 1
    print("  ✅ Added VIDEO and VIDEO_NOTE message handlers")
else:
    print("  ⚠️  Video handlers already registered")

with open('/opt/mythos/telegram_bot/mythos_bot.py', 'w') as f:
    f.write(content)

print(f"\n  Total changes: {changes}")
PYEOF

# ── Step 3: Set vision model env ─────────────────────────────────────────────
echo ""
echo "Step 3: Checking vision model config..."
if grep -q "OLLAMA_VISION_MODEL" "$MYTHOS/.env"; then
    echo "  ⚠️  OLLAMA_VISION_MODEL already set"
else
    echo "OLLAMA_VISION_MODEL=llava:13b" >> "$MYTHOS/.env"
    echo "  ✅ Added OLLAMA_VISION_MODEL=llava:13b to .env"
fi

# ── Step 4: Verify llava is pulled ───────────────────────────────────────────
echo ""
echo "Step 4: Checking llava model..."
if ollama list 2>/dev/null | grep -q "llava:13b"; then
    echo "  ✅ llava:13b available"
else
    echo "  ⚠️  llava:13b not pulled — run: ollama pull llava:13b"
fi

# ── Step 5: Restart bot ─────────────────────────────────────────────────────
echo ""
echo "Step 5: Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

BOT_STATUS=$(sudo systemctl is-active mythos-bot.service)
echo "  Bot: $BOT_STATUS"

if [ "$BOT_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0079 installed"
    echo "=========================================="
    echo ""
    echo "What's new:"
    echo "  📸 Photos in chat mode → llava vision analysis → Iris responds"
    echo "  🎬 Videos → audio extraction → whisper transcription → Iris responds"
    echo "  🎥 Video notes (round videos) → same pipeline as videos"
    echo "  All media saved to /opt/mythos/media/ and recorded in media_files"
    echo ""
    echo "Test:"
    echo "  Send a photo in Telegram (not in sell mode)"
    echo "  Send a short video or video note"
else
    echo ""
    echo "⚠️  Bot failed to start. Check:"
    echo "  journalctl -u mythos-bot.service -n 20 --no-pager"
fi
