#!/bin/bash
# Patch 0077 — Message Buffer
# Collects multi-chunk Telegram messages before sending to Iris as one
set -e

echo "=========================================="
echo "Patch 0077 — Message Buffer"
echo "=========================================="

MYTHOS=/opt/mythos
BOT="$MYTHOS/telegram_bot/mythos_bot.py"

cp "$BOT" "$BOT.bak.$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('/opt/mythos/telegram_bot/mythos_bot.py', 'r') as f:
    content = f.read()

changes = 0

# ── 1. Add asyncio import if missing ────────────────────────────────────────
if 'import asyncio' not in content:
    content = content.replace('import os', 'import os\nimport asyncio', 1)
    changes += 1
    print("  ✅ Added asyncio import")

# ── 2. Add message buffer dict after session storage ────────────────────────
# Find where sessions are stored and add buffer nearby
if 'MESSAGE_BUFFER' not in content:
    # Add after the MEDIA_BASE_PATH or similar global
    content = content.replace(
        'MEDIA_BASE_PATH = "/opt/mythos/media"',
        'MEDIA_BASE_PATH = "/opt/mythos/media"\n'
        '\n'
        '# Message buffer for collecting multi-chunk messages\n'
        '# { telegram_id: {"chunks": [str], "timer": asyncio.Task, "update": Update, "context": Context} }\n'
        'MESSAGE_BUFFER = {}\n'
        'MESSAGE_BUFFER_DELAY = 1.5  # seconds to wait for more chunks\n'
    )
    changes += 1
    print("  ✅ Added MESSAGE_BUFFER globals")

# ── 3. Replace handle_message with buffered version ─────────────────────────
old_handler = '''async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start")
        return
    
    if is_sell_mode(session):
        await update.message.reply_text(
            "📦 Sell mode - send photos only.\\n"
            "/done to exit"
        )
        return
    
    user_message = update.message.text
    mode = session["current_mode"]
    model = session["current_model"]
    conversation_id = session.get("conversation_id")
    
    await update.message.chat.send_action("typing")
    
    # Log activity
    preview = user_message[:30] + "..." if len(user_message) > 30 else user_message
    log_activity(session, mode, preview)
    
    try:
        response = requests.post(
            f"{API_URL}/message",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "message": user_message,
                "mode": mode,
                "model_preference": model,
                "conversation_id": conversation_id
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data["response"]
            
            if len(bot_response) > 4000:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
        else:
            await update.message.reply_text(f"❌ API Error: {response.status_code}")
    
    except requests.Timeout:
        await update.message.reply_text("⏱️ Timed out")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")'''

new_handler = '''async def _process_buffered_message(telegram_id: int):
    """Process collected message chunks as a single message"""
    if telegram_id not in MESSAGE_BUFFER:
        return
    
    buf = MESSAGE_BUFFER.pop(telegram_id)
    combined_message = "\\n".join(buf["chunks"])
    update = buf["update"]
    context = buf["context"]
    
    session = get_or_create_session(telegram_id)
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start")
        return
    
    mode = session["current_mode"]
    model = session["current_model"]
    conversation_id = session.get("conversation_id")
    
    await update.message.chat.send_action("typing")
    
    # Log activity
    chunk_count = len(buf["chunks"])
    preview = combined_message[:30] + "..." if len(combined_message) > 30 else combined_message
    if chunk_count > 1:
        log_activity(session, mode, f"[{chunk_count} chunks] {preview}")
        logger.info(f"Processing buffered message: {chunk_count} chunks, {len(combined_message)} chars")
    else:
        log_activity(session, mode, preview)
    
    try:
        response = requests.post(
            f"{API_URL}/message",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "message": combined_message,
                "mode": mode,
                "model_preference": model,
                "conversation_id": conversation_id
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data["response"]
            
            if len(bot_response) > 4000:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
        else:
            await update.message.reply_text(f"❌ API Error: {response.status_code}")
    
    except requests.Timeout:
        await update.message.reply_text("⏱️ Timed out")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages — buffers multi-chunk messages before processing"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start")
        return
    
    if is_sell_mode(session):
        await update.message.reply_text(
            "📦 Sell mode - send photos only.\\n"
            "/done to exit"
        )
        return
    
    user_message = update.message.text
    
    # Buffer the message chunk
    if telegram_id in MESSAGE_BUFFER:
        # Cancel existing timer, add chunk, restart timer
        buf = MESSAGE_BUFFER[telegram_id]
        buf["timer"].cancel()
        buf["chunks"].append(user_message)
        buf["update"] = update  # keep latest update for reply
        buf["context"] = context
    else:
        # First chunk — start new buffer
        MESSAGE_BUFFER[telegram_id] = {
            "chunks": [user_message],
            "update": update,
            "context": context,
            "timer": None,
        }
    
    # Set timer — when it fires, process all collected chunks
    async def fire():
        await asyncio.sleep(MESSAGE_BUFFER_DELAY)
        await _process_buffered_message(telegram_id)
    
    MESSAGE_BUFFER[telegram_id]["timer"] = asyncio.ensure_future(fire())'''

if '_process_buffered_message' not in content:
    content = content.replace(old_handler, new_handler)
    changes += 1
    print("  ✅ Replaced handle_message with buffered version")
else:
    print("  ⚠️  Buffered handler already present")

with open('/opt/mythos/telegram_bot/mythos_bot.py', 'w') as f:
    f.write(content)

print(f"\n  Total changes: {changes}")
PYEOF

echo ""
echo "Restarting bot..."
sudo systemctl restart mythos-bot.service
sleep 3

BOT_STATUS=$(sudo systemctl is-active mythos-bot.service)
echo "  Bot: $BOT_STATUS"

if [ "$BOT_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0077 installed"
    echo "=========================================="
    echo ""
    echo "What's new:"
    echo "  • Multi-chunk messages collected before processing"
    echo "  • 1.5s buffer window (waits for more chunks)"
    echo "  • Chunks joined with newlines, sent as one message"
    echo "  • Single Iris response for the complete message"
    echo ""
    echo "Test: Send a long message that Telegram splits into multiple chunks."
else
    echo ""
    echo "⚠️  Bot failed to start. Check:"
    echo "  journalctl -u mythos-bot.service -n 20 --no-pager"
fi
