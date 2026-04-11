"""
Route Planner Telegram Handler — /today, /plan, /add_errand, /optimize, /routes, /add_route, /add_recurring, /locations

Patch 0199: Route Planner for Iris/Mythos.
"""

import logging
from datetime import date, time, datetime
from telegram import Update
from telegram.ext import ContextTypes

import sys
sys.path.insert(0, '/opt/mythos')

from route_planner.planner import RoutePlanner, format_schedule_telegram

logger = logging.getLogger(__name__)

planner = RoutePlanner()


async def handle_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /today or /plan — Show today's assembled schedule.
    Usage: /today [tomorrow|YYYY-MM-DD]
    """
    try:
        target = date.today()
        if context.args:
            arg = context.args[0].lower()
            if arg == 'tomorrow':
                from datetime import timedelta
                target = date.today() + timedelta(days=1)
            else:
                try:
                    target = date.fromisoformat(arg)
                except ValueError:
                    await update.message.reply_text("⚠️ Invalid date. Use YYYY-MM-DD or 'tomorrow'.")
                    return

        schedule = planner.get_today(target)

        if not schedule['stops']:
            await update.message.reply_text(
                f"📅 **{schedule['day_name']}, {schedule['date']}**\n\n"
                f"Nothing scheduled. Use /add\\_errand to add tasks.",
                parse_mode='Markdown'
            )
            return

        msg = format_schedule_telegram(schedule)
        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in /today: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_add_errand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_errand <description> [location] — Add a one-off errand for today.

    Examples:
        /add_errand groceries Price Chopper
        /add_errand hardware store Tractor Supply
        /add_errand pizza
        /add_errand oil change AutoZone
    """
    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /add\\_errand <description> [location]\n\n"
                "Examples:\n"
                "  /add\\_errand groceries Price Chopper\n"
                "  /add\\_errand pizza\n"
                "  /add\\_errand hardware Tractor Supply\n\n"
                "Use /locations to see known places.",
                parse_mode='Markdown'
            )
            return

        text = ' '.join(context.args)

        # Try to parse "description @ location" or "description location"
        name = text
        location_hint = None

        if ' @ ' in text:
            parts = text.split(' @ ', 1)
            name = parts[0].strip()
            location_hint = parts[1].strip()
        else:
            # Try to match known location names in the text
            # Common patterns: "groceries Price Chopper", "pizza Magros"
            known_keywords = _get_location_keywords()
            for keyword, loc_name in known_keywords.items():
                if keyword.lower() in text.lower():
                    # The location keyword is in the text — split it out
                    name_part = text.lower().replace(keyword.lower(), '').strip()
                    if name_part:
                        name = name_part.title()
                    else:
                        name = f"Stop at {loc_name}"
                    location_hint = loc_name
                    break

            # Special: "pizza" without location → Magro's
            if not location_hint and 'pizza' in text.lower():
                name = 'Pizza pickup'
                location_hint = 'Magros'

            # Special: "groceries" without location → Price Chopper
            if not location_hint and ('groceries' in text.lower() or 'grocery' in text.lower()):
                name = 'Groceries'
                location_hint = 'Price Chopper'

            # Special: "walmart" as an errand description
            if not location_hint and 'walmart' in text.lower():
                name = 'Walmart run'
                location_hint = 'Walmart'

        result = planner.add_errand(
            name=name,
            location_name=location_hint,
        )

        loc_display = result.get('resolved_location', location_hint or 'unresolved')
        await update.message.reply_text(
            f"✅ Added errand: **{name}**\n"
            f"📍 {loc_display}\n"
            f"⏱ {result.get('duration_minutes', 15)} min\n\n"
            f"Use /today to see your schedule or /optimize to plan your route.",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error in /add_errand: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_optimize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /optimize — Re-run optimization on today's schedule after adding errands.
    """
    try:
        target = date.today()
        if context.args:
            arg = context.args[0].lower()
            if arg == 'tomorrow':
                from datetime import timedelta
                target = date.today() + timedelta(days=1)

        schedule = planner.optimize_today(target)

        if not schedule.get('optimized'):
            await update.message.reply_text(
                "No errands to optimize — your day is just recurring commitments.\n"
                "Use /add\\_errand to add tasks first.",
                parse_mode='Markdown'
            )
            return

        msg = format_schedule_telegram(schedule)

        placed = schedule.get('errands_placed', 0)
        total = schedule.get('errands_pending', 0)
        header = f"🗺 **Optimized Route** — {placed}/{total} errands placed\n\n"

        await update.message.reply_text(header + msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in /optimize: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /routes — Show all known routes and drive times.
    """
    try:
        routes = planner.get_known_routes()
        if not routes:
            await update.message.reply_text("No known routes. Use /add\\_route to add one.", parse_mode='Markdown')
            return

        lines = ["🗺 **Known Routes**\n"]
        for r in routes:
            note = f" _{r['notes']}_" if r.get('notes') else ''
            lines.append(f"  {r['from_name']} → {r['to_name']}: **{r['drive_minutes']} min**{note}")

        await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in /routes: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_add_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_route <from> > <to> <minutes> [notes] — Add or update a known route.

    Examples:
        /add_route Home > Walmart 15
        /add_route School > Norwich 15 construction on Rt 12
    """
    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /add\\_route <from> > <to> <minutes> [notes]\n\n"
                "Example: /add\\_route Home > Walmart 15",
                parse_mode='Markdown'
            )
            return

        text = ' '.join(context.args)

        if ' > ' not in text:
            await update.message.reply_text("Use '>' to separate from and to.\nExample: /add\\_route Home > Walmart 15", parse_mode='Markdown')
            return

        parts = text.split(' > ', 1)
        from_name = parts[0].strip()
        rest = parts[1].strip().split()

        # Find the minutes (first token that's a number)
        to_parts = []
        minutes = None
        notes_parts = []
        found_minutes = False
        for token in rest:
            if not found_minutes and token.isdigit():
                minutes = int(token)
                found_minutes = True
            elif found_minutes:
                notes_parts.append(token)
            else:
                to_parts.append(token)

        if not to_parts or minutes is None:
            await update.message.reply_text("Couldn't parse. Use: /add\\_route Home > Walmart 15", parse_mode='Markdown')
            return

        to_name = ' '.join(to_parts)
        notes = ' '.join(notes_parts) if notes_parts else None

        result = planner.add_route(from_name, to_name, minutes, notes=notes, bidirectional=True)

        await update.message.reply_text(
            f"✅ Route saved (both directions):\n"
            f"  {from_name} ↔ {to_name}: **{minutes} min**"
            + (f"\n  📝 {notes}" if notes else ''),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error in /add_route: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /locations — Show all known locations.
    """
    try:
        locs = planner.get_known_locations()
        if not locs:
            await update.message.reply_text("No known locations.")
            return

        lines = ["📍 **Known Locations**\n"]
        current_cat = None
        for loc in locs:
            cat = loc.get('category', 'other')
            if cat != current_cat:
                current_cat = cat
                lines.append(f"\n**{cat.title()}:**")
            phone = f" | 📞 {loc['phone']}" if loc.get('phone') else ''
            dwell = f" | ~{loc['default_dwell_minutes']}min" if loc.get('default_dwell_minutes') else ''
            lines.append(f"  • {loc['name']}{phone}{dwell}")

        await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in /locations: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_add_recurring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_recurring <name> | <time> | <type> | [days] | [location] | [notes]

    Types: daily, weekday, specific_days
    Days (for specific_days): M,T,W,Th,F,Sa,Su

    Examples:
        /add_recurring Gym | 6:00 AM | weekday
        /add_recurring Therapy | 2:00 PM | specific_days | T,Th
    """
    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /add\\_recurring name | time | type | [days] | [location] | [notes]\n\n"
                "Types: daily, weekday, specific\\_days\n"
                "Days: M,T,W,Th,F,Sa,Su\n\n"
                "Examples:\n"
                "  /add\\_recurring Gym | 6:00 AM | weekday\n"
                "  /add\\_recurring Therapy | 2:00 PM | specific\\_days | T,Th",
                parse_mode='Markdown'
            )
            return

        text = ' '.join(context.args)
        parts = [p.strip() for p in text.split('|')]

        if len(parts) < 3:
            await update.message.reply_text("Need at least: name | time | type", parse_mode='Markdown')
            return

        name = parts[0]
        time_str = parts[1]
        sched_type = parts[2].lower().replace(' ', '_')

        # Parse time
        for fmt in ('%I:%M %p', '%H:%M', '%I:%M%p', '%I%p', '%I %p'):
            try:
                parsed_time = datetime.strptime(time_str, fmt).strftime('%H:%M')
                break
            except ValueError:
                continue
        else:
            await update.message.reply_text(f"Couldn't parse time: {time_str}")
            return

        # Parse days
        days_of_week = None
        day_map = {'m': 0, 'mo': 0, 'mon': 0, 't': 1, 'tu': 1, 'tue': 1,
                    'w': 2, 'we': 2, 'wed': 2, 'th': 3, 'thu': 3,
                    'f': 4, 'fr': 4, 'fri': 4, 'sa': 5, 'sat': 5,
                    'su': 6, 'sun': 6}
        if sched_type == 'specific_days' and len(parts) > 3:
            day_tokens = [d.strip().lower() for d in parts[3].split(',')]
            days_of_week = [day_map[d] for d in day_tokens if d in day_map]

        location = parts[4].strip() if len(parts) > 4 else None
        notes = parts[5].strip() if len(parts) > 5 else None

        result = planner.add_recurring(
            name=name,
            schedule_type=sched_type,
            time_at=parsed_time,
            location_name=location,
            days_of_week=days_of_week,
            notes=notes,
        )

        days_display = ''
        if days_of_week:
            rev_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
            days_display = f"\n  📆 {', '.join(rev_map[d] for d in sorted(days_of_week))}"

        await update.message.reply_text(
            f"✅ Recurring added: **{name}**\n"
            f"  🕐 {time_str} ({sched_type}){days_display}"
            + (f"\n  📍 {location}" if location else ''),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error in /add_recurring: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_errand_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /errand_done <id> — Mark an errand as completed.
    """
    try:
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Usage: /errand\\_done <id>", parse_mode='Markdown')
            return

        errand_id = int(context.args[0])
        if planner.complete_errand(errand_id):
            await update.message.reply_text(f"✅ Errand #{errand_id} marked complete.")
        else:
            await update.message.reply_text(f"⚠️ Errand #{errand_id} not found.")

    except Exception as e:
        logger.error(f"Error in /errand_done: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


def _get_location_keywords() -> dict:
    """
    Return a dict of keyword → known_location_name for fuzzy matching in errand descriptions.
    This is a static quick-match list; the planner does DB lookup as fallback.
    """
    return {
        'price chopper': 'Price Chopper',
        'pricechopper': 'Price Chopper',
        'walmart': 'Walmart Supercenter',
        'tractor supply': 'Tractor Supply',
        'tsc': 'Tractor Supply',
        'dollar general': 'Dollar General',
        'autozone': 'AutoZone',
        'auto zone': 'AutoZone',
        'advance auto': 'Advance Auto Parts',
        'magros': 'Magros Pizzeria',
        "magro's": 'Magros Pizzeria',
        'pizza hut': 'Pizza Hut Norwich',
        'roma': 'Roma Pizzeria',
    }
