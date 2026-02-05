#!/usr/bin/env python3
"""
Mythos Telegram Bot - Pulse Handler
/opt/mythos/telegram_bot/handlers/pulse_handler.py

Provides passive financial visibility for the household.

Commands:
    /pulse - Show current financial pulse (on-demand)

Scheduled:
    Weekly pulse sent to Ka and Seraphe (Sunday 6pm EST)
"""
import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from telegram import Update, Bot
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment
load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# Household Telegram IDs from environment
TELEGRAM_ID_KA = os.getenv('TELEGRAM_ID_KA')
TELEGRAM_ID_SERAPHE = os.getenv('TELEGRAM_ID_SERAPHE')


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


def generate_pulse_message() -> str:
    """Generate the financial pulse message"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        today = datetime.now()
        current_day = today.day
        
        # ============================================================
        # 1. GET CURRENT CHECKING BALANCES
        # ============================================================
        cur.execute("""
            SELECT 
                abbreviation,
                bank_name,
                current_balance,
                balance_updated_at
            FROM accounts 
            WHERE is_active = true 
              AND account_type = 'checking'
            ORDER BY abbreviation
        """)
        checking_accounts = cur.fetchall()
        
        # Calculate checking total (exclude NBT estate funds from "available")
        checking_total = Decimal('0')
        main_checking = Decimal('0')  # SUN + USAA only
        
        for acct in checking_accounts:
            bal = Decimal(str(acct['current_balance'] or 0))
            checking_total += bal
            if acct['abbreviation'] in ('SUN', 'USAA'):
                main_checking += bal
        
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
        
        bills_14_day = []
        bills_total = Decimal('0')
        
        for bill in all_bills:
            day = bill['expected_day']
            if day is None:
                continue
            
            # Check if within next 14 days (handle month wrap)
            if current_day <= day <= current_day + 14:
                bills_14_day.append(bill)
                bills_total += Decimal(str(bill['expected_amount']))
            elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                bills_14_day.append(bill)
                bills_total += Decimal(str(bill['expected_amount']))
        
        # ============================================================
        # 3. GET INCOME EXPECTED IN NEXT 14 DAYS
        # ============================================================
        cur.execute("""
            SELECT 
                ri.source_name,
                ri.expected_amount,
                ri.expected_day,
                ri.frequency,
                ri.next_date,
                a.abbreviation as acct
            FROM recurring_income ri
            LEFT JOIN accounts a ON ri.account_id = a.id
            WHERE ri.is_active = true
            ORDER BY COALESCE(ri.next_date, make_date(2099,1,1)), COALESCE(ri.expected_day, 99)
        """)
        all_income = cur.fetchall()
        
        income_14_day = []
        income_total = Decimal('0')
        income_to_main = Decimal('0')  # Only to USAA + Sunmark
        
        today_date = today.date() if hasattr(today, 'date') else today
        fourteen_days = today_date + timedelta(days=14)
        
        for inc in all_income:
            day = inc['expected_day']
            freq = inc['frequency']
            amount = Decimal(str(inc['expected_amount']))
            acct = inc['acct']
            next_date = inc['next_date']
            
            include = False
            display_day = None
            
            if freq == 'biweekly' and next_date:
                # Use actual next_date for biweekly
                if today_date <= next_date <= fourteen_days:
                    include = True
                    display_day = next_date.day
            elif day is not None:
                # Monthly - use expected_day
                if current_day <= day <= current_day + 14:
                    include = True
                    display_day = day
                elif current_day + 14 > 31 and day <= (current_day + 14 - 31):
                    include = True
                    display_day = day
            
            if include:
                # Add display_day to the income dict for output
                inc_with_day = dict(inc)
                inc_with_day['display_day'] = display_day
                income_14_day.append(inc_with_day)
                income_total += amount
                if acct in ('USAA', 'SUN'):
                    income_to_main += amount
        
        # ============================================================
        # 4. CALCULATE PROJECTION
        # ============================================================
        projected = main_checking + income_to_main - bills_total
        
        conn.close()
        
        # ============================================================
        # 5. BUILD MESSAGE
        # ============================================================
        # Determine status emoji
        if projected < 0:
            status_emoji = "🔴"
            status_word = "TIGHT"
        elif projected < 500:
            status_emoji = "🟡"
            status_word = "WATCH"
        else:
            status_emoji = "🟢"
            status_word = "OK"
        
        # Get individual account balances
        sun_balance = Decimal('0')
        usaa_balance = Decimal('0')
        sid_balance = Decimal('0')
        
        for acct in checking_accounts:
            if acct['abbreviation'] == 'SUN':
                sun_balance = Decimal(str(acct['current_balance'] or 0))
            elif acct['abbreviation'] == 'USAA':
                usaa_balance = Decimal(str(acct['current_balance'] or 0))
            elif acct['abbreviation'] == 'SID':
                sid_balance = Decimal(str(acct['current_balance'] or 0))
        
        lines = [
            f"📊 **Financial Pulse**",
            f"_{today.strftime('%A, %B %d')}_",
            "",
            f"**Available Now**",
            f"  Sunmark: {format_currency(sun_balance)}",
            f"  USAA: {format_currency(usaa_balance)}",
            f"  _Total: {format_currency(main_checking)}_",
        ]
        
        # Add Sidney if it has balance
        if sid_balance > 0:
            lines.append(f"  Sidney: {format_currency(sid_balance)}")
        
        # Income details
        lines.append("")
        lines.append(f"**📥 Income Next 14 Days**")
        if income_14_day:
            for inc in income_14_day:
                day = inc.get('display_day') or inc.get('expected_day')
                day_str = str(day) if day else "~"
                source = inc['source_name']
                amount = Decimal(str(inc['expected_amount']))
                acct = inc['acct'] or '?'
                lines.append(f"  {day_str}: {source} → {acct} ({format_currency(amount)})")
            lines.append(f"  _Total: +{format_currency(income_total)}_")
        else:
            lines.append("  None expected")
        
        # Bills summary
        lines.append("")
        lines.append(f"**📤 Bills Next 14 Days**")
        lines.append(f"  Total: -{format_currency(bills_total)}")
        
        # Add warning for big bills
        big_bills = [b for b in bills_14_day if Decimal(str(b['expected_amount'])) >= 200]
        if big_bills:
            lines.append("")
            lines.append("**⚠️ Big Bills Coming**")
            for bill in big_bills[:3]:  # Show top 3
                day = bill['expected_day']
                lines.append(f"  {day}: {bill['merchant_name']} ({format_currency(bill['expected_amount'])})")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"Error generating pulse: {e}")
        return f"❌ Error generating pulse: {e}"


async def pulse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pulse command - show financial pulse on demand"""
    message = generate_pulse_message()
    await update.message.reply_text(message, parse_mode='Markdown')


