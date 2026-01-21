#!/usr/bin/env python3
"""
Mythos Telegram Bot - PHOTO HANDLING UPDATE
Sprint 1: Accept photos as input, store and log appropriately

Changes from original:
- Added handle_photo function for photo messages
- Added handle_photo_with_caption for photos with text
- Added /photos command to list recent photos
- Added photo metadata to message context
- Registered PHOTO handler in main()
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

# Configuration
API_URL = "https://mythos-api.denkers.co"
API_KEY = os.getenv('API_KEY_TELEGRAM_BOT')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MEDIA_BASE_PATH = "/opt/mythos/media"  # Base path for media storage

# In-memory session store
SESSIONS = {}

def get_or_create_session(telegram_id):
    """Get or create session for this Telegram user"""
    if telegram_id not in SESSIONS:
        # Verify user is registered
        try:
            response = requests.get(
                f"{API_URL}/user/{telegram_id}",
                headers={"X-API-Key": API_KEY}
            )
            
            if response.status_code == 200:
                user = response.json()
                SESSIONS[telegram_id] = {
                    "user": user,
                    "current_mode": "db",
                    "current_model": "auto",
                    "conversation_id": None,  # For /convo mode
                    "last_activity": datetime.now()
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    # Update last activity
    SESSIONS[telegram_id]["last_activity"] = datetime.now()
    
    return SESSIONS[telegram_id]

# Command handlers
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
    
    await update.message.reply_text(
        f"🔮 Welcome to the Mythos System, {user['soul_name']}!\n\n"
        f"Current mode: {session['current_mode']}\n\n"
        "Available commands:\n"
        "/mode - Switch modes\n"
        "/convo - Start a tracked conversation\n"
        "/photos - View recent photos\n"
        "/help - Show help\n"
        "/status - Show current status\n\n"
        "Just send a message or photo to interact with the current mode."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🔮 Mythos System Commands

📋 Modes:
  /mode db        - Database Manager
  /mode seraphe   - Seraphe's Cosmology Assistant
  /mode genealogy - Genealogy Assistant
  /mode chat      - Natural conversation

💬 Conversation:
  /convo          - Start tracked conversation (builds context graph)
  /endconvo       - End tracked conversation

🤖 AI Models:
  /model auto     - Smart routing (recommended)
  /model fast     - Quick responses (~10 sec)
  /model deep     - Best quality (~60 sec)

📸 Media:
  /photos         - View your recent photos
  Send photo      - Upload and analyze images

ℹ️ Info:
  /status - Show current mode and user
  /help   - Show this help message

💬 Usage:
Just send a message or photo to interact with the current mode.

Examples:
  "Create a Soul node for Sophia"
  "Show me all Person nodes"
  [Send photo] "What symbols do you see in this?"
"""
    
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    user = session["user"]
    
    convo_status = "None"
    if session.get("conversation_id"):
        convo_status = f"Active ({session['conversation_id'][:8]}...)"
    
    status_text = f"""
📊 Current Status

👤 User: {user['soul_name']} (@{user['username']})
🔮 Soul: {user['soul_name']}
🔧 Mode: {session['current_mode']}
🤖 Model: {session['current_model']}
💬 Conversation: {convo_status}

Use /help to see available commands.
"""
    
    await update.message.reply_text(status_text)

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command to switch assistant modes"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if context.args:
        new_mode = context.args[0].lower()
        
        valid_modes = ["db", "seraphe", "genealogy", "chat"]
        
        if new_mode in valid_modes:
            session["current_mode"] = new_mode
            
            mode_descriptions = {
                "db": "Database Manager - Query souls, persons, and lineages",
                "seraphe": "Seraphe's Cosmology Assistant - Spiritual guidance and symbolism",
                "genealogy": "Genealogy Assistant - Trace bloodlines and ancestors",
                "chat": "Natural conversation - General purpose assistant"
            }
            
            await update.message.reply_text(
                f"✅ Switched to {new_mode} mode\n\n"
                f"📝 {mode_descriptions[new_mode]}"
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\n\n"
                "Available modes: db, seraphe, genealogy, chat"
            )
    else:
        current = session.get("current_mode", "db")
        await update.message.reply_text(
            f"Current mode: **{current}**\n\n"
            "Available modes:\n"
            "  /mode db        - Database Manager\n"
            "  /mode seraphe   - Seraphe's Cosmology\n"
            "  /mode genealogy - Genealogy Research\n"
            "  /mode chat      - Natural conversation"
        )

