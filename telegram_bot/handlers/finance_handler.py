#!/usr/bin/env python3
"""
Mythos Telegram Bot - Finance Handlers
/opt/mythos/telegram_bot/handlers/finance_handler.py

Commands:
    /balance - Show current account balances
    /finance - Show financial summary (balances + this month's activity)
    /spending - Show spending by category
    /report - Show full financial status report (HTML formatted, live from DB)
    /setbalance <ACCT> <amount> - Set current balance for an account (e.g., /setbalance USAA 1431.65)
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

# Load environment
load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)


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


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "-"
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"


def fmt_right(amount, width=10):
    """Format amount as currency string, right-aligned for monospace"""
    if amount is None:
        return " " * (width - 1) + "-"
    return f"${amount:,.2f}".rjust(width)


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command - show current account balances"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get most recent balance for each account
        cur.execute("""
            SELECT DISTINCT ON (a.id)
                a.bank_name,
                a.account_name,
                t.balance,
                t.transaction_date
            FROM accounts a
            LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
            WHERE a.is_active = true
            ORDER BY a.id, t.transaction_date DESC
        """)
        accounts = cur.fetchall()
        
        if not accounts:
            await update.message.reply_text("No accounts found.")
            conn.close()
            return
        
        lines = ["💰 **Account Balances**", ""]
        total = 0
        
        for acct in accounts:
            balance = acct['balance']
            if balance is not None:
                total += float(balance)
                balance_str = format_currency(balance)
                date_str = acct['transaction_date'].strftime('%m/%d') if acct['transaction_date'] else "?"
                lines.append(f"**{acct['bank_name']}** ({acct['account_name']})")
                lines.append(f"  {balance_str}  _{date_str}_")
            else:
                lines.append(f"**{acct['bank_name']}** ({acct['account_name']})")
                lines.append(f"  _No balance data_")
        
        lines.append("")
        lines.append(f"**Total:** {format_currency(total)}")
        
        conn.close()
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Balance command error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def finance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /finance command - comprehensive financial summary"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        lines = ["📊 **Financial Summary**", ""]
        
        # Account balances
        cur.execute("""
            SELECT DISTINCT ON (a.id)
                a.bank_name,
                t.balance,
                t.transaction_date
            FROM accounts a
            LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
            WHERE a.is_active = true
            ORDER BY a.id, t.transaction_date DESC
        """)
        accounts = cur.fetchall()
        
        total_balance = 0
        lines.append("💰 **Balances**")
        for acct in accounts:
            if acct['balance'] is not None:
                total_balance += float(acct['balance'])
                lines.append(f"  {acct['bank_name']}: {format_currency(acct['balance'])}")
        lines.append(f"  **Total: {format_currency(total_balance)}**")
        lines.append("")
        
        # This month's activity
        cur.execute("""
            SELECT 
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses,
                COUNT(*) as count
            FROM transactions
            WHERE DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
        """)
        month = cur.fetchone()
        
        income = float(month['income'] or 0)
        expenses = float(month['expenses'] or 0)
        net = income - expenses
        
        month_name = datetime.now().strftime('%B')
        lines.append(f"📅 **{month_name}**")
        lines.append(f"  Income: {format_currency(income)}")
        lines.append(f"  Expenses: {format_currency(expenses)}")
        net_emoji = "📈" if net >= 0 else "📉"
        lines.append(f"  {net_emoji} Net: {format_currency(net)}")
        lines.append(f"  _({month['count']} transactions)_")
        lines.append("")
        
        # Recent transactions (last 5)
        cur.execute("""
            SELECT 
                transaction_date,
                amount,
                COALESCE(merchant_name, LEFT(description, 25)) as merchant
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            LIMIT 5
        """)
        recent = cur.fetchall()
        
        if recent:
            lines.append("📝 **Recent**")
            for tx in recent:
                date_str = tx['transaction_date'].strftime('%m/%d')
                merchant = tx['merchant'][:20] if tx['merchant'] else '-'
                amount_str = format_currency(tx['amount'])
                lines.append(f"  {date_str} {amount_str} {merchant}")
        
        conn.close()
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Finance command error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def spending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /spending command - show spending by category"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get spending by category for current month
        cur.execute("""
            SELECT 
                COALESCE(category_primary, 'Uncategorized') as category,
                SUM(ABS(amount)) as total,
                COUNT(*) as count
            FROM transactions
            WHERE amount < 0
              AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY category_primary
            ORDER BY total DESC
            LIMIT 10
        """)
        categories = cur.fetchall()
        
        if not categories:
            await update.message.reply_text("No spending data for this month.")
            conn.close()
            return
        
        month_name = datetime.now().strftime('%B')
        lines = [f"📊 **{month_name} Spending**", ""]
        
        total_spending = 0
        for cat in categories:
            total = float(cat['total'])
            total_spending += total
            lines.append(f"**{cat['category']}**")
            lines.append(f"  {format_currency(total)} ({cat['count']} txns)")
        
        lines.append("")
        lines.append(f"**Total: {format_currency(total_spending)}**")
        
        conn.close()
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Spending command error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command - full financial status report (HTML formatted, live from DB)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        today = datetime.now()
        date_str = today.strftime("%B %d, %Y")
        current_day = today.day
        
        # ============================================================
        # 1. GET CURRENT BALANCES
        # ============================================================
        cur.execute("""
            SELECT DISTINCT ON (a.id)
                a.id,
                a.bank_name,
                a.abbreviation,
                COALESCE(t.balance, 0) as balance,
                t.transaction_date
            FROM accounts a
            LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
            WHERE a.is_active = true
            ORDER BY a.id, t.transaction_date DESC
        """)
        accounts = {row['abbreviation']: row for row in cur.fetchall()}
        
        # Calculate totals
        main_checking = Decimal('0')
        if 'SUN' in accounts and accounts['SUN']['balance']:
            main_checking += Decimal(str(accounts['SUN']['balance']))
        if 'USAA' in accounts and accounts['USAA']['balance']:
            main_checking += Decimal(str(accounts['USAA']['balance']))
        
        total_all = sum(Decimal(str(a['balance'] or 0)) for a in accounts.values())
        
        # ============================================================
        # 2. GET BILLS DUE IN NEXT 14 DAYS
        # ============================================================
        cur.execute("""
            SELECT 
                rb.merchant_name,
                rb.expected_amount,
                rb.expected_day,
                a.abbreviation as acct
            FROM recurring_bills rb
            LEFT JOIN accounts a ON rb.account_id = a.id
            WHERE rb.is_active = true
            ORDER BY COALESCE(rb.expected_day, 99)
        """)
        all_bills = cur.fetchall()
        
        # Filter to next 14 days (handle month wrap)
        bills_14_day = []
        bills_total = Decimal('0')
        
        for bill in all_bills:
            day = bill['expected_day']
            if day is None:
                continue  # Skip bills without a set day
            
            # Simple check: is this day within next 14 days?
            if current_day <= day <= current_day + 14:
                bills_14_day.append(bill)
                bills_total += Decimal(str(bill['expected_amount']))
            elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                # Handle month wrap
                bills_14_day.append(bill)
                bills_total += Decimal(str(bill['expected_amount']))
        
        # ============================================================
        # 3. GET INCOME EXPECTED IN NEXT 14 DAYS
        # ============================================================
        cur.execute("""
            SELECT 
                ri.source_name,
                ri.description,
                ri.expected_amount,
                ri.expected_day,
                ri.frequency,
                a.abbreviation as acct
            FROM recurring_income ri
            LEFT JOIN accounts a ON ri.account_id = a.id
            WHERE ri.is_active = true
            ORDER BY COALESCE(ri.expected_day, 99)
        """)
        all_income = cur.fetchall()
        
        # Filter to next 14 days
        income_14_day = []
        income_total = Decimal('0')
        income_to_main = Decimal('0')  # Only USAA + Sunmark
        
        for inc in all_income:
            day = inc['expected_day']
            freq = inc['frequency']
            amount = Decimal(str(inc['expected_amount']))
            acct = inc['acct']
            
            include = False
            
            if freq == 'biweekly':
                # Always include biweekly in 14-day window
                include = True
            elif day is not None:
                if current_day <= day <= current_day + 14:
                    include = True
                elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                    include = True
            
            if include:
                income_14_day.append(inc)
                income_total += amount
                if acct in ('USAA', 'SUN'):
                    income_to_main += amount
        
        # ============================================================
        # 4. CALCULATE PROJECTIONS
        # ============================================================
        projected_main = main_checking + income_to_main - bills_total
        
        # Sidney projection
        sidney_balance = Decimal(str(accounts.get('SID', {}).get('balance') or 0))
        sidney_income = sum(
            Decimal(str(i['expected_amount'])) 
            for i in income_14_day 
            if i['acct'] == 'SID'
        )
        projected_sidney = sidney_balance + sidney_income
        
        # NBT (just show balance, it's an estate account)
        nbt_balance = Decimal(str(accounts.get('NBT', {}).get('balance') or 0))
        
        conn.close()
        
        # ============================================================
        # 5. BUILD HTML REPORT
        # ============================================================
        html = f"""<b>💰 FINANCIAL STATUS</b>
