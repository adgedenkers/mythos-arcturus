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