async def send_weekly_pulse(context: ContextTypes.DEFAULT_TYPE):
    """Send weekly pulse to household members (called by scheduler)"""
    logger.info("Sending weekly financial pulse...")
    
    message = "🗓️ **Weekly Financial Pulse**\n\n" + generate_pulse_message()
    
    bot: Bot = context.bot
    
    # Send to Ka
    if TELEGRAM_ID_KA:
        try:
            await bot.send_message(
                chat_id=int(TELEGRAM_ID_KA),
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Weekly pulse sent to Ka ({TELEGRAM_ID_KA})")
        except Exception as e:
            logger.error(f"Failed to send pulse to Ka: {e}")
    
    # Send to Seraphe
    if TELEGRAM_ID_SERAPHE:
        try:
            await bot.send_message(
                chat_id=int(TELEGRAM_ID_SERAPHE),
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Weekly pulse sent to Seraphe ({TELEGRAM_ID_SERAPHE})")
        except Exception as e:
            logger.error(f"Failed to send pulse to Seraphe: {e}")


def setup_pulse_scheduler(application):
    """Set up the weekly pulse scheduler
    
    Call this from the main bot after building the application.
    Sends pulse every Sunday at 6:00 PM EST.
    """
    from telegram.ext import Application
    
    job_queue = application.job_queue
    
    if job_queue is None:
        logger.warning("JobQueue not available - weekly pulse disabled")
        return
    
    # Sunday = 6 (Monday=0, Sunday=6)
    # 6:00 PM EST = 18:00
    # Note: Server should be in EST, but we use time() for local time
    from datetime import time
    
    job_queue.run_daily(
        send_weekly_pulse,
        time=time(hour=18, minute=0, second=0),  # 6:00 PM
        days=(6,),  # Sunday only
        name="weekly_pulse"
    )
    
    logger.info("Weekly pulse scheduler configured: Sundays at 6:00 PM")
