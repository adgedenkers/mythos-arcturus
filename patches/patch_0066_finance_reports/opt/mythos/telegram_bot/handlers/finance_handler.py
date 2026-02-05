"""
Finance Reporting Commands for Mythos Telegram Bot
/opt/mythos/telegram_bot/handlers/finance_handler.py

Commands:
- /spend [month] - Spending breakdown by category
- /monthly - Month-by-month spending trend
- /compare - This month vs last month
- /top [n] - Top merchants by spending
- /txn [category] - List transactions (paginated)
- /next, /back - Pagination controls
"""

import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from telegram import Update
from telegram.ext import ContextTypes

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# Pagination state stored per user
user_pagination = {}


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def format_currency(amount) -> str:
    """Format amount as currency"""
    if amount is None:
        return "$0.00"
    amt = Decimal(str(amount))
    if amt >= 0:
        return f"${amt:,.2f}"
    else:
        return f"-${abs(amt):,.2f}"


def get_category_icon(category: str) -> str:
    """Get emoji icon for category"""
    icons = {
        'Income': '💰',
        'Salary': '💵',
        'Shopping': '🛍️',
        'Groceries': '🛒',
        'Dining': '🍽️',
        'Gas': '⛽',
        'Utilities': '💡',
        'Entertainment': '🎬',
        'Healthcare': '🏥',
        'Transport': '🚗',
        'Transfer': '↔️',
        'Credit Card': '💳',
        'ATM/Cash': '🏧',
    }
    return icons.get(category, '📌')


