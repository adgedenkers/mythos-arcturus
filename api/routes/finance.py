#!/usr/bin/env python3
"""
Mythos API - Finance Routes
/opt/mythos/api/routes/finance.py
v3 - patch 0093: Persistent bill overrides, forecast view
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

class CategoryRename(BaseModel):
    old_name: str
    new_name: str

class CategoryMerge(BaseModel):
    source: str
    target: str

class BillOverrideBody(BaseModel):
    paid: bool
    paid_amount: Optional[float] = None
    paid_date: Optional[str] = None   # YYYY-MM-DD
    note: Optional[str] = None

class BillUpdate(BaseModel):
    merchant_name: Optional[str] = None
    merchant_pattern: Optional[str] = None
    expected_amount: Optional[float] = None
    amount_variance: Optional[float] = None
    expected_day: Optional[int] = None
    category_primary: Optional[str] = None
    notes: Optional[str] = None


# ── Summary ────────────────────────────────────────────────

@router.get("/summary")
async def get_summary(request: Request):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (a.id) a.abbreviation, COALESCE(t.balance, 0) as balance
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        WHERE a.is_active = true AND a.account_type IN ('checking', 'savings')
        ORDER BY a.id, t.transaction_date DESC
    """)
    balances = {r['abbreviation']: float(r['balance']) for r in cur.fetchall()}
    now = datetime.now(); month_start = date(now.year, now.month, 1)
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
    conn = get_db(); cur = conn.cursor()
    conditions = ["t.description != 'Balance checkpoint'"]
    params = []
    if month:
        try:
            parts = month.split('-'); year, mon = int(parts[0]), int(parts[1])
            start = date(year, mon, 1); end = date(year, mon, monthrange(year, mon)[1])
            conditions.append("t.transaction_date BETWEEN %s AND %s"); params.extend([start, end])
        except: pass
    if category:
        if category == '__uncategorized__':
            conditions.append("(t.category_primary IS NULL OR t.category_primary = '')")
        else:
            conditions.append("t.category_primary = %s"); params.append(category)
    if account:
        conditions.append("a.abbreviation = %s"); params.append(account.upper())
    if search:
        conditions.append("(t.description ILIKE %s OR t.original_description ILIKE %s)")
        params.extend([f'%{search}%', f'%{search}%'])
    params.append(limit)
    cur.execute(f"""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, t.balance, t.category_primary, t.merchant_name,
               a.abbreviation as account
        FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id
        WHERE {' AND '.join(conditions)}
        ORDER BY t.transaction_date DESC, t.id DESC LIMIT %s
    """, params)
    txns = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"transactions": txns, "count": len(txns)})


@router.patch("/transactions/{txn_id}")
async def update_transaction(request: Request, txn_id: int, update: TransactionUpdate):
    conn = get_db(); cur = conn.cursor()
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
    result = cur.fetchone(); conn.commit(); conn.close()
    if not result: raise HTTPException(status_code=404, detail="Transaction not found")
    return json_response({"success": True, "id": txn_id})




# ── Apply Category to All Matching ─────────────────────────
class ApplyCategoryBody(BaseModel):
    category_primary: str
    merchant_name: Optional[str] = None
    pattern: Optional[str] = None  # override auto-detected pattern