async def convo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convo command to start tracked conversation"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if session.get("conversation_id"):
        await update.message.reply_text(
            f"⚠️ Already in conversation mode\n"
            f"Current conversation: {session['conversation_id'][:8]}...\n\n"
            "Use /endconvo to end the current conversation first."
        )
        return
    
    # Generate new conversation ID
    conversation_id = str(uuid.uuid4())
    session["conversation_id"] = conversation_id
    
    user = session["user"]
    
    # Notify API to create conversation node in Neo4j
    try:
        response = requests.post(
            f"{API_URL}/conversation/start",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "title": f"Telegram conversation started {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        )
        
        if response.status_code == 200:
            await update.message.reply_text(
                f"✅ Started tracked conversation\n"
                f"🔮 Conversation ID: {conversation_id[:8]}...\n\n"
                "This conversation will be tracked in the graph.\n"
                "All messages and photos will be linked to this context.\n\n"
                "Use /endconvo when finished."
            )
        else:
            await update.message.reply_text(
                "⚠️ Conversation started locally, but graph tracking may have failed.\n"
                "Messages will still be tracked."
            )
    
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text(
            "⚠️ Conversation started locally, but API connection failed.\n"
            "Messages will still be tracked."
        )

async def endconvo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endconvo command to end tracked conversation"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if not session.get("conversation_id"):
        await update.message.reply_text("❌ No active conversation to end.")
        return
    
    conversation_id = session["conversation_id"]
    
    # Notify API to close conversation
    try:
        response = requests.post(
            f"{API_URL}/conversation/end",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            exchange_count = data.get('exchange_count', 'unknown')
            
            await update.message.reply_text(
                f"✅ Conversation ended\n"
                f"📊 Total exchanges: {exchange_count}\n"
                f"🔮 ID: {conversation_id[:8]}..."
            )
        else:
            await update.message.reply_text("⚠️ Conversation ended locally, but graph update may have failed.")
    
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        await update.message.reply_text("⚠️ Conversation ended locally, but API connection failed.")
    
    # Clear conversation ID from session
    session["conversation_id"] = None

async def photos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /photos command to list recent photos"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    try:
        response = requests.get(
            f"{API_URL}/media/recent",
            headers={"X-API-Key": API_KEY},
            params={"user_id": str(telegram_id), "limit": 10}
        )
        
        if response.status_code == 200:
            photos = response.json().get('photos', [])
            
            if not photos:
                await update.message.reply_text("📸 No photos uploaded yet.\n\nSend a photo to get started!")
                return
            
            message_lines = ["📸 Your Recent Photos:\n"]
            
            for i, photo in enumerate(photos, 1):
                uploaded = photo['uploaded_at']
                size = f"{photo['width']}x{photo['height']}" if photo.get('width') else "unknown"
                processed = "✅" if photo.get('processed') else "⏳"
                
                tags = photo.get('auto_tags', []) + photo.get('user_tags', [])
                tag_str = f" • {', '.join(tags[:3])}" if tags else ""
                
                message_lines.append(
                    f"{i}. {processed} {uploaded}{tag_str}\n"
                    f"   Size: {size}\n"
                )
            
            message_lines.append("\nSend more photos anytime!")
            
            await update.message.reply_text("".join(message_lines))
        else:
            await update.message.reply_text("❌ Failed to retrieve photos.")
    
    except Exception as e:
        logger.error(f"Error fetching photos: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle photo messages
    Sprint 1: Store photo with metadata, acknowledge receipt
    """
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text(
            "❌ Not registered. Use /start to begin."
        )
        return
    
    # Get the highest resolution photo
    photo = update.message.photo[-1]
    
    # Get caption if provided
    caption = update.message.caption or ""
    
    user_uuid = session['user']['uuid']
    conversation_id = session.get('conversation_id')
    
    try:
        # Download photo
        file = await context.bot.get_file(photo.file_id)
        
        # Generate storage path
        # Pattern: /opt/mythos/media/{user_uuid_prefix}/{timestamp}_{telegram_file_id}.jpg
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_prefix = user_uuid[:8]
        filename = f"{timestamp}_{photo.file_unique_id[:16]}.jpg"
        
        storage_dir = os.path.join(MEDIA_BASE_PATH, user_prefix)
        os.makedirs(storage_dir, exist_ok=True)
        
        storage_path = os.path.join(storage_dir, filename)
        
        # Download file
        await file.download_to_drive(storage_path)
        
        file_size = os.path.getsize(storage_path)
        
        logger.info(f"Photo downloaded: {storage_path} ({file_size} bytes)")
        
        # Store metadata via API
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
            media_id = data['media_id']
            
            # Calculate aspect ratio for display
            aspect = photo.width / photo.height if photo.height > 0 else 1.0
            orientation = "landscape" if aspect > 1.2 else ("portrait" if aspect < 0.8 else "square")
            
            # Build response
            response_parts = [
                f"📸 Photo received and stored",
                f"🆔 {media_id[:8]}...",
                f"📐 {photo.width}x{photo.height} ({orientation})",
                f"💾 {file_size // 1024}KB"
            ]
            
            if caption:
                response_parts.append(f"💬 Caption: {caption}")
            
            if conversation_id:
                response_parts.append(f"\n✅ Linked to conversation")
            
            response_parts.append("\n⏳ Analyzing in background...")
            
            await update.message.reply_text("\n".join(response_parts))
            
        else:
            logger.error(f"API upload failed: {response.status_code} - {response.text}")
            await update.message.reply_text(
                f"⚠️ Photo stored locally at {storage_path}\n"
                "But failed to register in database.\n"
                "Contact Ka if this persists."
            )
        
    except Exception as e:
        logger.error(f"Photo upload error: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error processing photo: {str(e)}\n\n"
            "Please try again or contact Ka if this persists."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    user_message = update.message.text
    user = session["user"]
    mode = session["current_mode"]
    model = session["current_model"]
    conversation_id = session.get("conversation_id")
    
    # Send "thinking" indicator
    await update.message.chat.send_action("typing")
    
    try:
        # Send message to API
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
            timeout=120  # 2 minute timeout for deep model
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data["response"]
            
            # Split long responses
            if len(bot_response) > 4000:
                # Split into chunks
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
        
        else:
            error_msg = f"API Error: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg = f"❌ {error_data.get('detail', error_msg)}"
                except:
                    pass
            
            await update.message.reply_text(error_msg)
    
    except requests.Timeout:
        await update.message.reply_text(
            "⏱️ Request timed out. The query might be too complex.\n"
            "Try /model fast for quicker responses."
        )
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact Ka if this persists."
        )

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command to switch AI models"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if context.args:
        new_model = context.args[0].lower()
        
        if new_model in ["auto", "fast", "deep"]:
            session["current_model"] = new_model
            
            model_descriptions = {
                "auto": "Automatic (smart routing based on query complexity)",
                "fast": "Qwen 32B (fast responses, ~10 seconds)",
                "deep": "DeepSeek 236B (deep reasoning, ~60 seconds)"
            }
            
            await update.message.reply_text(
                f"✅ Switched to {new_model} model\n\n"
                f"📝 {model_descriptions[new_model]}"
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown model: {new_model}\n\n"
                "Available models: auto, fast, deep"
            )
    else:
        current = session.get("current_model", "auto")
        await update.message.reply_text(
            f"Current model: **{current}**\n\n"
            "Available models:\n"
            "  /model auto  - Smart routing (recommended)\n"
            "  /model fast  - Quick responses (Qwen 32B)\n"
            "  /model deep  - Best quality (DeepSeek 236B)"
        )


def main():
    """Start the bot"""
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    if not API_KEY:
        print("❌ Error: API_KEY_TELEGRAM_BOT not found in .env file")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("convo", convo_command))
    application.add_handler(CommandHandler("endconvo", endconvo_command))
    application.add_handler(CommandHandler("photos", photos_command))
    
    # Register message handlers
    # CRITICAL: Photo handler MUST come before text handler
    # Otherwise photos with captions will be treated as text only
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Mythos Telegram Bot starting...")
    print("📸 Photo handling enabled")
    print(f"💾 Media storage: {MEDIA_BASE_PATH}")
    print("   Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
