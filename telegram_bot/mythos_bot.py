#!/usr/bin/env python3
"""
Mythos Telegram Bot
Provides mobile access to Mythos system via Telegram
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
        "/help - Show help\n"
        "/status - Show current status\n\n"
        "Just send a message to interact with the current mode."
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

ℹ️ Info:
  /status - Show current mode and user
  /help   - Show this help message

💬 Usage:
Just send a message to interact with the current mode.

Examples:
  "Create a Soul node for Sophia"
  "Show me all Person nodes"
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
🎯 Mode: {session['current_mode']}
🤖 Model: {session.get('current_model', 'auto')}
💬 Conversation: {convo_status}
📅 Last Activity: {session['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    await update.message.reply_text(status_text)

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Check if user specified a mode
    if context.args:
        new_mode = context.args[0].lower()
        
        if new_mode in ["db", "seraphe", "genealogy", "chat"]:
            session["current_mode"] = new_mode
            
            mode_descriptions = {
                "db": "Database Manager - queries Neo4j/PostgreSQL",
                "seraphe": "Seraphe's Cosmology Assistant",
                "genealogy": "Genealogy Assistant",
                "chat": "Chat - natural conversation with Ollama"
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
        # Show current mode and available modes
        await update.message.reply_text(
            f"Current mode: {session['current_mode']}\n\n"
            "Available modes:\n"
            "  /mode db        - Database Manager\n"
            "  /mode seraphe   - Cosmology Assistant\n"
            "  /mode genealogy - Genealogy Assistant\n"
            "  /mode chat      - Natural conversation"
        )

async def convo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convo command - start a tracked conversation"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Check if already in a conversation
    if session.get("conversation_id"):
        await update.message.reply_text(
            f"⚠️ You're already in a conversation.\n\n"
            f"ID: {session['conversation_id'][:8]}...\n\n"
            "Use /endconvo to end it first, or just continue chatting."
        )
        return
    
    # Check for optional title argument
    title = " ".join(context.args) if context.args else None
    
    # Generate new conversation ID
    conversation_id = f"convo-{uuid.uuid4()}"
    session["conversation_id"] = conversation_id
    session["conversation_started"] = datetime.now()
    
    # Call API to create conversation node
    try:
        response = requests.post(
            f"{API_URL}/conversation/start",
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "title": title
            },
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            title_msg = f"\nTitle: {title}" if title else ""
            await update.message.reply_text(
                f"🎙️ Conversation started!{title_msg}\n\n"
                f"ID: {conversation_id[:8]}...\n\n"
                "Everything you discuss will be tracked in the knowledge graph.\n"
                "Use /endconvo when finished."
            )
        else:
            # Still allow conversation locally even if API fails
            logger.warning(f"API conversation start failed: {response.status_code}")
            await update.message.reply_text(
                f"🎙️ Conversation started (local only)\n\n"
                f"ID: {conversation_id[:8]}...\n\n"
                "⚠️ Graph tracking unavailable - API returned error.\n"
                "Use /endconvo when finished."
            )
    
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text(
            f"🎙️ Conversation started (local only)\n\n"
            f"ID: {conversation_id[:8]}...\n\n"
            "⚠️ Graph tracking unavailable - could not reach API.\n"
            "Use /endconvo when finished."
        )

async def endconvo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endconvo command - end a tracked conversation"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if not session.get("conversation_id"):
        await update.message.reply_text(
            "ℹ️ No active conversation to end.\n\n"
            "Use /convo to start one."
        )
        return
    
    conversation_id = session["conversation_id"]
    started = session.get("conversation_started", datetime.now())
    duration = datetime.now() - started
    
    # Call API to close conversation
    try:
        response = requests.post(
            f"{API_URL}/conversation/end",
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id
            },
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            exchange_count = data.get("exchange_count", "?")
            await update.message.reply_text(
                f"✅ Conversation ended.\n\n"
                f"Duration: {duration.seconds // 60} minutes\n"
                f"Exchanges: {exchange_count}\n\n"
                "Knowledge has been captured in the graph."
            )
        else:
            await update.message.reply_text(
                f"✅ Conversation ended (local).\n\n"
                f"Duration: {duration.seconds // 60} minutes\n\n"
                "⚠️ Could not update graph - API error."
            )
    
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        await update.message.reply_text(
            f"✅ Conversation ended (local).\n\n"
            f"Duration: {duration.seconds // 60} minutes\n\n"
            "⚠️ Could not update graph - API unreachable."
        )
    
    # Clear conversation from session
    session["conversation_id"] = None
    session["conversation_started"] = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    telegram_id = update.effective_user.id
    user_message = update.message.text
    
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text(
            "❌ You are not registered. Use /start to begin."
        )
        return
    
    current_mode = session["current_mode"]
    conversation_id = session.get("conversation_id")
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Build request payload
        payload = {
            "user_id": str(telegram_id),
            "message": user_message,
            "mode": current_mode,
            "model_preference": session.get("current_model", "auto")
        }
        
        # Add conversation_id if in convo mode
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        # Call the API
        response = requests.post(
            f"{API_URL}/message",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=120  # Increased timeout for convo mode with extraction
        )
        
        if response.status_code == 200:
            data = response.json()
            reply_text = data["response"]
            
            # Split if too long for Telegram (4096 char limit)
            if len(reply_text) > 4096:
                chunks = [reply_text[i:i+4096] for i in range(0, len(reply_text), 4096)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(reply_text)
        
        else:
            await update.message.reply_text(
                f"❌ API Error: {response.status_code}\n{response.text}"
            )
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            f"❌ Error communicating with Mythos API:\n{str(e)}"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

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
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("convo", convo_command))
    application.add_handler(CommandHandler("endconvo", endconvo_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Mythos Telegram Bot starting...")
    print("   Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