@router.post("/transactions/{txn_id}/apply-category")
async def apply_category_to_all(request: Request, txn_id: int, body: ApplyCategoryBody):
    """
    Apply a category to all transactions matching the same vendor pattern.
    Also upserts a category_mapping rule so future imports get categorized.
    
    1. Reads the target transaction's description/original_description
    2. Finds the best pattern to match on
    3. Updates all matching transactions
    4. Upserts a category_mapping rule
    """
    conn = get_db(); cur = conn.cursor()
    
    # Get the target transaction
    cur.execute("""
        SELECT id, description, original_description, merchant_name, category_primary
        FROM transactions WHERE id = %s
    """, (txn_id,))
    txn = cur.fetchone()
    if not txn:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Determine the match pattern
    if body.pattern:
        pattern = body.pattern.strip()
    elif body.merchant_name:
        pattern = body.merchant_name.strip()
    elif txn['merchant_name']:
        pattern = txn['merchant_name'].strip()
    elif txn['description']:
        # Use the description, but try to extract a clean vendor name
        # Take the first significant word(s) — skip common prefixes
        desc = txn['description'].strip()
        # Remove common prefixes
        for prefix in ['DEP:', 'EXT:', 'POS', 'ATM', 'ACH', 'PP*', 'Paypal:']:
            if desc.upper().startswith(prefix.upper()):
                desc = desc[len(prefix):].strip()
        pattern = desc.split('  ')[0].split(' #')[0].strip()  # Take before double-space or #number
        if len(pattern) < 3:
            pattern = txn['description'].strip()
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot determine match pattern")
    
    new_category = body.category_primary.strip()
    new_merchant = (body.merchant_name or '').strip() or None
    
    # Update all matching transactions
    cur.execute("""
        UPDATE transactions
        SET category_primary = %s,
            merchant_name = COALESCE(%s, merchant_name)
        WHERE (
            LOWER(description) LIKE LOWER(%s)
            OR LOWER(original_description) LIKE LOWER(%s)
        )
        AND id != %s
        RETURNING id
    """, (
        new_category,
        new_merchant,
        f'%{pattern}%',
        f'%{pattern}%',
        txn_id,
    ))
    bulk_updated = cur.rowcount
    
    # Also update the original transaction
    cur.execute("""
        UPDATE transactions
        SET category_primary = %s, merchant_name = COALESCE(%s, merchant_name)
        WHERE id = %s
    """, (new_category, new_merchant, txn_id))
    
    # Upsert category_mapping rule
    # Check if a mapping with this pattern already exists
    cur.execute("""
        SELECT id, category_primary FROM category_mappings
        WHERE LOWER(pattern) = LOWER(%s) AND is_active = true
    """, (pattern,))
    existing = cur.fetchone()
    
    if existing:
        # Update existing mapping
        cur.execute("""
            UPDATE category_mappings
            SET category_primary = %s, merchant_name = %s
            WHERE id = %s
        """, (new_category, new_merchant, existing['id']))
        mapping_action = 'updated'
    else:
        # Create new mapping
        cur.execute("""
            INSERT INTO category_mappings (pattern, pattern_type, category_primary, merchant_name, priority, is_active)
            VALUES (%s, 'contains', %s, %s, 90, true)
        """, (pattern, new_category, new_merchant))
        mapping_action = 'created'
    
    conn.commit()
    conn.close()
    
    return json_response({
        "success": True,
        "txn_id": txn_id,
        "pattern": pattern,
        "category": new_category,
        "merchant": new_merchant,
        "bulk_updated": bulk_updated,
        "mapping_action": mapping_action,
    })

# ── Categories ─────────────────────────────────────────────

@router.get("/categories")
async def get_categories(request: Request):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT category_primary, COUNT(*) as txn_count
        FROM transactions
        WHERE category_primary IS NOT NULL AND category_primary != ''
        GROUP BY category_primary ORDER BY category_primary
    """)
    cats = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"categories": cats})


@router.post("/categories/rename")
async def rename_category(request: Request, body: CategoryRename):
    if not body.new_name.strip(): raise HTTPException(status_code=400, detail="New name required")
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE transactions SET category_primary = %s WHERE category_primary = %s",
                (body.new_name.strip(), body.old_name))
    affected = cur.rowcount; conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected})


@router.post("/categories/merge")
async def merge_categories(request: Request, body: CategoryMerge):
    if body.source == body.target: raise HTTPException(status_code=400, detail="Source and target must differ")
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE transactions SET category_primary = %s WHERE category_primary = %s",
                (body.target, body.source))
    affected = cur.rowcount; conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected, "merged_into": body.target})


@router.delete("/categories/{name}")
async def delete_category(request: Request, name: str):
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE transactions SET category_primary = NULL WHERE category_primary = %s", (name,))
    affected = cur.rowcount; conn.commit(); conn.close()
    return json_response({"success": True, "affected": affected})


# ── Accounts ───────────────────────────────────────────────

@router.get("/accounts")
async def get_accounts(request: Request):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.abbreviation, a.bank_name, a.account_name, a.account_type,
               a.current_balance, a.balance_updated_at, a.is_active,
               a.credit_limit, a.min_payment, a.payment_due_day, a.notes,
               (SELECT COUNT(*) FROM transactions t WHERE t.account_id = a.id) as txn_count,
               (SELECT MAX(t.transaction_date) FROM transactions t WHERE t.account_id = a.id) as last_txn_date
        FROM accounts a ORDER BY a.is_active DESC, a.id
    """)
    accounts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"accounts": accounts})


