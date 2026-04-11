"""
Smart Overview API — Patch 0152
Single endpoint returning:
  - safe_to_spend: discretionary money without jeopardizing any bill in next 14 days
  - paycheck_countdown: next income, days until, balance just before it hits
  - spending_velocity: current pace vs historical average
  - afford_windows: for each of next 30 days, max spendable amount
  - bill_triage: upcoming bills classified as fixed vs flexible

Patch 0152: Added account filtering via ?account= query parameter.
  - 'combined' or omitted → both USAA + SUN (default behavior)
  - 'usaa' → USAA only
  - 'sun' → SUN only
"""
import os
import json
import logging
import sys
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

def _parse_account_filter(account_param, cur=None):
    """Map frontend account param to list of DB account abbreviations.
    Patch 0192: combined now queries include_in_overview flag from DB."""
    if account_param and account_param.lower() == 'usaa':
        return ['USAA']
    elif account_param and account_param.lower() == 'sun':
        return ['SUN']
    if cur:
        cur.execute("""
            SELECT abbreviation FROM accounts
            WHERE is_active = true AND include_in_overview = true
              AND account_type IN ('checking', 'savings')
            ORDER BY id
        """)
        accts = [r['abbreviation'] for r in cur.fetchall()]
        if accts:
            return accts
    return ['USAA', 'SUN']

def _load_forecast(cur, days, account_param=None):
    sys.path.insert(0, '/opt/mythos/telegram_bot/handlers')
    from forecast_handler import (
        get_current_balances, get_upcoming_bills, get_upcoming_income,
        build_forecast, PRIMARY_ACCOUNTS
    )
    acct_list = _parse_account_filter(account_param, cur)
    balances = get_current_balances(cur)
    bills = get_upcoming_bills(cur, days)
    income = get_upcoming_income(cur, days)
    forecast = build_forecast(balances, bills, income, acct_list, days)
    return forecast, balances
