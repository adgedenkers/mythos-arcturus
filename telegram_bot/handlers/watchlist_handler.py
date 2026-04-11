#!/usr/bin/env python3
"""Handle /watch — family watchlist with streaming deep links."""

import logging
import psycopg2
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

logger = logging.getLogger('handler.watchlist')

DB_DSN = "dbname=mythos user=adge"

# ── Platform Registry ──────────────────────────────────────────────────
# Each platform: (display_name, search_url_template, app_uri_template)
# {q} = URL-encoded title, {title} = raw title
PLATFORMS = {
    'netflix':    ('Netflix',        'https://www.netflix.com/search?q={q}',          'nflx://www.netflix.com/search?q={q}'),
    'hulu':       ('Hulu',           'https://www.hulu.com/search?q={q}',             'hulu://search?query={q}'),
    'disney':     ('Disney+',        'https://www.disneyplus.com/search?q={q}',       'disneyplus://search?q={q}'),
    'prime':      ('Prime Video',    'https://www.amazon.com/s?i=instant-video&k={q}','intent://watch?gti=amzn1#Intent;scheme=amzn;end'),
    'peacock':    ('Peacock',        'https://www.peacocktv.com/search?q={q}',        'peacock://search?q={q}'),
    'paramount':  ('Paramount+',    'https://www.paramountplus.com/search/?q={q}',   'paramountplus://search?q={q}'),
    'max':        ('Max',            'https://play.max.com/search?q={q}',             'hbomax://search?q={q}'),
    'mgm':        ('MGM+ (Prime)',   'https://www.amazon.com/s?i=instant-video&k={q}+mgm','intent://watch?gti=amzn1#Intent;scheme=amzn;end'),
    'appletv':    ('Apple TV+',      'https://tv.apple.com/search?term={q}',          'com.apple.tv://search?q={q}'),
    'tubi':       ('Tubi',           'https://tubitv.com/search/{q}',                 'tubi://search?q={q}'),
    'youtube':    ('YouTube',        'https://www.youtube.com/results?search_query={q}','youtube://results?search_query={q}'),
    'other':      ('Other',          None,                                             None),
}

PLATFORM_SHORTCUTS = {
    'hbo': 'max',
    'hbomax': 'max',
    'disney+': 'disney',
    'disneyplus': 'disney',
    'paramount+': 'paramount',
    'apple': 'appletv',
    'apple tv': 'appletv',
    'amazon': 'prime',
    'amazon prime': 'prime',
    'mgm+': 'mgm',
    'mgm plus': 'mgm',
}

# Conversation states
TITLE, PLATFORM, MEDIA_TYPE, WHO = range(4)


def _get_conn():
    return psycopg2.connect(DB_DSN)


def _resolve_platform(raw: str) -> str:
    """Resolve a platform name to its canonical key."""
    key = raw.strip().lower().replace('+', '+')
    if key in PLATFORMS:
        return key
    if key in PLATFORM_SHORTCUTS:
        return PLATFORM_SHORTCUTS[key]
    # fuzzy: check if input is substring of any platform name
    for k, (name, _, _) in PLATFORMS.items():
        if key in name.lower() or key in k:
            return k
    return None


def _make_deep_link(platform_key: str, title: str) -> str:
    """Build the best available link for a platform + title."""
    from urllib.parse import quote_plus
    if platform_key not in PLATFORMS:
        return None
    _, web_url, app_uri = PLATFORMS[platform_key]
    q = quote_plus(title)
    # Use web URL — it's the most reliable from Telegram on mobile
    # App URI schemes are inconsistent across Android/iOS versions
    if web_url:
        return web_url.replace('{q}', q)
    return None


def _format_entry(row, idx=None) -> str:
    """Format a single watchlist entry."""
    id_, title, media_type, platform, status, added_by, notes, created_at, watched_at = row
    platform_info = PLATFORMS.get(platform, (platform.title(), None, None))
    display_name = platform_info[0]

    status_icon = {'want': '📋', 'watching': '▶️', 'watched': '✅'}.get(status, '❓')
    type_icon = '🎬' if media_type == 'movie' else '📺'
    num = f"#{idx} " if idx is not None else ""

    line = f"{status_icon} {num}{type_icon} *{title}*\n"
    line += f"   {display_name}"
    if added_by:
        who = 'Adge' if added_by == 'adge' else 'Seraphe'
        line += f" · added by {who}"
    if notes:
        line += f"\n   _{notes}_"

    return line


