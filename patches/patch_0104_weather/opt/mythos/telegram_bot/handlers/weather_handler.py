"""
Weather handler for Telegram bot.
Usage:
  /weather              → Oxford, NY (default)
  /weather 13827        → By zip code
  /weather Denver, CO   → By city/state
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from core.weather_service import fetch_weather, format_weather_telegram, _geocode, DEFAULT_LAT, DEFAULT_LON, DEFAULT_NAME

logger = logging.getLogger(__name__)


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weather command."""
    # Parse location from args
    if context.args:
        query = " ".join(context.args)
        location = _geocode(query)
        if not location:
            await update.message.reply_text(
                f"Couldn't find location: {query}\n"
                f"Try a zip code (13827) or city/state (Denver, CO)"
            )
            return
        lat = location['lat']
        lon = location['lon']
        name = location['name']
    else:
        lat = DEFAULT_LAT
        lon = DEFAULT_LON
        name = DEFAULT_NAME

    await update.message.reply_text(f"Fetching weather for {name}...")

    data = fetch_weather(lat, lon)
    if not data:
        await update.message.reply_text("Weather service unavailable. Try again later.")
        return

    msg = format_weather_telegram(data, name)
    await update.message.reply_text(msg, parse_mode='Markdown')
