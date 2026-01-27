#!/usr/bin/env python3
"""
Mythos Telegram Bot - WITH SELL MODE + CHAT MODE
Updated to include:
- Item selling via photo analysis
- Direct Ollama chat with conversation context
- Default mode: chat
- Enhanced /status with activity summary
"""

import os
import logging
import uuid
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('/opt/mythos/.env')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import sell mode handlers
from handlers import (
    listed_command,
    sold_command,
    enter_sell_mode,
    handle_sell_photos,
    sell_done_command,
    sell_status_command,
    sell_undo_command,
    is_sell_mode,
    export_command,
    inventory_command
)

# Import chat mode handler
from handlers.chat_mode import (
    handle_chat_message,
    clear_chat_context,
    get_chat_stats,
    get_recent_topics
)

# Patch management handlers
from handlers.patch_handlers import (
    patch_command,
    patch_status_command,
    patch_list_command,
    patch_apply_command,
    patch_rollback_command,
    patch_rollback_confirm_command
)

# Configuration
API_URL = "https://mythos-api.denkers.co"
API_KEY = os.getenv('API_KEY_TELEGRAM_BOT')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MEDIA_BASE_PATH = "/opt/mythos/media"

# Default mode for new sessions
DEFAULT_MODE = "chat"

# In-memory session store
SESSIONS = {}

