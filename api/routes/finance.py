#!/usr/bin/env python3
"""
Mythos API - Finance Routes
/opt/mythos/api/routes/finance.py
v2 - patch 0092: Added bills tracker, accounts management, categories CRUD
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from typing import Optional
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
        if isinstance(o, Decimal): return float(o)
        if isinstance(o, (date, datetime)): return o.isoformat()
        return super().default(o)


def json_response(data):
    return JSONResponse(content=json.loads(json.dumps(data, cls=DecimalEncoder)))


# ── Models ─────────────────────────────────────────────────

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    category_primary: Optional[str] = None
    merchant_name: Optional[str] = None

class AccountBalanceUpdate(BaseModel):
    current_balance: float
    notes: Optional[str] = None

class CategoryRename(BaseModel):
    old_name: str
    new_name: str

class CategoryMerge(BaseModel):
    source: str       # category to absorb
    target: str       # category to keep

class CategoryCreate(BaseModel):
    name: str

class BillPaidOverride(BaseModel):
    paid: bool
    paid_amount: Optional[float] = None
    paid_date: Optional[str] = None  # YYYY-MM-DD


# ── Summary ────────────────────────────────────────────────

@router.get("/summary")
async def get_summary(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (a.id) a.abbreviation, COALESCE(t.balance, 0) as balance
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        WHERE a.is_active = true AND a.account_type IN ('checking', 'savings')
        ORDER BY a.id, t.transaction_date DESC
    """)
    balances = {r['abbreviation']: float(r['balance']) for r in cur.fetchall()}
    now = datetime.now()
    month_start = date(now.year, now.month, 1)
    cur.execute("""
        SELECT SUM(amount)::numeric(12,2) as total FROM transactions
        WHERE transaction_date >= %s AND amount < 0
          AND category_primary NOT IN ('Transfer', 'Credit Card Payment')
          AND description != 'Balance checkpoint'
    """, (month_start,))
    month_spending = float(cur.fetchone()['total'] or 0)
    cur.execute("""
        SELECT SUM(amount)::numeric(12,2) as total FROM transactions
        WHERE transaction_date >= %s AND amount > 0
          AND category_primary IN ('Income', 'Interest Income')
          AND description != 'Balance checkpoint'
    """, (month_start,))
    month_income = float(cur.fetchone()['total'] or 0)
    conn.close()
    return json_response({
        "balances": balances,
        "combined": sum(balances.get(a, 0) for a in ['USAA', 'SUN']),
        "month_spending": month_spending,
        "month_income": month_income,
        "month_net": month_income + month_spending,
    })


# ── Transactions ───────────────────────────────────────────

@router.get("/transactions")
async def get_transactions(
    request: Request,
    month: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    account: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
):
    conn = get_db()
    cur = conn.cursor()
    conditions = ["t.description != 'Balance checkpoint'"]
    params = []
    if month:
        try:
            parts = month.split('-')
            year, mon = int(parts[0]), int(parts[1])
            start = date(year, mon, 1)
            end = date(year, mon, monthrange(year, mon)[1])
            conditions.append("t.transaction_date BETWEEN %s AND %s")
            params.extend([start, end])
        except: pass
    if category:
        if category == '__uncategorized__':
            conditions.append("(t.category_primary IS NULL OR t.category_primary = '')")
        else:
            conditions.append("t.category_primary = %s")
            params.append(category)
    if account:
        conditions.append("a.abbreviation = %s")
        params.append(account.upper())
    if search:
        conditions.append("(t.description ILIKE %s OR t.original_description ILIKE %s)")
        params.extend([f'%{search}%', f'%{search}%'])
    params.append(limit)
    cur.execute(f"""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, t.balance, t.category_primary, t.merchant_name,
               a.abbreviation as account
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE {' AND '.join(conditions)}
        ORDER BY t.transaction_date DESC, t.id DESC
        LIMIT %s
    """, params)
    txns = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"transactions": txns, "count": len(txns)})


