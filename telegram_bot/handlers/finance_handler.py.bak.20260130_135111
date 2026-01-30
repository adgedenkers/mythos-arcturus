#!/usr/bin/env python3
"""
Mythos Telegram Bot - Finance Handlers
/opt/mythos/telegram_bot/handlers/finance_handler.py

Commands:
    /balance - Show current account balances
    /finance - Show financial summary (balances + this month's activity)
    /spending - Show spending by category
"""

import os
import logging
from datetime import datetime
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
