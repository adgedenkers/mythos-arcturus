#!/usr/bin/env python3
"""
Backlog handler for Mythos Telegram Bot
Shows the development backlog — ordered, stream-tagged, phase-tagged, effort-estimated.
Separate from /task which handles personal life tasks.

Commands:
    /backlog              — show all open dev items by priority_order
    /backlog NEU          — filter by stream (NEU, LOG, MNE, SEN, SYS)
    /backlog all          — include done/dismissed
    /backlog docs         — show documentation backlog
    /backlog done N       — mark item N as done
    /backlog active N     — mark item N as active (in progress)
    /backlog open N       — reset item N to open
"""
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

VALID_STREAMS = {'NEU', 'LOG', 'MNE', 'SEN', 'SYS'}

STREAM_NAMES = {
    'NEU': 'NEURO',
    'LOG': 'LOGOS',
    'MNE': 'MNEMOS',
    'SEN': 'SENSUS',
    'SYS': 'SYSTEM',
}

STREAM_EMOJI = {
    'NEU': '🧠',
    'LOG': '📚',
    'MNE': '💾',
    'SEN': '🌐',
    'SYS': '⚙️',
}


def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432')
    )


EFFORT_ICON = {
    'small': 'S',
    'medium': 'M',
    'large': 'L',
}

STATUS_ICON = {
    'open': '⬜',
    'active': '🔄',
    'in_progress': '🔄',
    'done': '✅',
    'dismissed': '❌',
}