@router.patch("/accounts/{account_id}/balance")
async def update_account_balance(request: Request, account_id: int, body: AccountBalanceUpdate):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        UPDATE accounts SET current_balance = %s, balance_updated_at = NOW()
        WHERE id = %s RETURNING id, abbreviation
    """, (body.current_balance, account_id))
    result = cur.fetchone(); conn.commit(); conn.close()
    if not result: raise HTTPException(status_code=404, detail="Account not found")
    return json_response({"success": True, "id": account_id, "abbreviation": result['abbreviation'], "balance": body.current_balance})


# ── Bills Tracker ──────────────────────────────────────────

@router.patch("/bills/{bill_id}")
async def update_bill(request: Request, bill_id: int, update: BillUpdate):
    """Update a recurring bill's match pattern, amount, or other fields."""
    conn = get_db(); cur = conn.cursor()
    fields, params = [], []
    if update.merchant_name is not None:
        fields.append("merchant_name = %s"); params.append(update.merchant_name.strip())
    if update.merchant_pattern is not None:
        fields.append("merchant_pattern = %s"); params.append(update.merchant_pattern.strip() or None)
    if update.expected_amount is not None:
        fields.append("expected_amount = %s"); params.append(update.expected_amount)
    if update.amount_variance is not None:
        fields.append("amount_variance = %s"); params.append(update.amount_variance)
    if update.expected_day is not None:
        fields.append("expected_day = %s"); params.append(update.expected_day if update.expected_day > 0 else None)
    if update.category_primary is not None:
        fields.append("category_primary = %s"); params.append(update.category_primary.strip() or None)
    if update.notes is not None:
        fields.append("notes = %s"); params.append(update.notes.strip() or None)
    if not fields:
        conn.close(); raise HTTPException(status_code=400, detail="No fields to update")
    params.append(bill_id)
    cur.execute(f"UPDATE recurring_bills SET {', '.join(fields)} WHERE id = %s RETURNING id, merchant_name", params)
    result = cur.fetchone(); conn.commit(); conn.close()
    if not result: raise HTTPException(status_code=404, detail="Bill not found")
    return json_response({"success": True, "id": bill_id, "merchant_name": result['merchant_name']})

@router.get("/bills/test-pattern")
async def test_bill_pattern(
    request: Request,
    pattern: str = Query(..., description="Pattern to test against transaction descriptions"),
    limit: int = Query(default=20, ge=1, le=50),
):
    """Test a match pattern against recent transactions."""
    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "SELECT t.id, t.transaction_date, t.description, t.original_description, "
        "t.amount, a.abbreviation as account "
        "FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id "
        "WHERE t.amount < 0 AND (t.description ILIKE %s OR t.original_description ILIKE %s) "
        "ORDER BY t.transaction_date DESC LIMIT %s",
        (f'%{pattern}%', f'%{pattern}%', limit)
    )
    matches = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"pattern": pattern, "matches": matches, "count": len(matches)})