def get_or_create_session(telegram_id):
    """Get or create session for this Telegram user"""
    if telegram_id not in SESSIONS:
        try:
            response = requests.get(
                f"{API_URL}/user/{telegram_id}",
                headers={"X-API-Key": API_KEY}
            )
            
            if response.status_code == 200:
                user = response.json()
                SESSIONS[telegram_id] = {
                    "user": user,
                    "current_mode": DEFAULT_MODE,  # Now defaults to chat
                    "current_model": "auto",
                    "conversation_id": None,
                    "last_activity": datetime.now(),
                    "sell_session": None,
                    "chat_context": None,  # For chat mode conversation history
                    "activity_log": []  # Track recent activity for /status
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    SESSIONS[telegram_id]["last_activity"] = datetime.now()
    return SESSIONS[telegram_id]


def log_activity(session: dict, activity_type: str, details: str):
    """Log an activity to the session for /status reporting"""
    activity_log = session.get("activity_log", [])
    activity_log.append({
        "time": datetime.now().isoformat(),
        "type": activity_type,
        "details": details
    })
    # Keep only last 10 activities
    session["activity_log"] = activity_log[-10:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text(
            "❌ You are not registered in the Mythos system.\n\n"
            f"Your Telegram ID: {telegram_id}\n\n"
            "Please contact Ka to register your account."
        )
        return
    
    user = session["user"]
    log_activity(session, "start", "Session started")
    
    # Initialize chat context for new sessions
    if session.get("chat_context") is None:
        clear_chat_context(session)
    
    await update.message.reply_text(
        f"🔮 Welcome to Mythos, {user['soul_name']}!\n\n"
        f"You're in **chat** mode - just type to talk.\n\n"
        "Quick commands:\n"
        "`/mode db` - Query databases\n"
        "`/mode sell` - Sell items\n"
        "`/status` - What's happening\n"
        "`/help` - All commands",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🔮 **Mythos System Help**

━━━━━━━━━━━━━━━━━━━━━━━━
**QUICK START - MODES**
━━━━━━━━━━━━━━━━━━━━━━━━

`/mode chat` - Talk with local AI (default)
`/mode db` - Query Neo4j/Postgres databases
`/mode sell` - Sell items via photo analysis
`/mode seraphe` - Cosmology assistant
`/mode genealogy` - Bloodline research

━━━━━━━━━━━━━━━━━━━━━━━━
**CHAT MODE** (default)
━━━━━━━━━━━━━━━━━━━━━━━━

Just type to chat! Context is maintained.
`/status` - See what you've been discussing
`/clear` - Reset conversation context
`/model fast` - Use faster model
`/model deep` - Use best quality model

━━━━━━━━━━━━━━━━━━━━━━━━
**SELL MODE**
━━━━━━━━━━━━━━━━━━━━━━━━

`/mode sell` - Enter sell mode
Send 3 photos → Auto-analyzed → Added to inventory
`/done` - Exit sell mode
`/undo` - Remove last item
`/inventory` - View all items
`/export` - Generate FB listings
`/listed <id>` - Mark as listed
`/sold <id>` - Mark as sold

━━━━━━━━━━━━━━━━━━━━━━━━
**CONVERSATIONS**
━━━━━━━━━━━━━━━━━━━━━━━━

`/convo` - Start tracked conversation
`/endconvo` - End tracked conversation

━━━━━━━━━━━━━━━━━━━━━━━━
**SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━━━

`/status` - Current mode, activity & context
`/patch_status` - System version
`/photos` - View recent photos
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - comprehensive status with activity summary"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Check if in sell mode - delegate to sell status
    if is_sell_mode(session):
        await sell_status_command(update, context, session)
        return
    
    user = session["user"]
    mode = session.get("current_mode", "chat")
    model = session.get("current_model", "auto")
    
    # Build status message
    lines = [f"📊 **Status for {user['soul_name']}**", ""]
    
    # Current mode
    mode_emoji = {
        "chat": "💬",
        "db": "🗄️",
        "sell": "📦",
        "seraphe": "🔮",
        "genealogy": "🌳"
    }
    lines.append(f"{mode_emoji.get(mode, '🔧')} **Mode:** {mode}")
    lines.append(f"🤖 **Model:** {model}")
    
    # Tracked conversation status
    if session.get("conversation_id"):
        lines.append(f"📝 **Tracked Convo:** Active ({session['conversation_id'][:8]}...)")
    
    # Chat mode specific info
    if mode == "chat":
        stats = get_chat_stats(session)
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("**💬 Chat Context**")
        lines.append(f"Messages this session: {stats['message_count']}")
        
        # Get recent topics/summary
        topics = get_recent_topics(session)
        if topics:
            lines.append("")
            lines.append("**Recent topics:**")
            for topic in topics[:5]:
                lines.append(f"• {topic}")
        
        if stats['message_count'] > 0:
            lines.append("")
            lines.append("_Use /clear to reset conversation_")
    
    # Recent activity log
    activity_log = session.get("activity_log", [])
    if activity_log:
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("**📋 Recent Activity**")
        for activity in activity_log[-5:]:
            time_str = activity['time'][11:16]  # Extract HH:MM
            lines.append(f"• {time_str} - {activity['details']}")
    
    # Footer with tips
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    if mode == "chat":
        lines.append("_Just type to continue chatting_")
    elif mode == "db":
        lines.append("_Ask questions about souls, persons, lineages_")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command to switch modes"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if context.args:
        new_mode = context.args[0].lower()
        
        valid_modes = ["db", "seraphe", "genealogy", "chat", "sell"]
        
        if new_mode in valid_modes:
            old_mode = session.get("current_mode", "chat")
            
            # Handle sell mode specially
            if new_mode == "sell":
                log_activity(session, "mode_change", f"Entered sell mode")
                await enter_sell_mode(update, session)
                return
            
            # Exit sell mode if switching away
            if is_sell_mode(session):
                session["sell_session"] = None
            
            # Initialize chat context when entering chat mode
            if new_mode == "chat":
                if session.get("chat_context") is None:
                    clear_chat_context(session)
            
            session["current_mode"] = new_mode
            log_activity(session, "mode_change", f"Switched to {new_mode} mode")
            
            mode_descriptions = {
                "db": "Database Manager - Query souls, persons, and lineages via natural language",
                "seraphe": "Seraphe's Cosmology Assistant - Spiritual guidance and symbolism",
                "genealogy": "Genealogy Assistant - Trace bloodlines and ancestors",
                "chat": "Chat Mode - Direct conversation with local Ollama LLM\n\nJust type to chat! Context is maintained across messages.\nUse /clear to reset conversation."
            }
            
            await update.message.reply_text(
                f"✅ Switched to **{new_mode}** mode\n\n"
                f"📝 {mode_descriptions[new_mode]}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\n\n"
                "Available modes: db, seraphe, genealogy, chat, sell"
            )
    else:
        current = session.get("current_mode", "chat")
        await update.message.reply_text(
            f"Current mode: **{current}**\n\n"
            "Available modes:\n"
            "  `/mode chat`      - Talk with AI (default)\n"
            "  `/mode db`        - Database queries\n"
            "  `/mode sell`      - Sell items\n"
            "  `/mode seraphe`   - Cosmology\n"
            "  `/mode genealogy` - Bloodlines",
            parse_mode='Markdown'
        )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - reset chat context"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    clear_chat_context(session)
    log_activity(session, "clear", "Chat context cleared")
    await update.message.reply_text("🔄 Chat context cleared. Starting fresh conversation.")


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /done command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if is_sell_mode(session):
        await sell_done_command(update, context, session)
        log_activity(session, "sell", "Exited sell mode")
    else:
        await update.message.reply_text("Nothing to finish. Not in sell mode.")


async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /undo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if is_sell_mode(session):
        await sell_undo_command(update, context, session)
    else:
        await update.message.reply_text("Nothing to undo. Not in sell mode.")


async def convo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if session.get("conversation_id"):
        await update.message.reply_text(
            f"⚠️ Already in conversation mode\n"
            f"Current: {session['conversation_id'][:8]}...\n\n"
            "Use /endconvo to end first."
        )
        return
    
    conversation_id = str(uuid.uuid4())
    session["conversation_id"] = conversation_id
    log_activity(session, "convo", f"Started tracked conversation")
    
    try:
        response = requests.post(
            f"{API_URL}/conversation/start",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "title": f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            await update.message.reply_text(
                f"🗣️ Conversation started\n"
                f"ID: {conversation_id[:8]}...\n\n"
                "All messages will be tracked.\n"
                "Use /endconvo when finished."
            )
        else:
            await update.message.reply_text(
                f"⚠️ Local conversation started\n"
                f"ID: {conversation_id[:8]}...\n"
                "(API notification failed)"
            )
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text(
            f"⚠️ Conversation started locally\n"
            f"ID: {conversation_id[:8]}..."
        )


async def endconvo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endconvo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if not session.get("conversation_id"):
        await update.message.reply_text("No active conversation.")
        return
    
    conversation_id = session["conversation_id"]
    session["conversation_id"] = None
    log_activity(session, "convo", "Ended tracked conversation")
    
    try:
        requests.post(
            f"{API_URL}/conversation/end",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id
            },
            timeout=10
        )
    except:
        pass
    
    await update.message.reply_text(
        f"✅ Conversation ended\n"
        f"ID: {conversation_id[:8]}..."
    )


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if context.args:
        new_model = context.args[0].lower()
        
        if new_model in ["auto", "fast", "deep"]:
            session["current_model"] = new_model
            log_activity(session, "model", f"Switched to {new_model} model")
            
            descriptions = {
                "auto": "Automatic (qwen2.5:32b)",
                "fast": "Fast (llama3.2:3b, ~5s)",
                "deep": "Best quality (qwen2.5:32b, ~30s)"
            }
            
            await update.message.reply_text(
                f"✅ Model: **{new_model}**\n{descriptions[new_model]}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown model: {new_model}\n"
                "Available: auto, fast, deep"
            )
    else:
        current = session.get("current_model", "auto")
        await update.message.reply_text(
            f"Current model: **{current}**\n\n"
            "`/model auto` - Smart routing (qwen2.5:32b)\n"
            "`/model fast` - Quick (llama3.2:3b)\n"
            "`/model deep` - Best (qwen2.5:32b)",
            parse_mode='Markdown'
        )


async def photos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /photos command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    try:
        response = requests.get(
            f"{API_URL}/media/recent/{telegram_id}",
            headers={"X-API-Key": API_KEY},
            params={"limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            
            if not photos:
                await update.message.reply_text("No photos yet.")
                return
            
            lines = [f"📸 Recent Photos ({len(photos)})\n"]
            for i, photo in enumerate(photos, 1):
                processed = "✅" if photo.get('processed') else "⏳"
                lines.append(f"{i}. {processed} {photo.get('filename', 'unknown')}")
            
            await update.message.reply_text("\n".join(lines))
        else:
            await update.message.reply_text("❌ Failed to get photos.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def inventory_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for inventory command"""
    await inventory_command(update, context)


async def export_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for export command"""
    await export_command(update, context)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages - routes to sell mode or general handling"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Not registered. Use /start")
        return
    
    # Route to sell mode if active
    if is_sell_mode(session):
        # Handle both photos and image documents
        if update.message.photo:
            await handle_sell_photos(update, context, session)
        elif update.message.document and update.message.document.mime_type.startswith('image/'):
            # Convert document to photo-like structure for sell mode
            await handle_sell_photos(update, context, session)
        return
    
    # Otherwise, standard photo handling (not in sell mode)
    if not update.message.photo:
        return
    
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    user_uuid = session['user']['uuid']
    conversation_id = session.get('conversation_id')
    
    try:
        file = await context.bot.get_file(photo.file_id)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_prefix = user_uuid[:8]
        filename = f"{timestamp}_{photo.file_unique_id[:16]}.jpg"
        
        storage_dir = os.path.join(MEDIA_BASE_PATH, user_prefix)
        os.makedirs(storage_dir, exist_ok=True)
        
        storage_path = os.path.join(storage_dir, filename)
        await file.download_to_drive(storage_path)
        
        file_size = os.path.getsize(storage_path)
        
        response = requests.post(
            f"{API_URL}/media/upload",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "filename": filename,
                "file_path": storage_path,
                "file_size": file_size,
                "width": photo.width,
                "height": photo.height,
                "telegram_file_id": photo.file_id,
                "telegram_file_unique_id": photo.file_unique_id,
                "caption": caption,
                "mime_type": "image/jpeg"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(
                f"📸 Photo received\n"
                f"🆔 {data['media_id'][:8]}...\n"
                f"💾 {file_size // 1024}KB"
            )
        else:
            await update.message.reply_text("⚠️ Photo saved locally.")
            
    except Exception as e:
        logger.error(f"Photo error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start")
        return
    
    # In sell mode, text is ignored (photos only)
    if is_sell_mode(session):
        await update.message.reply_text(
            "📦 In sell mode - send photos only.\n"
            "Use /done to exit or /status to check progress."
        )
        return
    
    user_message = update.message.text
    user = session["user"]
    mode = session["current_mode"]
    model = session["current_model"]
    conversation_id = session.get("conversation_id")
    
    await update.message.chat.send_action("typing")
    
    # Route to chat mode handler if in chat mode
    if mode == "chat":
        try:
            response_text = await handle_chat_message(user_message, session, model)
            
            # Log activity with truncated message
            preview = user_message[:50] + "..." if len(user_message) > 50 else user_message
            log_activity(session, "chat", f"Asked: {preview}")
            
            # Handle long responses
            if len(response_text) > 4000:
                chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response_text)
            return
            
        except Exception as e:
            logger.error(f"Chat mode error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Chat error: {e}")
            return
    
    # For other modes, use the API
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
            
            # Log activity
            preview = user_message[:50] + "..." if len(user_message) > 50 else user_message
            log_activity(session, mode, f"Query: {preview}")
            
            if len(bot_response) > 4000:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
        else:
            await update.message.reply_text(f"❌ API Error: {response.status_code}")
    
    except requests.Timeout:
        await update.message.reply_text("⏱️ Request timed out.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred.")


def main():
    """Start the bot"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    if not API_KEY:
        print("❌ API_KEY_TELEGRAM_BOT not found")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("convo", convo_command))
    application.add_handler(CommandHandler("endconvo", endconvo_command))
    application.add_handler(CommandHandler("photos", photos_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Sell mode commands
    application.add_handler(CommandHandler("done", done_command))
    application.add_handler(CommandHandler("undo", undo_command))
    application.add_handler(CommandHandler("inventory", inventory_wrapper))
    application.add_handler(CommandHandler("export", export_wrapper))
    application.add_handler(CommandHandler("listed", listed_command))
    application.add_handler(CommandHandler("sold", sold_command))
    
    # Patch management commands
    application.add_handler(CommandHandler("patch", patch_command))
    application.add_handler(CommandHandler("patch_status", patch_status_command))
    application.add_handler(CommandHandler("patch_list", patch_list_command))
    application.add_handler(CommandHandler("patch_apply", patch_apply_command))
    application.add_handler(CommandHandler("patch_rollback", patch_rollback_command))
    application.add_handler(CommandHandler("patch_rollback_confirm", patch_rollback_confirm_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print("🤖 Mythos Telegram Bot starting...")
    print(f"💬 Default mode: {DEFAULT_MODE}")
    print("📦 Sell mode enabled")
    print("📸 Photo analysis via Ollama")
    print("   Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