<i>{date_str}</i>

<b>━━━ CURRENT POSITION ━━━</b>
<pre>
"""
        # List all accounts with balances
        for abbr in ['USAA', 'SUN', 'SID', 'DVA', 'NBT']:
            if abbr in accounts:
                acct = accounts[abbr]
                name = acct['bank_name']
                bal = Decimal(str(acct['balance'] or 0))
                html += f"{name:<18} {fmt_right(bal)}\n"
        
        html += f"""───────────────────────────
TOTAL              {fmt_right(total_all)}
</pre>
"""
        # Add note for NBT if it exists
        if 'NBT' in accounts and accounts['NBT']['balance']:
            html += "<i>*NBT estate funds</i>\n"

        html += f"""
<b>━━━ BILLS DUE (14 days) ━━━</b>
<pre>
"""
        if bills_14_day:
            for bill in bills_14_day:
                day = bill['expected_day']
                name = bill['merchant_name'][:16]
                amount = Decimal(str(bill['expected_amount']))
                acct = bill['acct'] or '?'
                warn = " ⚠️" if amount >= 100 else ""
                html += f"{day:<4} {name:<16} {fmt_right(amount)} {acct}{warn}\n"
            html += f"""───────────────────────────
TOTAL OUT          {fmt_right(bills_total)}
</pre>
"""
        else:
            html += "No bills due in next 14 days\n</pre>\n"

        html += f"""
