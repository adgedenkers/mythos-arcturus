#!/usr/bin/env python3
"""
Mythos Finance - Post-Import Analyzer
/opt/mythos/finance/post_import_analyzer.py

Runs after a bank CSV import to:
1. Match imported transactions against recurring bills
2. Summarize categorization results
3. Send a formatted Telegram report with:
   - New transactions imported (count + total)
   - Bills matched/paid
   - Unpaid bills remaining this month
   - Categorization breakdown
   - Any uncategorized transactions flagged

Called by the patch monitor after successful CSV import.

Usage:
    # From patch monitor (programmatic)
    from post_import_analyzer import PostImportAnalyzer
    analyzer = PostImportAnalyzer()
    report = analyzer.analyze_import(bank='usaa', imported_count=12, source_file='bk_download.csv')
    analyzer.send_telegram_report(report)
    
    # Standalone (re-analyze recent imports)
    python post_import_analyzer.py --bank usaa --count 12
    python post_import_analyzer.py --match-all --month 2026-02
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

import psycopg2
from psycopg2.extras import RealDictCursor

# Add finance dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from bill_matcher import BillMatcher

logger = logging.getLogger(__name__)

MYTHOS_ROOT = Path("/opt/mythos")
VENV_PY = MYTHOS_ROOT / ".venv/bin/python"
TELEGRAM_ID_KA = os.getenv('TELEGRAM_ID_KA')
TELEGRAM_ID_SERAPHE = os.getenv('TELEGRAM_ID_SERAPHE')


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


class PostImportAnalyzer:
    """Analyzes newly imported transactions and generates a comprehensive report."""
    
    def __init__(self):
        self.conn = get_db_connection()
        self.cur = self.conn.cursor()
    
    def analyze_import(self, bank: str, imported_count: int, skipped_count: int = 0,
                       source_file: str = None, prompt_balance: bool = False):
        """
        Analyze a completed import and build a report.
        
        Args:
            bank: 'sunmark' or 'usaa'
            imported_count: number of new transactions imported
            skipped_count: number of duplicates skipped
            source_file: original filename
            prompt_balance: if True, include balance prompt for USAA
            
        Returns:
            dict with full report data
        """
        report = {
            'bank': bank.upper(),
            'source_file': source_file,
            'imported': imported_count,
            'skipped': skipped_count,
            'timestamp': datetime.now().isoformat(),
            'new_transactions': [],
            'bill_matches': [],
            'unpaid_bills': [],
            'category_summary': {},
            'uncategorized': [],
            'account_balance': None,
            'prompt_balance': prompt_balance,
        }
        
        if imported_count == 0:
            return report
        
        # Get the newly imported transactions (most recent N by created_at)
        account_id = 1 if bank.lower() == 'sunmark' else 2
        self.cur.execute("""
            SELECT id, transaction_date, description, original_description, 
                   amount, category_primary, merchant_name, balance
            FROM transactions
            WHERE account_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (account_id, imported_count + skipped_count))
        
        recent_txns = self.cur.fetchall()
        
        # Filter to just the imported ones (the newest N)
        # Since we ordered by created_at DESC, the first `imported_count` are the new ones
        new_txns = recent_txns[:imported_count]
        new_ids = [t['id'] for t in new_txns]
        
        report['new_transactions'] = [{
            'id': t['id'],
            'date': str(t['transaction_date']),
            'description': t['description'],
            'amount': float(t['amount']),
            'category': t['category_primary'] or 'Uncategorized',
        } for t in new_txns]
        
        # ---- Bill Matching ----
        matcher = BillMatcher(conn=self.conn)
        match_results = matcher.match_transactions(transaction_ids=new_ids)
        report['bill_matches'] = match_results['matched']
        
        # Get unpaid bills for current month
        current_month = date.today().strftime('%Y-%m')
        unpaid = matcher.get_unpaid_bills(current_month)
        report['unpaid_bills'] = [{
            'name': b['merchant_name'],
            'amount': float(b['expected_amount']),
            'due_day': b['expected_day'],
        } for b in unpaid]
        
        # ---- Category Summary ----
        cat_counts = {}
        for t in new_txns:
            cat = t['category_primary'] or 'Uncategorized'
            if cat not in cat_counts:
                cat_counts[cat] = {'count': 0, 'total': Decimal('0')}
            cat_counts[cat]['count'] += 1
            cat_counts[cat]['total'] += t['amount']
        
        report['category_summary'] = {
            cat: {'count': v['count'], 'total': float(v['total'])}
            for cat, v in sorted(cat_counts.items(), key=lambda x: x[1]['total'])
        }
        
        # Flagged uncategorized
        report['uncategorized'] = [
            {'date': str(t['transaction_date']), 'description': t['description'], 'amount': float(t['amount'])}
            for t in new_txns if not t['category_primary']
        ]
        
        # ---- Account Balance ----
        self.cur.execute(
            "SELECT current_balance, balance_updated_at FROM accounts WHERE id = %s",
            (account_id,)
        )
        acct = self.cur.fetchone()
        if acct and acct['current_balance']:
            report['account_balance'] = float(acct['current_balance'])
        
        return report
    
    def format_telegram_html(self, report):
        """Format the report as Telegram HTML message."""
        bank = report['bank']
        imported = report['imported']
        skipped = report['skipped']
        
        if imported == 0:
            msg = f"ℹ️ <b>Finance Import — Up to Date</b>\n\n"
            msg += f"Bank: {bank}\n"
            msg += f"All {skipped} transactions already in DB\n"
            
            if report.get('prompt_balance'):
                msg += f"\n💡 Set USAA balance:\n<code>/setbalance USAA [amount]</code>"
            return msg
        
        # ---- Header ----
        total_amount = sum(t['amount'] for t in report['new_transactions'])
        income = sum(t['amount'] for t in report['new_transactions'] if t['amount'] > 0)
        expense = sum(t['amount'] for t in report['new_transactions'] if t['amount'] < 0)
        
        msg = f"✅ <b>Finance Import Complete</b>\n\n"
        msg += f"<b>Bank:</b> {bank}\n"
        msg += f"<b>New:</b> {imported} transactions"
        if skipped:
            msg += f" ({skipped} skipped)"
        msg += "\n"
        
        if income > 0:
            msg += f"<b>Income:</b> +${income:,.2f}\n"
        if expense < 0:
            msg += f"<b>Spending:</b> ${expense:,.2f}\n"
        
        if report.get('account_balance') is not None:
            msg += f"<b>Balance:</b> ${report['account_balance']:,.2f}\n"
        
        # ---- Bill Matches ----
        if report['bill_matches']:
            msg += f"\n📋 <b>Bills Matched ({len(report['bill_matches'])})</b>\n"
            for m in report['bill_matches']:
                expected = m['expected']
                actual = m['actual']
                delta = ""
                if abs(actual - expected) > 1:
                    diff = actual - expected
                    delta = f" ({'+' if diff > 0 else ''}{diff:,.2f})"
                msg += f"  ✓ {m['bill_name']} — ${actual:,.2f}{delta}\n"
        
        # ---- Unpaid Bills ----
        if report['unpaid_bills']:
            today = date.today().day
            upcoming = [b for b in report['unpaid_bills'] if b['due_day'] and b['due_day'] >= today]
            overdue = [b for b in report['unpaid_bills'] if b['due_day'] and b['due_day'] < today]
            no_day = [b for b in report['unpaid_bills'] if not b['due_day']]
            
            remaining_total = sum(b['amount'] for b in report['unpaid_bills'] if b['due_day'])
            msg += f"\n📅 <b>Remaining This Month</b> (~${remaining_total:,.2f})\n"
            
            if overdue:
                for b in overdue:
                    msg += f"  ⚠️ {b['name']} — ${b['amount']:,.2f} (due day {b['due_day']})\n"
            if upcoming:
                for b in upcoming[:8]:  # Cap at 8 to avoid message length issues
                    msg += f"  ○ {b['name']} — ${b['amount']:,.2f} (day {b['due_day']})\n"
                if len(upcoming) > 8:
                    msg += f"  ... +{len(upcoming) - 8} more\n"
        
        # ---- Category Breakdown ----
        if report['category_summary']:
            msg += f"\n📊 <b>Categories</b>\n"
            # Sort by total amount (most negative first = biggest spending)
            sorted_cats = sorted(report['category_summary'].items(), key=lambda x: x[1]['total'])
            for cat, data in sorted_cats[:10]:
                total = data['total']
                count = data['count']
                if total < 0:
                    msg += f"  {cat}: ${total:,.2f} ({count})\n"
                else:
                    msg += f"  {cat}: +${total:,.2f} ({count})\n"
        
        # ---- Uncategorized ----
        if report['uncategorized']:
            msg += f"\n❓ <b>Uncategorized ({len(report['uncategorized'])})</b>\n"
            for t in report['uncategorized'][:5]:
                msg += f"  • {t['description'][:30]} ${t['amount']:,.2f}\n"
            if len(report['uncategorized']) > 5:
                msg += f"  ... +{len(report['uncategorized']) - 5} more\n"
        
        # ---- USAA Balance Prompt ----
        if report.get('prompt_balance'):
            msg += f"\n💡 <b>Update USAA balance:</b>\n<code>/setbalance USAA [amount]</code>"
        
        return msg
    
    def send_telegram_report(self, report):
        """Send the formatted report via Telegram."""
        html_msg = self.format_telegram_html(report)
        self._send_telegram(html_msg)
    
    def _send_telegram(self, message):
        """Send message via Telegram notification script."""
        try:
            bot_script = MYTHOS_ROOT / "telegram_bot" / "send_notification.py"
            if bot_script.exists():
                subprocess.run(
                    [str(VENV_PY), str(bot_script), message],
                    capture_output=True,
                    timeout=30
                )
            else:
                logger.warning("Telegram notification script not found")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    def close(self):
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='Post-import analysis')
    parser.add_argument('--bank', required=True, choices=['sunmark', 'usaa'])
    parser.add_argument('--count', type=int, default=0, help='Number of imported transactions')
    parser.add_argument('--skipped', type=int, default=0)
    parser.add_argument('--match-all', action='store_true', help='Run bill matching on all unmatched transactions')
    parser.add_argument('--month', help='Restrict to billing month (YYYY-MM)')
    parser.add_argument('--send', action='store_true', help='Send report via Telegram')
    args = parser.parse_args()
    
    analyzer = PostImportAnalyzer()
    
    try:
        if args.match_all:
            # Just run bill matching standalone
            matcher = BillMatcher()
            results = matcher.match_transactions(month=args.month)
            print(f"Matched: {len(results['matched'])}")
            print(f"Already tracked: {results['already_tracked']}")
            print(f"No match: {results['no_match']}")
            for m in results['matched']:
                print(f"  ✓ {m['bill_name']:25} ${m['actual']:>8.2f} — {m['date']}")
            matcher.close()
        else:
            report = analyzer.analyze_import(
                bank=args.bank,
                imported_count=args.count,
                skipped_count=args.skipped,
                prompt_balance=(args.bank == 'usaa'),
            )
            
            # Print report
            print(analyzer.format_telegram_html(report))
            
            if args.send:
                analyzer.send_telegram_report(report)
                print("\n✓ Report sent to Telegram")
    finally:
        analyzer.close()


if __name__ == '__main__':
    main()
