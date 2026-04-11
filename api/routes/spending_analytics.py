#!/usr/bin/env python3
"""
Mythos API - Spending Analytics Endpoint
/opt/mythos/api/routes/spending_analytics.py
Provides aggregated spending data for the React Spending Analytics component.

Patch 0152: Added account filtering via ?account= query parameter.
  - 'combined' or omitted → both USAA + SUN (default behavior)
  - 'usaa' → USAA only
  - 'sun' → SUN only
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/finance/spending", tags=["finance"])
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

def _parse_account_filter(account_param):
    """Map frontend account param to list of DB account abbreviations."""
    if not account_param or account_param == 'combined':
        return ['USAA', 'SUN']
    elif account_param.lower() == 'usaa':
        return ['USAA']
    elif account_param.lower() == 'sun':
        return ['SUN']
    return ['USAA', 'SUN']

def _acct_join_clause(acct_list):
    """Build a JOIN clause to filter transactions by account."""
    placeholders = ','.join(['%s'] * len(acct_list))
    return f"JOIN accounts a ON transactions.account_id = a.id AND a.abbreviation IN ({placeholders})"

@router.get("/analytics")
async def spending_analytics(
    request: Request,
    months: int = Query(default=8, ge=2, le=24),
):
    """
    Returns monthly spending by category, income totals, and top merchants.
    Used by the React Spending Analytics component.
    """
    account_param = request.query_params.get('account', 'combined')
    acct_list = _parse_account_filter(account_param)
    acct_join = _acct_join_clause(acct_list)

    conn = get_db()
    cur = conn.cursor()
    # Determine month range
    now = datetime.now()
    # Current month (partial)
    end_month = date(now.year, now.month, 1)
    # Go back N months
    start_month = end_month
    for _ in range(months - 1):
        start_month = (start_month - timedelta(days=1)).replace(day=1)
    # ── Monthly spending by category ────────────────────────
    cur.execute(f"""
        SELECT
            TO_CHAR(transactions.transaction_date, 'YYYY-MM') as month,
            transactions.category_primary,
            SUM(ABS(transactions.amount))::numeric(12,2) as total
        FROM transactions
        {acct_join}
        WHERE transactions.transaction_date >= %s
          AND transactions.amount < 0
          AND transactions.category_primary IS NOT NULL
          AND transactions.category_primary != ''
          AND transactions.category_primary NOT IN ('Transfer', 'Credit Card Payment')
          AND transactions.description != 'Balance checkpoint'
        GROUP BY month, transactions.category_primary
        ORDER BY month, total DESC
    """, (*acct_list, start_month))
    cat_rows = cur.fetchall()
    # Build month list
    month_list = []
    m = start_month
    while m <= end_month:
        month_list.append(m.strftime('%Y-%m'))
        if m.month == 12:
            m = date(m.year + 1, 1, 1)
        else:
            m = date(m.year, m.month + 1, 1)
    # Pivot into {month: {category: amount}}
    by_month = {mo: {} for mo in month_list}
    all_categories = set()
    for row in cat_rows:
        mo = row['month']
        cat = row['category_primary']
        if mo in by_month:
            by_month[mo][cat] = float(row['total'])
            all_categories.add(cat)
    # Sort categories by total across all months (descending)
    cat_totals = {}
    for cat in all_categories:
        cat_totals[cat] = sum(by_month[mo].get(cat, 0) for mo in month_list)
    sorted_cats = sorted(cat_totals.keys(), key=lambda c: cat_totals[c], reverse=True)
    # Build monthly data array
    monthly_data = []
    for mo in month_list:
        parts = mo.split('-')
        yr, mn = int(parts[0]), int(parts[1])
        month_total = sum(by_month[mo].values())
        entry = {
            "month": mo,
            "label": date(yr, mn, 1).strftime('%b %y'),
            "total": round(month_total, 2),
            "categories": {cat: by_month[mo].get(cat, 0) for cat in sorted_cats},
        }
        monthly_data.append(entry)
    # ── Monthly income ──────────────────────────────────────
    cur.execute(f"""
        SELECT
            TO_CHAR(transactions.transaction_date, 'YYYY-MM') as month,
            SUM(transactions.amount)::numeric(12,2) as total
        FROM transactions
        {acct_join}
        WHERE transactions.transaction_date >= %s
          AND transactions.amount > 0
          AND transactions.category_primary IN ('Income', 'Interest Income', 'Paycheck')
          AND transactions.description != 'Balance checkpoint'
        GROUP BY month
        ORDER BY month
    """, (*acct_list, start_month))
    income_rows = cur.fetchall()
    income_by_month = {r['month']: float(r['total']) for r in income_rows}
    for entry in monthly_data:
        entry['income'] = income_by_month.get(entry['month'], 0)
        entry['net'] = round(entry['income'] - entry['total'], 2)
    # ── Top merchants ───────────────────────────────────────
    cur.execute(f"""
        SELECT
            COALESCE(transactions.merchant_name, transactions.description) as merchant,
            transactions.category_primary as category,
            COUNT(*) as txn_count,
            SUM(ABS(transactions.amount))::numeric(12,2) as total
        FROM transactions
        {acct_join}
        WHERE transactions.transaction_date >= %s
          AND transactions.amount < 0
          AND transactions.category_primary NOT IN ('Transfer', 'Credit Card Payment')
          AND transactions.description != 'Balance checkpoint'
        GROUP BY merchant, transactions.category_primary
        ORDER BY total DESC
        LIMIT 15
    """, (*acct_list, start_month))
    merchants = []
    for row in cur.fetchall():
        # Calculate trend (last 2 months vs prior 2 months)
        merchant_name = row['merchant']
        cur.execute(f"""
            SELECT
                TO_CHAR(transactions.transaction_date, 'YYYY-MM') as month,
                SUM(ABS(transactions.amount))::numeric(12,2) as total
            FROM transactions
            {acct_join}
            WHERE (COALESCE(transactions.merchant_name, transactions.description)) = %s
              AND transactions.amount < 0
              AND transactions.transaction_date >= %s
            GROUP BY month
            ORDER BY month
        """, (*acct_list, merchant_name, start_month))
        trend_rows = cur.fetchall()
        trend_data = {r['month']: float(r['total']) for r in trend_rows}
        # Simple trend: compare last 2 months avg vs prior months avg
        if len(month_list) >= 4:
            recent = sum(trend_data.get(mo, 0) for mo in month_list[-2:]) / 2
            earlier = sum(trend_data.get(mo, 0) for mo in month_list[:-2]) / max(len(month_list) - 2, 1)
            if earlier > 0:
                if recent > earlier * 1.15:
                    trend = "up"
                elif recent < earlier * 0.85:
                    trend = "down"
                else:
                    trend = "flat"
            else:
                trend = "flat"
        else:
            trend = "flat"
        merchants.append({
            "name": merchant_name,
            "category": row['category'],
            "count": row['txn_count'],
            "total": float(row['total']),
            "avg": round(float(row['total']) / row['txn_count'], 2),
            "trend": trend,
        })
    # ── Current month burn rate ─────────────────────────────
    current_month_key = now.strftime('%Y-%m')
    current_spending = sum(
        by_month.get(current_month_key, {}).values()
    )
    day_of_month = now.day
    days_in_current = monthrange(now.year, now.month)[1]
    daily_burn = current_spending / max(day_of_month, 1)
    projected = daily_burn * days_in_current
    current_income = income_by_month.get(current_month_key, 0)
    burn_rate = {
        "daily": round(daily_burn, 2),
        "projected": round(projected, 2),
        "days_elapsed": day_of_month,
        "days_in_month": days_in_current,
        "days_left": days_in_current - day_of_month,
        "runway": round(current_income - projected, 2),
    }
    # ── Averages ────────────────────────────────────────────
    # Exclude current (partial) month from average
    complete_months = monthly_data[:-1] if len(monthly_data) > 1 else monthly_data
    avg_spending = sum(m['total'] for m in complete_months) / max(len(complete_months), 1)
    conn.close()
    return json_response({
        "account_filter": account_param,
        "months": monthly_data,
        "categories": sorted_cats,
        "merchants": merchants,
        "burn_rate": burn_rate,
        "avg_monthly_spending": round(avg_spending, 2),
        "current_month": {
            "key": current_month_key,
            "spending": round(current_spending, 2),
            "income": current_income,
            "net": round(current_income - current_spending, 2),
        },
    })