async def backlog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /backlog command"""
    args = context.args if context.args else []

    if not args:
        await backlog_list(update, context, scope='dev')
        return

    sub = args[0].upper()

    # Check if it's a stream filter
    if sub in VALID_STREAMS:
        await backlog_list(update, context, scope='dev', stream_filter=sub)
        return

    sub = sub.lower()

    if sub == 'all':
        await backlog_list(update, context, scope='dev', show_all=True)
    elif sub == 'docs':
        await backlog_list(update, context, scope='docs')
    elif sub == 'streams':
        await backlog_stream_summary(update, context)
    elif sub == 'done':
        if len(args) < 2:
            await update.message.reply_text("Usage: `/backlog done <number>`", parse_mode='Markdown')
            return
        await backlog_set_status(update, context, args[1], 'done')
    elif sub == 'active':
        if len(args) < 2:
            await update.message.reply_text("Usage: `/backlog active <number>`", parse_mode='Markdown')
            return
        await backlog_set_status(update, context, args[1], 'active')
    elif sub == 'open':
        if len(args) < 2:
            await update.message.reply_text("Usage: `/backlog open <number>`", parse_mode='Markdown')
            return
        await backlog_set_status(update, context, args[1], 'open')
    else:
        await update.message.reply_text(
            "📋 **Backlog commands:**\n"
            "`/backlog` — all dev items\n"
            "`/backlog NEU` — filter by stream\n"
            "`/backlog streams` — stream summary\n"
            "`/backlog docs` — documentation\n"
            "`/backlog all` — include completed\n"
            "`/backlog done N` — mark done\n"
            "`/backlog active N` — mark active\n"
            "`/backlog open N` — reset to open\n\n"
            "**Streams:** NEU LOG MNE SEN SYS",
            parse_mode='Markdown'
        )


async def backlog_stream_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show count of open items per stream"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                stream,
                COUNT(*) FILTER (WHERE status IN ('open', 'active', 'in_progress')) as open_count,
                COUNT(*) FILTER (WHERE status = 'active') as active_count,
                COUNT(*) FILTER (WHERE status = 'done') as done_count
            FROM idea_backlog
            WHERE is_archived = false
              AND stream IS NOT NULL
              AND domain IS DISTINCT FROM 'task'
              AND domain IS DISTINCT FROM 'documentation'
            GROUP BY stream
            ORDER BY
                CASE stream
                    WHEN 'NEU' THEN 1
                    WHEN 'LOG' THEN 2
                    WHEN 'MNE' THEN 3
                    WHEN 'SEN' THEN 4
                    WHEN 'SYS' THEN 5
                END
        """)
        rows = cur.fetchall()

        # Also count untagged
        cur.execute("""
            SELECT COUNT(*) as cnt
            FROM idea_backlog
            WHERE is_archived = false
              AND stream IS NULL
              AND status IN ('open', 'active', 'in_progress')
              AND domain IS DISTINCT FROM 'task'
              AND domain IS DISTINCT FROM 'documentation'
        """)
        untagged = cur.fetchone()['cnt']

        cur.close()
        conn.close()

        lines = ["📊 **Backlog by Stream**\n"]
        total_open = 0
        total_active = 0

        for row in rows:
            s = row['stream'] or '???'
            emoji = STREAM_EMOJI.get(s, '·')
            name = STREAM_NAMES.get(s, s)
            active_str = f" ({row['active_count']} active)" if row['active_count'] else ""
            lines.append(f"{emoji} **{s}** {name}: {row['open_count']} open{active_str} · {row['done_count']} done")
            total_open += row['open_count']
            total_active += row['active_count']

        if untagged:
            lines.append(f"❓ **???** Untagged: {untagged} open")
            total_open += untagged

        lines.append(f"\n_{total_open} total open · {total_active} active_")
        lines.append("_/backlog NEU · /backlog SYS · etc._")

        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in stream summary: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def backlog_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       scope: str = 'dev', show_all: bool = False,
                       stream_filter: str = None):
    """List backlog items"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        params = []

        # Build domain filter
        if scope == 'docs':
            domain_filter = "AND (domain = 'documentation' OR priority_order BETWEEN 100 AND 199)"
            header_emoji = "📝"
            header_text = "Documentation Backlog"
        else:
            domain_filter = """AND (domain IS DISTINCT FROM 'task' AND idea_type IS DISTINCT FROM 'task')
                              AND (domain IS DISTINCT FROM 'documentation')
                              AND (priority_order IS NULL OR priority_order < 100 OR priority_order >= 200)"""
            header_emoji = "🔧"
            header_text = "Development Backlog"

        # Stream filter
        stream_clause = ""
        if stream_filter:
            stream_clause = "AND stream = %s"
            params.append(stream_filter)
            emoji = STREAM_EMOJI.get(stream_filter, '🔧')
            name = STREAM_NAMES.get(stream_filter, stream_filter)
            header_emoji = emoji
            header_text = f"{stream_filter} · {name} Backlog"

        status_filter = ""
        if not show_all:
            status_filter = "AND status IN ('open', 'active', 'in_progress')"

        query = f"""
            SELECT id, idea, status, priority_order, phase, estimated_effort, stream
            FROM idea_backlog
            WHERE is_archived = false
              {domain_filter}
              {stream_clause}
              {status_filter}
            ORDER BY
                CASE status
                    WHEN 'active' THEN 0
                    WHEN 'in_progress' THEN 0
                    WHEN 'open' THEN 1
                    WHEN 'done' THEN 2
                    WHEN 'dismissed' THEN 3
                END,
                priority_order ASC NULLS LAST,
                created_at ASC
            LIMIT 40
        """
        cur.execute(query, params)
        items = cur.fetchall()
        cur.close()
        conn.close()

        if not items:
            await update.message.reply_text(f"{header_emoji} **{header_text}**\n\nNo items found.")
            return

        lines = [f"{header_emoji} **{header_text}**\n"]

        # Show stream column only when NOT filtered to a single stream
        show_stream_col = stream_filter is None and scope != 'docs'

        if show_stream_col:
            lines.append("`#  Str Eff Phase  Item`")
            lines.append("`── ─── ─── ───── ────────────────────────`")
        else:
            lines.append("`#  Eff Phase  Status  Item`")
            lines.append("`── ─── ───── ──────  ────────────────────────`")

        for idx, item in enumerate(items, 1):
            s_icon = STATUS_ICON.get(item['status'], '⬜')
            effort = EFFORT_ICON.get(item['estimated_effort'], '·')
            phase = item['phase'] or '·····'
            phase_str = f"{phase:<5}"
            stream = item['stream'] or '···'

            # Truncate idea
            idea = item['idea']
            if show_stream_col:
                max_len = 26
            else:
                max_len = 28
            if len(idea) > max_len:
                idea = idea[:max_len - 1] + '…'

            # Priority order display
            pos = item['priority_order']
            pos_str = f"{pos:<3}" if pos else "·  "

            if show_stream_col:
                lines.append(f"`{pos_str} {stream} {effort:<3} {phase_str}` {s_icon} {idea}")
            else:
                lines.append(f"`{pos_str} {effort:<3} {phase_str}` {s_icon} {idea}")

        lines.append("")
        count_open = sum(1 for i in items if i['status'] in ('open', 'active', 'in_progress'))
        count_done = sum(1 for i in items if i['status'] == 'done')
        lines.append(f"_{count_open} open · {count_done} done_")

        if stream_filter:
            lines.append("_/backlog done N · /backlog active N_")
        else:
            lines.append("_/backlog NEU · /backlog streams · /backlog done N_")

        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

        # Store IDs for status commands
        context.user_data['backlog_ids'] = [i['id'] for i in items]

    except Exception as e:
        logger.error(f"Error listing backlog: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def backlog_set_status(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             item_num: str, new_status: str):
    """Change status of a backlog item"""
    try:
        num = int(item_num)
    except ValueError:
        await update.message.reply_text("❌ Please provide an item number")
        return

    backlog_ids = context.user_data.get('backlog_ids', [])

    if not backlog_ids:
        await update.message.reply_text("❌ Run `/backlog` first to see items", parse_mode='Markdown')
        return

    if num < 1 or num > len(backlog_ids):
        await update.message.reply_text(f"❌ Invalid number. Choose 1-{len(backlog_ids)}")
        return

    item_id = backlog_ids[num - 1]

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT idea, stream FROM idea_backlog WHERE id = %s", (item_id,))
        item = cur.fetchone()

        if not item:
            await update.message.reply_text("❌ Item not found")
            cur.close()
            conn.close()
            return

        # Build update
        updates = ["status = %s", "last_updated = NOW()"]
        params = [new_status]

        if new_status == 'done':
            updates.append("completed_at = NOW()")
        elif new_status == 'active':
            updates.append("started_at = NOW()")
        elif new_status == 'open':
            updates.append("completed_at = NULL")
            updates.append("started_at = NULL")

        cur.execute(
            f"UPDATE idea_backlog SET {', '.join(updates)} WHERE id = %s",
            params + [item_id]
        )
        conn.commit()
        cur.close()
        conn.close()

        idea = item['idea']
        if len(idea) > 50:
            idea = idea[:47] + '…'

        stream_tag = f"[{item['stream']}] " if item.get('stream') else ""
        icon = STATUS_ICON.get(new_status, '⬜')
        await update.message.reply_text(f"{icon} {stream_tag}**{idea}** → {new_status}", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error updating backlog item: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