async def spend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /spend [month] - Show spending breakdown by category
    Examples: /spend, /spend jan, /spend 2025-12
    """
    try:
        # Parse month argument
        now = datetime.now()
        target_month = now.month
        target_year = now.year
        month_name = now.strftime('%B %Y')
        
        if context.args:
            arg = context.args[0].lower()
            # Try parsing as month name
            months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                     'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
            if arg in months:
                target_month = months[arg]
                # If month is in future, assume last year
                if target_month > now.month:
                    target_year = now.year - 1
            # Try parsing as YYYY-MM
            elif '-' in arg:
                try:
                    parts = arg.split('-')
                    target_year = int(parts[0])
                    target_month = int(parts[1])
                except:
                    pass
            month_name = datetime(target_year, target_month, 1).strftime('%B %Y')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get spending by category for the month (excluding transfers/credit card)
        cur.execute("""
            SELECT 
                category_primary,
                COUNT(*) as cnt,
                SUM(amount) as total
            FROM transactions
            WHERE EXTRACT(MONTH FROM transaction_date) = %s
              AND EXTRACT(YEAR FROM transaction_date) = %s
              AND category_primary NOT IN ('Transfer', 'Credit Card', 'ATM/Cash')
              AND amount < 0
            GROUP BY category_primary
            ORDER BY total
        """, (target_month, target_year))
        
        expenses = cur.fetchall()
        
        # Get income for the month
        cur.execute("""
            SELECT SUM(amount) as total
            FROM transactions
            WHERE EXTRACT(MONTH FROM transaction_date) = %s
              AND EXTRACT(YEAR FROM transaction_date) = %s
              AND category_primary IN ('Income', 'Salary')
        """, (target_month, target_year))
        
        income_row = cur.fetchone()
        income_total = Decimal(str(income_row['total'] or 0))
        
        conn.close()
        
        # Build message
        lines = [
            f"📊 **Spending: {month_name}**",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        expense_total = Decimal('0')
        for row in expenses:
            cat = row['category_primary']
            total = Decimal(str(row['total']))
            expense_total += total
            icon = get_category_icon(cat)
            lines.append(f"{icon} {cat}: {format_currency(total)}")
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"💸 **Expenses:** {format_currency(expense_total)}",
            f"💰 **Income:** {format_currency(income_total)}",
            f"📈 **Net:** {format_currency(income_total + expense_total)}"
        ])
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in spend_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def monthly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /monthly - Show month-by-month spending trend
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get monthly totals for last 6 months
        cur.execute("""
            SELECT 
                TO_CHAR(transaction_date, 'YYYY-MM') as month,
                TO_CHAR(transaction_date, 'Mon') as month_name,
                SUM(CASE WHEN amount < 0 AND category_primary NOT IN ('Transfer', 'Credit Card', 'ATM/Cash') 
                    THEN amount ELSE 0 END) as expenses,
                SUM(CASE WHEN category_primary IN ('Income', 'Salary') 
                    THEN amount ELSE 0 END) as income
            FROM transactions
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(transaction_date, 'YYYY-MM'), TO_CHAR(transaction_date, 'Mon')
            ORDER BY month DESC
        """)
        
        months = cur.fetchall()
        conn.close()
        
        lines = [
            "📅 **Monthly Trend**",
            "━━━━━━━━━━━━━━━━━━━━",
            "Month   | Expenses  | Income    | Net"
        ]
        
        for row in months:
            month = row['month_name']
            expenses = Decimal(str(row['expenses'] or 0))
            income = Decimal(str(row['income'] or 0))
            net = income + expenses
            
            # Trend indicator
            if net > 0:
                trend = "🟢"
            elif net > -500:
                trend = "🟡"
            else:
                trend = "🔴"
            
            lines.append(f"{month}  | {format_currency(expenses):>9} | {format_currency(income):>9} | {trend} {format_currency(net)}")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in monthly_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /compare - Compare this month vs last month
    """
    try:
        now = datetime.now()
        this_month = now.month
        this_year = now.year
        
        if this_month == 1:
            last_month = 12
            last_year = this_year - 1
        else:
            last_month = this_month - 1
            last_year = this_year
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get this month's spending by category
        cur.execute("""
            SELECT 
                category_primary,
                SUM(amount) as total
            FROM transactions
            WHERE EXTRACT(MONTH FROM transaction_date) = %s
              AND EXTRACT(YEAR FROM transaction_date) = %s
              AND category_primary NOT IN ('Transfer', 'Credit Card', 'ATM/Cash')
              AND amount < 0
            GROUP BY category_primary
        """, (this_month, this_year))
        this_data = {row['category_primary']: Decimal(str(row['total'])) for row in cur.fetchall()}
        
        # Get last month's spending by category
        cur.execute("""
            SELECT 
                category_primary,
                SUM(amount) as total
            FROM transactions
            WHERE EXTRACT(MONTH FROM transaction_date) = %s
              AND EXTRACT(YEAR FROM transaction_date) = %s
              AND category_primary NOT IN ('Transfer', 'Credit Card', 'ATM/Cash')
              AND amount < 0
            GROUP BY category_primary
        """, (last_month, last_year))
        last_data = {row['category_primary']: Decimal(str(row['total'])) for row in cur.fetchall()}
        
        conn.close()
        
        # Combine categories
        all_cats = set(this_data.keys()) | set(last_data.keys())
        
        this_month_name = datetime(this_year, this_month, 1).strftime('%b')
        last_month_name = datetime(last_year, last_month, 1).strftime('%b')
        
        lines = [
            f"📊 **{this_month_name} vs {last_month_name}**",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        this_total = Decimal('0')
        last_total = Decimal('0')
        
        comparisons = []
        for cat in all_cats:
            this_amt = this_data.get(cat, Decimal('0'))
            last_amt = last_data.get(cat, Decimal('0'))
            this_total += this_amt
            last_total += last_amt
            
            diff = this_amt - last_amt
            if last_amt != 0:
                pct = (diff / abs(last_amt)) * 100
            else:
                pct = 0
            
            comparisons.append((cat, this_amt, last_amt, diff, pct))
        
        # Sort by this month's spending
        comparisons.sort(key=lambda x: x[1])
        
        for cat, this_amt, last_amt, diff, pct in comparisons:
            icon = get_category_icon(cat)
            
            # Trend arrow (remember: negative spending, so "up" is worse)
            if diff < -50:  # Spending less this month (good)
                trend = "↓🟢"
            elif diff > 50:  # Spending more this month (bad)
                trend = "↑🔴"
            else:
                trend = "→"
            
            lines.append(f"{icon} {cat}")
            lines.append(f"   {this_month_name}: {format_currency(this_amt)} | {last_month_name}: {format_currency(last_amt)} {trend}")
        
        # Total comparison
        total_diff = this_total - last_total
        if total_diff < 0:
            total_trend = "↓🟢 Less"
        else:
            total_trend = "↑🔴 More"
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"**Total:** {format_currency(this_total)} vs {format_currency(last_total)}",
            f"**Diff:** {format_currency(total_diff)} {total_trend}"
        ])
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in compare_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /top [n] - Show top merchants by spending
    """
    try:
        limit = 15
        if context.args:
            try:
                limit = int(context.args[0])
                limit = min(max(limit, 5), 30)  # Clamp between 5 and 30
            except:
                pass
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                description,
                COUNT(*) as cnt,
                SUM(amount) as total
            FROM transactions
            WHERE amount < 0
              AND category_primary NOT IN ('Transfer', 'Credit Card', 'ATM/Cash')
            GROUP BY description
            ORDER BY total
            LIMIT %s
        """, (limit,))
        
        merchants = cur.fetchall()
        conn.close()
        
        lines = [
            f"🏪 **Top {limit} Merchants**",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for i, row in enumerate(merchants, 1):
            desc = row['description'][:25]
            total = format_currency(row['total'])
            cnt = row['cnt']
            lines.append(f"{i}. {desc}")
            lines.append(f"   {total} ({cnt}x)")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in top_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def txn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /txn [category] - List transactions (paginated)
    """
    try:
        user_id = update.effective_user.id
        page_size = 10
        
        # Determine category filter
        category = None
        if context.args:
            category = ' '.join(context.args).title()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Build query
        if category:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                WHERE category_primary ILIKE %s
                ORDER BY transaction_date DESC
                LIMIT %s
            """, (f'%{category}%', page_size + 1))  # +1 to check if more exist
        else:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                ORDER BY transaction_date DESC
                LIMIT %s
            """, (page_size + 1,))
        
        rows = cur.fetchall()
        
        # Count total
        if category:
            cur.execute("SELECT COUNT(*) FROM transactions WHERE category_primary ILIKE %s", (f'%{category}%',))
        else:
            cur.execute("SELECT COUNT(*) FROM transactions")
        total_count = cur.fetchone()['count']
        
        conn.close()
        
        has_more = len(rows) > page_size
        rows = rows[:page_size]
        
        # Store pagination state
        user_pagination[user_id] = {
            'type': 'txn',
            'category': category,
            'offset': 0,
            'page_size': page_size,
            'total': total_count
        }
        
        # Build message
        filter_text = f" ({category})" if category else ""
        lines = [
            f"📋 **Transactions{filter_text}**",
            f"Showing 1-{len(rows)} of {total_count}",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for row in rows:
            date = row['transaction_date'].strftime('%m/%d')
            desc = row['description'][:30]
            amt = format_currency(row['amount'])
            lines.append(f"`{date}` {desc}")
            lines.append(f"       {amt}")
        
        if has_more:
            lines.append("")
            lines.append("Type /next for more")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in txn_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /next - Show next page of results
    """
    try:
        user_id = update.effective_user.id
        
        if user_id not in user_pagination:
            await update.message.reply_text("No active pagination. Run /txn first.")
            return
        
        state = user_pagination[user_id]
        state['offset'] += state['page_size']
        
        if state['offset'] >= state['total']:
            await update.message.reply_text("No more results.")
            state['offset'] -= state['page_size']
            return
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        category = state['category']
        offset = state['offset']
        page_size = state['page_size']
        
        if category:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                WHERE category_primary ILIKE %s
                ORDER BY transaction_date DESC
                LIMIT %s OFFSET %s
            """, (f'%{category}%', page_size + 1, offset))
        else:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                ORDER BY transaction_date DESC
                LIMIT %s OFFSET %s
            """, (page_size + 1, offset))
        
        rows = cur.fetchall()
        conn.close()
        
        has_more = len(rows) > page_size
        rows = rows[:page_size]
        
        start = offset + 1
        end = offset + len(rows)
        
        filter_text = f" ({category})" if category else ""
        lines = [
            f"📋 **Transactions{filter_text}**",
            f"Showing {start}-{end} of {state['total']}",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for row in rows:
            date = row['transaction_date'].strftime('%m/%d')
            desc = row['description'][:30]
            amt = format_currency(row['amount'])
            lines.append(f"`{date}` {desc}")
            lines.append(f"       {amt}")
        
        nav = []
        if offset > 0:
            nav.append("/back")
        if has_more:
            nav.append("/next")
        
        if nav:
            lines.append("")
            lines.append(" | ".join(nav))
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in next_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /back - Show previous page of results
    """
    try:
        user_id = update.effective_user.id
        
        if user_id not in user_pagination:
            await update.message.reply_text("No active pagination. Run /txn first.")
            return
        
        state = user_pagination[user_id]
        state['offset'] = max(0, state['offset'] - state['page_size'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        category = state['category']
        offset = state['offset']
        page_size = state['page_size']
        
        if category:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                WHERE category_primary ILIKE %s
                ORDER BY transaction_date DESC
                LIMIT %s OFFSET %s
            """, (f'%{category}%', page_size + 1, offset))
        else:
            cur.execute("""
                SELECT id, transaction_date, description, amount, category_primary
                FROM transactions
                ORDER BY transaction_date DESC
                LIMIT %s OFFSET %s
            """, (page_size + 1, offset))
        
        rows = cur.fetchall()
        conn.close()
        
        has_more = len(rows) > page_size
        rows = rows[:page_size]
        
        start = offset + 1
        end = offset + len(rows)
        
        filter_text = f" ({category})" if category else ""
        lines = [
            f"📋 **Transactions{filter_text}**",
            f"Showing {start}-{end} of {state['total']}",
            "━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for row in rows:
            date = row['transaction_date'].strftime('%m/%d')
            desc = row['description'][:30]
            amt = format_currency(row['amount'])
            lines.append(f"`{date}` {desc}")
            lines.append(f"       {amt}")
        
        nav = []
        if offset > 0:
            nav.append("/back")
        if has_more:
            nav.append("/next")
        
        if nav:
            lines.append("")
            lines.append(" | ".join(nav))
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in back_command: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


def register_handlers(app):
    """Register all finance handlers with the application"""
    from telegram.ext import CommandHandler
    
    app.add_handler(CommandHandler("spend", spend_command))
    app.add_handler(CommandHandler("monthly", monthly_command))
    app.add_handler(CommandHandler("compare", compare_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("txn", txn_command))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(CommandHandler("back", back_command))
    
    logger.info("Finance handlers registered: /spend, /monthly, /compare, /top, /txn, /next, /back")
