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
import asyncio
import sys
sys.path.insert(0, '/opt/mythos')
import logging
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import requests

from handlers.review_handler import handle_review
from handlers.ontology_handler import handle_define
from handlers.people_handler import handle_people

from handlers.checkin_handler import handle_checkin, handle_routines, handle_rdone, handle_rskip, handle_routine_add
from handlers.calendar_handler import handle_calendar
from telegram_bot.handlers.analyst_handler import cmd_briefing, cmd_priorities, cmd_transfers
from core.morning_briefing import MorningBriefing

from telegram_bot.handlers.weather_handler import cmd_weather

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
from handlers import astrology_handler

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

# Finance commands
from handlers.finance_handler import (
    spend_command,
    monthly_command,
    compare_command,
    top_command,
    txn_command,
    next_command,
    back_command,
    setbalance_command,
    report_command,
    balance_command,
    finance_command,
    spending_command
)
from handlers.snapshot_handler import (
    snapshot_command,
    setbal_command
)

# Iris consciousness commands
from handlers.iris_handler import (
    iris_command,
    iris_test_command,
    iris_run_command,
    iris_task_command
)

# Ollama model management
from handlers.ollama_models import (
    models_command,
    pull_command,
    pulling_command,
    setmodel_command,
    removemodel_command
)



# Voice transcription
from handlers.voice_handler import handle_voice, handle_audio

# Media handlers (photo vision, video transcription)
from handlers.media_handler import handle_photo_media, handle_video_media

# Task tracking commands
from handlers.task_handler import task_command, tasks_command

# Help system
from handlers.help_handler import help_command as help_command_handler

# Pulse handler (household finance visibility)
from handlers.pulse_handler import pulse_command, setup_pulse_scheduler
from handlers.forecast_handler import forecast_command, projection_command, bills_command, income_command
from handlers.diag_handler import handle_diag
# Configuration
API_URL = "https://mythos-api.denkers.co"
API_KEY = os.getenv('API_KEY_TELEGRAM_BOT')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MEDIA_BASE_PATH = "/opt/mythos/media"

# Message buffer for collecting multi-chunk messages
# { telegram_id: {"chunks": [str], "timer": asyncio.Task, "update": Update, "context": Context} }
MESSAGE_BUFFER = {}
MESSAGE_BUFFER_DELAY = 1.5  # seconds to wait for more chunks


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
                    "current_mode": DEFAULT_MODE,
                    "current_model": "thinking",
                    "conversation_id": None,
                    "last_activity": datetime.now(),
                    "sell_session": None,
                    "chat_context": None,
                    "activity_log": []
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    SESSIONS[telegram_id]["last_activity"] = datetime.now()
    # Ensure chat_id is available for consciousness stream (Patch 0122)
    if "chat_id" not in SESSIONS[telegram_id]:
        SESSIONS[telegram_id]["chat_id"] = telegram_id  # Default: DM chat_id = telegram_id
    return SESSIONS[telegram_id]