# ── /watch command ──────────────────────────────────────────────────────

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /watch — main entry point. Routes to subcommands."""
    args = context.args if context.args else []

    if not args:
        return await _watch_list(update, context)

    sub = args[0].lower()

    if sub == 'add':
        # If they gave a title inline: /watch add Breaking Bad
        if len(args) > 1:
            title = ' '.join(args[1:])
            context.user_data['watch_title'] = title
            return await _ask_platform(update, context)
        else:
            await update.message.reply_text("What do you want to add to the watchlist?")
            return TITLE

    elif sub == 'list':
        return await _watch_list(update, context)

    elif sub == 'search':
        if len(args) > 1:
            term = ' '.join(args[1:])
            return await _watch_search(update, context, term)
        else:
            await update.message.reply_text("Search for what? `/watch search breaking bad`")
            return ConversationHandler.END

    elif sub == 'done':
        if len(args) > 1:
            return await _watch_set_status(update, context, args[1], 'watched')
        else:
            await update.message.reply_text("Which one? Use the # from `/watch list`")
            return ConversationHandler.END

    elif sub == 'watching':
        if len(args) > 1:
            return await _watch_set_status(update, context, args[1], 'watching')
        else:
            await update.message.reply_text("Which one? Use the # from `/watch list`")
            return ConversationHandler.END

    elif sub == 'drop':
        if len(args) > 1:
            return await _watch_drop(update, context, args[1])
        else:
            await update.message.reply_text("Which one? Use the # from `/watch list`")
            return ConversationHandler.END

    else:
        # Assume they typed a title: /watch Breaking Bad
        title = ' '.join(args)
        context.user_data['watch_title'] = title
        return await _ask_platform(update, context)


async def _ask_platform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show platform selection buttons."""
    title = context.user_data.get('watch_title', '?')
    buttons = []
    row = []
    # Show most-used platforms as buttons
    for key in ['netflix', 'hulu', 'disney', 'prime', 'max', 'peacock', 'paramount', 'mgm', 'appletv', 'tubi', 'other']:
        name = PLATFORMS[key][0]
        row.append(InlineKeyboardButton(name, callback_data=f"wp_{key}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"Adding *{title}* — where is it streaming?",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    return PLATFORM


async def platform_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle platform button press."""
    query = update.callback_query
    await query.answer()

    platform_key = query.data.replace('wp_', '')
    context.user_data['watch_platform'] = platform_key

    # Ask show vs movie
    buttons = [
        [
            InlineKeyboardButton("📺 Show", callback_data="wt_show"),
            InlineKeyboardButton("🎬 Movie", callback_data="wt_movie"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"Show or movie?",
        reply_markup=keyboard
    )
    return MEDIA_TYPE


async def media_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle show/movie button press."""
    query = update.callback_query
    await query.answer()

    media_type = query.data.replace('wt_', '')
    context.user_data['watch_media_type'] = media_type

    # Ask who's adding
    buttons = [
        [
            InlineKeyboardButton("Adge", callback_data="ww_adge"),
            InlineKeyboardButton("Seraphe", callback_data="ww_seraphe"),
            InlineKeyboardButton("Both", callback_data="ww_both"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"Who's adding this?",
        reply_markup=keyboard
    )
    return WHO


async def who_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle who button press — save the entry."""
    query = update.callback_query
    await query.answer()

    added_by = query.data.replace('ww_', '')
    title = context.user_data.get('watch_title', 'Unknown')
    platform = context.user_data.get('watch_platform', 'other')
    media_type = context.user_data.get('watch_media_type', 'show')

    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO watchlist (title, media_type, platform, status, added_by)
               VALUES (%s, %s, %s, 'want', %s) RETURNING id""",
            (title, media_type, platform, added_by)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to add watchlist entry: {e}")
        await query.edit_message_text(f"❌ Error adding to watchlist: {e}")
        return ConversationHandler.END

    platform_name = PLATFORMS.get(platform, (platform,))[0]
    type_icon = '🎬' if media_type == 'movie' else '📺'
    who_name = 'Adge' if added_by == 'adge' else ('Seraphe' if added_by == 'seraphe' else 'Both')

    # Build response with deep link button
    text = f"✅ Added to watchlist!\n\n{type_icon} *{title}*\n{platform_name} · {who_name}"
    deep_link = _make_deep_link(platform, title)

    if deep_link:
        buttons = [[InlineKeyboardButton(f"🔗 Open in {platform_name}", url=deep_link)]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await query.edit_message_text(text, parse_mode='Markdown')

    # Clear state
    for k in ['watch_title', 'watch_platform', 'watch_media_type']:
        context.user_data.pop(k, None)

    return ConversationHandler.END


async def title_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle typed title after /watch add with no args."""
    context.user_data['watch_title'] = update.message.text.strip()
    return await _ask_platform(update, context)


# ── List / Search / Status ──────────────────────────────────────────────

async def _watch_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show active watchlist (want + watching)."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT id, title, media_type, platform, status, added_by, notes, created_at, watched_at
               FROM watchlist
               WHERE status IN ('want', 'watching')
               ORDER BY
                   CASE status WHEN 'watching' THEN 0 ELSE 1 END,
                   created_at DESC"""
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to list watchlist: {e}")
        msg = update.message or update.callback_query.message
        await msg.reply_text(f"❌ Error: {e}")
        return ConversationHandler.END

    msg = update.message or update.callback_query.message

    if not rows:
        await msg.reply_text("📋 Watchlist is empty. Add something with `/watch add`")
        return ConversationHandler.END

    # Build numbered list with deep link buttons
    lines = ["📋 *Watchlist*\n"]
    buttons = []
    for idx, row in enumerate(rows, 1):
        lines.append(_format_entry(row, idx))
        # Add deep link button for each entry
        deep_link = _make_deep_link(row[3], row[1])  # platform, title
        if deep_link:
            platform_name = PLATFORMS.get(row[3], (row[3],))[0]
            buttons.append([InlineKeyboardButton(
                f"#{idx} {row[1][:25]} → {platform_name}",
                url=deep_link
            )])

    lines.append(f"\n_{len(rows)} items_")
    text = '\n'.join(lines)

    if buttons:
        # Show max 10 buttons to avoid Telegram limits
        keyboard = InlineKeyboardMarkup(buttons[:10])
        await msg.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await msg.reply_text(text, parse_mode='Markdown')

    return ConversationHandler.END


async def _watch_search(update: Update, context: ContextTypes.DEFAULT_TYPE, term: str) -> int:
    """Search watchlist by title."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT id, title, media_type, platform, status, added_by, notes, created_at, watched_at
               FROM watchlist
               WHERE title ILIKE %s
               ORDER BY created_at DESC
               LIMIT 20""",
            (f'%{term}%',)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to search watchlist: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
        return ConversationHandler.END

    if not rows:
        await update.message.reply_text(f"No matches for \"{term}\"")
        return ConversationHandler.END

    lines = [f"🔍 *Search: {term}*\n"]
    buttons = []
    for idx, row in enumerate(rows, 1):
        lines.append(_format_entry(row, idx))
        deep_link = _make_deep_link(row[3], row[1])
        if deep_link:
            platform_name = PLATFORMS.get(row[3], (row[3],))[0]
            buttons.append([InlineKeyboardButton(
                f"#{idx} {row[1][:25]} → {platform_name}",
                url=deep_link
            )])

    text = '\n'.join(lines)
    if buttons:
        keyboard = InlineKeyboardMarkup(buttons[:10])
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')

    return ConversationHandler.END


async def _watch_set_status(update: Update, context: ContextTypes.DEFAULT_TYPE, num_str: str, new_status: str) -> int:
    """Set status on a watchlist item by its list position."""
    try:
        num = int(num_str)
    except ValueError:
        await update.message.reply_text("Use the # from `/watch list`")
        return ConversationHandler.END

    try:
        conn = _get_conn()
        cur = conn.cursor()
        # Get ordered list to map position → id
        cur.execute(
            """SELECT id, title, platform FROM watchlist
               WHERE status IN ('want', 'watching')
               ORDER BY
                   CASE status WHEN 'watching' THEN 0 ELSE 1 END,
                   created_at DESC"""
        )
        rows = cur.fetchall()

        if num < 1 or num > len(rows):
            await update.message.reply_text(f"No item #{num}. You have {len(rows)} items.")
            cur.close()
            conn.close()
            return ConversationHandler.END

        target_id, title, platform = rows[num - 1]

        watched_clause = ", watched_at = NOW()" if new_status == 'watched' else ""
        cur.execute(
            f"""UPDATE watchlist
                SET status = %s, updated_at = NOW(){watched_clause}
                WHERE id = %s""",
            (new_status, target_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update watchlist: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
        return ConversationHandler.END

    icons = {'watched': '✅', 'watching': '▶️', 'want': '📋'}
    await update.message.reply_text(f"{icons.get(new_status, '✅')} *{title}* → {new_status}")

    return ConversationHandler.END


async def _watch_drop(update: Update, context: ContextTypes.DEFAULT_TYPE, num_str: str) -> int:
    """Remove a watchlist item by its list position."""
    try:
        num = int(num_str)
    except ValueError:
        await update.message.reply_text("Use the # from `/watch list`")
        return ConversationHandler.END

    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT id, title FROM watchlist
               WHERE status IN ('want', 'watching')
               ORDER BY
                   CASE status WHEN 'watching' THEN 0 ELSE 1 END,
                   created_at DESC"""
        )
        rows = cur.fetchall()

        if num < 1 or num > len(rows):
            await update.message.reply_text(f"No item #{num}. You have {len(rows)} items.")
            cur.close()
            conn.close()
            return ConversationHandler.END

        target_id, title = rows[num - 1]
        cur.execute("DELETE FROM watchlist WHERE id = %s", (target_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to drop watchlist entry: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
        return ConversationHandler.END

    await update.message.reply_text(f"🗑️ Removed *{title}* from watchlist", parse_mode='Markdown')
    return ConversationHandler.END


async def watch_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the add flow."""
    for k in ['watch_title', 'watch_platform', 'watch_media_type']:
        context.user_data.pop(k, None)
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# ── Build ConversationHandler ────────────────────────────────────────────

def build_watch_handler() -> ConversationHandler:
    """Build the /watch ConversationHandler."""
    return ConversationHandler(
        entry_points=[CommandHandler("watch", watch_command)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_received)],
            PLATFORM: [CallbackQueryHandler(platform_callback, pattern=r'^wp_')],
            MEDIA_TYPE: [CallbackQueryHandler(media_type_callback, pattern=r'^wt_')],
            WHO: [CallbackQueryHandler(who_callback, pattern=r'^ww_')],
        },
        fallbacks=[CommandHandler("cancel", watch_cancel)],
        per_message=False,
    )
