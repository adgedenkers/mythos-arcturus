#!/usr/bin/env python3
"""
Mythos Telegram Bot - Forecast & Projection Handlers
/opt/mythos/telegram_bot/handlers/forecast_handler.py

Commands:
    /forecast       - Combined USAA+SUN balance projection (30 days)
    /forecast usaa  - USAA only forecast
    /forecast sun   - Sunmark only forecast
    /forecast 14    - Combined forecast for 14 days
    /projection     - Quick summary: current → projected with key dates
    /bills          - Show upcoming bills in next 14 days
    /income         - Show expected income in next 30 days
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
    current_month = today.month
    current_year = today.year
    days_in_month = monthrange(current_year, current_month)[1]
    
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
            for target_day in [1, 15]:
                for m, y in [(current_month, current_year), (next_month, next_year)]:
                    dim = monthrange(y, m)[1]
                    d = min(target_day, dim)
                    inc_date = date(y, m, d)
                    if today <= inc_date <= end_date:
                        income_by_date.setdefault(inc_date, []).append(inc)
        elif day is not None:
            if day <= days_in_month:
                inc_date = date(current_year, current_month, day)
            else:
                inc_date = date(current_year, current_month, days_in_month)
            
            if today <= inc_date <= end_date:
                income_by_date.setdefault(inc_date, []).append(inc)
            
            if day <= days_in_next:
                inc_date_next = date(next_year, next_month, day)
            else:
                inc_date_next = date(next_year, next_month, days_in_next)
            
            if today <= inc_date_next <= end_date:
                income_by_date.setdefault(inc_date_next, []).append(inc)
    
    return income_by_date


# Account groupings
PRIMARY_ACCOUNTS = ['USAA', 'SUN']
ACCOUNT_LABELS = {
    'USAA': 'USAA',
    'SUN': 'Sunmark',
}


def parse_forecast_args(args):
    """
    Parse /forecast arguments.
    Returns (account_filter, days)
    account_filter: list of account abbreviations to include, or PRIMARY_ACCOUNTS for combined
    """
    account_filter = PRIMARY_ACCOUNTS  # default: combined
    days = 30
    
    for arg in (args or []):
        arg_upper = arg.upper()
        if arg_upper in ('USAA',):
            account_filter = ['USAA']
        elif arg_upper in ('SUN', 'SUNMARK'):
            account_filter = ['SUN']
        else:
            try:
                days = min(max(int(arg), 7), 60)
            except ValueError:
                pass
    
    return account_filter, days


def matches_filter(item, account_filter):
    """Check if a bill/income item matches the account filter"""
    acct = item.get('acct')
    if acct is None:
        # Unassigned bills show in all views
        return True
    return acct in account_filter


def build_forecast(balances, bills_by_date, income_by_date, account_filter, days):
    """Build forecast data - shared by forecast and projection"""
    today = date.today()
    
    combined = sum(
        Decimal(str(balances.get(acct, {}).get('balance', 0)))
        for acct in account_filter
    )
    
    running = combined
    lowest = combined
    lowest_date = today
    went_negative = False
    negative_date = None
    
    day_data = []
    
    for i in range(days + 1):
        d = today + timedelta(days=i)
        day_bills = [b for b in bills_by_date.get(d, []) if matches_filter(b, account_filter)]
        day_income = [inc for inc in income_by_date.get(d, []) if matches_filter(inc, account_filter)]
        
        day_out = sum(Decimal(str(b['expected_amount'])) for b in day_bills)
        day_in = sum(Decimal(str(inc['expected_amount'])) for inc in day_income)
        day_change = day_in - day_out
        
        if i > 0:
            running += day_change
        
        if running < lowest:
            lowest = running
            lowest_date = d
        
        if running < 0 and not went_negative:
            went_negative = True
            negative_date = d
        
        day_data.append({
            'date': d,
            'day_index': i,
            'bills': day_bills,
            'income': day_income,
            'day_out': day_out,
            'day_in': day_in,
            'day_change': day_change,
            'running': running,
        })
    
    return {
        'starting': combined,
        'ending': running,
        'lowest': lowest,
        'lowest_date': lowest_date,
        'went_negative': went_negative,
        'negative_date': negative_date,
        'days': day_data,
    }


async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /forecast [usaa|sun] [days] - Day-by-day balance projection
    """
    try:
        account_filter, days = parse_forecast_args(context.args)
        
        conn = get_db_connection()
        cur = conn.cursor()
        balances = get_current_balances(cur)
        bills_by_date = get_upcoming_bills(cur, days)
        income_by_date = get_upcoming_income(cur, days)
        conn.close()
        
        forecast = build_forecast(balances, bills_by_date, income_by_date, account_filter, days)
        
        # Build label
        if account_filter == ['USAA']:
            label = "USAA"
        elif account_filter == ['SUN']:
            label = "Sunmark"
        else:
            label = "USAA+SUN"
        
        lines = [
            f"📈 <b>{days}-Day Forecast ({label})</b>",
            f"<i>Starting: {fmt(forecast['starting'])}</i>",
            "",
            "<pre>",
            f"{'Date':<8} {'Change':>9} {'Balance':>10}  Events",
            f"{'─'*8} {'─'*9} {'─'*10}  {'─'*20}",
        ]
        
        for dd in forecast['days']:
            has_activity = dd['bills'] or dd['income']
            is_today = dd['day_index'] == 0
            is_last = dd['day_index'] == days
            
            if not (has_activity or is_today or is_last):
                continue
            
            date_str = 'TODAY' if is_today else dd['date'].strftime('%m/%d')
            
            if dd['day_change'] > 0:
                change_str = f"+{fmt(dd['day_change'])}"
            elif dd['day_change'] < 0:
                change_str = f"{fmt(dd['day_change'])}"
            else:
                change_str = ""
            
            events = []
            for inc in dd['income']:
                events.append(f"💰{inc['source_name'][:10]}")
            for b in dd['bills']:
                events.append(f"💸{b['merchant_name'][:10]}")
            
            event_str = " ".join(events[:3])
            if len(events) > 3:
                event_str += f" +{len(events)-3}"
            
            warn = ""
            if dd['running'] < 0:
                warn = " ⛔"
            elif dd['running'] < 200:
                warn = " ⚠️"
            
            lines.append(
                f"{date_str:<8} {change_str:>9} {fmt(dd['running']):>10}{warn}  {event_str}"
            )
        
        lines.append("</pre>")
        lines.append("")
        
        if forecast['went_negative']:
            lines.append(f"⛔ <b>OVERDRAFT: Goes negative {forecast['negative_date'].strftime('%m/%d')}</b>")
            lines.append(f"   Projected low: {fmt(forecast['lowest'])} on {forecast['lowest_date'].strftime('%m/%d')}")
        elif forecast['lowest'] < Decimal('200'):
            lines.append(f"⚠️ <b>LOW: {fmt(forecast['lowest'])} on {forecast['lowest_date'].strftime('%m/%d')}</b>")
        else:
            lines.append(f"✅ Lowest: {fmt(forecast['lowest'])} on {forecast['lowest_date'].strftime('%m/%d')}")
        
        lines.append(f"📅 End: {fmt(forecast['ending'])}")
        
        # Add hints for other views
        if len(account_filter) > 1:
            lines.append(f"\n<i>/forecast usaa or /forecast sun for per-account view</i>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Forecast error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def projection_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /projection [usaa|sun] - Quick summary of financial projection
    """
    try:
        account_filter = PRIMARY_ACCOUNTS
        if context.args:
            arg = context.args[0].upper()
            if arg in ('USAA',):
                account_filter = ['USAA']
            elif arg in ('SUN', 'SUNMARK'):
                account_filter = ['SUN']
        
        conn = get_db_connection()
        cur = conn.cursor()
        balances = get_current_balances(cur)
        bills_by_date = get_upcoming_bills(cur, 30)
        income_by_date = get_upcoming_income(cur, 30)
        conn.close()
        
        today = date.today()
        
        total_now = sum(
            Decimal(str(balances.get(acct, {}).get('balance', 0)))
            for acct in account_filter
        )
        
        total_bills_14 = Decimal('0')
        total_bills_30 = Decimal('0')
        total_income_14 = Decimal('0')
        total_income_30 = Decimal('0')
        
        for d, bills in bills_by_date.items():
            for b in bills:
                if matches_filter(b, account_filter):
                    amt = Decimal(str(b['expected_amount']))
                    total_bills_30 += amt
                    if (d - today).days <= 14:
                        total_bills_14 += amt
        
        for d, incomes in income_by_date.items():
            for inc in incomes:
                if matches_filter(inc, account_filter):
                    amt = Decimal(str(inc['expected_amount']))
                    total_income_30 += amt
                    if (d - today).days <= 14:
                        total_income_14 += amt
        
        projected_14 = total_now + total_income_14 - total_bills_14
        projected_30 = total_now + total_income_30 - total_bills_30
        
        # Label
        if account_filter == ['USAA']:
            label = "USAA"
        elif account_filter == ['SUN']:
            label = "Sunmark"
        else:
            label = "Combined"
            # Show individual balances too
        
        next_income = None
        for d in sorted(income_by_date.keys()):
            if d > today:
                for inc in income_by_date[d]:
                    if matches_filter(inc, account_filter):
                        next_income = (d, inc)
                        break
                if next_income:
                    break
        
        next_big_bill = None
        for d in sorted(bills_by_date.keys()):
            if d > today:
                for b in bills_by_date[d]:
                    amt = Decimal(str(b['expected_amount']))
                    if amt >= 100 and matches_filter(b, account_filter):
                        next_big_bill = (d, b)
                        break
                if next_big_bill:
                    break
        
        lines = [
            f"📊 <b>Projection ({label})</b>",
            f"<i>{today.strftime('%B %d, %Y')}</i>",
            "",
        ]
        
        if len(account_filter) > 1:
            # Show individual balances for combined view
            for acct in account_filter:
                bal = Decimal(str(balances.get(acct, {}).get('balance', 0)))
                lines.append(f"  {ACCOUNT_LABELS.get(acct, acct)}: {fmt(bal)}")
            lines.append(f"<b>Total: {fmt(total_now)}</b>")
        else:
            lines.append(f"<b>Now: {fmt(total_now)}</b>")
        
        lines.extend([
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
        ])
        
        if next_income:
            d, inc = next_income
            lines.append(f"\n💰 Next: {inc['source_name']} ({fmt(inc['expected_amount'])}) on {d.strftime('%m/%d')}")
        
        if next_big_bill:
            d, b = next_big_bill
            lines.append(f"💸 Next big: {b['merchant_name']} ({fmt(b['expected_amount'])}) on {d.strftime('%m/%d')}")
        
        if projected_14 < 0:
            lines.append(f"\n⛔ <b>OVERDRAFT RISK in next 14 days!</b>")
            lines.append(f"Use /forecast for day-by-day breakdown")
        elif projected_14 < 200:
            lines.append(f"\n⚠️ <b>Tight — under $200 projected in 14 days</b>")
        
        if len(account_filter) > 1:
            lines.append(f"\n<i>/projection usaa or /projection sun for per-account</i>")
        
        await update.message.reply_text("\n".join(lines), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Projection error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def bills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /bills [usaa|sun] - Show upcoming bills in next 14 days
    """
    try:
        account_filter = PRIMARY_ACCOUNTS
        if context.args:
            arg = context.args[0].upper()
            if arg in ('USAA',):
                account_filter = ['USAA']
            elif arg in ('SUN', 'SUNMARK'):
                account_filter = ['SUN']
        
        conn = get_db_connection()
        cur = conn.cursor()
        bills_by_date = get_upcoming_bills(cur, 14)
        conn.close()
        
        today = date.today()
        total = Decimal('0')
        
        if account_filter == ['USAA']:
            label = "USAA"
        elif account_filter == ['SUN']:
            label = "Sunmark"
        else:
            label = "All"
        
        lines = [
            f"💸 <b>Bills Due - {label} (Next 14 Days)</b>",
            "",
            "<pre>",
            f"{'Date':<8} {'Amount':>9}  Merchant",
            f"{'─'*8} {'─'*9}  {'─'*20}",
        ]
        
        for d in sorted(bills_by_date.keys()):
            for b in bills_by_date[d]:
                if not matches_filter(b, account_filter):
                    continue
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
    /income [usaa|sun] - Show expected income in next 30 days
    """
    try:
        account_filter = PRIMARY_ACCOUNTS
        if context.args:
            arg = context.args[0].upper()
            if arg in ('USAA',):
                account_filter = ['USAA']
            elif arg in ('SUN', 'SUNMARK'):
                account_filter = ['SUN']
        
        conn = get_db_connection()
        cur = conn.cursor()
        income_by_date = get_upcoming_income(cur, 30)
        conn.close()
        
        today = date.today()
        total = Decimal('0')
        
        if account_filter == ['USAA']:
            label = "USAA"
        elif account_filter == ['SUN']:
            label = "Sunmark"
        else:
            label = "All"
        
        lines = [
            f"💰 <b>Expected Income - {label} (Next 30 Days)</b>",
            "",
            "<pre>",
            f"{'Date':<8} {'Amount':>10}  Source",
            f"{'─'*8} {'─'*10}  {'─'*20}",
        ]
        
        for d in sorted(income_by_date.keys()):
            for inc in income_by_date[d]:
                if not matches_filter(inc, account_filter):
                    continue
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
