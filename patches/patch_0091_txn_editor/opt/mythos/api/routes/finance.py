#!/usr/bin/env python3
"""
Mythos API - Finance Routes
/opt/mythos/api/routes/finance.py
Protected endpoints serving live financial data for the web dashboard.
All routes require JWT authentication via AuthMiddleware.
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, HTTPException
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
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)
def json_response(data):
    return JSONResponse(content=json.loads(json.dumps(data, cls=DecimalEncoder)))

# ========== TRANSACTION UPDATE MODEL ==========
class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    category_primary: Optional[str] = None
    merchant_name: Optional[str] = None

# ========== BALANCES ==========
@router.get("/balances")
async def get_balances(request: Request):
    """Get current account balances"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (a.id)
            a.id, a.abbreviation, a.bank_name, a.account_type,
            COALESCE(t.balance, 0) as balance,
            t.transaction_date as balance_date
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        WHERE a.is_active = true
        ORDER BY a.id, t.transaction_date DESC
    """)
    accounts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"accounts": accounts})

# ========== MONTHLY REPORT ==========
@router.get("/report")
async def get_report(request: Request, months: int = Query(default=6, ge=1, le=12)):
    """Get full monthly report data"""
    import sys
    sys.path.insert(0, '/opt/mythos/finance')
    from report_generator import get_current_balances, get_recurring_bills, build_month_data, DecimalEncoder as DE
    conn = get_db()
    cur = conn.cursor()
    balances = get_current_balances(cur)
    bills = get_recurring_bills(cur)
    today = date.today()
    months_data = []
    for i in range(months):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months_data.append(build_month_data(cur, y, m, bills))
    conn.close()
    return json_response({
        "generated": datetime.now().isoformat(),
        "balances": balances,
        "months": months_data,
    })

# ========== SPENDING ==========
@router.get("/spending")
async def get_spending(
    request: Request,
    month: Optional[str] = Query(default=None, description="YYYY-MM format"),
):
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
    start = date(year, mon, 1)
    end = date(year, mon, monthrange(year, mon)[1])
    cur.execute("""
        SELECT category_primary, COUNT(*) as txn_count,
               SUM(amount)::numeric(12,2) as total
        FROM transactions
        WHERE transaction_date BETWEEN %s AND %s
          AND description != 'Balance checkpoint'
        GROUP BY category_primary
        ORDER BY total
    """, (start, end))
    categories = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"month": f"{year}-{mon:02d}", "categories": categories})

# ========== TRANSACTIONS ==========
@router.get("/transactions")
async def get_transactions(
    request: Request,
    month: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    account: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
):
    """Get transactions with optional filters"""
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
        except:
            pass
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

# ========== TRANSACTION UPDATE ==========
@router.patch("/transactions/{txn_id}")
async def update_transaction(request: Request, txn_id: int, update: TransactionUpdate):
    """Update a transaction's description, category, or merchant name"""
    conn = get_db()
    cur = conn.cursor()
    # Build dynamic update
    fields = []
    params = []
    if update.description is not None:
        fields.append("description = %s")
        params.append(update.description.strip())
    if update.category_primary is not None:
        fields.append("category_primary = %s")
        params.append(update.category_primary.strip() or None)
    if update.merchant_name is not None:
        fields.append("merchant_name = %s")
        params.append(update.merchant_name.strip() or None)
    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    params.append(txn_id)
    cur.execute(
        f"UPDATE transactions SET {', '.join(fields)} WHERE id = %s RETURNING id",
        params
    )
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return json_response({"success": True, "id": txn_id})

# ========== CATEGORIES LIST ==========
@router.get("/categories")
async def get_categories(request: Request):
    """Get all distinct categories in use"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT category_primary
        FROM transactions
        WHERE category_primary IS NOT NULL AND category_primary != ''
        ORDER BY category_primary
    """)
    cats = [r['category_primary'] for r in cur.fetchall()]
    conn.close()
    return json_response({"categories": cats})

# ========== FORECAST ==========
@router.get("/forecast")
async def get_forecast(
    request: Request,
    account: Optional[str] = Query(default=None),
    days: int = Query(default=30, ge=7, le=60),
):
    conn = get_db()
    cur = conn.cursor()
    import sys
    sys.path.insert(0, '/opt/mythos/telegram_bot/handlers')
    try:
        from forecast_handler import (
            get_current_balances, get_upcoming_bills, get_upcoming_income,
            build_forecast, PRIMARY_ACCOUNTS
        )
    except ImportError:
        conn.close()
        return json_response({"error": "Forecast handler not available"})
    balances = get_current_balances(cur)
    bills = get_upcoming_bills(cur, days)
    income = get_upcoming_income(cur, days)
    conn.close()
    if account and account.upper() in ('USAA', 'SUN'):
        acct_filter = [account.upper()]
    else:
        acct_filter = PRIMARY_ACCOUNTS
    forecast = build_forecast(balances, bills, income, acct_filter, days)
    day_list = []
    for dd in forecast['days']:
        day_list.append({
            'date': dd['date'].isoformat(),
            'day_change': float(dd['day_change']),
            'running': float(dd['running']),
            'bills': [{'merchant': b['merchant_name'], 'amount': float(b['expected_amount'])} for b in dd['bills']],
            'income': [{'source': i['source_name'], 'amount': float(i['expected_amount'])} for i in dd['income']],
        })
    return json_response({
        'account_filter': acct_filter,
        'starting': float(forecast['starting']),
        'ending': float(forecast['ending']),
        'lowest': float(forecast['lowest']),
        'lowest_date': forecast['lowest_date'].isoformat(),
        'went_negative': forecast['went_negative'],
        'negative_date': forecast['negative_date'].isoformat() if forecast['negative_date'] else None,
        'days': day_list,
    })

# ========== RECURRING ==========
@router.get("/bills")
async def get_bills(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.frequency, rb.category_primary, rb.notes,
               a.abbreviation as account
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true
        ORDER BY rb.expected_day NULLS LAST
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
        FROM recurring_income ri
        LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true
        ORDER BY ri.expected_day NULLS LAST
    """)
    income = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"income": income})

# ========== SUMMARY ==========
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
        SELECT SUM(amount)::numeric(12,2) as total
        FROM transactions
        WHERE transaction_date >= %s AND amount < 0
          AND category_primary NOT IN ('Transfer', 'Credit Card Payment')
          AND description != 'Balance checkpoint'
    """, (month_start,))
    month_spending = float(cur.fetchone()['total'] or 0)
    cur.execute("""
        SELECT SUM(amount)::numeric(12,2) as total
        FROM transactions
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
