"""
SEN-0002: Solar weather Telegram handler
Provides /solar command for current space weather conditions.
"""

import psycopg2
import psycopg2.extras
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Import the summary function from the ingest module
import sys
sys.path.insert(0, '/opt/mythos')


async def solar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current solar and space weather conditions."""
    try:
        conn = psycopg2.connect(dbname="mythos", user="adge", host="localhost")
        try:
            # Import here to avoid circular imports at module load
            from observatory.ingest.solar_ingest import get_current_conditions
            summary = get_current_conditions(conn)
        finally:
            conn.close()

        await update.message.reply_text(
            f"🌞 **Solar & Space Weather**\n\n{summary}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error reading solar data: {e}")


def register(app):
    """Register handlers with the bot application."""
    app.add_handler(CommandHandler("solar", solar_command))
