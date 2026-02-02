#!/usr/bin/env python3
"""
Mythos Telegram Bot - Snapshot Handler
/opt/mythos/telegram_bot/handlers/snapshot_handler.py

The "Seraphe Report" - a simple, clear financial snapshot.
Shows exactly where things stand without narrative or defense.

Commands:
    /snapshot - Full financial snapshot (the main report)
    /setbal <ACCT> <amount> - Quick balance update (alias for setbalance)
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


def fmt(amount, width=10):
    """Format currency, right-aligned"""
    if amount is None:
        return " " * (width - 1) + "-"
    val = Decimal(str(amount))
    if val >= 0:
        return f"${val:,.2f}".rjust(width)
    else:
        return f"-${abs(val):,.2f}".rjust(width)


async def snapshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /snapshot - The Seraphe Report
    
    Simple. Clear. No narrative.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        today = datetime.now()
        date_str = today.strftime("%b %d, %Y")
        
        # ============================================================
        # 1. GET ALL ACCOUNT BALANCES
        # ============================================================
        cur.execute("""
            SELECT 
                abbreviation,
                bank_name,
                account_name,
                account_type,
                COALESCE(current_balance, 0) as balance,
                balance_updated_at,
                credit_limit,
                min_payment,
                payment_due_day
            FROM accounts
            WHERE is_active = true
            ORDER BY 
                CASE account_type 
                    WHEN 'checking' THEN 1 
                    WHEN 'savings' THEN 2
                    WHEN 'credit' THEN 3 
                    WHEN 'loan' THEN 4 
                    ELSE 5 
                END,
                bank_name
        """)
        accounts = cur.fetchall()
        
        # Separate by type
        checking = [a for a in accounts if a['account_type'] == 'checking']
        credit_cards = [a for a in accounts if a['account_type'] == 'credit']
        loans = [a for a in accounts if a['account_type'] == 'loan']
        
        # Calculate totals
        total_cash = sum(Decimal(str(a['balance'] or 0)) for a in checking)
        total_credit_debt = sum(abs(Decimal(str(a['balance'] or 0))) for a in credit_cards)
        total_loan_debt = sum(abs(Decimal(str(a['balance'] or 0))) for a in loans)
        total_debt = total_credit_debt + total_loan_debt
        net_worth = total_cash - total_debt
        
        # ============================================================
        # 2. GET PAYMENTS DUE IN NEXT 14 DAYS
        # ============================================================
        current_day = today.day
        
        # Credit card minimums due
        payments_due = []
        for cc in credit_cards:
            due_day = cc['payment_due_day']
            min_pmt = Decimal(str(cc['min_payment'] or 0))
            if due_day and min_pmt > 0:
                # Check if due in next 14 days
                if current_day <= due_day <= current_day + 14:
                    payments_due.append({
                        'name': cc['bank_name'],
                        'amount': min_pmt,
                        'day': due_day,
                        'type': 'cc_min'
                    })
                elif current_day + 14 > 31 and due_day <= (current_day + 14 - 31):
                    payments_due.append({
                        'name': cc['bank_name'],
                        'amount': min_pmt,
                        'day': due_day,
                        'type': 'cc_min'
                    })
        
        # Recurring bills from recurring_bills table
        cur.execute("""
            SELECT 
                merchant_name,
                expected_amount,
                expected_day
            FROM recurring_bills
            WHERE is_active = true
              AND expected_day IS NOT NULL
            ORDER BY expected_day
        """)
        bills = cur.fetchall()
        
        for bill in bills:
            day = bill['expected_day']
            if current_day <= day <= current_day + 14:
                payments_due.append({
                    'name': bill['merchant_name'],
                    'amount': Decimal(str(bill['expected_amount'])),
                    'day': day,
                    'type': 'bill'
                })
            elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                payments_due.append({
                    'name': bill['merchant_name'],
                    'amount': Decimal(str(bill['expected_amount'])),
                    'day': day,
                    'type': 'bill'
                })
        
        # Sort by day
        payments_due.sort(key=lambda x: x['day'])
        total_due = sum(p['amount'] for p in payments_due)
        
        # ============================================================
        # 3. GET INCOME EXPECTED IN NEXT 14 DAYS  
        # ============================================================
        cur.execute("""
            SELECT 
                source_name,
                expected_amount,
                expected_day,
                frequency
            FROM recurring_income
            WHERE is_active = true
            ORDER BY expected_day NULLS LAST
        """)
        income_rows = cur.fetchall()
        
        income_expected = []
        for inc in income_rows:
            day = inc['expected_day']
            freq = inc['frequency']
            amount = Decimal(str(inc['expected_amount']))
            
            include = False
            if freq == 'biweekly':
                include = True  # Always show biweekly in 14-day window
            elif day is not None:
                if current_day <= day <= current_day + 14:
                    include = True
                elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                    include = True
            
            if include:
                income_expected.append({
                    'name': inc['source_name'],
                    'amount': amount,
                    'day': day if day else '~'
                })
        
        total_income = sum(i['amount'] for i in income_expected)
        
        conn.close()
        
        # ============================================================
        # 4. BUILD THE REPORT
        # ============================================================
        
        lines = []
        lines.append(f"<b>💰 SNAPSHOT</b>  <i>{date_str}</i>")
        lines.append("")
        
        # === CASH ===
        lines.append("<b>━━━ CASH ━━━</b>")
        lines.append("<pre>")
        for acct in checking:
            name = acct['bank_name'][:14]
            bal = Decimal(str(acct['balance'] or 0))
            lines.append(f"{name:<14} {fmt(bal)}")
        lines.append(f"{'─' * 25}")
        lines.append(f"{'TOTAL':<14} {fmt(total_cash)}")
        lines.append("</pre>")
        
        # === DEBT ===
        lines.append("")
        lines.append("<b>━━━ DEBT ━━━</b>")
        lines.append("<pre>")
        for cc in credit_cards:
            name = cc['bank_name'][:14]
            bal = abs(Decimal(str(cc['balance'] or 0)))
            lines.append(f"{name:<14} {fmt(bal)}")
        for loan in loans:
            name = f"{loan['bank_name']} Loan"[:14]
            bal = abs(Decimal(str(loan['balance'] or 0)))
            lines.append(f"{name:<14} {fmt(bal)}")
        lines.append(f"{'─' * 25}")
        lines.append(f"{'TOTAL':<14} {fmt(total_debt)}")
        lines.append("</pre>")
        
        # === NET ===
        lines.append("")
        net_emoji = "📈" if net_worth >= 0 else "📉"
        lines.append(f"<b>{net_emoji} NET: {fmt(net_worth)}</b>")
        
        # === DUE NEXT 14 DAYS ===
        lines.append("")
        lines.append("<b>━━━ DUE (14 days) ━━━</b>")
        if payments_due:
            lines.append("<pre>")
            for p in payments_due[:10]:  # Limit to 10
                day = str(p['day']).rjust(2)
                name = p['name'][:12]
                amt = fmt(p['amount'], 8)
                lines.append(f"{day}  {name:<12} {amt}")
            lines.append(f"{'─' * 25}")
            lines.append(f"{'TOTAL':<14} {fmt(total_due, 8)}")
            lines.append("</pre>")
        else:
            lines.append("<i>Nothing due</i>")
        
        # === INCOME EXPECTED ===
        lines.append("")
        lines.append("<b>━━━ INCOME (14 days) ━━━</b>")
        if income_expected:
            lines.append("<pre>")
            for inc in income_expected[:8]:  # Limit to 8
                day = str(inc['day']).rjust(2)
                name = inc['name'][:12]
                amt = fmt(inc['amount'], 8)
                lines.append(f"{day}  {name:<12} {amt}")
            lines.append(f"{'─' * 25}")
            lines.append(f"{'TOTAL':<14} {fmt(total_income, 8)}")
            lines.append("</pre>")
        else:
            lines.append("<i>No expected income</i>")
        
        # === BOTTOM LINE ===
        lines.append("")
        projected = total_cash + total_income - total_due
        lines.append("<b>━━━ BOTTOM LINE ━━━</b>")
        lines.append(f"Cash now:      {fmt(total_cash)}")
        lines.append(f"+ Income:      {fmt(total_income)}")
        lines.append(f"- Due:         {fmt(total_due)}")
        lines.append(f"<b>= Projected:   {fmt(projected)}</b>")
        
        # Status
        lines.append("")
        if projected > 1000:
            lines.append("✅ <b>You're good</b>")
        elif projected > 0:
            lines.append("⚠️ <b>Tight but okay</b>")
        else:
            lines.append("🚨 <b>Shortfall ahead</b>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Snapshot command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def setbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setbal <ACCT> <amount> - Quick balance update
    
    Example: /setbal USAA 1431.65
             /setbal LLBEAN -8423.34
    """
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "<b>Usage:</b> /setbal ACCT amount\n\n"
                "<b>Checking:</b> USAA, SUN, SID, NBT, DVA\n"
                "<b>Credit:</b> LLBEAN, TSC, OLDNAVY, TJX, AMEX\n"
                "<b>Loan:</b> USAALOAN\n\n"
                "<i>Credit cards: use negative (e.g., -8423.34)</i>",
                parse_mode='HTML'
            )
            return
        
        acct_abbr = context.args[0].upper()
        
        try:
            amount_str = context.args[1].replace(',', '').replace('$', '')
            amount = Decimal(amount_str)
        except:
            await update.message.reply_text(f"❌ Invalid amount: {context.args[1]}")
            return
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update the balance
        cur.execute("""
            UPDATE accounts 
            SET current_balance = %s, 
                balance_updated_at = NOW()
            WHERE abbreviation = %s AND is_active = true
            RETURNING bank_name, account_name, current_balance
        """, (amount, acct_abbr))
        
        result = cur.fetchone()
        
        if not result:
            cur.execute("SELECT abbreviation, bank_name FROM accounts WHERE is_active = true ORDER BY abbreviation")
            valid = cur.fetchall()
            valid_list = ", ".join([a['abbreviation'] for a in valid])
            await update.message.reply_text(f"❌ Unknown: {acct_abbr}\n\nValid: {valid_list}")
            conn.close()
            return
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✓ <b>{result['bank_name']}</b> → {fmt(amount)}",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Setbal command error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