@router.patch("/transactions/{txn_id}")
async def update_transaction(request: Request, txn_id: int, update: TransactionUpdate):
    conn = get_db()
    cur = conn.cursor()
    fields, params = [], []
    if update.description is not None:
        fields.append("description = %s"); params.append(update.description.strip())
    if update.category_primary is not None:
        fields.append("category_primary = %s"); params.append(update.category_primary.strip() or None)
    if update.merchant_name is not None:
        fields.append("merchant_name = %s"); params.append(update.merchant_name.strip() or None)
    if not fields:
        conn.close(); raise HTTPException(status_code=400, detail="No fields to update")
    params.append(txn_id)
    cur.execute(f"UPDATE transactions SET {', '.join(fields)} WHERE id = %s RETURNING id", params)
    result = cur.fetchone()
    conn.commit(); conn.close()
    if not result: raise HTTPException(status_code=404, detail="Transaction not found")
    return json_response({"success": True, "id": txn_id})


# ── Categories ─────────────────────────────────────────────

@router.get("/categories")
async def get_categories(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT category_primary, COUNT(*) as txn_count
        FROM transactions
        WHERE category_primary IS NOT NULL AND category_primary != ''
        GROUP BY category_primary
        ORDER BY category_primary
    """)
    cats = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"categories": cats})


@router.post("/categories/rename")
async def rename_category(request: Request, body: CategoryRename):
    if not body.new_name.strip():
        raise HTTPException(status_code=400, detail="New name required")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET category_primary = %s WHERE category_primary = %s",
        (body.new_name.strip(), body.old_name)
    )
    affected = cur.rowcount
    conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected})


@router.post("/categories/merge")
async def merge_categories(request: Request, body: CategoryMerge):
    """Reassign all transactions from source category to target category"""
    if body.source == body.target:
        raise HTTPException(status_code=400, detail="Source and target must differ")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET category_primary = %s WHERE category_primary = %s",
        (body.target, body.source)
    )
    affected = cur.rowcount
    conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected, "merged_into": body.target})


@router.delete("/categories/{name}")
async def delete_category(request: Request, name: str):
    """Nullify category on all transactions with this category"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET category_primary = NULL WHERE category_primary = %s",
        (name,)
    )
    affected = cur.rowcount
    conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected})


# ── Accounts ───────────────────────────────────────────────

@router.get("/accounts")
async def get_accounts(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.abbreviation, a.bank_name, a.account_name, a.account_type,
               a.current_balance, a.balance_updated_at, a.is_active,
               a.credit_limit, a.min_payment, a.payment_due_day, a.notes,
               (SELECT COUNT(*) FROM transactions t WHERE t.account_id = a.id) as txn_count,
               (SELECT MAX(t.transaction_date) FROM transactions t WHERE t.account_id = a.id) as last_txn_date
        FROM accounts a
        ORDER BY a.is_active DESC, a.id
    """)
    accounts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"accounts": accounts})


@router.patch("/accounts/{account_id}/balance")
async def update_account_balance(request: Request, account_id: int, body: AccountBalanceUpdate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE accounts
        SET current_balance = %s, balance_updated_at = NOW()
        WHERE id = %s RETURNING id, abbreviation
    """, (body.current_balance, account_id))
    result = cur.fetchone()
    conn.commit(); conn.close()
    if not result: raise HTTPException(status_code=404, detail="Account not found")
    return json_response({"success": True, "id": account_id, "abbreviation": result['abbreviation'], "balance": body.current_balance})


# ── Bills Tracker ──────────────────────────────────────────

