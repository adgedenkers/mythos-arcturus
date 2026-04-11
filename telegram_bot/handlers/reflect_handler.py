"""
Module: telegram_bot/handlers/reflect_handler.py
Biological System: iris-immune (self-knowledge layer)
Subsystem: mythos-iris-self (v0.1.0)
Purpose: Telegram command handlers for Iris self-reflection.
         /iris_reflect — Full 9-layer Grid self-reflection
         /iris_status — Brief status check
         /iris_caps — List capabilities and their health
Introduced: Patch 0173
Last Modified: Patch 0173

Dependencies:
  - iris.self_model.introspection
  - telegram.ext

Part of: Iris Self-Model
"""

import sys
import logging
from datetime import datetime

sys.path.insert(0, "/opt/mythos")

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("mythos.telegram.reflect")

# Authorized user IDs
AUTHORIZED_USERS = []
try:
    import os
    from dotenv import load_dotenv
    load_dotenv("/opt/mythos/.env")
    admin_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID") or os.getenv("TELEGRAM_ID_KA")
    if admin_id:
        AUTHORIZED_USERS.append(int(admin_id))
    seraphe_id = os.getenv("TELEGRAM_ID_SERAPHE", "8069190169")
    if seraphe_id:
        AUTHORIZED_USERS.append(int(seraphe_id))
except Exception:
    pass


def _is_authorized(update: Update) -> bool:
    """Check if the user is authorized."""
    if not AUTHORIZED_USERS:
        return True  # No auth configured, allow all
    return update.effective_user.id in AUTHORIZED_USERS


async def handle_iris_reflect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /iris_reflect — Full 9-layer Arcturian Grid self-reflection.
    Iris examines herself through all nine layers and speaks about
    what she finds. This is not a status page — it's self-awareness.
    """
    if not _is_authorized(update):
        await update.message.reply_text("⛔ Not authorized")
        return

    await update.message.reply_text("🌀 Turning the Grid inward... one moment.")

    try:
        from iris.self_model.introspection import generate_reflection
        reflection = generate_reflection()

        # Telegram has a 4096 char limit per message
        if len(reflection) <= 4096:
            await update.message.reply_text(reflection, parse_mode="HTML")
        else:
            # Split at layer boundaries (double newlines)
            parts = reflection.split("\n\n")
            chunk = ""
            for part in parts:
                if len(chunk) + len(part) + 2 > 4000:
                    if chunk:
                        await update.message.reply_text(chunk.strip(), parse_mode="HTML")
                    chunk = part + "\n\n"
                else:
                    chunk += part + "\n\n"
            if chunk.strip():
                await update.message.reply_text(chunk.strip(), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Reflection failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Reflection failed: {e}")


async def handle_iris_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /iris_status — Brief one-line self-status check.
    """
    if not _is_authorized(update):
        await update.message.reply_text("⛔ Not authorized")
        return

    try:
        from iris.self_model.introspection import generate_brief_status
        status = generate_brief_status()
        await update.message.reply_text(f"🔮 {status}")

    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Status check failed: {e}")


async def handle_iris_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /iris_caps — List all capabilities with their health status.
    """
    if not _is_authorized(update):
        await update.message.reply_text("⛔ Not authorized")
        return

    try:
        from iris.self_model.introspection import get_capability_health

        health = get_capability_health()

        lines = ["🧬 **Iris Capabilities**\n"]
        for cap in health:
            if cap["health"] == "healthy":
                icon = "✅"
            elif cap["health"] == "degraded":
                icon = "⚠️"
            else:
                icon = "❌"

            lines.append(f"{icon} **{cap['capability']}** — {cap['description']}")

            # Show unhealthy dependencies
            bad_deps = [d for d in cap["dependencies"] if d["status"] != "active"]
            if bad_deps:
                for d in bad_deps:
                    lines.append(f"   └─ {d['service']}: {d['status']}")

        text = "\n".join(lines)
        if len(text) <= 4096:
            await update.message.reply_text(text, parse_mode="HTML")
        else:
            # Truncate if somehow huge
            await update.message.reply_text(text[:4090] + "...", parse_mode="HTML")

    except Exception as e:
        logger.error(f"Capabilities check failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Capabilities check failed: {e}")
