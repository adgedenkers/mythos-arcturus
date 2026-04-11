"""
SEN-0003: Earthquake Telegram handler
Provides /quakes command for current seismic activity summary.
"""

import psycopg2
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import sys
sys.path.insert(0, '/opt/mythos')


async def quakes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current seismic activity summary."""
    try:
        conn = psycopg2.connect(dbname="mythos", user="adge", host="localhost")
        try:
            from observatory.ingest.seismic_ingest import get_seismic_summary
            summary = get_seismic_summary(conn)
        finally:
            conn.close()

        await update.message.reply_text(
            f"🌍 **Global Seismic Activity**\n\n{summary}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error reading seismic data: {e}")


def register(app):
    app.add_handler(CommandHandler("quakes", quakes_command))