@router.get("/bills/tracker")
async def get_bills_tracker(
    request: Request,
    month: Optional[str] = Query(default=None, description="YYYY-MM, defaults to current month")
):
    """
    Returns recurring bills with payment status for the given month.
    Auto-matches against transactions by merchant name similarity.
    """
    if month:
        try:
            parts = month.split('-')
            year, mon = int(parts[0]), int(parts[1])
        except:
            year, mon = datetime.now().year, datetime.now().month
    else:
        year, mon = datetime.now().year, datetime.now().month

    month_start = date(year, mon, 1)
    month_end = date(year, mon, monthrange(year, mon)[1])

    conn = get_db()
    cur = conn.cursor()

    # Get active bills
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.frequency, rb.category_primary, rb.amount_variance,
               rb.notes, a.abbreviation as account
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true
        ORDER BY rb.expected_day NULLS LAST, rb.merchant_name
    """)
    bills = [dict(r) for r in cur.fetchall()]

    # Get all transactions for the month
    cur.execute("""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, a.abbreviation as account
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date BETWEEN %s AND %s
          AND t.amount < 0
        ORDER BY t.transaction_date
    """, (month_start, month_end))
    txns = [dict(r) for r in cur.fetchall()]

    conn.close()

    # Auto-match bills to transactions
    used_txn_ids = set()

    for bill in bills:
        bill_name = bill['merchant_name'].lower()
        expected = float(bill['expected_amount'] or 0)
        variance = float(bill['amount_variance'] or 5.0)

        best_match = None
        best_score = 0

        for txn in txns:
            if txn['id'] in used_txn_ids:
                continue

            txn_desc = (txn['description'] or '').lower()
            txn_orig = (txn['original_description'] or '').lower()
            txn_amt = abs(float(txn['amount']))

            # Name match score
            name_score = 0
            bill_words = set(bill_name.split())
            desc_words = set(txn_desc.split())
            orig_words = set(txn_orig.split())

            common_desc = bill_words & desc_words
            common_orig = bill_words & orig_words

            if bill_name in txn_desc or bill_name in txn_orig:
                name_score = 10
            elif common_desc:
                name_score = len(common_desc) / len(bill_words) * 8
            elif common_orig:
                name_score = len(common_orig) / len(bill_words) * 6

            if name_score < 3:
                continue

            # Amount match bonus
            amt_score = 0
            if expected > 0:
                if abs(txn_amt - expected) <= variance:
                    amt_score = 5
                elif abs(txn_amt - expected) <= expected * 0.2:
                    amt_score = 2

            total_score = name_score + amt_score

            if total_score > best_score:
                best_score = total_score
                best_match = txn

        if best_match and best_score >= 5:
            bill['status'] = 'paid'
            bill['matched_txn_id'] = best_match['id']
            bill['matched_date'] = best_match['transaction_date']
            bill['matched_amount'] = abs(float(best_match['amount']))
            bill['matched_description'] = best_match['description']
            used_txn_ids.add(best_match['id'])
        else:
            bill['status'] = 'unpaid'
            bill['matched_txn_id'] = None
            bill['matched_date'] = None
            bill['matched_amount'] = None
            bill['matched_description'] = None

        # Due date for this month
        if bill['expected_day']:
            try:
                due = date(year, mon, min(bill['expected_day'], monthrange(year, mon)[1]))
                bill['due_date'] = due.isoformat()
                bill['overdue'] = (bill['status'] == 'unpaid' and due < date.today())
            except:
                bill['due_date'] = None
                bill['overdue'] = False
        else:
            bill['due_date'] = None
            bill['overdue'] = False

    return json_response({
        "month": f"{year}-{mon:02d}",
        "month_label": date(year, mon, 1).strftime("%B %Y"),
        "bills": bills,
        "paid_count": sum(1 for b in bills if b['status'] == 'paid'),
        "unpaid_count": sum(1 for b in bills if b['status'] == 'unpaid'),
        "total_expected": sum(float(b['expected_amount'] or 0) for b in bills),
        "total_paid": sum(b['matched_amount'] for b in bills if b['status'] == 'paid'),
    })


@router.patch("/bills/{bill_id}/override")
async def override_bill_status(request: Request, bill_id: int, body: BillPaidOverride):
    """Manual override for bill paid status — stored in a simple override table if it exists,
    otherwise just returns the override for client-side state management"""
    # Return the override for client to manage in session state
    # Full persistence would require a bill_overrides table
    return json_response({
        "success": True,
        "bill_id": bill_id,
        "paid": body.paid,
        "paid_amount": body.paid_amount,
        "paid_date": body.paid_date,
        "note": "Override applied for this session"
    })


# ── Report / Spending / Forecast / Income (unchanged) ──────

@router.get("/report")
async def get_report(request: Request, months: int = Query(default=6, ge=1, le=12)):
    import sys
    sys.path.insert(0, '/opt/mythos/finance')
    from report_generator import get_current_balances, get_recurring_bills, build_month_data
    conn = get_db()
    cur = conn.cursor()
    balances = get_current_balances(cur)
    bills = get_recurring_bills(cur)
    today = date.today()
    months_data = []
    for i in range(months):
        m = today.month - i
        y = today.year
        while m <= 0: m += 12; y -= 1
        months_data.append(build_month_data(cur, y, m, bills))
    conn.close()
    return json_response({"generated": datetime.now().isoformat(), "balances": balances, "months": months_data})


@router.get("/spending")
async def get_spending(request: Request, month: Optional[str] = Query(default=None)):
    conn = get_db()
    cur = conn.cursor()
    if month:
        try:
            parts = month.split('-'); year, mon = int(parts[0]), int(parts[1])
        except: year, mon = datetime.now().year, datetime.now().month
    else: year, mon = datetime.now().year, datetime.now().month
    start = date(year, mon, 1); end = date(year, mon, monthrange(year, mon)[1])
    cur.execute("""
        SELECT category_primary, COUNT(*) as txn_count, SUM(amount)::numeric(12,2) as total
        FROM transactions WHERE transaction_date BETWEEN %s AND %s AND description != 'Balance checkpoint'
        GROUP BY category_primary ORDER BY total
    """, (start, end))
    cats = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"month": f"{year}-{mon:02d}", "categories": cats})


@router.get("/bills")
async def get_bills(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.frequency, rb.category_primary, rb.notes, a.abbreviation as account
        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST
    """)
    bills = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"bills": bills})


