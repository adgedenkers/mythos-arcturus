"""
Calendar Telegram Handler
=========================
/calendar       - Show this week's events
/calendar today - Show today
/calendar week  - Show this week
/calendar month - Show this month
/calendar add   - Quick add an event
"""

import os
import sys
import logging
from datetime import date, datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor
from telegram import Update
from telegram.ext import ContextTypes

sys.path.insert(0, '/opt/mythos/core')

logger = logging.getLogger(__name__)


def _get_conn():
    from dotenv import load_dotenv
    load_dotenv('/opt/mythos/.env')
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


async def handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /calendar command."""
    args = context.args if context.args else []

    if not args:
        await _show_week(update)
    elif args[0].lower() == 'week':
        await _show_week(update)
    elif args[0].lower() == 'month':
        await _show_month(update)
    elif args[0].lower() == 'today':
        await _show_today(update)
    elif args[0].lower() == 'add':
        await _quick_add(update, args[1:])
    else:
        await _show_week(update)


async def _show_today(update: Update):
    try:
        from calendar_formatter import format_day_view
        today = date.today()
        header = f"📅 <b>{today.strftime('%A, %B %d, %Y')}</b>\n\n"
        view = format_day_view(today)
        await update.message.reply_text(header + view, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Calendar today failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def _show_week(update: Update):
    try:
        from calendar_formatter import format_week_view
        view = format_week_view()
        await update.message.reply_text(view, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Calendar week failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def _show_month(update: Update):
    try:
        from calendar_formatter import format_month_view
        view = format_month_view()
        await update.message.reply_text(view, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Calendar month failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def _quick_add(update: Update, args: list):
    """Quick add: /calendar add 2/20 2pm Dentist for Fitz"""
    if len(args) < 2:
        await update.message.reply_text(
            "📅 <b>Quick add:</b>\n\n"
            "<code>/calendar add 2/20 2pm Dentist for Fitz</code>\n"
            "<code>/calendar add tomorrow 9am VA team meeting</code>\n"
            "<code>/calendar add 3/1 Tax prep</code>",
            parse_mode="HTML"
        )
        return

    date_str = args[0]
    time_str = None
    title_start = 1

    if len(args) > 1 and _looks_like_time(args[1]):
        time_str = args[1]
        title_start = 2

    title = " ".join(args[title_start:])
    if not title:
        await update.message.reply_text("❌ Need an event title.")
        return

    event_date = _parse_date(date_str)
    if not event_date:
        await update.message.reply_text(f"❌ Couldn't parse date: {date_str}")
        return

    event_time = _parse_time(time_str) if time_str else None

    person = 'adge'
    title_lower = title.lower()
    if any(n in title_lower for n in ['rebecca', 'seraphe', 'becky', 'lou']):
        person = 'rebecca'
    elif any(n in title_lower for n in ['fitz', 'son']):
        person = 'fitz'
    elif any(n in title_lower for n in ['family', 'all of us', 'everyone']):
        person = 'family'

    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO calendar_events (title, event_date, start_time, person, source)
            VALUES (%s, %s, %s, %s, 'manual')
            RETURNING id
        """, (title, event_date, event_time, person))
        conn.commit()
        cur.close()
        conn.close()

        time_display = f" at {event_time.strftime('%-I:%M %p')}" if event_time else ""
        person_display = f" ({person})" if person != 'adge' else ""

        await update.message.reply_text(
            f"✅ Added to calendar\n\n"
            f"📅 <b>{title}</b>{person_display}\n"
            f"{event_date.strftime('%A, %B %d, %Y')}{time_display}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Calendar add failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


def _looks_like_time(s: str) -> bool:
    s = s.lower().strip()
    return s.endswith('am') or s.endswith('pm') or (':' in s and len(s) <= 8)


def _parse_time(s: str):
    if not s:
        return None
    s = s.lower().strip()
    for fmt in ['%I:%M%p', '%I:%M %p', '%I%p', '%I %p', '%H:%M']:
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    return None


def _parse_date(s: str):
    import re
    s = s.lower().strip()
    today = date.today()

    if s in ('today', 'tonight'):
        return today
    if s == 'tomorrow':
        return today + timedelta(days=1)
    if s == 'yesterday':
        return today - timedelta(days=1)

    days = {
        'monday': 0, 'mon': 0, 'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2, 'thursday': 3, 'thu': 3, 'thur': 3,
        'friday': 4, 'fri': 4, 'saturday': 5, 'sat': 5, 'sunday': 6, 'sun': 6,
    }
    if s in days:
        target = days[s]
        delta = (target - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return today + timedelta(days=delta)

    m = re.match(r'^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?$', s)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        year = today.year
        if m.group(3):
            y = int(m.group(3))
            year = y if y > 100 else 2000 + y
        try:
            d = date(year, month, day)
            if d < today and not m.group(3):
                d = date(year + 1, month, day)
            return d
        except ValueError:
            return None
    return None
