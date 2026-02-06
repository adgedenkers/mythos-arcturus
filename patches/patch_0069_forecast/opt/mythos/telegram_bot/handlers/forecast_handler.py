#!/usr/bin/env python3
"""
Mythos Telegram Bot - Forecast & Projection Handlers
/opt/mythos/telegram_bot/handlers/forecast_handler.py

Commands:
    /forecast  - Day-by-day balance projection for next 30 days
    /projection - Quick summary: current → projected with key dates
    /bills     - Show upcoming bills in next 14 days
    /income    - Show expected income in next 14 days
"""
import os
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from calendar import monthrange
from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def fmt(amount):
    """Format currency"""
    if amount is None:
        return "-"
    if amount >= 0:
        return f"${amount:,.2f}"
    return f"-${abs(amount):,.2f}"


def get_current_balances(cur):
    """Get most recent balance for each active checking account"""
    cur.execute("""
        SELECT DISTINCT ON (a.id)
            a.id, a.abbreviation, a.bank_name,
            COALESCE(t.balance, 0) as balance,
            t.transaction_date
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        WHERE a.is_active = true AND a.account_type IN ('checking', 'savings')
        ORDER BY a.id, t.transaction_date DESC
    """)
    return {row['abbreviation']: row for row in cur.fetchall()}


def get_upcoming_bills(cur, days_ahead=30):
    """Get bills expected in the next N days, mapped to specific dates"""
    today = date.today()
    current_day = today.day
    current_month = today.month
    current_year = today.year
    days_in_month = monthrange(current_year, current_month)[1]
    
    # Next month info
    if current_month == 12:
        next_month, next_year = 1, current_year + 1
    else:
        next_month, next_year = current_month + 1, current_year
    days_in_next = monthrange(next_year, next_month)[1]
    
    cur.execute("""
        SELECT rb.merchant_name, rb.expected_amount, rb.expected_day, 
               rb.frequency, a.abbreviation as acct, a.id as account_id
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true AND rb.expected_day IS NOT NULL
        ORDER BY rb.expected_day
    """)
    all_bills = cur.fetchall()
    
    bills_by_date = {}
    end_date = today + timedelta(days=days_ahead)
    
    for bill in all_bills:
        day = bill['expected_day']
        
        # This month occurrence
        if day <= days_in_month:
            bill_date = date(current_year, current_month, day)
        else:
            bill_date = date(current_year, current_month, days_in_month)
        
        if today <= bill_date <= end_date:
            bills_by_date.setdefault(bill_date, []).append(bill)
        
        # Next month occurrence
        if day <= days_in_next:
            bill_date_next = date(next_year, next_month, day)
        else:
            bill_date_next = date(next_year, next_month, days_in_next)
        
        if today <= bill_date_next <= end_date:
            bills_by_date.setdefault(bill_date_next, []).append(bill)
    
    return bills_by_date


def get_upcoming_income(cur, days_ahead=30):
    """Get income expected in the next N days, mapped to specific dates"""
    today = date.today()
    current_day = today.day
    current_month = today.month
    current_year = today.year
    days_in_month = monthrange(current_year, current_month)[1]
    
    if current_month == 12:
        next_month, next_year = 1, current_year + 1
    else:
        next_month, next_year = current_month + 1, current_year
    days_in_next = monthrange(next_year, next_month)[1]
    
    cur.execute("""
        SELECT ri.source_name, ri.expected_amount, ri.expected_day,
               ri.frequency, a.abbreviation as acct, a.id as account_id
        FROM recurring_income ri
        LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true
        ORDER BY ri.expected_day NULLS LAST
    """)
    all_income = cur.fetchall()
    
    income_by_date = {}
    end_date = today + timedelta(days=days_ahead)
    
    for inc in all_income:
        day = inc['expected_day']
        freq = inc['frequency']
        
        if freq == 'biweekly':
            # Biweekly: find next occurrence from last known pay date
            # Approximate: put one at day 1 and day 15 of each month
            for target_day in [1, 15]:
                for m, y in [(current_month, current_year), (next_month, next_year)]:
                    dim = monthrange(y, m)[1]
                    d = min(target_day, dim)
                    inc_date = date(y, m, d)
                    if today <= inc_date <= end_date:
                        income_by_date.setdefault(inc_date, []).append(inc)
        elif day is not None:
            # This month
            if day <= days_in_month:
                inc_date = date(current_year, current_month, day)
            else:
                inc_date = date(current_year, current_month, days_in_month)
            
            if today <= inc_date <= end_date:
                income_by_date.setdefault(inc_date, []).append(inc)
            
            # Next month
            if day <= days_in_next:
                inc_date_next = date(next_year, next_month, day)
            else:
                inc_date_next = date(next_year, next_month, days_in_next)
            
            if today <= inc_date_next <= end_date:
                income_by_date.setdefault(inc_date_next, []).append(inc)
    
    return income_by_date


