#!/usr/bin/env python3
"""
Mythos Finance - Monthly Report Generator
/opt/mythos/finance/report_generator.py

Generates an HTML financial report with:
  Col 1: Recurring bills - paid/unpaid status with actual dates/amounts
  Col 2: Spending breakdown by category with expandable transactions
  Col 3: Income/expense totals with visual bars

Usage:
    python report_generator.py                 # Last 6 months
    python report_generator.py --months 3      # Last 3 months
    python report_generator.py --output /path  # Custom output path
"""
import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import monthrange
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

TEMPLATE_PATH = Path(__file__).parent / 'report_template.html'
DEFAULT_OUTPUT = Path('/opt/mythos/finance/reports')


def get_db_connection():
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


def get_current_balances(cur):
    """Get current account balances"""
    cur.execute("""
        SELECT DISTINCT ON (a.id)
            a.abbreviation as name,
            COALESCE(t.balance, 0) as balance
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        WHERE a.is_active = true AND a.account_type IN ('checking', 'savings')
        ORDER BY a.id, t.transaction_date DESC
    """)
    return [dict(r) for r in cur.fetchall()]


def get_recurring_bills(cur):
    """Get all active recurring bills"""
    cur.execute("""
        SELECT rb.merchant_name, rb.expected_amount, rb.expected_day,
               rb.frequency, a.abbreviation as acct
        FROM recurring_bills rb
        LEFT JOIN accounts a ON rb.account_id = a.id
        WHERE rb.is_active = true AND rb.expected_day IS NOT NULL
        ORDER BY rb.expected_day
    """)
    return [dict(r) for r in cur.fetchall()]


def match_bill_to_transactions(bill, transactions, month_start, month_end):
    """
    Try to find a transaction that matches this recurring bill.
    Returns the matching transaction or None.
    """
    merchant = bill['merchant_name'].lower()
    expected = float(bill['expected_amount'])
    
    # Build search patterns from merchant name
    patterns = [merchant]
    
    # Common mapping of bill names to transaction descriptions
    bill_to_desc = {
        'youtube premium': ['youtube', 'google'],
        'openai': ['openai'],
        'bartles pharmacy': ['bartles'],
        'progressive': ['progressive'],
        'claude ai': ['claude'],
        'peacock': ['peacock'],
        'usaa loan': ['icpayment', 'usaa loan'],
        'barclaycard payment': ['barclaycard', 'ext: barclaycard'],
        'at&t': ['at&t'],
        'l.l.bean mc payment': ['llbean', 'l.l.bean'],
        'ancestry': ['ancestry'],
        'google one': ['google one'],
        'starlink': ['starlink'],
        'walmart+': ['walmart+', 'wmt plus'],
        'amex payment': ['amex', 'ext: amex'],
        'rocket money': ['rocket money', 'ext: rocket'],
        'sunmark loan tfr': ['tfr to loan', 'withdrawal tfr'],
        'tractor supply card': ['ext: tractor'],
        'tjx rewards payment': ['ext: tjx'],
        'nyseg': ['nyseg', 'new york state electric'],
        'wansor moses chiro': ['wansor'],
        'norwich family health': ['norwich family'],
        'netflix': ['netflix'],
        'amazon prime': ['amazon prime'],
        'discovery+': ['discovery'],
        'hugging face': ['hugging', 'huggingface'],
        'disney+': ['disney'],
        'blueox propane': ['blueox'],
    }
    
    key = merchant
    if key in bill_to_desc:
        patterns = bill_to_desc[key]
    
    # Search transactions in this month
    matches = []
    for txn in transactions:
        txn_date = txn['transaction_date']
        if not (month_start <= txn_date <= month_end):
            continue
        
        desc_lower = txn['description'].lower()
        orig_lower = (txn.get('original_description') or '').lower()
        
        for pattern in patterns:
            if pattern in desc_lower or pattern in orig_lower:
                matches.append(txn)
                break
    
    if not matches:
        return None
    
    # If multiple matches, pick the one closest to expected amount
    best = min(matches, key=lambda t: abs(abs(float(t['amount'])) - expected))
    return best


