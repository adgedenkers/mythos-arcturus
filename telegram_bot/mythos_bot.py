#!/usr/bin/env python3
"""
Mythos Telegram Bot
Provides mobile access to Mythos system via Telegram
"""

import os
import logging
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
    
    status_text = f"""
📊 Current Status

👤 User: {user['soul_name']} (@{user['username']})
🎯 Mode: {session['current_mode']}
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
        
        if new_mode in ["db", "seraphe", "genealogy"]:
            session["current_mode"] = new_mode
            await update.message.reply_text(
                f"✅ Switched to {new_mode} mode"
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\n\n"
                "Available modes: db, seraphe, genealogy"
            )
    else:
        # Show current mode and available modes
        await update.message.reply_text(
            f"Current mode: {session['current_mode']}\n\n"
            "Available modes:\n"
            "  /mode db        - Database Manager\n"
            "  /mode seraphe   - Cosmology Assistant\n"
            "  /mode genealogy - Genealogy Assistant"
        )

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
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Call the API
        response = requests.post(
            f"{API_URL}/message",
            json={
                "user_id": str(telegram_id),
                "message": user_message,
                "mode": current_mode
            },
            headers={"X-API-Key": API_KEY},
            timeout=30
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Mythos Telegram Bot starting...")
    print("   Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()