def log_activity(session: dict, activity_type: str, details: str):
    """Log an activity to the session for /status reporting"""
    activity_log = session.get("activity_log", [])
    activity_log.append({
        "time": datetime.now().isoformat(),
        "type": activity_type,
        "details": details
    })
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
    model = session.get("current_model", "thinking")
    
    # Check for /setmodel override to show actual model
    try:
        from handlers.ollama_models import USER_MODEL_OVERRIDE
        override = USER_MODEL_OVERRIDE.get(telegram_id)
        if override:
            model = override
    except ImportError:
        pass
    
    # Build status message - cleaner format
    mode_emoji = {
        "chat": "💬",
        "db": "🗄️",
        "sell": "📦",
        "seraphe": "🔮",
        "genealogy": "🌳"
    }
    
    lines = [
        f"📊 **{user['soul_name']}**",
        "",
        f"{mode_emoji.get(mode, '🔧')} Mode: **{mode}**",
        f"🤖 Model: **{model}**",
    ]
    
    # Tracked conversation status
    if session.get("conversation_id"):
        lines.append(f"📝 Tracked: `{session['conversation_id'][:8]}...`")
    
    # Chat mode specific info
    if mode == "chat":
        stats = get_chat_stats(session)
        if stats['message_count'] > 0:
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append(f"💬 **Chat** ({stats['message_count']} messages)")
            
            # Get recent topics/summary
            topics = get_recent_topics(session)
            if topics:
                for topic in topics[:3]:
                    lines.append(f"• {topic}")
            
            lines.append("")
            lines.append("_/clear to reset_")
    
    # Recent activity log
    activity_log = session.get("activity_log", [])
    if activity_log:
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("**📋 Recent**")
        for activity in activity_log[-3:]:
            time_str = activity['time'][11:16]
            lines.append(f"• {time_str} {activity['details'][:40]}")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command — switch Iris modes or legacy modes (sell, db)"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Import mode list from assembler
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_available_modes
        iris_modes = {m['name']: m for m in get_available_modes()}
    except Exception:
        iris_modes = {}
    
    if context.args:
        new_mode = context.args[0].lower()
        sub_mode = context.args[1].lower() if len(context.args) > 1 else None
        
        # Legacy modes: sell, db
        if new_mode == "sell":
            log_activity(session, "mode_change", "Entered sell mode")
            await enter_sell_mode(update, session)
            return
        
        if new_mode == "db":
            if is_sell_mode(session):
                session["sell_session"] = None
            session["current_mode"] = "db"
            log_activity(session, "mode_change", "→ db")
            await update.message.reply_text("✅ **db** mode\n\nDatabase queries - ask about souls, persons, lineages", parse_mode='Markdown')
            return
        
        # Iris modes
        if new_mode in iris_modes:
            if is_sell_mode(session):
                session["sell_session"] = None
            session["current_mode"] = "chat"  # Ensure chat handler routes messages
            session["iris_mode"] = new_mode
            session["iris_sub_mode"] = sub_mode
            
            mode_info = iris_modes[new_mode]
            emoji = mode_info.get('emoji', '')
            desc = mode_info.get('description', '')
            
            log_activity(session, "mode_change", f"→ {emoji} {new_mode}" + (f" ({sub_mode})" if sub_mode else ""))
            
            msg = f"{emoji} **{new_mode.upper()}** mode"
            if sub_mode:
                msg += f" ({sub_mode})"
            if desc:
                msg += f"\n{desc}"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            mode_list = ", ".join(sorted(iris_modes.keys())) if iris_modes else "hearthfire, forge, roots, oracle, scribe, sentry"
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\n\n"
                f"**Iris modes:** {mode_list}\n"
                "**Legacy:** db, sell",
                parse_mode='Markdown'
            )
    else:
        current_iris = session.get("iris_mode", "hearthfire")
        current_sub = session.get("iris_sub_mode")
        emoji = iris_modes.get(current_iris, {}).get('emoji', '🔥') if iris_modes else '🔥'
        
        lines = [f"Current: {emoji} **{current_iris}**" + (f" ({current_sub})" if current_sub else "")]
        lines.append("")
        
        if iris_modes:
            for m in sorted(iris_modes.values(), key=lambda x: x['name']):
                e = m.get('emoji', '')
                n = m.get('name', '')
                d = m.get('description', '')
                lines.append(f"`/mode {n}` {e} {d}")
        else:
            lines.append("`/mode hearthfire` 🔥 Spiritual/personal")
            lines.append("`/mode forge` ⚒️ System admin")
            lines.append("`/mode roots` 🌳 Genealogy")
            lines.append("`/mode oracle` 🔮 Research/harmonics")
            lines.append("`/mode scribe` 📜 Writing")
            lines.append("`/mode sentry` 🛡️ Financial")
        
        lines.append("")
        lines.append("`/mode db` Database queries")
        lines.append("`/mode sell` Sell items")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /personality command — view/adjust personality sliders"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_resolved_personality
    except Exception as e:
        await update.message.reply_text(f"❌ Prompt assembler not available: {e}")
        return
    
    iris_mode = session.get("iris_mode", "hearthfire")
    user_info = session.get("user", {})
    overrides = session.get("personality_overrides")
    
    if context.args:
        args = context.args
        
        if args[0].lower() == "reset":
            session["personality_overrides"] = None
            await update.message.reply_text("🔄 Personality reset to defaults")
            return
        
        if len(args) >= 2:
            slider_name = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                await update.message.reply_text(f"❌ Value must be a number (0-100)")
                return
            
            value = max(0, min(100, value))
            
            valid_sliders = ['verbosity', 'warmth', 'humor', 'truth', 'speculation', 'autonomy', 'mystical', 'formality', 'challenge']
            if slider_name not in valid_sliders:
                await update.message.reply_text(f"❌ Unknown slider: {slider_name}\nAvailable: {', '.join(valid_sliders)}")
                return
            
            if not session.get("personality_overrides"):
                session["personality_overrides"] = {}
            session["personality_overrides"][slider_name] = value
            
            await update.message.reply_text(f"🎛️ **{slider_name}** → {value}", parse_mode='Markdown')
            return
    
    # Show current resolved values
    resolved = get_resolved_personality(
        mode=iris_mode,
        user_info=user_info,
        session_overrides=overrides
    )
    
    slider_emojis = {
        'verbosity': '📏', 'warmth': '🌡️', 'humor': '😏', 'truth': '⚡',
        'speculation': '🔮', 'autonomy': '🧭', 'mystical': '✨', 'formality': '👔', 'challenge': '⚔️'
    }
    
    lines = [f"🎛️ **Personality** (mode: {iris_mode})\n"]
    for k, v in sorted(resolved.items()):
        emoji = slider_emojis.get(k, '•')
        bar = '█' * (v // 10) + '░' * (10 - v // 10)
        override_mark = " *" if overrides and k in overrides else ""
        lines.append(f"{emoji} `{k:12s}` {bar} {v}{override_mark}")
    
    lines.append("")
    lines.append("`/personality <slider> <0-100>` to adjust")
    lines.append("`/personality reset` to clear overrides")
    if overrides:
        lines.append("\n* = session override")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')



async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /personality command — view/adjust personality sliders"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_resolved_personality
    except Exception as e:
        await update.message.reply_text(f"❌ Prompt assembler not available: {e}")
        return
    
    iris_mode = session.get("iris_mode", "hearthfire")
    user_info = session.get("user", {})
    overrides = session.get("personality_overrides")
    
    if context.args:
        args = context.args
        
        if args[0].lower() == "reset":
            session["personality_overrides"] = None
            await update.message.reply_text("🔄 Personality reset to defaults")
            return
        
        if len(args) >= 2:
            slider_name = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                await update.message.reply_text(f"❌ Value must be a number (0-100)")
                return
            
            value = max(0, min(100, value))
            
            valid_sliders = ['verbosity', 'warmth', 'humor', 'truth', 'speculation', 'autonomy', 'mystical', 'formality', 'challenge']
            if slider_name not in valid_sliders:
                await update.message.reply_text(f"❌ Unknown slider: {slider_name}\nAvailable: {', '.join(valid_sliders)}")
                return
            
            if not session.get("personality_overrides"):
                session["personality_overrides"] = {}
            session["personality_overrides"][slider_name] = value
            
            await update.message.reply_text(f"🎛️ **{slider_name}** → {value}", parse_mode='Markdown')
            return
    
    # Show current resolved values
    resolved = get_resolved_personality(
        mode=iris_mode,
        user_info=user_info,
        session_overrides=overrides
    )
    
    slider_emojis = {
        'verbosity': '📏', 'warmth': '🌡️', 'humor': '😏', 'truth': '⚡',
        'speculation': '🔮', 'autonomy': '🧭', 'mystical': '✨', 'formality': '👔', 'challenge': '⚔️'
    }
    
    lines = [f"🎛️ **Personality** (mode: {iris_mode})\n"]
    for k, v in sorted(resolved.items()):
        emoji = slider_emojis.get(k, '•')
        bar = '█' * (v // 10) + '░' * (10 - v // 10)
        override_mark = " *" if overrides and k in overrides else ""
        lines.append(f"{emoji} `{k:12s}` {bar} {v}{override_mark}")
    
    lines.append("")
    lines.append("`/personality <slider> <0-100>` to adjust")
    lines.append("`/personality reset` to clear overrides")
    if overrides:
        lines.append("\n* = session override")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')



async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /personality command — view/adjust personality sliders"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_resolved_personality
    except Exception as e:
        await update.message.reply_text(f"❌ Prompt assembler not available: {e}")
        return
    
    iris_mode = session.get("iris_mode", "hearthfire")
    user_info = session.get("user", {})
    overrides = session.get("personality_overrides")
    
    if context.args:
        args = context.args
        
        if args[0].lower() == "reset":
            session["personality_overrides"] = None
            await update.message.reply_text("🔄 Personality reset to defaults")
            return
        
        if len(args) >= 2:
            slider_name = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                await update.message.reply_text(f"❌ Value must be a number (0-100)")
                return
            
            value = max(0, min(100, value))
            
            valid_sliders = ['verbosity', 'warmth', 'humor', 'truth', 'speculation', 'autonomy', 'mystical', 'formality', 'challenge']
            if slider_name not in valid_sliders:
                await update.message.reply_text(f"❌ Unknown slider: {slider_name}\nAvailable: {', '.join(valid_sliders)}")
                return
            
            if not session.get("personality_overrides"):
                session["personality_overrides"] = {}
            session["personality_overrides"][slider_name] = value
            
            await update.message.reply_text(f"🎛️ **{slider_name}** → {value}", parse_mode='Markdown')
            return
    
    # Show current resolved values
    resolved = get_resolved_personality(
        mode=iris_mode,
        user_info=user_info,
        session_overrides=overrides
    )
    
    slider_emojis = {
        'verbosity': '📏', 'warmth': '🌡️', 'humor': '😏', 'truth': '⚡',
        'speculation': '🔮', 'autonomy': '🧭', 'mystical': '✨', 'formality': '👔', 'challenge': '⚔️'
    }
    
    lines = [f"🎛️ **Personality** (mode: {iris_mode})\n"]
    for k, v in sorted(resolved.items()):
        emoji = slider_emojis.get(k, '•')
        bar = '█' * (v // 10) + '░' * (10 - v // 10)
        override_mark = " *" if overrides and k in overrides else ""
        lines.append(f"{emoji} `{k:12s}` {bar} {v}{override_mark}")
    
    lines.append("")
    lines.append("`/personality <slider> <0-100>` to adjust")
    lines.append("`/personality reset` to clear overrides")
    if overrides:
        lines.append("\n* = session override")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - reset chat context"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    clear_chat_context(session)
    log_activity(session, "clear", "Chat context cleared")
    await update.message.reply_text("🔄 Context cleared")


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
        await update.message.reply_text("Not in sell mode.")


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
        await update.message.reply_text("Not in sell mode.")


async def convo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if session.get("conversation_id"):
        await update.message.reply_text(
            f"⚠️ Already tracking: `{session['conversation_id'][:8]}...`\n\n"
            "Use /endconvo to end first.",
            parse_mode='Markdown'
        )
        return
    
    conversation_id = str(uuid.uuid4())
    session["conversation_id"] = conversation_id
    log_activity(session, "convo", "Started tracking")
    
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
        
        await update.message.reply_text(
            f"🗣️ Tracking started\nID: `{conversation_id[:8]}...`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text(
            f"⚠️ Tracking locally\nID: `{conversation_id[:8]}...`",
            parse_mode='Markdown'
        )


async def endconvo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endconvo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if not session.get("conversation_id"):
        await update.message.reply_text("No active tracking.")
        return
    
    conversation_id = session["conversation_id"]
    session["conversation_id"] = None
    log_activity(session, "convo", "Ended tracking")
    
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
    
    await update.message.reply_text(f"✅ Tracking ended")


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if context.args:
        new_model = context.args[0].lower()
        
        if new_model in ["auto", "fast", "deep", "thinking"]:
            session["current_model"] = new_model
            log_activity(session, "model", f"→ {new_model}")
            
            descriptions = {
                "auto": "qwen2.5:32b",
                "fast": "llama3.2:3b (~5s)",
                "deep": "qwen2.5:32b (~30s)",
                "thinking": "qwen3:30b-a3b (deep reasoning)",
            }
            
            await update.message.reply_text(
                f"✅ Model: **{new_model}** ({descriptions[new_model]})",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown: {new_model}\n"
                "Use: auto, fast, deep, thinking"
            )
    else:
        current = session.get("current_model", "thinking")
        await update.message.reply_text(
            f"Current: **{current}**\n\n"
            "`/model thinking` - qwen3:30b-a3b (DEFAULT)\n"
            "`/model auto` - qwen2.5:32b\n"
            "`/model fast` - llama3.2:3b\n"
            "`/model deep` - qwen2.5:32b",
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
            
            lines = [f"📸 Recent ({len(photos)})\n"]
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
    """Handle photo messages - routes to sell mode or media handler"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Not registered. Use /start")
        return
    
    if is_sell_mode(session):
        if update.message.photo:
            await handle_sell_photos(update, context, session)
        elif update.message.document and update.message.document.mime_type.startswith("image/"):
            await handle_sell_photos(update, context, session)
        return
    
    # Chat mode — use vision analysis
    await handle_photo_media(update, context)
async def _process_buffered_message(telegram_id: int):
    """Process collected message chunks as a single message"""
    if telegram_id not in MESSAGE_BUFFER:
        return
    
    buf = MESSAGE_BUFFER.pop(telegram_id)
    combined_message = "\n".join(buf["chunks"])
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
            "📦 Sell mode - send photos only.\n"
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
    
    MESSAGE_BUFFER[telegram_id]["timer"] = asyncio.ensure_future(fire())


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
    application.add_handler(CommandHandler("help", help_command_handler))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("personality", personality_command))
    application.add_handler(CommandHandler("personality", personality_command))
    application.add_handler(CommandHandler("personality", personality_command))
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
    
    # Finance commands
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("finance", finance_command))
    application.add_handler(CommandHandler("spending", spending_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("setbalance", setbalance_command))
    application.add_handler(CommandHandler("spend", spend_command))
    application.add_handler(CommandHandler("monthly", monthly_command))
    application.add_handler(CommandHandler("compare", compare_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("txn", txn_command))
    application.add_handler(CommandHandler("next", next_command))
    
    # Astrology commands
    application.add_handler(CommandHandler("chart", astrology_handler.handle_chart))
    application.add_handler(CommandHandler("planets", astrology_handler.handle_planets))
    application.add_handler(CommandHandler("houses", astrology_handler.handle_houses))
    application.add_handler(CommandHandler("aspects", astrology_handler.handle_aspects))
    application.add_handler(CommandHandler("group_planets", astrology_handler.handle_group_planets))
    application.add_handler(CommandHandler("back", back_command))
    application.add_handler(CommandHandler("snapshot", snapshot_command))
    application.add_handler(CommandHandler("pulse", pulse_command))
    application.add_handler(CommandHandler("forecast", forecast_command))
    application.add_handler(CommandHandler("projection", projection_command))
    application.add_handler(CommandHandler("bills", bills_command))
    application.add_handler(CommandHandler("income", income_command))
    application.add_handler(CommandHandler("setbal", setbal_command))

    # Iris consciousness commands
    application.add_handler(CommandHandler("iris", iris_command))
    application.add_handler(CommandHandler("iris_test", iris_test_command))
    application.add_handler(CommandHandler("iris_run", iris_run_command))
    application.add_handler(CommandHandler("iris_task", iris_task_command))

    # Ollama model management commands
    application.add_handler(CommandHandler("models", models_command))
    application.add_handler(CommandHandler("pull", pull_command))
    application.add_handler(CommandHandler("pulling", pulling_command))
    application.add_handler(CommandHandler("setmodel", setmodel_command))
    application.add_handler(CommandHandler("removemodel", removemodel_command))
    

    application.add_handler(CommandHandler("task", task_command))
    application.add_handler(CommandHandler("tasks", tasks_command))

    application.add_handler(CommandHandler('review', handle_review))
    application.add_handler(CommandHandler('checkin', handle_checkin))
    application.add_handler(CommandHandler('routines', handle_routines))
    application.add_handler(CommandHandler('rdone', handle_rdone))
    application.add_handler(CommandHandler('rskip', handle_rskip))
    application.add_handler(CommandHandler('routine_add', handle_routine_add))
    application.add_handler(CommandHandler('calendar', handle_calendar))
    application.add_handler(CommandHandler('briefing', cmd_briefing))
    application.add_handler(CommandHandler('analyze', cmd_briefing))
    application.add_handler(CommandHandler('priorities', cmd_priorities))
    application.add_handler(CommandHandler('transfers', cmd_transfers))

    application.add_handler(CommandHandler('weather', cmd_weather))

    # --- Diagnostics ---
    application.add_handler(CommandHandler('diag', handle_diag))

    # Ontology
    async def define_cmd(update, context):
        text = " ".join(context.args) if context.args else ""
        result = handle_define(text)
        if isinstance(result, tuple):
            text_msg, related = result
            if related:
                buttons = []
                row = []
                for name in related:
                    row.append(InlineKeyboardButton(name, callback_data=f"def:{name[:60]}"))
                    if len(row) == 2:
                        buttons.append(row)
                        row = []
                if row:
                    buttons.append(row)
                await update.message.reply_text(text_msg, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await update.message.reply_text(text_msg)
        else:
            await update.message.reply_text(result)

    async def define_callback(update, context):
        query = update.callback_query
        await query.answer()
        term_name = query.data[4:]  # strip "def:"
        result = handle_define(term_name)
        if isinstance(result, tuple):
            text_msg, related = result
            if related:
                buttons = []
                row = []
                for name in related:
                    row.append(InlineKeyboardButton(name, callback_data=f"def:{name[:60]}"))
                    if len(row) == 2:
                        buttons.append(row)
                        row = []
                if row:
                    buttons.append(row)
                await query.message.reply_text(text_msg, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await query.message.reply_text(text_msg)
        else:
            await query.message.reply_text(result)

    application.add_handler(CommandHandler("define", define_cmd))
    application.add_handler(CallbackQueryHandler(define_callback, pattern="^def:"))

    # People database
    async def people_cmd(update, context):
        text = " ".join(context.args) if context.args else ""
        result = handle_people(text)
        await update.message.reply_text(result)
    application.add_handler(CommandHandler("people", people_cmd))

    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video_media))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_media))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print("🤖 Mythos Bot starting...")
    print(f"💬 Default mode: {DEFAULT_MODE}")
    
    # Morning briefing scheduler
    morning = MorningBriefing(application)
    morning.start()

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
