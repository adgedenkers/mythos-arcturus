#!/usr/bin/env python3
"""
Weekly Financial Review Generator
=================================
Generates a structured weekly financial snapshot for decision-making.
This is NOT another tracking tool. This is the thing you sit with
and use to steer.

Usage:
    python3 weekly_review.py                  # Current week review
    python3 weekly_review.py --json           # JSON output (for API)
    python3 weekly_review.py --week 2026-02-10  # Specific week starting date
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

import psycopg2
import psycopg2.extras


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def get_connection():
    import os
    from dotenv import load_dotenv
    load_dotenv('/opt/mythos/.env')
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )


def get_week_bounds(start_date=None):
    """Get Monday-Sunday bounds for the review week."""
    if start_date is None:
        today = date.today()
        # Find the most recent Monday
        start = today - timedelta(days=today.weekday())
    else:
        start = start_date
    end = start + timedelta(days=6)
    return start, end


def get_month_bounds():
    """Get current month bounds."""
    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return month_start, month_end


def fetch_account_balances(cur):
    """Current balances across all active accounts."""
    cur.execute("""
        SELECT abbreviation, bank_name, account_type, current_balance,
               credit_limit, min_payment, payment_due_day,
               balance_updated_at
        FROM accounts
        WHERE is_active = true
        ORDER BY
            CASE account_type
                WHEN 'checking' THEN 1
                WHEN 'credit' THEN 2
                WHEN 'loan' THEN 3
            END, id
    """)
    rows = cur.fetchall()

    checking_total = sum(r['current_balance'] for r in rows if r['account_type'] == 'checking')
    credit_total = sum(r['current_balance'] for r in rows if r['account_type'] == 'credit')
    loan_total = sum(r['current_balance'] for r in rows if r['account_type'] == 'loan')

    return {
        "accounts": [dict(r) for r in rows],
        "checking_total": checking_total,
        "credit_total": credit_total,
        "loan_total": loan_total,
        "net_position": checking_total + credit_total + loan_total,
    }


def fetch_week_transactions(cur, week_start, week_end):
    """All transactions for the review week."""
    cur.execute("""
        SELECT t.transaction_date, t.description, t.amount,
               t.category_primary, t.merchant_name,
               a.abbreviation as account
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date >= %s AND t.transaction_date <= %s
        ORDER BY t.transaction_date DESC, t.amount
    """, (week_start, week_end))
    return [dict(r) for r in cur.fetchall()]


def fetch_week_spending_by_category(cur, week_start, week_end):
    """Spending grouped by category for the week."""
    cur.execute("""
        SELECT category_primary,
               COUNT(*) as txn_count,
               SUM(ABS(amount))::numeric(10,2) as total
        FROM transactions
        WHERE amount < 0
          AND transaction_date >= %s AND transaction_date <= %s
        GROUP BY category_primary
        ORDER BY total DESC
    """, (week_start, week_end))
    return [dict(r) for r in cur.fetchall()]


def fetch_month_spending_by_category(cur, month_start, month_end):
    """Spending grouped by category for the full month so far."""
    today = date.today()
    cur.execute("""
        SELECT category_primary,
               COUNT(*) as txn_count,
               SUM(ABS(amount))::numeric(10,2) as total
        FROM transactions
        WHERE amount < 0
          AND transaction_date >= %s AND transaction_date <= %s
        GROUP BY category_primary
        ORDER BY total DESC
    """, (month_start, today))
    return [dict(r) for r in cur.fetchall()]


def fetch_income_this_month(cur, month_start):
    """Income received so far this month."""
    today = date.today()
    cur.execute("""
        SELECT category_primary,
               COUNT(*) as txn_count,
               SUM(amount)::numeric(10,2) as total
        FROM transactions
        WHERE amount > 0
          AND transaction_date >= %s AND transaction_date <= %s
          AND category_primary IN ('Income', 'Paycheck')
        GROUP BY category_primary
        ORDER BY total DESC
    """, (month_start, today))
    return [dict(r) for r in cur.fetchall()]


def fetch_expected_income(cur):
    """Expected monthly income from recurring_income."""
    cur.execute("""
        SELECT source_name, description, expected_amount, frequency,
               expected_day, account_id
        FROM recurring_income
        WHERE is_active = true
        ORDER BY expected_amount DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    # Calculate monthly total (biweekly = amount * 26/12)
    monthly = Decimal('0')
    for r in rows:
        if r['frequency'] == 'biweekly':
            monthly += r['expected_amount'] * Decimal('26') / Decimal('12')
        else:
            monthly += r['expected_amount']
    return {"sources": rows, "monthly_total": monthly}


