#!/usr/bin/env python3
"""
Backlog handler for Mythos Telegram Bot
Shows the development backlog — ordered, phase-tagged, effort-estimated.
Separate from /task which handles personal life tasks.

Commands:
    /backlog          — show open dev items by priority_order
    /backlog all      — include done/dismissed
    /backlog docs     — show documentation backlog
    /backlog done N   — mark item N as done
    /backlog active N — mark item N as active (in progress)
    /backlog open N   — reset item N to open
"""
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


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
    """
    Handle /backlog command
    """
    args = context.args if context.args else []

    if not args:
        await backlog_list(update, context, scope='dev')
        return

    sub = args[0].lower()

    if sub == 'all':
        await backlog_list(update, context, scope='dev', show_all=True)
    elif sub == 'docs':
        await backlog_list(update, context, scope='docs')
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
            "`/backlog` — dev items\n"
            "`/backlog docs` — documentation\n"
            "`/backlog all` — include completed\n"
            "`/backlog done N` — mark done\n"
            "`/backlog active N` — mark active\n"
            "`/backlog open N` — reset to open",
            parse_mode='Markdown'
        )


async def backlog_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       scope: str = 'dev', show_all: bool = False):
    """List backlog items"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Build domain filter
        if scope == 'docs':
            domain_filter = "AND (domain = 'documentation' OR priority_order BETWEEN 100 AND 199)"
            header = "📝 **Documentation Backlog**\n"
        else:
            # Dev items: everything that's NOT a personal task and NOT documentation
            domain_filter = """AND (domain IS DISTINCT FROM 'task' AND idea_type IS DISTINCT FROM 'task')
                              AND (domain IS DISTINCT FROM 'documentation')
                              AND (priority_order IS NULL OR priority_order < 100 OR priority_order >= 200)"""
            header = "🔧 **Development Backlog**\n"

        status_filter = ""
        if not show_all:
            status_filter = "AND status IN ('open', 'active', 'in_progress')"

        query = f"""
            SELECT id, idea, status, priority_order, phase, estimated_effort
            FROM idea_backlog
            WHERE is_archived = false
              {domain_filter}
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
        cur.execute(query)
        items = cur.fetchall()
        cur.close()
        conn.close()

        if not items:
            await update.message.reply_text(f"{header}\nNo items found.")
            return

        lines = [header]

        # Table header
        lines.append("`#  Eff Phase  Status  Item`")
        lines.append("`── ─── ───── ──────  ────────────────────────`")

        for idx, item in enumerate(items, 1):
            s_icon = STATUS_ICON.get(item['status'], '⬜')
            effort = EFFORT_ICON.get(item['estimated_effort'], '·')
            phase = item['phase'] or '·····'
            phase_str = f"{phase:<5}"

            # Truncate idea
            idea = item['idea']
            max_len = 28
            if len(idea) > max_len:
                idea = idea[:max_len - 2] + '…'

            # Priority order display
            pos = item['priority_order']
            pos_str = f"{pos:<3}" if pos else "·  "

            lines.append(f"`{pos_str} {effort:<3} {phase_str}` {s_icon} {idea}")

        lines.append("")
        count_open = sum(1 for i in items if i['status'] in ('open', 'active', 'in_progress'))
        count_done = sum(1 for i in items if i['status'] == 'done')
        lines.append(f"_{count_open} open · {count_done} done_")
        lines.append("_/backlog done N · /backlog active N_")

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

        cur.execute("SELECT idea FROM idea_backlog WHERE id = %s", (item_id,))
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

        icon = STATUS_ICON.get(new_status, '⬜')
        await update.message.reply_text(f"{icon} **{idea}** → {new_status}", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error updating backlog item: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