<b>━━━ INCOME EXPECTED (14 days) ━━━</b>
<pre>
"""
        if income_14_day:
            for inc in income_14_day:
                day = inc['expected_day']
                day_str = str(day) if day else "~"
                source = inc['source_name'][:16]
                amount = Decimal(str(inc['expected_amount']))
                acct = inc['acct'] or '?'
                html += f"{day_str:<4} {source:<16} {fmt_right(amount)} {acct}\n"
            html += f"""───────────────────────────
TOTAL IN           {fmt_right(income_total)}
</pre>
"""
        else:
            html += "No income expected in next 14 days\n</pre>\n"

        # Projection section
        target_date = (today + timedelta(days=14)).strftime("%b %d")
        html += f"""
<b>━━━ PROJECTION: {target_date} ━━━</b>
<pre>
USAA + Sunmark now {fmt_right(main_checking)}
+ Income (to these){fmt_right(income_to_main)}
- Bills            {fmt_right(bills_total)}
───────────────────────────
PROJECTED          {fmt_right(projected_main)}
</pre>

<b>Other Accounts:</b>
<pre>
Sidney FCU         {fmt_right(sidney_balance)}
 + expected income {fmt_right(sidney_income)}
 = projected       {fmt_right(projected_sidney)}
"""
        if nbt_balance > 0:
            html += f"""
