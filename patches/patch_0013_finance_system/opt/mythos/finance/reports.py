#!/usr/bin/env python3
"""
Mythos Finance - Reports
/opt/mythos/finance/reports.py

Generate financial reports from the database.

Usage:
    python reports.py summary
    python reports.py monthly
    python reports.py category
    python reports.py merchants
    python reports.py search <term>
    python reports.py uncategorized
    python reports.py recurring
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment
load_dotenv('/opt/mythos/.env')


def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "       -"
    return f"${amount:>10,.2f}"


def print_table(headers, rows, alignments=None):
    """Print a formatted table"""
    if not rows:
        print("No data found.")
        return
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))


def cmd_summary(args):
    """Show account summary"""
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n" + "=" * 60)
    print("FINANCIAL SUMMARY")
    print("=" * 60)
    
    # Account balances (from most recent transaction)
    print("\n📊 Account Summary:")
    cur.execute("""
        SELECT DISTINCT ON (a.id)
            a.bank_name,
            a.account_name,
            t.balance,
            t.transaction_date
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id AND t.balance IS NOT NULL
        ORDER BY a.id, t.transaction_date DESC
    """)
    for row in cur.fetchall():
        balance = format_currency(row['balance']) if row['balance'] else "N/A"
        date = row['transaction_date'] or "No transactions"
        print(f"  {row['bank_name']} - {row['account_name']}: {balance} (as of {date})")
    
    # This month's totals
    print("\n📅 This Month:")
    cur.execute("""
        SELECT 
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
    """)
    row = cur.fetchone()
    income = row['income'] or 0
    expenses = row['expenses'] or 0
    print(f"  Income:   {format_currency(income)}")
    print(f"  Expenses: {format_currency(expenses)}")
    print(f"  Net:      {format_currency(income - expenses)}")
    print(f"  Transactions: {row['transaction_count']}")
    
    # Recent transactions
    print("\n📝 Recent Transactions:")
    cur.execute("""
        SELECT 
            transaction_date,
            amount,
            COALESCE(merchant_name, LEFT(description, 30)) as merchant,
            category_primary
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
        LIMIT 10
    """)
    rows = [(
        row['transaction_date'],
        format_currency(row['amount']),
        row['merchant'][:30] if row['merchant'] else '-',
        row['category_primary'] or 'Uncategorized'
    ) for row in cur.fetchall()]
    print_table(['Date', 'Amount', 'Merchant', 'Category'], rows)
    
    # Import history
    print("\n📥 Recent Imports:")
    cur.execute("""
        SELECT 
            imported_at,
            source_file,
            imported_count,
            skipped_count
        FROM import_logs
        ORDER BY imported_at DESC
        LIMIT 5
    """)
    rows = [(
        row['imported_at'].strftime('%Y-%m-%d %H:%M'),
        row['source_file'],
        row['imported_count'],
        row['skipped_count']
    ) for row in cur.fetchall()]
    if rows:
        print_table(['Date', 'File', 'Imported', 'Skipped'], rows)
    else:
        print("  No imports yet.")
    
    conn.close()


def cmd_monthly(args):
    """Show monthly breakdown"""
    conn = get_connection()
    cur = conn.cursor()
    
    months = args.months or 6
    
    print(f"\n📅 Monthly Summary (Last {months} months):")
    cur.execute("""
        SELECT 
            DATE_TRUNC('month', transaction_date)::date as month,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses,
            COUNT(*) as transactions
        FROM transactions
        WHERE transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
        GROUP BY 1
        ORDER BY 1 DESC
    """, (months,))
    
    rows = [(
        row['month'].strftime('%Y-%m'),
        format_currency(row['income']),
        format_currency(row['expenses']),
        format_currency((row['income'] or 0) - (row['expenses'] or 0)),
        row['transactions']
    ) for row in cur.fetchall()]
    print_table(['Month', 'Income', 'Expenses', 'Net', 'Count'], rows)
    
    conn.close()


def cmd_category(args):
    """Show spending by category"""
    conn = get_connection()
    cur = conn.cursor()
    
    months = args.months or 3
    
    print(f"\n📊 Spending by Category (Last {months} months):")
    cur.execute("""
        SELECT 
            COALESCE(category_primary, 'Uncategorized') as category,
            SUM(ABS(amount)) as total,
            COUNT(*) as count,
            AVG(ABS(amount)) as avg_amount
        FROM transactions
        WHERE amount < 0
          AND transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
        GROUP BY 1
        ORDER BY 2 DESC
    """, (months,))
    
    rows = [(
        row['category'],
        format_currency(row['total']),
        row['count'],
        format_currency(row['avg_amount'])
    ) for row in cur.fetchall()]
    print_table(['Category', 'Total', 'Count', 'Average'], rows)
    
    conn.close()


def cmd_merchants(args):
    """Show top merchants"""
    conn = get_connection()
    cur = conn.cursor()
    
    limit = args.limit or 20
    months = args.months or 3
    
    print(f"\n🏪 Top Merchants (Last {months} months):")
    cur.execute("""
        SELECT 
            COALESCE(merchant_name, LEFT(description, 30)) as merchant,
            SUM(ABS(amount)) as total,
            COUNT(*) as count,
            MAX(transaction_date) as last_transaction
        FROM transactions
        WHERE amount < 0
          AND transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT %s
    """, (months, limit))
    
    rows = [(
        row['merchant'][:35] if row['merchant'] else '-',
        format_currency(row['total']),
        row['count'],
        row['last_transaction']
    ) for row in cur.fetchall()]
    print_table(['Merchant', 'Total Spent', 'Count', 'Last Transaction'], rows)
    
    conn.close()


def cmd_search(args):
    """Search transactions"""
    conn = get_connection()
    cur = conn.cursor()
    
    term = args.term
    
    print(f"\n🔍 Search Results for: '{term}'")
    cur.execute("""
        SELECT 
            transaction_date,
            amount,
            COALESCE(merchant_name, LEFT(description, 30)) as merchant,
            description,
            category_primary
        FROM transactions
        WHERE description ILIKE %s
           OR original_description ILIKE %s
           OR merchant_name ILIKE %s
        ORDER BY transaction_date DESC
        LIMIT 50
    """, (f'%{term}%', f'%{term}%', f'%{term}%'))
    
    rows = [(
        row['transaction_date'],
        format_currency(row['amount']),
        row['merchant'][:30] if row['merchant'] else '-',
        row['category_primary'] or '-'
    ) for row in cur.fetchall()]
    print_table(['Date', 'Amount', 'Merchant', 'Category'], rows)
    
    conn.close()


def cmd_uncategorized(args):
    """Show uncategorized transactions"""
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n❓ Uncategorized Transactions:")
    cur.execute("""
        SELECT 
            transaction_date,
            amount,
            description,
            original_description
        FROM transactions
        WHERE category_primary IS NULL 
           OR category_primary = 'Uncategorized'
           OR category_primary = 'Category Pending'
        ORDER BY transaction_date DESC
        LIMIT 50
    """)
    
    rows = [(
        row['transaction_date'],
        format_currency(row['amount']),
        row['description'][:50]
    ) for row in cur.fetchall()]
    print_table(['Date', 'Amount', 'Description'], rows)
    
    print("\nTo add a category mapping:")
    print("  INSERT INTO category_mappings (pattern, pattern_type, category_primary, merchant_name)")
    print("  VALUES ('PATTERN', 'contains', 'Category', 'Merchant Name');")
    
    conn.close()


def cmd_recurring(args):
    """Detect recurring transactions"""
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n🔄 Detected Recurring Transactions:")
    cur.execute("""
        SELECT 
            COALESCE(merchant_name, LEFT(description, 30)) as merchant,
            COUNT(*) as occurrences,
            AVG(ABS(amount)) as avg_amount,
            STDDEV(ABS(amount)) as amount_variance,
            MIN(transaction_date) as first_seen,
            MAX(transaction_date) as last_seen
        FROM transactions
        WHERE amount < 0
          AND transaction_date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY 1
        HAVING COUNT(*) >= 3
           AND STDDEV(ABS(amount)) < 10  -- Low variance suggests recurring
        ORDER BY occurrences DESC, avg_amount DESC
        LIMIT 30
    """)
    
    rows = [(
        row['merchant'][:30] if row['merchant'] else '-',
        row['occurrences'],
        format_currency(row['avg_amount']),
        row['first_seen'],
        row['last_seen']
    ) for row in cur.fetchall()]
    print_table(['Merchant', 'Count', 'Avg Amount', 'First', 'Last'], rows)
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Financial Reports')
    subparsers = parser.add_subparsers(dest='command', help='Report type')
    
    # Summary
    sub = subparsers.add_parser('summary', help='Account summary')
    sub.set_defaults(func=cmd_summary)
    
    # Monthly
    sub = subparsers.add_parser('monthly', help='Monthly breakdown')
    sub.add_argument('--months', type=int, default=6, help='Number of months')
    sub.set_defaults(func=cmd_monthly)
    
    # Category
    sub = subparsers.add_parser('category', help='Spending by category')
    sub.add_argument('--months', type=int, default=3, help='Number of months')
    sub.set_defaults(func=cmd_category)
    
    # Merchants
    sub = subparsers.add_parser('merchants', help='Top merchants')
    sub.add_argument('--limit', type=int, default=20, help='Number of merchants')
    sub.add_argument('--months', type=int, default=3, help='Number of months')
    sub.set_defaults(func=cmd_merchants)
    
    # Search
    sub = subparsers.add_parser('search', help='Search transactions')
    sub.add_argument('term', help='Search term')
    sub.set_defaults(func=cmd_search)
    
    # Uncategorized
    sub = subparsers.add_parser('uncategorized', help='Uncategorized transactions')
    sub.set_defaults(func=cmd_uncategorized)
    
    # Recurring
    sub = subparsers.add_parser('recurring', help='Detect recurring transactions')
    sub.set_defaults(func=cmd_recurring)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
