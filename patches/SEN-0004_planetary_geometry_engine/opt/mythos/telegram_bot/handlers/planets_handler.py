"""
SEN-0004: Planetary geometry Telegram handler
Provides /planets command for current planetary positions and geometry.
"""

import psycopg2
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import sys
sys.path.insert(0, '/opt/mythos')


async def planets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current planetary positions and geometry."""
    try:
        conn = psycopg2.connect(dbname="mythos", user="adge", host="localhost")
        try:
            from observatory.geometry.planetary_engine import get_geometry_summary
            summary = get_geometry_summary(conn)
        finally:
            conn.close()

        await update.message.reply_text(
            f"🌌 **Planetary Geometry**\n\n{summary}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error reading planetary data: {e}")


def register(app):
    app.add_handler(CommandHandler("planets", planets_command))
