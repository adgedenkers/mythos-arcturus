#!/usr/bin/env python3
"""
Mythos Finance - Bill Matcher
/opt/mythos/finance/bill_matcher.py

Matches imported transactions against recurring_bills to track payments.
Called after import to identify which bills have been paid.

Usage:
    # As module (called from importer or patch monitor)
    from bill_matcher import BillMatcher
    matcher = BillMatcher()
    results = matcher.match_transactions(transaction_ids)
    
    # Standalone - match all unmatched transactions
    python bill_matcher.py
    python bill_matcher.py --month 2026-02
    python bill_matcher.py --dry-run
"""

import os
import sys
import argparse
import logging
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


class BillMatcher:
    """
    Matches transactions to recurring bills.
    
    Matching logic:
    1. Load all active recurring_bills with merchant_pattern
    2. For each transaction, check if description matches any bill's pattern (case-insensitive)
    3. Verify amount is within expected_amount ± amount_variance
    4. If match found, create entry in bill_payments (unless already tracked for that month)
    """
    
    def __init__(self, conn=None):
        self.bills = []
        self._own_conn = False
        if conn:
            self.conn = conn
        else:
            self.conn = get_db_connection()
            self._own_conn = True
        self._load_bills()
    
    def _load_bills(self):
        """Load active recurring bills with patterns"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, merchant_name, merchant_pattern, expected_amount, 
                   amount_variance, frequency, expected_day, category_primary, notes
            FROM recurring_bills
            WHERE is_active = true
              AND merchant_pattern IS NOT NULL
              AND merchant_pattern != ''
            ORDER BY id
        """)
        self.bills = cur.fetchall()
    
    def _determine_billing_month(self, txn_date, bill):
        """
        Determine which billing month a transaction belongs to.
        
        If the bill is due on day 15 and the transaction hits on day 14,
        it belongs to the current month's cycle.
        If it hits on day 16, it could be late for current month or early for next.
        We use a simple rule: transaction belongs to the month it occurs in.
        """
        if isinstance(txn_date, str):
            txn_date = datetime.strptime(txn_date, '%Y-%m-%d').date()
        return txn_date.strftime('%Y-%m')
    
    def match_single_transaction(self, txn):
        """
        Try to match a single transaction dict against known bills.
        
        Args:
            txn: dict with keys: id, description, original_description, amount, transaction_date
            
        Returns:
            dict with match info or None
        """
        desc = (txn.get('description') or '').upper()
        orig = (txn.get('original_description') or '').upper()
        amount = abs(Decimal(str(txn.get('amount', 0))))
        
        # Skip income transactions
        if txn.get('amount', 0) > 0:
            return None
        
        for bill in self.bills:
            pattern = bill['merchant_pattern'].upper()
            
            # Check pattern match against description or original_description
            if pattern not in desc and pattern not in orig:
                continue
            
            # Check amount within variance
            expected = abs(Decimal(str(bill['expected_amount'])))
            variance = Decimal(str(bill['amount_variance'] or 5))
            
            # For bills marked as varying significantly (high variance in notes),
            # be more lenient — just confirm it's a debit, pattern matches
            notes = (bill.get('notes') or '').lower()
            is_variable = any(word in notes for word in ['varies', 'variable', 'ext:'])
            
            if is_variable:
                # Variable bills: just need pattern match + it's a debit
                pass
            else:
                # Fixed bills: check amount is within variance
                if abs(amount - expected) > variance:
                    continue
            
            return {
                'bill_id': bill['id'],
                'bill_name': bill['merchant_name'],
                'expected_amount': expected,
                'actual_amount': amount,
                'matched_pattern': bill['merchant_pattern'],
            }
        
        return None
    
    def match_transactions(self, transaction_ids=None, month=None, dry_run=False):
        """
        Match transactions against recurring bills and record payments.
        
        Args:
            transaction_ids: list of specific transaction IDs to check (e.g. from recent import)
                            If None, checks all unmatched transactions
            month: billing month to restrict to (e.g. '2026-02')
            dry_run: if True, don't write to DB
            
        Returns:
            dict with results: matched, already_tracked, unmatched counts + details
        """
        cur = self.conn.cursor()
        
        # Build query for transactions to check
        if transaction_ids:
            cur.execute("""
                SELECT id, description, original_description, amount, transaction_date, 
                       category_primary, account_id
                FROM transactions
                WHERE id = ANY(%s)
                  AND amount < 0
                ORDER BY transaction_date DESC
            """, (transaction_ids,))
        else:
            # Get all debit transactions not yet matched to bill_payments
            query = """
                SELECT t.id, t.description, t.original_description, t.amount, 
                       t.transaction_date, t.category_primary, t.account_id
                FROM transactions t
                LEFT JOIN bill_payments bp ON bp.transaction_id = t.id
                WHERE t.amount < 0
                  AND bp.id IS NULL
            """
            params = []
            if month:
                query += " AND TO_CHAR(t.transaction_date, 'YYYY-MM') = %s"
                params.append(month)
            query += " ORDER BY t.transaction_date DESC"
            cur.execute(query, params if params else None)
        
        transactions = cur.fetchall()
        
        results = {
            'total_checked': len(transactions),
            'matched': [],
            'already_tracked': 0,
            'no_match': 0,
        }
        
        for txn in transactions:
            match = self.match_single_transaction(txn)
            
            if not match:
                results['no_match'] += 1
                continue
            
            billing_month = self._determine_billing_month(txn['transaction_date'], 
                                                           next(b for b in self.bills if b['id'] == match['bill_id']))
            
            # Check if already tracked for this month
            cur.execute("""
                SELECT id FROM bill_payments
                WHERE bill_id = %s AND billing_month = %s AND matched_automatically = true
            """, (match['bill_id'], billing_month))
            
            existing = cur.fetchone()
            if existing:
                results['already_tracked'] += 1
                continue
            
            # Record the payment
            if not dry_run:
                try:
                    cur.execute("""
                        INSERT INTO bill_payments (bill_id, transaction_id, payment_date, amount_paid, billing_month, matched_automatically)
                        VALUES (%s, %s, %s, %s, %s, true)
                        ON CONFLICT DO NOTHING
                    """, (
                        match['bill_id'],
                        txn['id'],
                        txn['transaction_date'],
                        abs(txn['amount']),
                        billing_month,
                    ))
                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Failed to record bill payment: {e}")
                    continue
            
            # Also mark transaction as recurring
            if not dry_run:
                try:
                    cur.execute(
                        "UPDATE transactions SET is_recurring = true WHERE id = %s",
                        (txn['id'],)
                    )
                    self.conn.commit()
                except Exception:
                    self.conn.rollback()
            
            results['matched'].append({
                'bill_name': match['bill_name'],
                'bill_id': match['bill_id'],
                'transaction_id': txn['id'],
                'expected': float(match['expected_amount']),
                'actual': float(match['actual_amount']),
                'date': str(txn['transaction_date']),
                'billing_month': billing_month,
            })
        
        return results
    
    def get_unpaid_bills(self, month=None):
        """
        Get bills that haven't been paid yet this month.
        
        Args:
            month: billing month (default: current month)
            
        Returns:
            list of unpaid bill dicts
        """
        if not month:
            month = date.today().strftime('%Y-%m')
        
        cur = self.conn.cursor()
        cur.execute("""
            SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day, 
                   rb.frequency, rb.notes
            FROM recurring_bills rb
            WHERE rb.is_active = true
              AND rb.frequency = 'monthly'
              AND rb.id NOT IN (
                  SELECT bill_id FROM bill_payments WHERE billing_month = %s
              )
            ORDER BY rb.expected_day
        """, (month,))
        
        return cur.fetchall()
    
    def close(self):
        if self._own_conn and self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='Match transactions to recurring bills')
    parser.add_argument('--month', help='Billing month (YYYY-MM)')
    parser.add_argument('--dry-run', action='store_true', help='Show matches without writing')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    
    matcher = BillMatcher()
    
    try:
        results = matcher.match_transactions(month=args.month, dry_run=args.dry_run)
        
        print(f"\nBill Matching Results:")
        print(f"  Transactions checked: {results['total_checked']}")
        print(f"  Bills matched:        {len(results['matched'])}")
        print(f"  Already tracked:      {results['already_tracked']}")
        print(f"  No match:             {results['no_match']}")
        
        if results['matched']:
            print(f"\nMatched Bills:")
            for m in results['matched']:
                print(f"  ✓ {m['bill_name']:25} ${m['actual']:>8.2f} (expected ${m['expected']:>8.2f}) — {m['date']}")
        
        # Show unpaid
        month = args.month or date.today().strftime('%Y-%m')
        unpaid = matcher.get_unpaid_bills(month)
        if unpaid:
            print(f"\nUnpaid bills for {month}:")
            for bill in unpaid:
                day = bill['expected_day'] or '??'
                print(f"  ○ {bill['merchant_name']:25} ${float(bill['expected_amount']):>8.2f}  due day {day}")
    finally:
        matcher.close()


if __name__ == '__main__':
    main()