# Primary accounts for projection (checking accounts we care about)
PRIMARY_ACCOUNTS = ['USAA', 'SUN']


async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /forecast - Day-by-day balance projection for next 30 days
    Shows running balance with bills and income on each day
    """
    try:
        days = 30
        if context.args:
            try:
                days = min(max(int(context.args[0]), 7), 60)
            except:
                pass
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        balances = get_current_balances(cur)
        bills_by_date = get_upcoming_bills(cur, days)
        income_by_date = get_upcoming_income(cur, days)
        
        conn.close()
        
        # Combined balance of primary accounts
        combined = sum(
            Decimal(str(balances.get(acct, {}).get('balance', 0)))
            for acct in PRIMARY_ACCOUNTS
        )
        
        today = date.today()
        running = combined
        lowest = combined
        lowest_date = today
        went_negative = False
        negative_date = None
        
        lines = [
            f"📈 <b>30-Day Forecast</b>",
            f"<i>Starting: {fmt(combined)} (USAA+SUN)</i>",
            "",
            "<pre>",
            f"{'Date':<8} {'Change':>9} {'Balance':>10}  Events",
            f"{'─'*8} {'─'*9} {'─'*10}  {'─'*20}",
        ]
        
        for i in range(days + 1):
            d = today + timedelta(days=i)
            day_bills = bills_by_date.get(d, [])
            day_income = income_by_date.get(d, [])
            
            # Only primary account bills/income
            day_out = sum(
                Decimal(str(b['expected_amount']))
                for b in day_bills
                if b.get('acct') in PRIMARY_ACCOUNTS or b.get('acct') is None
            )
            day_in = sum(
                Decimal(str(inc['expected_amount']))
                for inc in day_income
                if inc.get('acct') in PRIMARY_ACCOUNTS
            )
            
            day_change = day_in - day_out
            
            if i > 0:  # Don't apply changes on day 0 (today's balance is current)
                running += day_change
            
            # Track lowest
            if running < lowest:
                lowest = running
                lowest_date = d
            
            # Track first negative
            if running < 0 and not went_negative:
                went_negative = True
                negative_date = d
            
            # Only show days with activity or key dates
            has_activity = day_bills or day_income
            is_today = i == 0
            is_weekend = d.weekday() >= 5
            show_day = has_activity or is_today or i == days
            
            if show_day:
                date_str = d.strftime('%m/%d') if not is_today else 'TODAY'
                
                if day_change > 0:
                    change_str = f"+{fmt(day_change)}"
                elif day_change < 0:
                    change_str = f"{fmt(day_change)}"
                else:
                    change_str = ""
                
                # Build event list
                events = []
                for inc in day_income:
                    if inc.get('acct') in PRIMARY_ACCOUNTS:
                        events.append(f"💰{inc['source_name'][:10]}")
                for b in day_bills:
                    if b.get('acct') in PRIMARY_ACCOUNTS or b.get('acct') is None:
                        events.append(f"💸{b['merchant_name'][:10]}")
                
                event_str = " ".join(events[:3])
                if len(events) > 3:
                    event_str += f" +{len(events)-3}"
                
                # Warning indicator
                warn = ""
                if running < 0:
                    warn = " ⛔"
                elif running < 200:
                    warn = " ⚠️"
                
                lines.append(
                    f"{date_str:<8} {change_str:>9} {fmt(running):>10}{warn}  {event_str}"
                )
        
        lines.append("</pre>")
        lines.append("")
        
        # Summary
        if went_negative:
            lines.append(f"⛔ <b>OVERDRAFT WARNING: Goes negative on {negative_date.strftime('%m/%d')}</b>")
            lines.append(f"   Projected: {fmt(lowest)} on {lowest_date.strftime('%m/%d')}")
        elif lowest < Decimal('200'):
            lines.append(f"⚠️ <b>LOW BALANCE: {fmt(lowest)} on {lowest_date.strftime('%m/%d')}</b>")
        else:
            lines.append(f"✅ Lowest point: {fmt(lowest)} on {lowest_date.strftime('%m/%d')}")
        
        lines.append(f"📅 End of period: {fmt(running)}")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Forecast error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def projection_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /projection - Quick summary of financial projection
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        balances = get_current_balances(cur)
        bills_by_date = get_upcoming_bills(cur, 30)
        income_by_date = get_upcoming_income(cur, 30)
        
        conn.close()
        
        today = date.today()
        
        # Calculate totals for primary accounts
        total_now = sum(
            Decimal(str(balances.get(acct, {}).get('balance', 0)))
            for acct in PRIMARY_ACCOUNTS
        )
        
        total_bills_14 = Decimal('0')
        total_bills_30 = Decimal('0')
        total_income_14 = Decimal('0')
        total_income_30 = Decimal('0')
        
        for d, bills in bills_by_date.items():
            for b in bills:
                if b.get('acct') in PRIMARY_ACCOUNTS or b.get('acct') is None:
                    amt = Decimal(str(b['expected_amount']))
                    total_bills_30 += amt
                    if (d - today).days <= 14:
                        total_bills_14 += amt
        
        for d, incomes in income_by_date.items():
            for inc in incomes:
                if inc.get('acct') in PRIMARY_ACCOUNTS:
                    amt = Decimal(str(inc['expected_amount']))
                    total_income_30 += amt
                    if (d - today).days <= 14:
                        total_income_14 += amt
        
        projected_14 = total_now + total_income_14 - total_bills_14
        projected_30 = total_now + total_income_30 - total_bills_30
        
        # Next income date
        next_income = None
        for d in sorted(income_by_date.keys()):
            if d > today:
                for inc in income_by_date[d]:
                    if inc.get('acct') in PRIMARY_ACCOUNTS:
                        next_income = (d, inc)
                        break
                if next_income:
                    break
        
        # Next big bill
        next_big_bill = None
        for d in sorted(bills_by_date.keys()):
            if d > today:
                for b in bills_by_date[d]:
                    amt = Decimal(str(b['expected_amount']))
                    if amt >= 100 and (b.get('acct') in PRIMARY_ACCOUNTS or b.get('acct') is None):
                        next_big_bill = (d, b)
                        break
                if next_big_bill:
                    break
        
        lines = [
            f"📊 <b>Financial Projection</b>",
            f"<i>{today.strftime('%B %d, %Y')}</i>",
            "",
            f"<b>Now:</b> {fmt(total_now)}",
            "",
            "<b>━━━ Next 14 Days ━━━</b>",
            f"  + Income:   {fmt(total_income_14)}",
            f"  - Bills:    {fmt(total_bills_14)}",
            f"  = Projected: <b>{fmt(projected_14)}</b>",
            "",
            "<b>━━━ Next 30 Days ━━━</b>",
            f"  + Income:   {fmt(total_income_30)}",
            f"  - Bills:    {fmt(total_bills_30)}",
            f"  = Projected: <b>{fmt(projected_30)}</b>",
        ]
        
        if next_income:
            d, inc = next_income
            lines.append(f"\n💰 Next income: {inc['source_name']} ({fmt(inc['expected_amount'])}) on {d.strftime('%m/%d')}")
        
        if next_big_bill:
            d, b = next_big_bill
            lines.append(f"💸 Next big bill: {b['merchant_name']} ({fmt(b['expected_amount'])}) on {d.strftime('%m/%d')}")
        
        # Warning
        if projected_14 < 0:
            lines.append(f"\n⛔ <b>OVERDRAFT RISK in next 14 days!</b>")
            lines.append(f"Use /forecast for day-by-day breakdown")
        elif projected_14 < 200:
            lines.append(f"\n⚠️ <b>Tight — under $200 projected in 14 days</b>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Projection error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def bills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /bills - Show upcoming bills in next 14 days
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        bills_by_date = get_upcoming_bills(cur, 14)
        conn.close()
        
        today = date.today()
        total = Decimal('0')
        
        lines = [
            f"💸 <b>Bills Due (Next 14 Days)</b>",
            "",
            "<pre>",
            f"{'Date':<8} {'Amount':>9}  Merchant",
            f"{'─'*8} {'─'*9}  {'─'*20}",
        ]
        
        for d in sorted(bills_by_date.keys()):
            for b in bills_by_date[d]:
                amt = Decimal(str(b['expected_amount']))
                total += amt
                days_away = (d - today).days
                date_str = d.strftime('%m/%d')
                if days_away == 0:
                    date_str = "TODAY"
                elif days_away == 1:
                    date_str = "TMRW"
                
                warn = " ⚠️" if amt >= 200 else ""
                acct = b.get('acct', '?')
                lines.append(f"{date_str:<8} {fmt(amt):>9}  {b['merchant_name'][:18]} ({acct}){warn}")
        
        lines.append(f"{'─'*8} {'─'*9}")
        lines.append(f"{'TOTAL':<8} {fmt(total):>9}")
        lines.append("</pre>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Bills error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def income_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /income - Show expected income in next 30 days
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        income_by_date = get_upcoming_income(cur, 30)
        conn.close()
        
        today = date.today()
        total = Decimal('0')
        
        lines = [
            f"💰 <b>Expected Income (Next 30 Days)</b>",
            "",
            "<pre>",
            f"{'Date':<8} {'Amount':>10}  Source",
            f"{'─'*8} {'─'*10}  {'─'*20}",
        ]
        
        for d in sorted(income_by_date.keys()):
            for inc in income_by_date[d]:
                amt = Decimal(str(inc['expected_amount']))
                total += amt
                date_str = d.strftime('%m/%d')
                acct = inc.get('acct', '?')
                lines.append(f"{date_str:<8} {fmt(amt):>10}  {inc['source_name'][:18]} ({acct})")
        
        lines.append(f"{'─'*8} {'─'*10}")
        lines.append(f"{'TOTAL':<8} {fmt(total):>10}")
        lines.append("</pre>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Income error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")
