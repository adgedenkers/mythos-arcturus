"""
Weekly Review Telegram Handler
==============================
/review - Generate and send weekly financial review via Telegram
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /review command — generate and send weekly financial snapshot."""
    try:
        await update.message.reply_text("📊 Generating weekly review...")

        # Import here to avoid circular imports
        import sys
        sys.path.insert(0, '/opt/mythos/finance')
        from weekly_review import generate_review

        review = generate_review()

        # Build the Telegram message (condensed for mobile)
        lines = []
        bal = review['balances']
        run = review['alerts']['runway']
        m = review['month']
        b = review['bills']
        cash = review['alerts']['cash_withdrawals']
        ff = review['alerts']['fast_food']

        lines.append("📊 <b>WEEKLY FINANCIAL REVIEW</b>")
        lines.append(f"Week of {review['review_week']['start']} → {review['review_week']['end']}")
        lines.append("")

        # Balances
        lines.append("💰 <b>BALANCES</b>")
        for a in bal['accounts']:
            if a['account_type'] == 'checking':
                lines.append(f"  {a['abbreviation']}: <b>${float(a['current_balance']):,.2f}</b>")
        lines.append(f"  Checking total: <b>${float(bal['checking_total']):,.2f}</b>")
        lines.append(f"  Credit debt: ${float(bal['credit_total']):,.2f}")
        lines.append(f"  Loan debt: ${float(bal['loan_total']):,.2f}")
        lines.append("")

        # Runway
        lines.append("🛤 <b>RUNWAY</b>")
        lines.append(f"  Spendable: <b>${float(run['spendable_cash']):,.2f}</b>")
        lines.append(f"  After bills: ${float(run['after_remaining_bills']):,.2f}")
        lines.append(f"  Daily avg spend: ${float(run['daily_discretionary_avg']):,.2f}")
        lines.append(f"  Days to zero: <b>{run['runway_days']}</b>")
        lines.append("")

        # Month
        lines.append(f"📅 <b>MONTH SO FAR</b> (day {review['review_month']['days_elapsed']})")
        lines.append(f"  Income: ${float(m['total_income']):,.2f}")
        lines.append(f"  Spent: ${float(m['total_spending']):,.2f}")
        lines.append(f"  Discretionary: ${float(m['discretionary_spending']):,.2f}")
        lines.append(f"  Net: <b>${float(m['net']):,.2f}</b>")
        lines.append("")

        # Top 5 categories
        lines.append("📉 <b>TOP SPENDING</b>")
        for c in m['spending_by_category'][:5]:
            cat = c['category_primary'] or 'Uncategorized'
            lines.append(f"  {cat}: ${float(c['total']):,.2f} ({c['txn_count']})")
        lines.append("")

        # Bills
        lines.append(f"📋 <b>BILLS</b>")
        lines.append(f"  Expected: ${float(b['total_expected']):,.2f}")
        lines.append(f"  Remaining: ${float(b['total_remaining']):,.2f}")
        if b['overdue']:
            lines.append("  ⚠️ <b>POSSIBLY UNPAID:</b>")
            for bill in b['overdue'][:5]:
                lines.append(f"    Day {bill['expected_day']}: {bill['merchant_name']} ${float(bill['expected_amount'] or 0):,.2f}")
        lines.append("")

        # Trouble spots
        lines.append("🔴 <b>WATCH</b>")
        lines.append(f"  Cash: ${float(cash['total']):,.2f} ({len(cash['withdrawals'])} pulls)")
        lines.append(f"  Fast food: ${float(ff['total']):,.2f} ({ff['count']} hits)")
        lines.append("")

        # Decision prompts
        lines.append("✏️ <b>DECISIONS THIS WEEK</b>")
        lines.append("  □ Spending limit rest of month?")
        lines.append("  □ Subscriptions to cut?")
        lines.append("  □ Extra CC payment this month?")
        lines.append("  □ Cash limit this week?")

        msg = "\n".join(lines)
        await update.message.reply_text(msg, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Review generation failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Review failed: {str(e)}")