def fetch_bills_status(cur, month_start):
    """Bills due this month and their payment status."""
    today = date.today()
    month_str = month_start.strftime('%Y-%m')

    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount,
               rb.expected_day, rb.category_primary, rb.account_id,
               a.abbreviation as account_abbr,
               bo.is_paid as override_paid,
               bo.paid_amount as override_amount
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        LEFT JOIN bill_overrides bo ON bo.bill_id = rb.id AND bo.month = %s
        WHERE rb.is_active = true
        ORDER BY rb.expected_day NULLS LAST
    """, (month_str,))

    bills = [dict(r) for r in cur.fetchall()]

    paid = []
    upcoming = []
    overdue = []

    for b in bills:
        day = b['expected_day']
        if b['override_paid']:
            paid.append(b)
        elif day is not None and day < today.day:
            # Due date has passed and not marked paid — could be auto-matched
            # but if no override, flag as potentially unpaid
            overdue.append(b)
        else:
            upcoming.append(b)

    total_expected = sum(b['expected_amount'] or 0 for b in bills)
    total_paid = sum(b['expected_amount'] or 0 for b in paid)

    return {
        "all_bills": bills,
        "paid": paid,
        "upcoming": upcoming,
        "overdue": overdue,
        "total_expected": total_expected,
        "total_paid_estimated": total_paid,
        "total_remaining": total_expected - total_paid,
    }


def fetch_large_transactions(cur, week_start, week_end, threshold=50):
    """Transactions over threshold that deserve attention."""
    cur.execute("""
        SELECT t.transaction_date, t.description, t.amount,
               t.category_primary, a.abbreviation as account
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE ABS(t.amount) >= %s
          AND t.transaction_date >= %s AND t.transaction_date <= %s
        ORDER BY ABS(t.amount) DESC
    """, (threshold, week_start, week_end))
    return [dict(r) for r in cur.fetchall()]


def fetch_cash_withdrawals(cur, month_start):
    """Cash withdrawals this month — the money black hole."""
    today = date.today()
    cur.execute("""
        SELECT transaction_date, description, ABS(amount)::numeric(10,2) as amount,
               a.abbreviation as account
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE category_primary = 'Cash'
          AND amount < 0
          AND transaction_date >= %s AND transaction_date <= %s
        ORDER BY transaction_date DESC
    """, (month_start, today))
    rows = [dict(r) for r in cur.fetchall()]
    total = sum(r['amount'] for r in rows)
    return {"withdrawals": rows, "total": total}


def fetch_fast_food_spending(cur, month_start):
    """Fast food this month — death by a thousand cuts."""
    today = date.today()
    cur.execute("""
        SELECT COUNT(*) as count,
               SUM(ABS(amount))::numeric(10,2) as total
        FROM transactions
        WHERE category_primary = 'Fast Food'
          AND amount < 0
          AND transaction_date >= %s AND transaction_date <= %s
    """, (month_start, today))
    row = cur.fetchone()
    return {"count": row['count'], "total": row['total'] or Decimal('0')}


def calculate_runway(balances, bills_remaining, daily_avg_discretionary):
    """How many days until checking accounts hit zero at current pace."""
    available = balances['checking_total']
    # Subtract NBT estate (id=5, abbreviation NBT) — not spending money
    for a in balances['accounts']:
        if a['abbreviation'] == 'NBT':
            available -= a['current_balance']
        if a['abbreviation'] == 'DVA':
            available -= a['current_balance']
        if a['abbreviation'] == 'SID':
            available -= a['current_balance']

    # Subtract remaining bills this month
    remaining_after_bills = available - bills_remaining

    if daily_avg_discretionary > 0:
        days = int(remaining_after_bills / daily_avg_discretionary)
    else:
        days = 999

    return {
        "spendable_cash": available,
        "after_remaining_bills": remaining_after_bills,
        "daily_discretionary_avg": daily_avg_discretionary,
        "runway_days": days,
    }


def generate_review(week_start_str=None):
    """Generate the complete weekly review."""
    if week_start_str:
        ws = datetime.strptime(week_start_str, '%Y-%m-%d').date()
    else:
        ws = None

    week_start, week_end = get_week_bounds(ws)
    month_start, month_end = get_month_bounds()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        balances = fetch_account_balances(cur)
        week_txns = fetch_week_transactions(cur, week_start, week_end)
        week_spending = fetch_week_spending_by_category(cur, week_start, week_end)
        month_spending = fetch_month_spending_by_category(cur, month_start, month_end)
        month_income = fetch_income_this_month(cur, month_start)
        expected_income = fetch_expected_income(cur)
        bills = fetch_bills_status(cur, month_start)
        large_txns = fetch_large_transactions(cur, week_start, week_end)
        cash = fetch_cash_withdrawals(cur, month_start)
        fast_food = fetch_fast_food_spending(cur, month_start)

        # Calculate daily discretionary average for the month so far
        days_elapsed = (date.today() - month_start).days or 1
        total_month_discretionary = sum(
            c['total'] for c in month_spending
            if c['category_primary'] not in (
                'Transfer', 'Loan', 'Insurance', 'Credit Card Payment'
            )
        )
        daily_avg = total_month_discretionary / Decimal(str(days_elapsed))

        runway = calculate_runway(
            balances,
            bills['total_remaining'],
            daily_avg
        )

        # Week totals
        week_total_out = sum(t['amount'] for t in week_txns if t['amount'] < 0)
        week_total_in = sum(t['amount'] for t in week_txns if t['amount'] > 0)

        # Month totals
        month_total_spending = sum(c['total'] for c in month_spending)
        month_total_income = sum(c['total'] for c in month_income)

        # Discretionary spending (exclude fixed categories)
        fixed_categories = {
            'Transfer', 'Loan', 'Insurance', 'Credit Card Payment',
            'Internet', 'Utilities', 'Bills & Utilities'
        }
        month_discretionary = sum(
            c['total'] for c in month_spending
            if c['category_primary'] not in fixed_categories
        )
        month_fixed = month_total_spending - month_discretionary

        review = {
            "generated_at": datetime.now().isoformat(),
            "review_week": {
                "start": week_start,
                "end": week_end,
            },
            "review_month": {
                "start": month_start,
                "end": month_end,
                "days_elapsed": days_elapsed,
                "days_remaining": (month_end - date.today()).days,
            },

            # === SECTION 1: WHERE ARE WE RIGHT NOW ===
            "balances": balances,

            # === SECTION 2: WHAT HAPPENED THIS WEEK ===
            "week": {
                "total_in": week_total_in,
                "total_out": abs(week_total_out),
                "net": week_total_in + week_total_out,
                "spending_by_category": week_spending,
                "large_transactions": large_txns,
                "transaction_count": len(week_txns),
            },

            # === SECTION 3: MONTH SO FAR ===
            "month": {
                "total_income": month_total_income,
                "total_spending": month_total_spending,
                "net": month_total_income - month_total_spending,
                "spending_by_category": month_spending,
                "discretionary_spending": month_discretionary,
                "fixed_spending": month_fixed,
                "daily_average_discretionary": round(daily_avg, 2),
                "income_received": month_income,
            },

            # === SECTION 4: BILLS ===
            "bills": bills,

            # === SECTION 5: TROUBLE SPOTS ===
            "alerts": {
                "cash_withdrawals": cash,
                "fast_food": fast_food,
                "runway": runway,
            },

            # === SECTION 6: EXPECTED INCOME ===
            "expected_income": expected_income,

            # === SECTION 7: DECISIONS NEEDED ===
            # This section is intentionally empty — it's for Adge to fill in
            "decisions": {
                "notes": "",
                "action_items": [],
            },
        }

        return review

    finally:
        cur.close()
        conn.close()


def print_terminal_review(review):
    """Print a clean terminal-friendly review."""
    r = review
    week = r['review_week']
    month = r['review_month']

    print("=" * 60)
    print(f"  WEEKLY FINANCIAL REVIEW")
    print(f"  Week of {week['start']} → {week['end']}")
    print(f"  Generated: {r['generated_at'][:16]}")
    print("=" * 60)

    # Balances
    print(f"\n{'─' * 60}")
    print("  WHERE WE STAND")
    print(f"{'─' * 60}")
    bal = r['balances']
    for a in bal['accounts']:
        marker = ""
        if a['account_type'] == 'credit' and a['credit_limit']:
            usage = abs(float(a['current_balance'])) / float(a['credit_limit']) * 100
            if usage > 85:
                marker = " ⚠️ NEAR LIMIT"
            elif usage > 50:
                marker = f" ({usage:.0f}% used)"
        print(f"    {a['abbreviation']:8s} {a['bank_name']:18s} ${float(a['current_balance']):>10,.2f}{marker}")
    print(f"    {'':8s} {'':18s} {'─' * 14}")
    print(f"    {'':8s} {'Checking total':18s} ${float(bal['checking_total']):>10,.2f}")
    print(f"    {'':8s} {'Credit card debt':18s} ${float(bal['credit_total']):>10,.2f}")
    print(f"    {'':8s} {'Loan debt':18s} ${float(bal['loan_total']):>10,.2f}")
    print(f"    {'':8s} {'NET POSITION':18s} ${float(bal['net_position']):>10,.2f}")

    # Runway
    print(f"\n{'─' * 60}")
    print("  RUNWAY")
    print(f"{'─' * 60}")
    run = r['alerts']['runway']
    print(f"    Spendable cash (excl NBT/DVA/SID): ${float(run['spendable_cash']):>10,.2f}")
    print(f"    After remaining bills this month:   ${float(run['after_remaining_bills']):>10,.2f}")
    print(f"    Daily discretionary avg:            ${float(run['daily_discretionary_avg']):>10,.2f}")
    print(f"    Days until zero at this pace:        {run['runway_days']} days")

    # Week summary
    print(f"\n{'─' * 60}")
    print("  THIS WEEK")
    print(f"{'─' * 60}")
    w = r['week']
    print(f"    Money in:  ${float(w['total_in']):>10,.2f}")
    print(f"    Money out: ${float(w['total_out']):>10,.2f}")
    print(f"    Net:       ${float(w['net']):>10,.2f}")
    if w['spending_by_category']:
        print(f"\n    Category breakdown:")
        for c in w['spending_by_category'][:10]:
            print(f"      {c['category_primary'] or 'Uncategorized':25s} ${float(c['total']):>8,.2f}  ({c['txn_count']} txns)")

    # Big transactions
    if w['large_transactions']:
        print(f"\n    Large transactions (>$50):")
        for t in w['large_transactions']:
            direction = "IN " if t['amount'] > 0 else "OUT"
            print(f"      {direction} ${abs(float(t['amount'])):>8,.2f}  {t['description'][:35]}")

    # Month so far
    print(f"\n{'─' * 60}")
    print(f"  MONTH SO FAR  (day {month['days_elapsed']} of ~{month['days_elapsed'] + month['days_remaining']})")
    print(f"{'─' * 60}")
    m = r['month']
    print(f"    Income received:       ${float(m['total_income']):>10,.2f}")
    print(f"    Total spent:           ${float(m['total_spending']):>10,.2f}")
    print(f"      Fixed (bills/utils): ${float(m['fixed_spending']):>10,.2f}")
    print(f"      Discretionary:       ${float(m['discretionary_spending']):>10,.2f}")
    print(f"    Net:                   ${float(m['net']):>10,.2f}")

    print(f"\n    Top spending categories:")
    for c in m['spending_by_category'][:10]:
        bar_len = min(int(float(c['total']) / 50), 30)
        bar = "█" * bar_len
        print(f"      {c['category_primary'] or 'Uncategorized':25s} ${float(c['total']):>8,.2f} {bar}")

    # Bills
    print(f"\n{'─' * 60}")
    print("  BILLS THIS MONTH")
    print(f"{'─' * 60}")
    b = r['bills']
    print(f"    Total expected: ${float(b['total_expected']):>10,.2f}")
    print(f"    Paid/matched:   ${float(b['total_paid_estimated']):>10,.2f}")
    print(f"    Remaining:      ${float(b['total_remaining']):>10,.2f}")
    if b['overdue']:
        print(f"\n    ⚠️  POSSIBLY UNPAID (due date passed):")
        for bill in b['overdue']:
            print(f"      Day {bill['expected_day']:2d}: {bill['merchant_name']:25s} ${float(bill['expected_amount'] or 0):>8,.2f}")
    if b['upcoming']:
        print(f"\n    Coming up:")
        for bill in b['upcoming']:
            day = bill['expected_day'] or '??'
            print(f"      Day {str(day):2s}: {bill['merchant_name']:25s} ${float(bill['expected_amount'] or 0):>8,.2f}")

    # Trouble spots
    print(f"\n{'─' * 60}")
    print("  TROUBLE SPOTS")
    print(f"{'─' * 60}")
    cash = r['alerts']['cash_withdrawals']
    ff = r['alerts']['fast_food']
    print(f"    Cash withdrawals this month: ${float(cash['total']):>8,.2f} ({len(cash['withdrawals'])} withdrawals)")
    print(f"    Fast food this month:        ${float(ff['total']):>8,.2f} ({ff['count']} transactions)")

    # Decision space
    print(f"\n{'─' * 60}")
    print("  DECISIONS THIS WEEK")
    print(f"{'─' * 60}")
    print("    □ What's the spending limit for the rest of the month?")
    print("    □ Any subscriptions to cut?")
    print("    □ Which credit card gets extra payment?")
    print("    □ Cash withdrawal limit this week?")
    print("    □ Anything coming up that needs to be set aside?")
    print(f"\n{'─' * 60}")
    print("    Write your notes below or discuss with Rebecca.")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly Financial Review")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--week", type=str, help="Week start date (YYYY-MM-DD)")
    args = parser.parse_args()

    review = generate_review(args.week)

    if args.json:
        print(json.dumps(review, cls=DecimalEncoder, indent=2))
    else:
        print_terminal_review(review)