def build_month_data(cur, year, month, bills):
    """Build complete data for one month"""
    month_start = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    month_end = date(year, month, days_in_month)
    month_label = month_start.strftime('%B %Y')
    short_label = month_start.strftime('%b %Y')
    
    # Get all transactions for this month
    cur.execute("""
        SELECT t.id, t.transaction_date, t.description, t.original_description,
               t.amount, t.balance, t.category_primary, t.merchant_name,
               a.abbreviation as acct
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date BETWEEN %s AND %s
          AND t.description != 'Balance checkpoint'
        ORDER BY t.transaction_date, t.id
    """, (month_start, month_end))
    transactions = [dict(r) for r in cur.fetchall()]
    
    # ---- BILLS STATUS ----
    bill_statuses = []
    matched_txn_ids = set()
    
    for bill in bills:
        match = match_bill_to_transactions(bill, transactions, month_start, month_end)
        
        expected_day = bill['expected_day']
        
        status = {
            'merchant': bill['merchant_name'],
            'expected': float(bill['expected_amount']),
            'expected_day': f"{month}/{expected_day:02d}" if expected_day else '',
            'paid': False,
            'actual_amount': 0,
            'paid_date': '',
            'late': False,
            'acct': bill.get('acct', ''),
        }
        
        if match:
            status['paid'] = True
            status['actual_amount'] = abs(float(match['amount']))
            status['paid_date'] = match['transaction_date'].strftime('%m/%d')
            matched_txn_ids.add(match['id'])
            
            # Late if paid more than 5 days after expected
            if expected_day:
                paid_day = match['transaction_date'].day
                if paid_day > expected_day + 5:
                    status['late'] = True
        
        bill_statuses.append(status)
    
    # ---- CATEGORY BREAKDOWN ----
    # Group non-bill transactions by category
    categories = {}
    for txn in transactions:
        cat = txn['category_primary'] or 'Uncategorized'
        if cat not in categories:
            categories[cat] = {'name': cat, 'total': 0, 'transactions': []}
        
        categories[cat]['total'] += float(txn['amount'])
        categories[cat]['transactions'].append({
            'date': txn['transaction_date'].isoformat(),
            'description': txn['description'],
            'amount': float(txn['amount']),
            'acct': txn.get('acct', ''),
        })
    
    cat_list = sorted(categories.values(), key=lambda c: c['total'])
    
    return {
        'key': f"{year}-{month:02d}",
        'label': short_label,
        'full_label': month_label,
        'bills': bill_statuses,
        'categories': cat_list,
    }


def generate_report(num_months=6, output_path=None):
    """Generate the full HTML report"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get current balances
    balances = get_current_balances(cur)
    
    # Get recurring bills
    bills = get_recurring_bills(cur)
    
    # Build data for each month
    today = date.today()
    months_data = []
    
    for i in range(num_months):
        # Go backwards from current month
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        
        month_data = build_month_data(cur, y, m, bills)
        months_data.append(month_data)
    
    conn.close()
    
    # Build full report data
    report_data = {
        'generated': datetime.now().isoformat(),
        'balances': balances,
        'months': months_data,
    }
    
    # Load template
    template = TEMPLATE_PATH.read_text()
    
    # Inject data
    data_json = json.dumps(report_data, cls=DecimalEncoder)
    html = template.replace('"__REPORT_DATA__"', data_json)
    
    # Write output
    if output_path is None:
        DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
        output_path = DEFAULT_OUTPUT / f"report_{today.strftime('%Y%m%d')}.html"
    else:
        output_path = Path(output_path)
    
    output_path.write_text(html)
    print(f"✓ Report generated: {output_path}")
    print(f"  Months: {num_months}")
    print(f"  Balances: {', '.join(f'{b['name']}: ${b['balance']:,.2f}' for b in balances)}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Generate monthly financial report')
    parser.add_argument('--months', type=int, default=6, help='Number of months (default: 6)')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    generate_report(num_months=args.months, output_path=args.output)


if __name__ == '__main__':
    main()