NBT (estate)       {fmt_right(nbt_balance)}
"""
        html += "</pre>"

        # Add timestamp
        html += f"\n\n<i>Generated: {today.strftime('%Y-%m-%d %H:%M')}</i>"
        
        await update.message.reply_text(html, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Report command error: {e}")
        await update.message.reply_text(f"❌ Error generating report: {e}")


async def setbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setbalance command - set current balance for an account
    
    Usage: /setbalance USAA 1431.65
           /setbalance SUN 976.47
    """
    try:
        # Parse arguments
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /setbalance <ACCT> <amount>\n\n"
                "Examples:\n"
                "  /setbalance USAA 1431.65\n"
                "  /setbalance SUN 976.47\n"
                "  /setbalance SID 2086.00\n\n"
                "Valid accounts: USAA, SUN, SID, DVA, NBT"
            )
            return
        
        acct_abbr = context.args[0].upper()
        
        # Parse amount (handle commas)
        try:
            amount_str = context.args[1].replace(',', '').replace('$', '')
            amount = Decimal(amount_str)
        except:
            await update.message.reply_text(f"❌ Invalid amount: {context.args[1]}")
            return
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Look up account by abbreviation
        cur.execute("""
            SELECT id, bank_name, abbreviation 
            FROM accounts 
            WHERE abbreviation = %s AND is_active = true
        """, (acct_abbr,))
        
        account = cur.fetchone()
        
        if not account:
            # List valid accounts
            cur.execute("SELECT abbreviation, bank_name FROM accounts WHERE is_active = true")
            valid = cur.fetchall()
            valid_list = ", ".join([f"{a['abbreviation']} ({a['bank_name']})" for a in valid])
            await update.message.reply_text(f"❌ Unknown account: {acct_abbr}\n\nValid accounts: {valid_list}")
            conn.close()
            return
        
        account_id = account['id']
        bank_name = account['bank_name']
        
        # Create unique hash for this balance entry
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        hash_id = f"balance-{acct_abbr.lower()}-{date_str}-{today.strftime('%H%M%S')}"
        
        # Insert balance checkpoint transaction
        cur.execute("""
            INSERT INTO transactions (
                account_id, 
                transaction_date, 
                description, 
                amount, 
                balance, 
                category_primary,
                hash_id, 
                imported_by, 
                notes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """, (
            account_id,
            date_str,
            'Balance checkpoint',
            Decimal('0'),  # No actual transaction amount
            amount,        # The verified balance
            'Transfer',    # Neutral category
            hash_id,
            'telegram',
            f'Manual balance set via /setbalance by user'
        ))
        
        new_id = cur.fetchone()['id']
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✓ {bank_name} ({acct_abbr}) balance set to {format_currency(amount)}\n"
            f"  as of {today.strftime('%b %d, %Y %H:%M')}"
        )
        
    except Exception as e:
        logger.error(f"Setbalance command error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# ============================================================
# Additional Finance Report Commands (added by patch 0066)
# ============================================================

# Pagination state stored per user
_user_pagination = {}


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
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
            
            lines.append(f"{month}: {format_currency(expenses)} exp | {format_currency(income)} inc | {trend} {format_currency(net)}")
        
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
            comparisons.append((cat, this_amt, last_amt, diff))
        
        # Sort by this month's spending
        comparisons.sort(key=lambda x: x[1])
        
        for cat, this_amt, last_amt, diff in comparisons:
            icon = get_category_icon(cat)
            
            # Trend arrow (remember: negative spending, so less negative is better)
            if diff < -50:  # Spending less this month (good)
                trend = "↓🟢"
            elif diff > 50:  # Spending more this month (bad)
                trend = "↑🔴"
            else:
                trend = "→"
            
            lines.append(f"{icon} {cat}: {format_currency(this_amt)} vs {format_currency(last_amt)} {trend}")
        
        # Total comparison
        total_diff = this_total - last_total
        if total_diff < 0:
            total_trend = "↓🟢"
        else:
            total_trend = "↑🔴"
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"**Total:** {format_currency(this_total)} vs {format_currency(last_total)} {total_trend}"
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
        _user_pagination[user_id] = {
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
        
        if user_id not in _user_pagination:
            await update.message.reply_text("No active pagination. Run /txn first.")
            return
        
        state = _user_pagination[user_id]
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
        
        if user_id not in _user_pagination:
            await update.message.reply_text("No active pagination. Run /txn first.")
            return
        
        state = _user_pagination[user_id]
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