SAFETY_BUFFER = 100
@router.get("/smart-overview")
async def smart_overview(request: Request):
    account_param = request.query_params.get('account', 'combined')
    acct_list = _parse_account_filter(account_param)
    conn = get_db()
    cur = conn.cursor()
    today = date.today()
    now = datetime.now()
    day_of_month = today.day
    days_in_month = monthrange(today.year, today.month)[1]
    try:
        forecast, balances = _load_forecast(cur, 45, account_param)
    except Exception as e:
        conn.close()
        return json_response({"error": f"Forecast unavailable: {e}"})
    forecast_days = forecast.get('days', [])
    current_combined = float(forecast.get('starting', 0))
    # ── 1. SAFE TO SPEND ──────────────────────────────────────
    days_14 = forecast_days[:14]
    lowest_14 = min((float(d['running']) for d in days_14), default=current_combined) if days_14 else current_combined
    safe_to_spend = max(0, round(lowest_14, 2))
    safe_to_spend_buffered = max(0, round(lowest_14 - SAFETY_BUFFER, 2))
    # ── 2. PAYCHECK COUNTDOWN ─────────────────────────────────
    next_paycheck = None
    for day_data in forecast_days:
        inc_list = day_data.get('income', [])
        if not inc_list:
            continue
        due = day_data['date']
        if isinstance(due, str):
            due = date.fromisoformat(due)
        if due <= today:
            continue
        days_until = (due - today).days
        inc = inc_list[0]
        inc_amount = float(inc.get('expected_amount', 0))
        balance_before = round(float(day_data['running']) - inc_amount, 2)
        next_paycheck = {
            'source': inc.get('source_name', 'Income'),
            'amount': round(inc_amount, 2),
            'date': due.isoformat(),
            'days_until': days_until,
            'balance_before': balance_before,
        }
        break
    # ── 3. SPENDING VELOCITY ──────────────────────────────────
    # Build account filter for SQL
    acct_placeholders = ','.join(['%s'] * len(acct_list))
    acct_join = f"""
        JOIN accounts a ON transactions.account_id = a.id
        AND a.abbreviation IN ({acct_placeholders})
    """

    month_start = date(today.year, today.month, 1)
    cur.execute(f"""
        SELECT COALESCE(SUM(ABS(transactions.amount)), 0) as total
        FROM transactions
        {acct_join}
        WHERE transactions.transaction_date BETWEEN %s AND %s AND transactions.amount < 0
        AND transactions.description != 'Balance checkpoint'
    """, (*acct_list, month_start, today))
    this_month_spent = float(cur.fetchone()['total'])
    ninety_ago = today - timedelta(days=90)
    cur.execute(f"""
        SELECT COALESCE(SUM(ABS(transactions.amount)), 0) as total,
               COUNT(DISTINCT transactions.transaction_date) as active_days
        FROM transactions
        {acct_join}
        WHERE transactions.transaction_date BETWEEN %s AND %s AND transactions.amount < 0
        AND transactions.description != 'Balance checkpoint'
    """, (*acct_list, ninety_ago, today - timedelta(days=1)))
    hist = cur.fetchone()
    hist_days = max(int(hist['active_days']), 1)
    avg_daily = float(hist['total']) / hist_days
    current_daily = this_month_spent / max(day_of_month, 1)
    projected_month = current_daily * days_in_month
    avg_month = avg_daily * days_in_month
    pace_ratio = round(current_daily / avg_daily, 2) if avg_daily > 0 else 1.0
    spending_velocity = {
        'this_month_spent': round(this_month_spent, 2),
        'day_of_month': day_of_month,
        'days_in_month': days_in_month,
        'current_daily_rate': round(current_daily, 2),
        'historical_daily_rate': round(avg_daily, 2),
        'projected_month_total': round(projected_month, 2),
        'historical_month_avg': round(avg_month, 2),
        'pace_ratio': pace_ratio,
        'pace_label': 'on track' if pace_ratio <= 1.05 else 'above pace' if pace_ratio <= 1.2 else 'high',
    }
    # ── 4. AFFORD WINDOWS ─────────────────────────────────────
    afford_windows = []
    for i, day_data in enumerate(forecast_days[:30]):
        day_date = day_data['date']
        if isinstance(day_date, date):
            day_date = day_date.isoformat()
        remaining = forecast_days[i:]
        min_after = min((float(d['running']) for d in remaining), default=0)
        available = max(0, round(min_after - SAFETY_BUFFER, 2))
        afford_windows.append({
            'date': day_date,
            'available': available,
            'balance': round(float(day_data['running']), 2),
        })
    best_day = max(afford_windows, key=lambda x: x['available']) if afford_windows else None
    # ── 5. BILL TRIAGE ────────────────────────────────────────
    # Filter bills by account if not combined
    if len(acct_list) == 1:
        acct_where = f"AND a.abbreviation = %s"
        bill_params = (acct_list[0],)
    else:
        acct_where = ""
        bill_params = ()

    cur.execute(f"""
        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.category_primary, rb.notes, a.abbreviation as account
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true {acct_where}
        ORDER BY rb.expected_day NULLS LAST
    """, bill_params)
    all_bills = [dict(r) for r in cur.fetchall()]
    hard_categories = {'Loan', 'Mortgage', 'Insurance', 'Transfer'}
    hard_keywords = ['loan', 'mortgage', 'insurance', 'electric', 'water', 'sewer', 'usaa']
    triage_bills = []
    for bill in all_bills:
        exp_day = bill.get('expected_day')
        if exp_day is None:
            continue
        try:
            due = date(today.year, today.month, min(exp_day, days_in_month))
            if due < today:
                nm, ny = today.month + 1, today.year
                if nm > 12: nm, ny = 1, ny + 1
                due = date(ny, nm, min(exp_day, monthrange(ny, nm)[1]))
        except ValueError:
            continue
        days_until = (due - today).days
        if days_until > 14 or days_until < 0:
            continue
        cat = (bill.get('category_primary') or '').strip()
        merchant = (bill.get('merchant_name') or '').strip()
        is_hard = cat in hard_categories or any(k in merchant.lower() for k in hard_keywords)
        triage_bills.append({
            'id': bill['id'], 'merchant': merchant,
            'amount': float(bill.get('expected_amount') or 0),
            'due_date': due.isoformat(), 'days_until': days_until,
            'category': cat, 'flexibility': 'fixed' if is_hard else 'flexible',
            'account': bill.get('account') or 'USAA',
        })
    triage_bills.sort(key=lambda x: x['days_until'])
    conn.close()
    return json_response({
        'generated': now.isoformat(),
        'account_filter': account_param,
        'safe_to_spend': {
            'amount': safe_to_spend, 'buffered': safe_to_spend_buffered,
            'buffer': SAFETY_BUFFER, 'lowest_14_day': round(lowest_14, 2),
            'current_combined': round(current_combined, 2),
        },
        'paycheck_countdown': next_paycheck,
        'spending_velocity': spending_velocity,
        'afford_windows': afford_windows,
        'best_spend_day': best_day,
        'bill_triage': triage_bills,
    })