@router.get("/bills/tracker")
async def get_bills_tracker(
    request: Request,
    month: Optional[str] = Query(default=None),
):
    if month:
        try:
            parts = month.split('-'); year, mon = int(parts[0]), int(parts[1])
        except: year, mon = datetime.now().year, datetime.now().month
    else:
        year, mon = datetime.now().year, datetime.now().month

    month_key = f"{year}-{mon:02d}"
    month_start = date(year, mon, 1)
    month_end = date(year, mon, monthrange(year, mon)[1])

    conn = get_db(); cur = conn.cursor()

    # Active bills
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.merchant_pattern, rb.expected_amount,
               rb.expected_day, rb.frequency, rb.category_primary, rb.amount_variance,
               rb.notes, a.abbreviation as account
        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST, rb.merchant_name
    """)
    bills = [dict(r) for r in cur.fetchall()]

    # Month transactions (debits only)
    cur.execute("""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, a.abbreviation as account
        FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date BETWEEN %s AND %s AND t.amount < 0
        ORDER BY t.transaction_date
    """, (month_start, month_end))
    txns = [dict(r) for r in cur.fetchall()]

    # Load existing overrides for this month
    cur.execute("""
        SELECT bill_id, is_paid, paid_amount, paid_date, note
        FROM bill_overrides WHERE month = %s
    """, (month_key,))
    overrides = {r['bill_id']: dict(r) for r in cur.fetchall()}

    conn.close()

    # Auto-match
    used_txn_ids = set()
    for bill in bills:
        bill_name = bill['merchant_name'].lower()
        expected = float(bill['expected_amount'] or 0)
        variance = float(bill['amount_variance'] or 5.0)
        best_match = None; best_score = 0

        for txn in txns:
            if txn['id'] in used_txn_ids: continue
            txn_desc = (txn['description'] or '').lower()
            txn_orig = (txn['original_description'] or '').lower()
            txn_amt = abs(float(txn['amount']))
            name_score = 0
            bill_words = set(bill_name.split())
            if bill_name in txn_desc or bill_name in txn_orig:
                name_score = 10
            elif bill_words & set(txn_desc.split()):
                name_score = len(bill_words & set(txn_desc.split())) / len(bill_words) * 8
            elif bill_words & set(txn_orig.split()):
                name_score = len(bill_words & set(txn_orig.split())) / len(bill_words) * 6
            if name_score < 3: continue
            amt_score = 5 if expected > 0 and abs(txn_amt - expected) <= variance else (2 if expected > 0 and abs(txn_amt - expected) <= expected * 0.2 else 0)
            total_score = name_score + amt_score
            if total_score > best_score:
                best_score = total_score; best_match = txn

        if best_match and best_score >= 5:
            bill['auto_status'] = 'paid'
            bill['matched_txn_id'] = best_match['id']
            bill['matched_date'] = best_match['transaction_date']
            bill['matched_amount'] = abs(float(best_match['amount']))
            bill['matched_description'] = best_match['description']
            used_txn_ids.add(best_match['id'])
        else:
            bill['auto_status'] = 'unpaid'
            bill['matched_txn_id'] = None
            bill['matched_date'] = None
            bill['matched_amount'] = None
            bill['matched_description'] = None

        # Apply override if exists
        ov = overrides.get(bill['id'])
        if ov:
            bill['override'] = dict(ov)
            bill['status'] = 'paid' if ov['is_paid'] else 'unpaid'
            bill['override_paid_amount'] = float(ov['paid_amount']) if ov['paid_amount'] else None
            bill['override_paid_date'] = ov['paid_date']
        else:
            bill['override'] = None
            bill['status'] = bill['auto_status']
            bill['override_paid_amount'] = None
            bill['override_paid_date'] = None

        # Due date
        if bill['expected_day']:
            try:
                due = date(year, mon, min(bill['expected_day'], monthrange(year, mon)[1]))
                bill['due_date'] = due.isoformat()
                bill['overdue'] = (bill['status'] == 'unpaid' and due < date.today())
            except:
                bill['due_date'] = None; bill['overdue'] = False
        else:
            bill['due_date'] = None; bill['overdue'] = False

    paid_bills = [b for b in bills if b['status'] == 'paid']
    return json_response({
        "month": month_key,
        "month_label": date(year, mon, 1).strftime("%B %Y"),
        "bills": bills,
        "paid_count": len(paid_bills),
        "unpaid_count": len(bills) - len(paid_bills),
        "total_expected": sum(float(b['expected_amount'] or 0) for b in bills),
        "total_paid": sum(
            (b['override_paid_amount'] or b['matched_amount'] or 0)
            for b in bills if b['status'] == 'paid'
        ),
    })


@router.patch("/bills/{bill_id}/override")
async def override_bill_status(request: Request, bill_id: int, body: BillOverrideBody):
    """Persist a manual paid/unpaid override for a bill in a specific month"""
    # Get month from query param or default to current
    month = request.query_params.get('month') or datetime.now().strftime('%Y-%m')

    conn = get_db(); cur = conn.cursor()

    # Verify bill exists
    cur.execute("SELECT id FROM recurring_bills WHERE id = %s", (bill_id,))
    if not cur.fetchone():
        conn.close(); raise HTTPException(status_code=404, detail="Bill not found")

    paid_date = None
    if body.paid_date:
        try: paid_date = date.fromisoformat(body.paid_date)
        except: pass

    # Upsert override
    cur.execute("""
        INSERT INTO bill_overrides (bill_id, month, is_paid, paid_amount, paid_date, note)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (bill_id, month) DO UPDATE SET
            is_paid = EXCLUDED.is_paid,
            paid_amount = EXCLUDED.paid_amount,
            paid_date = EXCLUDED.paid_date,
            note = EXCLUDED.note,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
    """, (bill_id, month, body.paid, body.paid_amount, paid_date, body.note))
    result = cur.fetchone(); conn.commit(); conn.close()
    return json_response({"success": True, "bill_id": bill_id, "month": month, "paid": body.paid, "override_id": result['id']})


@router.delete("/bills/{bill_id}/override")
async def clear_bill_override(request: Request, bill_id: int):
    """Remove a manual override — reverts to auto-match status"""
    month = request.query_params.get('month') or datetime.now().strftime('%Y-%m')
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM bill_overrides WHERE bill_id = %s AND month = %s", (bill_id, month))
    deleted = cur.rowcount; conn.commit(); conn.close()
    return json_response({"success": True, "deleted": deleted})


# ── Forecast ───────────────────────────────────────────────

@router.get("/forecast")
async def get_forecast(
    request: Request,
    account: Optional[str] = Query(default=None, description="USAA, SUN, or combined"),
    days: int = Query(default=30, ge=7, le=60),
):
    import sys
    sys.path.insert(0, '/opt/mythos/telegram_bot/handlers')
    try:
        from forecast_handler import (
            get_current_balances, get_upcoming_bills, get_upcoming_income,
            build_forecast, PRIMARY_ACCOUNTS
        )
    except ImportError as e:
        return json_response({"error": f"Forecast handler not available: {e}"})

    conn = get_db(); cur = conn.cursor()
    balances = get_current_balances(cur)
    bills = get_upcoming_bills(cur, days)
    income = get_upcoming_income(cur, days)
    conn.close()

    acct_filter = [account.upper()] if account and account.upper() in ('USAA', 'SUN') else PRIMARY_ACCOUNTS
    forecast = build_forecast(balances, bills, income, acct_filter, days)

    day_list = []
    for dd in forecast['days']:
        day_list.append({
            'date': dd['date'].isoformat(),
            'day_index': dd['day_index'],
            'day_change': float(dd['day_change']),
            'running': float(dd['running']),
            'bills': [{'merchant': b['merchant_name'], 'amount': float(b['expected_amount']), 'acct': b.get('acct')} for b in dd['bills']],
            'income': [{'source': i['source_name'], 'amount': float(i['expected_amount']), 'acct': i.get('acct')} for i in dd['income']],
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


# ── Report / Spending / Bills / Income (unchanged) ─────────

@router.get("/report")
async def get_report(request: Request, months: int = Query(default=6, ge=1, le=12)):
    import sys; sys.path.insert(0, '/opt/mythos/finance')
    from report_generator import get_current_balances, get_recurring_bills, build_month_data
    conn = get_db(); cur = conn.cursor()
    balances = get_current_balances(cur); bills = get_recurring_bills(cur)
    today = date.today(); months_data = []
    for i in range(months):
        m = today.month - i; y = today.year
        while m <= 0: m += 12; y -= 1
        months_data.append(build_month_data(cur, y, m, bills))
    conn.close()
    return json_response({"generated": datetime.now().isoformat(), "balances": balances, "months": months_data})


@router.get("/spending")
async def get_spending(request: Request, month: Optional[str] = Query(default=None)):
    conn = get_db(); cur = conn.cursor()
    if month:
        try: parts = month.split('-'); year, mon = int(parts[0]), int(parts[1])
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
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT rb.id, rb.merchant_name, rb.merchant_pattern, rb.expected_amount,
               rb.expected_day, rb.amount_variance, rb.frequency, rb.category_primary,
               rb.notes, a.abbreviation as account
        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST
    """)
    bills = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"bills": bills})


@router.get("/income")
async def get_income_sources(request: Request):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT ri.id, ri.source_name, ri.expected_amount, ri.expected_day,
               ri.frequency, a.abbreviation as account
        FROM recurring_income ri LEFT JOIN accounts a ON ri.account_id = a.id
        WHERE ri.is_active = true ORDER BY ri.expected_day NULLS LAST
    """)
    income = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({"income": income})
