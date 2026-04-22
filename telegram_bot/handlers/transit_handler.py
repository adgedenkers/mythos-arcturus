"""
transit_handler.py — Telegram handler for daily transit reports.

Commands:
  /transits           — today's transit pressure for Adge (with Ollama interpretation)
  /transits seraphe   — today's transit pressure for Seraphe
  /transits brief     — Adge's transits, no interpretation (faster)
  /transits date YYYY-MM-DD — specific date for Adge

Wired in SEN-0009 (Letter E). Calls the existing transit_pressure.py +
transit_interpreter.py pipeline, now backed by natal_generator.load_natal()
for natal chart data.
"""
import logging
import sys
from datetime import date, datetime

log = logging.getLogger('iris.handlers.transits')

# Chart IDs (from astro_natal_charts, confirmed via SEN-0008 diag)
CHART_IDS = {
    'adge':    9,
    'seraphe': 11,
}

CHART_LABELS = {
    'adge':    'Ka\'tuar\'el (Adge)',
    'seraphe': 'Seraphe',
}


def register(application):
    """Register /transits command handler."""
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler('transits', handle_transits))
    log.info('Registered /transits command handler')


async def handle_transits(update, context):
    """Handle /transits and subcommands."""
    args = context.args or []

    # Parse subcommand / target person / date
    person = 'adge'
    target_date = date.today()
    brief_mode = False

    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == 'seraphe':
            person = 'seraphe'
        elif arg == 'brief':
            brief_mode = True
        elif arg == 'date' and i + 1 < len(args):
            try:
                target_date = datetime.strptime(args[i + 1], '%Y-%m-%d').date()
                i += 1
            except ValueError:
                await update.message.reply_text(
                    '⚠️ Invalid date format. Use YYYY-MM-DD.\nExample: /transits date 2026-04-28'
                )
                return
        i += 1

    chart_id = CHART_IDS[person]
    label = CHART_LABELS[person]
    date_str = target_date.strftime('%B %-d, %Y')

    await update.message.reply_text(
        f'⏳ Computing transits for {label} on {date_str}…'
    )

    try:
        sys.path.insert(0, '/opt/mythos')
        from astrology.spiral.transit_pressure import (
            run_daily_pressure,
            get_todays_pressure,
            format_pressure_brief,
        )
        from astrology.spiral.transit_interpreter import (
            interpret_transits,
            format_pressure_brief_with_interp,
        )

        # SEN-0012: run_daily_pressure computes + persists, then returns aspects.
        # get_todays_pressure alone only reads the cache — if nothing has run
        # the daily pipeline yet, it returns empty. run_daily_pressure is the
        # correct entry point (idempotent via unique constraint on the table).
        aspects = run_daily_pressure(chart_id, target_date=target_date)
        if not aspects:
            # Fallback: try reading existing cache (e.g. already computed today)
            aspects = get_todays_pressure(chart_id, target_date=target_date)

        if not aspects:
            await update.message.reply_text(
                f'No significant transits in orb for {label} on {date_str}.'
            )
            return

        if brief_mode:
            # Fast path — no Ollama calls
            text = f'🔭 *{label} — Transit Pressure*\n_{date_str}_\n\n'
            text += format_pressure_brief(aspects)
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            # Full path — Ollama interpretations
            # Only interpret building/exact aspects (watch-level are auto-noted)
            enriched = interpret_transits(aspects)
            text = f'🔭 *{label} — Daily Transits*\n_{date_str}_\n\n'
            pressure_text = format_pressure_brief_with_interp(enriched)
            text += pressure_text

            # Telegram max message length guard
            if len(text) > 4096:
                # Send in two parts
                await update.message.reply_text(text[:4000] + '…', parse_mode='Markdown')
                await update.message.reply_text('…' + text[4000:], parse_mode='Markdown')
            else:
                await update.message.reply_text(text, parse_mode='Markdown')

    except Exception as e:
        log.error(f'transit_handler error: {e}', exc_info=True)
        await update.message.reply_text(
            f'⚠️ Transit engine error: {e}\n'
            f'Try /transits brief for a faster fallback.'
        )