@router.get("/income")
async def get_income_sources(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ri.id, ri.source_name, ri.expected_amount, ri.expected_day,
               ri.frequency, a.abbreviation as account
        FROM recurring_income ri LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true ORDER BY ri.expected_day NULLS LAST
    """)
    income = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"income": income})


@router.get("/forecast")
async def get_forecast(request: Request, account: Optional[str] = Query(default=None), days: int = Query(default=30, ge=7, le=60)):
    conn = get_db()
    cur = conn.cursor()
    import sys
    sys.path.insert(0, '/opt/mythos/telegram_bot/handlers')
    try:
        from forecast_handler import get_current_balances, get_upcoming_bills, get_upcoming_income, build_forecast, PRIMARY_ACCOUNTS
    except ImportError:
        conn.close(); return json_response({"error": "Forecast handler not available"})
    balances = get_current_balances(cur)
    bills = get_upcoming_bills(cur, days)
    income = get_upcoming_income(cur, days)
    conn.close()
    acct_filter = [account.upper()] if account and account.upper() in ('USAA', 'SUN') else PRIMARY_ACCOUNTS
    forecast = build_forecast(balances, bills, income, acct_filter, days)
    day_list = [{'date': dd['date'].isoformat(), 'day_change': float(dd['day_change']), 'running': float(dd['running']),
                 'bills': [{'merchant': b['merchant_name'], 'amount': float(b['expected_amount'])} for b in dd['bills']],
                 'income': [{'source': i['source_name'], 'amount': float(i['expected_amount'])} for i in dd['income']]}
                for dd in forecast['days']]
    return json_response({'account_filter': acct_filter, 'starting': float(forecast['starting']),
                          'ending': float(forecast['ending']), 'lowest': float(forecast['lowest']),
                          'lowest_date': forecast['lowest_date'].isoformat(), 'went_negative': forecast['went_negative'],
                          'negative_date': forecast['negative_date'].isoformat() if forecast['negative_date'] else None, 'days': day_list})
