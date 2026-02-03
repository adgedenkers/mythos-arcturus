#!/usr/bin/env python3
"""
Task tracking handler for Mythos Telegram Bot
Uses existing idea_backlog table for task storage
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host="localhost",
        database="mythos",
        user="adge"
    )


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /task command
    
    Usage:
        /task add Buy groceries
        /task add -h Fix server issue (high priority)
        /task add -l Organize desk (low priority)  
        /task list
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
            "`/task add -l Someday thing` (low)",
            parse_mode='Markdown'
        )
        return
    
    # Check for priority flags
    priority = "medium"
    task_text_parts = []
    
    for arg in args:
        if arg == "-h" or arg == "--high":
            priority = "high"
        elif arg == "-l" or arg == "--low":
            priority = "low"
        elif arg == "-m" or arg == "--medium":
            priority = "medium"
        else:
            task_text_parts.append(arg)
    
    task_text = " ".join(task_text_parts).strip()
    
    if not task_text:
        await update.message.reply_text("❌ Task text is required")
        return
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO idea_backlog (idea, priority, status, domain, idea_type)
            VALUES (%s, %s, 'open', 'task', 'task')
            RETURNING id
        """, (task_text, priority))
        
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(priority, "🟡")
        
        await update.message.reply_text(
            f"✅ Task added {emoji}\n\n"
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
                SELECT id, idea, priority, status, created_at, completed_at
                FROM idea_backlog
                WHERE domain = 'task' OR idea_type = 'task'
                ORDER BY 
                    CASE status 
                        WHEN 'open' THEN 1 
                        WHEN 'in_progress' THEN 2 
                        ELSE 3 
                    END,
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
                SELECT id, idea, priority, status, created_at
                FROM idea_backlog
                WHERE (domain = 'task' OR idea_type = 'task')
                  AND status IN ('open', 'in_progress')
                  AND is_archived = false
                ORDER BY 
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
                "Add one with `/task add Do the thing`",
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
            if len(idea) > 45:
                idea = idea[:42] + "..."
            
            if show_all:
                lines.append(f"{s_emoji} `{idx}` {p_emoji} {idea}")
            else:
                lines.append(f"`{idx}` {p_emoji} {idea}")
        
        lines.append("")
        lines.append("_/task done N • /task drop N_")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
        # Store task IDs in context for done/drop commands
        context.user_data['task_ids'] = [t['id'] for t in tasks]
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
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
        await update.message.reply_text("❌ Run `/task list` first to see tasks", parse_mode='Markdown')
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
        await update.message.reply_text("❌ Run `/task list` first to see tasks", parse_mode='Markdown')
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
