#!/usr/bin/env python3
"""
Task tracking handler for Mythos Telegram Bot
Uses existing idea_backlog table for task storage
"""

import os
import logging
from datetime import datetime, timedelta
import re
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


def parse_due_date(date_str: str) -> datetime | None:
    """
    Parse flexible due date formats:
    - today, tomorrow, tonight
    - monday, tuesday, wed, thu, fri, sat, sun
    - 2/10, 2/10/26, 02/10/2026
    - 10th, 15th (assumes current/next month)
    """
    date_str = date_str.lower().strip()
    today = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    
    # Relative dates
    if date_str in ('today', 'tonight'):
        return today
    if date_str == 'tomorrow':
        return today + timedelta(days=1)
    
    # Day names
    days = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    
    if date_str in days:
        target_day = days[date_str]
        current_day = today.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:  # Target day is today or in the past, go to next week
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    # Ordinal dates (10th, 15th, 1st, 2nd, 3rd)
    ordinal_match = re.match(r'^(\d{1,2})(st|nd|rd|th)$', date_str)
    if ordinal_match:
        day = int(ordinal_match.group(1))
        result = today.replace(day=day)
        if result <= today:
            # Move to next month
            if today.month == 12:
                result = result.replace(year=today.year + 1, month=1)
            else:
                result = result.replace(month=today.month + 1)
        return result
    
    # Date formats: 2/10, 2/10/26, 02/10/2026
    date_patterns = [
        (r'^(\d{1,2})/(\d{1,2})$', '%m/%d'),  # 2/10
        (r'^(\d{1,2})/(\d{1,2})/(\d{2})$', '%m/%d/%y'),  # 2/10/26
        (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', '%m/%d/%Y'),  # 02/10/2026
    ]
    
    for pattern, fmt in date_patterns:
        if re.match(pattern, date_str):
            try:
                parsed = datetime.strptime(date_str, fmt)
                # If no year provided and date is in past, assume next year
                if fmt == '%m/%d':
                    parsed = parsed.replace(year=today.year)
                    if parsed < today:
                        parsed = parsed.replace(year=today.year + 1)
                return parsed.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
    
    return None


def format_due_date(due_date: datetime) -> str:
    """Format due date for display"""
    if not due_date:
        return ""
    
    today = datetime.now().date()
    due = due_date.date()
    diff = (due - today).days
    
    if diff < 0:
        return f"⚠️ {abs(diff)}d overdue"
    elif diff == 0:
        return "📍 today"
    elif diff == 1:
        return "📍 tomorrow"
    elif diff <= 7:
        return f"📅 {due_date.strftime('%a')}"
    else:
        return f"📅 {due_date.strftime('%-m/%-d')}"


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /task command
    
    Usage:
        /task add Buy groceries
        /task add -h Fix server issue (high priority)
        /task add -l Organize desk (low priority)
        /task add -d tomorrow Buy groceries
        /task add -d friday -h Submit report
        /task list
        /task due (show tasks with due dates)
        /task done 1
        /task drop 1
    """
    args = context.args if context.args else []
    
    if not args:
        await task_list(update, context)
        return
    
    subcommand = args[0].lower()
    
    if subcommand == "add":
        await task_add(update, context, args[1:])
    elif subcommand == "list":
        await task_list(update, context)
    elif subcommand == "due":
        await task_due(update, context)
    elif subcommand == "done":
        if len(args) < 2:
            await update.message.reply_text("Usage: `/task done <number>`", parse_mode='Markdown')
            return
        await task_done(update, context, args[1])
    elif subcommand == "drop":
        if len(args) < 2:
            await update.message.reply_text("Usage: `/task drop <number>`", parse_mode='Markdown')
            return
        await task_drop(update, context, args[1])
    elif subcommand == "all":
        await task_list(update, context, show_all=True)
    else:
        # Assume it's a task to add if no subcommand recognized
        await task_add(update, context, args)


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for /task list"""
    await task_list(update, context)


async def task_add(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list):
    """Add a new task"""
    if not args:
        await update.message.reply_text(
            "📝 **Add a task:**\n"
            "`/task add Buy groceries`\n"
            "`/task add -h Urgent thing` (high)\n"
            "`/task add -l Someday thing` (low)\n"
            "`/task add -d tomorrow Call mom`\n"
            "`/task add -d friday -h Submit report`\n\n"
            "**Due date formats:**\n"
            "today, tomorrow, monday-sunday\n"
            "10th, 15th (day of month)\n"
            "2/10, 2/10/26 (month/day)",
            parse_mode='Markdown'
        )
        return
    
    # Parse flags and task text
    priority = "medium"
    due_date = None
    task_text_parts = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ("-h", "--high"):
            priority = "high"
        elif arg in ("-l", "--low"):
            priority = "low"
        elif arg in ("-m", "--medium"):
            priority = "medium"
        elif arg in ("-d", "--due"):
            # Next arg should be the date
            if i + 1 < len(args):
                i += 1
                parsed = parse_due_date(args[i])
                if parsed:
                    due_date = parsed
                else:
                    # Couldn't parse, treat as task text
                    task_text_parts.append(args[i])
        else:
            task_text_parts.append(arg)
        
        i += 1
    
    task_text = " ".join(task_text_parts).strip()
    
    if not task_text:
        await update.message.reply_text("❌ Task text is required")
        return
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO idea_backlog (idea, priority, status, domain, idea_type, next_review)
            VALUES (%s, %s, 'open', 'task', 'task', %s)
            RETURNING id
        """, (task_text, priority, due_date))
        
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(priority, "🟡")
        
        due_str = ""
        if due_date:
            due_str = f"\n{format_due_date(due_date)}"
        
        await update.message.reply_text(
            f"✅ Task added {emoji}{due_str}\n\n"
            f"**{task_text}**",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def task_list(update: Update, context: ContextTypes.DEFAULT_TYPE, show_all: bool = False):
    """List open tasks"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if show_all:
            cur.execute("""
                SELECT id, idea, priority, status, created_at, completed_at, next_review
                FROM idea_backlog
                WHERE domain = 'task' OR idea_type = 'task'
                ORDER BY 
                    CASE status 
                        WHEN 'open' THEN 1 
                        WHEN 'in_progress' THEN 2 
                        ELSE 3 
                    END,
                    CASE WHEN next_review IS NOT NULL THEN 0 ELSE 1 END,
                    next_review ASC NULLS LAST,
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    created_at DESC
                LIMIT 50
            """)
        else:
            cur.execute("""
                SELECT id, idea, priority, status, created_at, next_review
                FROM idea_backlog
                WHERE (domain = 'task' OR idea_type = 'task')
                  AND status IN ('open', 'in_progress')
                  AND is_archived = false
                ORDER BY 
                    CASE WHEN next_review IS NOT NULL AND next_review < NOW() THEN 0 ELSE 1 END,
                    CASE WHEN next_review IS NOT NULL THEN 0 ELSE 1 END,
                    next_review ASC NULLS LAST,
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    created_at ASC
            """)
        
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        
        if not tasks:
            await update.message.reply_text(
                "📋 **No open tasks**\n\n"
                "Add one with `/task add Do the thing`\n"
                "Or with a due date: `/task add -d friday Do it`",
                parse_mode='Markdown'
            )
            return
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_emoji = {"open": "⬜", "in_progress": "🔄", "done": "✅", "dismissed": "❌"}
        
        lines = ["📋 **Tasks**\n"]
        
        for idx, task in enumerate(tasks, 1):
            p_emoji = priority_emoji.get(task['priority'], "🟡")
            s_emoji = status_emoji.get(task['status'], "⬜")
            
            # Truncate long tasks
            idea = task['idea']
            max_len = 35 if task.get('next_review') else 45
            if len(idea) > max_len:
                idea = idea[:max_len-3] + "..."
            
            # Due date
            due_str = ""
            if task.get('next_review'):
                due_str = f" {format_due_date(task['next_review'])}"
            
            if show_all:
                lines.append(f"{s_emoji} `{idx}` {p_emoji} {idea}{due_str}")
            else:
                lines.append(f"`{idx}` {p_emoji} {idea}{due_str}")
        
        lines.append("")
        lines.append("_/task done N • /task drop N_")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
        # Store task IDs in context for done/drop commands
        context.user_data['task_ids'] = [t['id'] for t in tasks]
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def task_due(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tasks with due dates, sorted by due date"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, idea, priority, status, next_review
            FROM idea_backlog
            WHERE (domain = 'task' OR idea_type = 'task')
              AND status IN ('open', 'in_progress')
              AND is_archived = false
              AND next_review IS NOT NULL
            ORDER BY 
                next_review ASC
        """)
        
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        
        if not tasks:
            await update.message.reply_text(
                "📅 **No tasks with due dates**\n\n"
                "Add one with `/task add -d friday Do the thing`",
                parse_mode='Markdown'
            )
            return
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        
        lines = ["📅 **Upcoming**\n"]
        
        for idx, task in enumerate(tasks, 1):
            p_emoji = priority_emoji.get(task['priority'], "🟡")
            
            idea = task['idea']
            if len(idea) > 30:
                idea = idea[:27] + "..."
            
            due_str = format_due_date(task['next_review'])
            
            lines.append(f"`{idx}` {p_emoji} {idea} {due_str}")
        
        lines.append("")
        lines.append("_/task done N • /task drop N_")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
        # Store task IDs in context for done/drop commands
        context.user_data['task_ids'] = [t['id'] for t in tasks]
        
    except Exception as e:
        logger.error(f"Error listing due tasks: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def task_done(update: Update, context: ContextTypes.DEFAULT_TYPE, task_num: str):
    """Mark a task as done"""
    try:
        num = int(task_num)
    except ValueError:
        await update.message.reply_text("❌ Please provide a task number")
        return
    
    task_ids = context.user_data.get('task_ids', [])
    
    if not task_ids:
        await update.message.reply_text("❌ Run `/tasks` first to see tasks", parse_mode='Markdown')
        return
    
    if num < 1 or num > len(task_ids):
        await update.message.reply_text(f"❌ Invalid task number. Choose 1-{len(task_ids)}")
        return
    
    task_id = task_ids[num - 1]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get task text first
        cur.execute("SELECT idea FROM idea_backlog WHERE id = %s", (task_id,))
        task = cur.fetchone()
        
        if not task:
            await update.message.reply_text("❌ Task not found")
            cur.close()
            conn.close()
            return
        
        # Mark as done
        cur.execute("""
            UPDATE idea_backlog
            SET status = 'done', completed_at = NOW(), last_updated = NOW()
            WHERE id = %s
        """, (task_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        idea = task['idea']
        if len(idea) > 50:
            idea = idea[:47] + "..."
        
        await update.message.reply_text(f"✅ Done: **{idea}**", parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def task_drop(update: Update, context: ContextTypes.DEFAULT_TYPE, task_num: str):
    """Drop/dismiss a task"""
    try:
        num = int(task_num)
    except ValueError:
        await update.message.reply_text("❌ Please provide a task number")
        return
    
    task_ids = context.user_data.get('task_ids', [])
    
    if not task_ids:
        await update.message.reply_text("❌ Run `/tasks` first to see tasks", parse_mode='Markdown')
        return
    
    if num < 1 or num > len(task_ids):
        await update.message.reply_text(f"❌ Invalid task number. Choose 1-{len(task_ids)}")
        return
    
    task_id = task_ids[num - 1]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get task text first
        cur.execute("SELECT idea FROM idea_backlog WHERE id = %s", (task_id,))
        task = cur.fetchone()
        
        if not task:
            await update.message.reply_text("❌ Task not found")
            cur.close()
            conn.close()
            return
        
        # Mark as dismissed
        cur.execute("""
            UPDATE idea_backlog
            SET status = 'dismissed', dismissed_at = NOW(), last_updated = NOW()
            WHERE id = %s
        """, (task_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        idea = task['idea']
        if len(idea) > 50:
            idea = idea[:47] + "..."
        
        await update.message.reply_text(f"🗑️ Dropped: ~~{idea}~~", parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error dropping task: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
