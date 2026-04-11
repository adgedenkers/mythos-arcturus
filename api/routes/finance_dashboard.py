#!/usr/bin/env python3
"""
Mythos API - Finance Dashboard v2 Routes
/opt/mythos/api/routes/finance_dashboard.py

Provides combined endpoints for the new finance dashboard:
- /api/finance/v2/dashboard — accounts with next events (income/bills)
- /api/finance/v2/bills-detail — bills with full payment history
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from typing import Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/finance/v2", tags=["finance-v2"])


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


@router.get("/dashboard")
async def get_dashboard():
    """
    Main dashboard view: each account with its current balance,
    upcoming bills, and expected income within the next 14 days.
    """
    conn = get_db()
    cur = conn.cursor()
    today = date.today()
    lookahead = today + timedelta(days=14)

    # All active accounts
    cur.execute("""
        SELECT id, bank_name, account_name, account_type,
               current_balance, balance_updated_at,
               credit_limit, min_payment, payment_due_day,
               include_in_overview
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
    accounts = [dict(r) for r in cur.fetchall()]

    # Upcoming bills (next 14 days)
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.category_primary, rb.notes, rb.frequency,
               a.id as account_id, a.bank_name as account_bank
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true AND rb.expected_day IS NOT NULL
        ORDER BY rb.expected_day
    """)
    all_bills = [dict(r) for r in cur.fetchall()]

    # Filter to bills due in next 14 days
    upcoming_bills = []
    for bill in all_bills:
        try:
            due_day = min(bill['expected_day'], monthrange(today.year, today.month)[1])
            due_date = date(today.year, today.month, due_day)
            # If due date has passed this month, look at next month
            if due_date < today:
                next_month = today.month + 1
                next_year = today.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                due_day = min(bill['expected_day'], monthrange(next_year, next_month)[1])
                due_date = date(next_year, next_month, due_day)
            if due_date <= lookahead:
                bill['due_date'] = due_date.isoformat()
                bill['days_until'] = (due_date - today).days
                upcoming_bills.append(bill)
        except (ValueError, TypeError):
            pass

    # Check if upcoming bills have been paid this month
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month, monthrange(today.year, today.month)[1])

    cur.execute("""
        SELECT bp.bill_id, bp.payment_date, bp.amount_paid
        FROM bill_payments bp
        WHERE bp.billing_month = %s
    """, (today.strftime('%Y-%m'),))
    paid_this_month = {}
    for r in cur.fetchall():
        paid_this_month[r['bill_id']] = dict(r)

    for bill in upcoming_bills:
        if bill['id'] in paid_this_month:
            bill['paid'] = True
            bill['paid_date'] = paid_this_month[bill['id']]['payment_date']
            bill['paid_amount'] = paid_this_month[bill['id']]['amount_paid']
        else:
            bill['paid'] = False

    # Upcoming income (next 14 days)
    cur.execute("""
        SELECT ri.id, ri.source_name, ri.description, ri.expected_amount,
               ri.expected_day, ri.frequency,
               a.id as account_id, a.bank_name as account_bank
        FROM recurring_income ri
        LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true
        ORDER BY ri.expected_day NULLS LAST
    """)
    all_income = [dict(r) for r in cur.fetchall()]

    upcoming_income = []
    for inc in all_income:
        if inc['expected_day']:
            try:
                inc_day = min(inc['expected_day'], monthrange(today.year, today.month)[1])
                inc_date = date(today.year, today.month, inc_day)
                if inc_date < today:
                    next_month = today.month + 1
                    next_year = today.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    inc_day = min(inc['expected_day'], monthrange(next_year, next_month)[1])
                    inc_date = date(next_year, next_month, inc_day)
                if inc_date <= lookahead:
                    inc['expected_date'] = inc_date.isoformat()
                    inc['days_until'] = (inc_date - today).days
                    upcoming_income.append(inc)
            except (ValueError, TypeError):
                pass
        elif inc['frequency'] == 'biweekly':
            # For biweekly without a fixed day, just include it
            inc['expected_date'] = None
            inc['days_until'] = None
            upcoming_income.append(inc)

    # Attach upcoming events to accounts
    for acct in accounts:
        acct['upcoming_bills'] = [
            b for b in upcoming_bills if b.get('account_id') == acct['id']
        ]
        acct['upcoming_income'] = [
            i for i in upcoming_income if i.get('account_id') == acct['id']
        ]
        # Calculate upcoming outflow for this account
        acct['upcoming_outflow'] = sum(
            float(b['expected_amount'] or 0)
            for b in acct['upcoming_bills']
            if not b.get('paid')
        )
        acct['upcoming_inflow'] = sum(
            float(i['expected_amount'] or 0)
            for i in acct['upcoming_income']
        )

    # Totals
    checking_total = sum(
        float(a['current_balance'] or 0) for a in accounts
        if a['account_type'] in ('checking', 'savings') and a['include_in_overview']
    )
    debt_total = sum(
        abs(float(a['current_balance'] or 0)) for a in accounts
        if a['account_type'] in ('credit', 'loan')
    )

    conn.close()
    return json_response({
        "as_of": today.isoformat(),
        "accounts": accounts,
        "checking_total": checking_total,
        "debt_total": debt_total,
        "net_worth": checking_total - debt_total,
        "upcoming_bills": upcoming_bills,
        "upcoming_income": upcoming_income,
    })


@router.get("/bills-detail")
async def get_bills_detail(
    month: Optional[str] = Query(default=None),
):
    """
    Bills with full payment history — master/detail view.
    Each bill includes all matched payments across all months.
    """
    conn = get_db()
    cur = conn.cursor()

    if month:
        try:
            parts = month.split('-')
            year, mon = int(parts[0]), int(parts[1])
        except:
            year, mon = datetime.now().year, datetime.now().month
    else:
        year, mon = datetime.now().year, datetime.now().month

    month_key = f"{year}-{mon:02d}"
    month_start = date(year, mon, 1)
    month_end = date(year, mon, monthrange(year, mon)[1])

    # All active bills
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.merchant_pattern, rb.expected_amount,
               rb.expected_day, rb.frequency, rb.category_primary,
               rb.amount_variance, rb.notes,
               a.bank_name as account_bank, a.account_name as account_name
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true
        ORDER BY rb.expected_day NULLS LAST, rb.merchant_name
    """)
    bills = [dict(r) for r in cur.fetchall()]

    # Get ALL payment history for each bill (last 12 months)
    twelve_months_ago = date(year - 1, mon, 1)
    cur.execute("""
        SELECT bp.bill_id, bp.payment_date, bp.amount_paid,
               bp.billing_month, bp.matched_automatically, bp.notes,
               t.description as txn_description,
               t.original_description as txn_original_description,
               a.bank_name as txn_bank
        FROM bill_payments bp
        LEFT JOIN transactions t ON bp.transaction_id = t.id
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE bp.payment_date >= %s
        ORDER BY bp.payment_date DESC
    """, (twelve_months_ago,))

    payments_by_bill = {}
    for r in cur.fetchall():
        bill_id = r['bill_id']
        if bill_id not in payments_by_bill:
            payments_by_bill[bill_id] = []
        payments_by_bill[bill_id].append(dict(r))

    # Also get auto-matched transactions for current month
    # (from the bills tracker logic)
    cur.execute("""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, a.bank_name as account_bank
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date BETWEEN %s AND %s AND t.amount < 0
        ORDER BY t.transaction_date
    """, (month_start, month_end))
    month_txns = [dict(r) for r in cur.fetchall()]

    # Auto-match current month
    used_txn_ids = set()
    for bill in bills:
        bill_name = bill['merchant_name'].lower()
        pattern = (bill.get('merchant_pattern') or '').lower()
        expected = float(bill['expected_amount'] or 0)
        variance = float(bill['amount_variance'] or 5.0)

        matched_txns = []
        for txn in month_txns:
            if txn['id'] in used_txn_ids:
                continue
            txn_desc = (txn['description'] or '').lower()
            txn_orig = (txn['original_description'] or '').lower()

            # Pattern match
            match = False
            if pattern and (pattern in txn_desc or pattern in txn_orig):
                match = True
            elif bill_name in txn_desc or bill_name in txn_orig:
                match = True

            if match:
                matched_txns.append(txn)
                used_txn_ids.add(txn['id'])

        bill['current_month_matches'] = matched_txns
        bill['current_month_total'] = sum(
            abs(float(t['amount'])) for t in matched_txns
        )
        bill['is_paid'] = len(matched_txns) > 0
        bill['payment_history'] = payments_by_bill.get(bill['id'], [])
        bill['payment_count'] = len(bill['payment_history'])

        # Due date
        if bill['expected_day']:
            try:
                due_day = min(bill['expected_day'], monthrange(year, mon)[1])
                due_date = date(year, mon, due_day)
                bill['due_date'] = due_date.isoformat()
                bill['overdue'] = (not bill['is_paid'] and due_date < date.today())
            except:
                bill['due_date'] = None
                bill['overdue'] = False
        else:
            bill['due_date'] = None
            bill['overdue'] = False

    paid_bills = [b for b in bills if b['is_paid']]
    unpaid_bills = [b for b in bills if not b['is_paid']]

    conn.close()
    return json_response({
        "month": month_key,
        "month_label": date(year, mon, 1).strftime("%B %Y"),
        "bills": bills,
        "paid_count": len(paid_bills),
        "unpaid_count": len(unpaid_bills),
        "total_expected": sum(float(b['expected_amount'] or 0) for b in bills),
        "total_paid": sum(b['current_month_total'] for b in paid_bills),
    })
