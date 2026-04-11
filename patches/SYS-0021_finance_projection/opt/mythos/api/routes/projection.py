#!/usr/bin/env python3
"""
Mythos API - Finance Projection Endpoint
/opt/mythos/api/routes/projection.py

Returns a full-month daily projection with per-account running balances.
Shows every day of the month with income/bills mapped to specific accounts.

SYS-0021: Finance Projection Page
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/finance", tags=["finance"])


def get_db():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


def json_response(data):
    return JSONResponse(content=json.loads(json.dumps(data, cls=DecimalEncoder)))


def _get_account_balances(cur):
    """Get current balance for USAA and Sunmark checking accounts."""
    import sys
    sys.path.insert(0, '/opt/mythos/telegram_bot/handlers')
    from forecast_handler import get_current_balances
    balances = get_current_balances(cur, overview_only=True)
    return {
        'USAA': Decimal(str(balances.get('USAA', {}).get('balance', 0))),
        'SUN': Decimal(str(balances.get('SUN', {}).get('balance', 0))),
    }


def _get_biweekly_dates(year, month, last_known_date=None):
    """
    Calculate biweekly pay dates for a given month.
    If last_known_date provided, project forward in 14-day intervals.
    Otherwise fall back to 1st and 15th approximation.
    """
    if last_known_date:
        dates = []
        d = last_known_date
        # Walk forward from last known date
        while d.month < month or d.year < year:
            d = d + timedelta(days=14)
        # Now d is at or past target month
        while d.year == year and d.month == month:
            dates.append(d)
            d = d + timedelta(days=14)
        # Also check if walking backward from first found date gives another in-month date
        if dates:
            check = dates[0] - timedelta(days=14)
            if check.year == year and check.month == month:
                dates.insert(0, check)
        return dates
    else:
        # Fallback: 1st and 15th
        dim = monthrange(year, month)[1]
        return [date(year, month, 1), date(year, month, 15)]


@router.get("/projection")
async def get_projection(
    month: Optional[str] = Query(default=None, description="YYYY-MM format"),
):
    """
    Full-month daily projection with per-account balances.
    Returns every day of the month with running USAA and Sunmark balances,
    plus all income/bill events mapped to their accounts.
    """
    # Parse month
    if month:
        try:
            parts = month.split('-')
            year, mon = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            year, mon = datetime.now().year, datetime.now().month
    else:
        year, mon = datetime.now().year, datetime.now().month

    today = date.today()
    days_in_month = monthrange(year, mon)[1]
    month_start = date(year, mon, 1)
    month_end = date(year, mon, days_in_month)
    month_key = f"{year}-{mon:02d}"

    conn = get_db()
    cur = conn.cursor()

    # ── 1. Get current account balances ─────────────────────
    acct_balances = _get_account_balances(cur)

    # ── 2. Get all recurring bills ──────────────────────────
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.frequency, rb.category_primary, a.abbreviation as acct
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true AND rb.expected_day IS NOT NULL
        ORDER BY rb.expected_day
    """)
    all_bills = [dict(r) for r in cur.fetchall()]

    # ── 3. Get all recurring income ─────────────────────────
    cur.execute("""
        SELECT ri.id, ri.source_name, ri.expected_amount, ri.expected_day,
               ri.frequency, ri.category_primary, a.abbreviation as acct
        FROM recurring_income ri
        LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true
        ORDER BY ri.expected_day NULLS LAST
    """)
    all_income = [dict(r) for r in cur.fetchall()]

    # ── 4. Get last known biweekly pay date ─────────────────
    cur.execute("""
        SELECT MAX(transaction_date) as last_pay
        FROM transactions
        WHERE (description ILIKE '%DFAS%' OR category_primary = 'Paycheck')
          AND amount > 0
    """)
    row = cur.fetchone()
    last_pay_date = row['last_pay'] if row else None

    # ── 5. Get actual transactions for the month ────────────
    cur.execute("""
        SELECT t.transaction_date, t.description, t.amount, t.category_primary,
               a.abbreviation as acct
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date BETWEEN %s AND %s
          AND t.description != 'Balance checkpoint'
        ORDER BY t.transaction_date, t.id
    """, (month_start, month_end))
    actual_txns = [dict(r) for r in cur.fetchall()]

    # ── 6. Get bill overrides for this month ────────────────
    cur.execute("""
        SELECT bill_id, is_paid, paid_amount, paid_date
        FROM bill_overrides WHERE month = %s
    """, (month_key,))
    overrides = {r['bill_id']: dict(r) for r in cur.fetchall()}

    conn.close()

    # ── 7. Build biweekly pay dates for target month ────────
    biweekly_dates = _get_biweekly_dates(year, mon, last_pay_date)

    # ── 8. Map events to dates ──────────────────────────────
    # Bills by date
    bills_by_date = {}
    for bill in all_bills:
        day = min(bill['expected_day'], days_in_month)
        try:
            bill_date = date(year, mon, day)
        except ValueError:
            continue
        bills_by_date.setdefault(bill_date, []).append({
            'id': bill['id'],
            'name': bill['merchant_name'],
            'amount': float(bill['expected_amount']),
            'category': bill['category_primary'],
            'acct': bill['acct'],  # which account it comes from
        })

    # Income by date
    income_by_date = {}
    for inc in all_income:
        freq = inc['frequency']
        acct = inc['acct']

        if freq == 'biweekly':
            # Use calculated biweekly dates
            for pay_date in biweekly_dates:
                income_by_date.setdefault(pay_date, []).append({
                    'id': inc['id'],
                    'source': inc['source_name'],
                    'amount': float(inc['expected_amount']),
                    'category': inc['category_primary'],
                    'acct': acct,
                })
        elif inc['expected_day']:
            day = min(inc['expected_day'], days_in_month)
            try:
                inc_date = date(year, mon, day)
            except ValueError:
                continue
            income_by_date.setdefault(inc_date, []).append({
                'id': inc['id'],
                'source': inc['source_name'],
                'amount': float(inc['expected_amount']),
                'category': inc['category_primary'],
                'acct': acct,
            })

    # Actual transactions by date and account
    actual_by_date = {}
    for txn in actual_txns:
        d = txn['transaction_date']
        actual_by_date.setdefault(d, []).append({
            'description': txn['description'],
            'amount': float(txn['amount']),
            'category': txn['category_primary'],
            'acct': txn['acct'],
        })

    # ── 9. Build day-by-day projection ──────────────────────
    # Start from current balances and work backward to month start,
    # or forward from month start
    usaa_running = float(acct_balances['USAA'])
    sun_running = float(acct_balances['SUN'])

    # If we're looking at the current month, we need to:
    # - Use actual transactions for days up to today
    # - Use projected bills/income for future days
    # - The starting balance = current balance adjusted backward
    is_current_month = (year == today.year and mon == today.month)
    is_past_month = (date(year, mon, days_in_month) < today)
    is_future_month = (month_start > today)

    if is_current_month:
        # Walk backward from today's balance to month start
        # Subtract future projected events, add back past actual events
        # Actually simpler: walk forward from a calculated start

        # Calculate what happened between month start and today from actual txns
        usaa_actual_change = 0.0
        sun_actual_change = 0.0
        for d in sorted(actual_by_date.keys()):
            if d > today:
                break
            for txn in actual_by_date[d]:
                if txn['acct'] == 'USAA':
                    usaa_actual_change += txn['amount']
                elif txn['acct'] == 'SUN':
                    sun_actual_change += txn['amount']

        # Starting balance = current balance - all actual changes this month
        usaa_start = usaa_running - usaa_actual_change
        sun_start = sun_running - sun_actual_change

    elif is_future_month:
        # For future months, project forward from current balances
        # through the rest of current month first, then into target month
        # Simplified: use current balances and apply current month remaining
        # projected events, then target month events
        usaa_start = usaa_running
        sun_start = sun_running

        # Apply remaining current month projected events
        if today.month != mon or today.year != year:
            curr_days = monthrange(today.year, today.month)[1]
            for day_num in range(today.day + 1, curr_days + 1):
                d = date(today.year, today.month, day_num)
                # Current month bills
                for bill in all_bills:
                    bday = min(bill['expected_day'], curr_days)
                    if bday == day_num:
                        amt = float(bill['expected_amount'])
                        if bill['acct'] == 'USAA':
                            usaa_start -= amt
                        elif bill['acct'] == 'SUN':
                            sun_start -= amt
                        else:
                            usaa_start -= amt  # default to USAA
                # Current month income
                for inc in all_income:
                    if inc['frequency'] == 'biweekly':
                        curr_biweekly = _get_biweekly_dates(today.year, today.month, last_pay_date)
                        if d in curr_biweekly:
                            amt = float(inc['expected_amount'])
                            if inc['acct'] == 'USAA':
                                usaa_start += amt
                            elif inc['acct'] == 'SUN':
                                sun_start += amt
                    elif inc['expected_day']:
                        iday = min(inc['expected_day'], curr_days)
                        if iday == day_num:
                            amt = float(inc['expected_amount'])
                            if inc['acct'] == 'USAA':
                                usaa_start += amt
                            elif inc['acct'] == 'SUN':
                                sun_start += amt
    else:
        # Past month — just use actual transactions
        # Start from current balance, walk backward through all months between
        # This is complex; for now, show actuals only
        usaa_start = usaa_running
        sun_start = sun_running

    # ── 10. Generate daily rows ─────────────────────────────
    days = []
    usaa_bal = usaa_start
    sun_bal = sun_start

    for day_num in range(1, days_in_month + 1):
        d = date(year, mon, day_num)
        is_past = d < today
        is_today_flag = d == today
        is_future = d > today

        day_events = []
        usaa_day_change = 0.0
        sun_day_change = 0.0

        if is_current_month and (is_past or is_today_flag):
            # Use actual transactions
            for txn in actual_by_date.get(d, []):
                day_events.append({
                    'type': 'income' if txn['amount'] > 0 else 'expense',
                    'name': txn['description'],
                    'amount': abs(txn['amount']),
                    'acct': txn['acct'],
                    'category': txn['category'],
                    'actual': True,
                })
                if txn['acct'] == 'USAA':
                    usaa_day_change += txn['amount']
                elif txn['acct'] == 'SUN':
                    sun_day_change += txn['amount']
                else:
                    # Other accounts — don't affect projection
                    pass
        else:
            # Use projected bills/income
            for bill in bills_by_date.get(d, []):
                day_events.append({
                    'type': 'bill',
                    'name': bill['name'],
                    'amount': bill['amount'],
                    'acct': bill['acct'],
                    'category': bill['category'],
                    'actual': False,
                })
                if bill['acct'] == 'USAA':
                    usaa_day_change -= bill['amount']
                elif bill['acct'] == 'SUN':
                    sun_day_change -= bill['amount']
                else:
                    # Unassigned bills — split to USAA by default
                    usaa_day_change -= bill['amount']

            for inc in income_by_date.get(d, []):
                day_events.append({
                    'type': 'income',
                    'name': inc['source'],
                    'amount': inc['amount'],
                    'acct': inc['acct'],
                    'category': inc['category'],
                    'actual': False,
                })
                if inc['acct'] == 'USAA':
                    usaa_day_change += inc['amount']
                elif inc['acct'] == 'SUN':
                    sun_day_change += inc['amount']
                else:
                    usaa_day_change += inc['amount']

        usaa_bal += usaa_day_change
        sun_bal += sun_day_change

        days.append({
            'date': d.isoformat(),
            'day': day_num,
            'weekday': d.strftime('%a'),
            'is_past': is_past,
            'is_today': is_today_flag,
            'is_future': is_future,
            'is_weekend': d.weekday() >= 5,
            'usaa_balance': round(usaa_bal, 2),
            'sun_balance': round(sun_bal, 2),
            'combined_balance': round(usaa_bal + sun_bal, 2),
            'usaa_change': round(usaa_day_change, 2),
            'sun_change': round(sun_day_change, 2),
            'combined_change': round(usaa_day_change + sun_day_change, 2),
            'events': day_events,
            'has_activity': len(day_events) > 0,
        })

    # ── 11. Compute summary stats ───────────────────────────
    combined_balances = [d['combined_balance'] for d in days]
    usaa_balances = [d['usaa_balance'] for d in days]
    sun_balances = [d['sun_balance'] for d in days]

    lowest_combined = min(combined_balances) if combined_balances else 0
    lowest_combined_date = days[combined_balances.index(lowest_combined)]['date'] if combined_balances else None

    total_income = sum(
        e['amount'] for d in days for e in d['events']
        if e['type'] == 'income'
    )
    total_bills = sum(
        e['amount'] for d in days for e in d['events']
        if e['type'] in ('bill', 'expense') and e.get('category') not in ('Transfer', 'Credit Card Payment')
    )

    return json_response({
        'month': month_key,
        'month_label': date(year, mon, 1).strftime('%B %Y'),
        'days_in_month': days_in_month,
        'is_current_month': is_current_month,
        'starting': {
            'usaa': round(usaa_start, 2),
            'sun': round(sun_start, 2),
            'combined': round(usaa_start + sun_start, 2),
        },
        'ending': {
            'usaa': round(usaa_bal, 2),
            'sun': round(sun_bal, 2),
            'combined': round(usaa_bal + sun_bal, 2),
        },
        'lowest': {
            'combined': round(lowest_combined, 2),
            'combined_date': lowest_combined_date,
            'usaa': round(min(usaa_balances), 2) if usaa_balances else 0,
            'sun': round(min(sun_balances), 2) if sun_balances else 0,
        },
        'totals': {
            'income': round(total_income, 2),
            'bills': round(total_bills, 2),
            'net': round(total_income - total_bills, 2),
        },
        'days': days,
    })
