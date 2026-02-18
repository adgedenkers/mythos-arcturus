"""
Checkin & Routines Telegram Handlers
=====================================
/checkin      - Morning briefing (or any time of day)
/rdone N      - Complete routine N from today's list
/rskip N      - Skip routine N
/routines     - Show today's routines and status
/routine add  - Add a new routine (interactive)
"""

import logging
import sys
from telegram import Update
from telegram.ext import ContextTypes

sys.path.insert(0, '/opt/mythos/core')

logger = logging.getLogger(__name__)


async def handle_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /checkin command — generate and send daily briefing.
    Also triggered by natural language greetings via Iris.
    """
    try:
        from routines_engine import generate_daily_briefing, format_briefing_telegram

        briefing = generate_daily_briefing()
        msg = format_briefing_telegram(briefing)

        await update.message.reply_text(msg, parse_mode="HTML")

        # Store routine list in context for /rdone and /rskip
        pending = briefing.get('routines_pending', [])
        context.user_data['routine_ids'] = [r['id'] for r in pending]
        context.user_data['routine_titles'] = [r['title'] for r in pending]

    except Exception as e:
        logger.error(f"Checkin failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Checkin failed: {str(e)}")


async def handle_routines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /routines — show today's routines with completion status."""
    try:
        from routines_engine import get_routines_due_today, ensure_today_instances, get_db_connection

        conn = get_db_connection()
        ensure_today_instances(conn)
        routines = get_routines_due_today(conn)
        conn.close()

        if not routines:
            await update.message.reply_text("📋 No routines scheduled for today.")
            return

        lines = ["📋 <b>Today's Routines</b>\n"]

        pending_ids = []
        pending_titles = []

        pending_idx = 1
        for r in routines:
            status = r.get('completion_status', 'pending')
            domain_emoji = {
                'finance': '💰', 'household': '🏠', 'health': '💊',
                'work': '💼', 'personal': '📌', 'mythos': '🔮',
                'spiritual': '✨'
            }
            emoji = domain_emoji.get(r.get('domain'), '📌')

            if status == 'done':
                lines.append(f"  ✅ {emoji} <s>{r['title']}</s>")
                if r.get('completed_at'):
                    lines.append(f"       <i>done at {r['completed_at'].strftime('%-I:%M %p')}</i>")
            elif status == 'skipped':
                lines.append(f"  ⏭ {emoji} <s>{r['title']}</s> <i>(skipped)</i>")
            else:
                time_str = ""
                if r.get('time_due'):
                    t = r['time_due']
                    if hasattr(t, 'strftime'):
                        time_str = f" (by {t.strftime('%-I:%M %p')})"
                    else:
                        time_str = f" (by {t})"
                lines.append(f"  <b>{pending_idx}.</b> {emoji} {r['title']}{time_str}")
                pending_ids.append(r['id'])
                pending_titles.append(r['title'])
                pending_idx += 1

        done_count = sum(1 for r in routines if r.get('completion_status') == 'done')
        lines.insert(1, f"Progress: {done_count}/{len(routines)} complete\n")

        lines.append("")
        lines.append("<i>/rdone N • /rskip N</i>")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")

        context.user_data['routine_ids'] = pending_ids
        context.user_data['routine_titles'] = pending_titles

    except Exception as e:
        logger.error(f"Routines list failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_rdone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rdone N — mark routine N as complete."""
    try:
        args = context.args if context.args else []
        if not args:
            await update.message.reply_text("Usage: /rdone <number>\nRun /routines first to see the list.")
            return

        try:
            num = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Please provide a routine number.")
            return

        routine_ids = context.user_data.get('routine_ids', [])
        routine_titles = context.user_data.get('routine_titles', [])

        if not routine_ids:
            await update.message.reply_text("❌ Run /checkin or /routines first.")
            return

        if num < 1 or num > len(routine_ids):
            await update.message.reply_text(f"❌ Choose 1-{len(routine_ids)}")
            return

        rid = routine_ids[num - 1]
        notes = " ".join(args[1:]) if len(args) > 1 else None

        from routines_engine import complete_routine
        title = complete_routine(rid, notes=notes)

        if title:
            # Remove from pending list
            routine_ids.pop(num - 1)
            routine_titles.pop(num - 1)
            context.user_data['routine_ids'] = routine_ids
            context.user_data['routine_titles'] = routine_titles

            remaining = len(routine_ids)
            if remaining == 0:
                await update.message.reply_text(f"✅ <b>{title}</b>\n\n🎯 All routines complete for today!", parse_mode="HTML")
            else:
                await update.message.reply_text(f"✅ <b>{title}</b>\n\n{remaining} remaining.", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Routine not found.")

    except Exception as e:
        logger.error(f"rdone failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_rskip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rskip N — skip routine N for today."""
    try:
        args = context.args if context.args else []
        if not args:
            await update.message.reply_text("Usage: /rskip <number> [reason]\nRun /routines first.")
            return

        try:
            num = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Please provide a routine number.")
            return

        routine_ids = context.user_data.get('routine_ids', [])
        routine_titles = context.user_data.get('routine_titles', [])

        if not routine_ids:
            await update.message.reply_text("❌ Run /checkin or /routines first.")
            return

        if num < 1 or num > len(routine_ids):
            await update.message.reply_text(f"❌ Choose 1-{len(routine_ids)}")
            return

        rid = routine_ids[num - 1]
        title = routine_titles[num - 1]
        reason = " ".join(args[1:]) if len(args) > 1 else None

        from routines_engine import skip_routine
        skip_routine(rid, reason=reason)

        # Remove from pending list
        routine_ids.pop(num - 1)
        routine_titles.pop(num - 1)
        context.user_data['routine_ids'] = routine_ids
        context.user_data['routine_titles'] = routine_titles

        await update.message.reply_text(f"⏭ Skipped: <b>{title}</b>", parse_mode="HTML")

    except Exception as e:
        logger.error(f"rskip failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_routine_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /routine_add — add a new routine.
    Usage: /routine_add daily|weekly|monthly "Title" [options]
    
    Examples:
        /routine_add daily Feed the animals -d household -t 07:00
        /routine_add weekly Grocery run -w 6 -d household
        /routine_add monthly Pay extra on Old Navy -m 20 -d finance
    """
    try:
        args = context.args if context.args else []
        if len(args) < 2:
            await update.message.reply_text(
                "📋 <b>Add a routine:</b>\n\n"
                "<code>/routine_add daily Feed the animals -d household -t 07:00</code>\n"
                "<code>/routine_add weekly Grocery run -w 6 -d household</code>\n"
                "<code>/routine_add monthly Pay extra CC -m 20 -d finance</code>\n\n"
                "<b>Options:</b>\n"
                "  -d domain (finance, household, health, work, personal, mythos, spiritual)\n"
                "  -t time due (HH:MM)\n"
                "  -w day of week (0=Mon..6=Sun)\n"
                "  -m day of month (1-31)\n"
                "  -p priority (high, medium, low)",
                parse_mode="HTML"
            )
            return

        frequency = args[0].lower()
        if frequency not in ('daily', 'weekly', 'monthly', 'weekdays', 'weekends'):
            await update.message.reply_text("❌ Frequency must be: daily, weekly, monthly, weekdays, weekends")
            return

        # Parse args
        title_parts = []
        domain = 'personal'
        time_due = None
        day_of_week = None
        day_of_month = None
        priority = 'medium'

        i = 1
        while i < len(args):
            if args[i] == '-d' and i + 1 < len(args):
                domain = args[i + 1]
                i += 2
            elif args[i] == '-t' and i + 1 < len(args):
                time_due = args[i + 1]
                i += 2
            elif args[i] == '-w' and i + 1 < len(args):
                day_of_week = int(args[i + 1])
                i += 2
            elif args[i] == '-m' and i + 1 < len(args):
                day_of_month = int(args[i + 1])
                i += 2
            elif args[i] == '-p' and i + 1 < len(args):
                priority = args[i + 1]
                i += 2
            else:
                title_parts.append(args[i])
                i += 1

        title = " ".join(title_parts)
        if not title:
            await update.message.reply_text("❌ Routine needs a title.")
            return

        from routines_engine import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO routines (title, frequency, domain, priority, time_due, day_of_week, day_of_month)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (title, frequency, domain, priority, time_due, day_of_week, day_of_month))

        result = cur.fetchone()
        conn.commit()
        conn.close()

        freq_display = frequency
        if frequency == 'weekly' and day_of_week is not None:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            freq_display = f"weekly ({days[day_of_week]})"
        elif frequency == 'monthly' and day_of_month:
            freq_display = f"monthly (day {day_of_month})"

        await update.message.reply_text(
            f"✅ Routine added!\n\n"
            f"<b>{title}</b>\n"
            f"📅 {freq_display} | 🏷 {domain} | {priority}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"routine_add failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")
