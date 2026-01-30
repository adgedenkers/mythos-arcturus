#!/usr/bin/env python3
"""
Mythos Telegram Bot - Finance Handlers
/opt/mythos/telegram_bot/handlers/finance_handler.py

Commands:
    /balance - Show current account balances
    /finance - Show financial summary (balances + this month's activity)
    /spending - Show spending by category
    /report - Show full financial status report (HTML formatted)
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
    """Handle /report command - full financial status report (HTML formatted)"""
    try:
        today = datetime.now()
        date_str = today.strftime("%B %d, %Y")
        
        # ============================================================
        # MANUAL CONFIGURATION - Update these values as needed
        # To update: edit this file directly or build a config system
        # ============================================================
        
        # Account balances (update regularly)
        balances = {
            'usaa': Decimal('1431.65'),
            'sunmark': Decimal('976.47'),
            'sidney': Decimal('2086.00'),
            'nbt': Decimal('7000.00'),  # Estate funds - remove when depleted
        }
        
        # NBT availability date (remove this section when no longer applicable)
        nbt_note = "*available Feb 5"
        show_nbt = True  # Set to False when NBT funds are gone
        
        # Known recurring income
        income = {
            'rebecca_disability': Decimal('2086.00'),   # ~3rd, to Sidney
            'dfas_adv': Decimal('352.00'),              # bi-weekly, to Adv FCU
            'dfas_usaa': Decimal('500.00'),             # bi-weekly, to USAA
            'dfas_sunmark': Decimal('1400.00'),         # bi-weekly, to Sunmark
            'ss_rebecca': Decimal('3097.00'),           # ~16th, to USAA
            'ss_fitz': Decimal('1650.00'),              # ~15th, to Sunmark
        }
        
        # Known bills for next 14 days (update each week)
        # Format: (date_str, name, amount)
        bills_14_day = [
            ('Feb 3-5', 'YouTube Premium', Decimal('22.99')),
            ('Feb 6', 'OpenAI', Decimal('64.80')),
            ('Feb 9', 'Progressive', Decimal('272.00')),
            ('Feb 12', 'Claude AI', Decimal('21.60')),
            ('Feb 13', 'USAA Loan', Decimal('1088.00')),
            ('Feb 14', 'AT&T', Decimal('257.00')),
            ('Feb 15', 'Starlink', Decimal('120.00')),
            ('Feb 15', 'Google One', Decimal('21.59')),
            ('Feb 16', 'Walmart+', Decimal('13.99')),
        ]
        
        # Action items (update as needed)
        action_items = [
            "Credit card balances — unknown",
            "OneMain loan amount — unknown",
            "Category cleanup needed",
        ]
        
        # ============================================================
        # END MANUAL CONFIGURATION
        # ============================================================
        
        # Calculate totals
        bills_total = sum(b[2] for b in bills_14_day)
        main_checking = balances['usaa'] + balances['sunmark']
        income_to_main = (
            income['dfas_usaa'] + 
            income['dfas_sunmark'] + 
            income['ss_rebecca'] + 
            income['ss_fitz']
        )
        projected_main = main_checking + income_to_main - bills_total
        projected_sidney = balances['sidney'] + income['rebecca_disability']
        
        if show_nbt:
            total_all = sum(balances.values())
        else:
            total_all = balances['usaa'] + balances['sunmark'] + balances['sidney']
        
        total_income = sum(income.values())
        
        # Build HTML report
        html = f"""<b>💰 FINANCIAL STATUS</b>
<i>{date_str}</i>

<b>━━━ CURRENT POSITION ━━━</b>
<pre>
USAA Checking      {fmt_right(balances['usaa'])}
Sunmark Checking   {fmt_right(balances['sunmark'])}
Sidney FCU         {fmt_right(balances['sidney'])}"""

        if show_nbt:
            html += f"""
NBT (estate)       {fmt_right(balances['nbt'])}"""
        
        html += f"""
───────────────────────────
TOTAL              {fmt_right(total_all)}
</pre>"""

        if show_nbt:
            html += f"""
<i>{nbt_note}</i>"""

        html += f"""

<b>━━━ BILLS DUE (14 days) ━━━</b>
<pre>
"""
        for date, name, amount in bills_14_day:
            warn = " ⚠️" if amount >= 100 else ""
            html += f"{date:<8} {name:<16} {fmt_right(amount)}{warn}\n"
        
        html += f"""───────────────────────────
TOTAL OUT          {fmt_right(bills_total)}
</pre>

<b>━━━ INCOME EXPECTED (14 days) ━━━</b>
<pre>
Feb 3   Rebecca Disability {fmt_right(income['rebecca_disability'])}
Feb 11  DFAS → Adv FCU     {fmt_right(income['dfas_adv'])}
Feb 11  DFAS → USAA        {fmt_right(income['dfas_usaa'])}
Feb 11  DFAS → Sunmark     {fmt_right(income['dfas_sunmark'])}
Feb 15  SS (Rebecca)       {fmt_right(income['ss_rebecca'])}
Feb 15  SS (Fitz)          {fmt_right(income['ss_fitz'])}
───────────────────────────
TOTAL IN           {fmt_right(total_income)}
</pre>

<b>━━━ PROJECTION: FEB 15 ━━━</b>
<pre>
USAA + Sunmark now {fmt_right(main_checking)}
+ Income (to these){fmt_right(income_to_main)}
- Bills            {fmt_right(bills_total)}
───────────────────────────
PROJECTED          {fmt_right(projected_main)}
</pre>

<b>Other Accounts:</b>
<pre>
Sidney FCU         {fmt_right(balances['sidney'])}
 + Feb 3 deposit   {fmt_right(income['rebecca_disability'])}
 = projected       {fmt_right(projected_sidney)}
"""

        if show_nbt:
            html += f"""
NBT (estate)       {fmt_right(balances['nbt'])}
 {nbt_note}
"""

        html += f"""</pre>

<b>━━━ ACTION ITEMS ━━━</b>
"""
        for item in action_items:
            html += f"◽ {item}\n"
        
        next_update = (today + timedelta(days=7)).strftime('%b %d, %Y')
        html += f"\n<i>Next update: {next_update}</i>"
        
        await update.message.reply_text(html, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Report command error: {e}")
        await update.message.reply_text(f"❌ Error generating report: {e}")
