#!/usr/bin/env python3
"""
Mythos Finance Importer v6
/opt/mythos/finance/importer.py

Changes in v6 (SYS-DRAFT_fix_transaction_hash):
- USAA: Replaced content-based hash dedup with overlap detection.
  Every transaction in the bank export is real. Dedup is now based on
  counting (date, amount, original_description) tuples in the file vs DB.
  If the file has more of a given tuple than the DB, the extras are new.
- Sunmark: Dedup now uses bank transaction number (already unique per row).
  If the transaction number exists in DB, skip. Otherwise import.
- Removed --allow-dupes flag (no longer needed — all transactions are trusted).
- Removed duplicate recalc_balances function.
- USAA pending transactions are logged but not imported (Status != 'Posted').
- File import is logged with file content hash to detect exact re-imports.

Usage:
    python importer.py sunmark /path/to/file.CSV
    python importer.py usaa /path/to/file.csv --balance 1243.19
    python importer.py usaa /path/to/file.csv --balance 1243.19 --dry-run
    python importer.py sunmark /path/to/file.CSV --dry-run
"""
import os
import sys
import csv
import hashlib
import argparse
import shutil
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from collections import Counter

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

from categorizer import Categorizer

ACCOUNT_IDS = {
    'sunmark': 1,
    'usaa': 2,
}

ARCHIVE_DIR = Path('/opt/mythos/finance/archive/imports')


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def hash_file_contents(filepath: str) -> str:
    """SHA256 of file contents for exact re-import detection."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def make_hash(account_id: int, date_str: str, amount: Decimal,
              original_description: str, sequence: int) -> str:
    """
    Hash that always includes a sequence number.
    sequence = the occurrence index of this (date, amount, orig_desc) tuple
    within this import. So if there are 3 Amazon $14.00 on the same day,
    they get sequence 0, 1, 2.
    """
    raw = f"{account_id}|{date_str}|{amount}|{original_description}|{sequence}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def parse_decimal(value: str) -> Decimal:
    if not value or value.strip() == '':
        return Decimal('0')
    clean = value.replace('$', '').replace(',', '').strip().strip('"')
    if clean == '' or clean == '-':
        return Decimal('0')
    try:
        return Decimal(clean)
    except InvalidOperation:
        return Decimal('0')


def parse_date(date_str: str) -> str:
    date_str = date_str.strip().strip('"')
    try:
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    raise ValueError(f"Cannot parse date: {date_str}")


def clean_description_sunmark(description: str, memo: str) -> str:
    desc = description.strip().strip('"')
    memo = memo.strip().strip('"') if memo else ''

    payment_processors = ['PAYPAL', 'VENMO', 'ZELLE', 'CASHAPP', 'CASH APP']
    payment_type = None
    desc_upper = desc.upper()
    for processor in payment_processors:
        if processor in desc_upper:
            payment_type = processor.title()
            if processor == 'CASHAPP' or processor == 'CASH APP':
                payment_type = 'CashApp'
            break

    type_patterns = [
        ('Overdraft Fee ', 'OD Fee:'),
        ('Overdraft Fee', 'OD Fee:'),
        ('External Withdrawal ', 'EXT:'),
        ('External Withdrawal', 'EXT:'),
        ('External Deposit ', 'DEP:'),
        ('External Deposit', 'DEP:'),
        ('ATM Withdrawal ', 'ATM:'),
        ('ATM Withdrawal', 'ATM:'),
        ('Deposit Shared Branch Mobile', 'Mobile Deposit:'),
        ('Deposit Shared Branch ', 'Branch Deposit:'),
        ('Deposit Shared Branch', 'Branch Deposit:'),
        ('Withdrawal Internet Transfer to ', 'Xfer to:'),
        ('Withdrawal Internet Transfer from ', 'Xfer from:'),
        ('Withdrawal Internet Transfer ', 'Xfer:'),
        ('Withdrawal Internet Transfer', 'Xfer:'),
        ('Internet Transfer to ', 'Xfer to:'),
        ('Internet Transfer from ', 'Xfer from:'),
        ('Point Of Sale Withdrawal ', ''),
        ('Point Of Sale Withdrawal', ''),
        ('Point Of Sale Deposit ', ''),
        ('Point Of Sale Deposit', ''),
        ('Point Of Sale Purchase ', ''),
        ('Point Of Sale Purchase', ''),
        ('Point Of Sale ', ''),
        ('Point Of Sale', ''),
    ]

    txn_prefix = ''
    remainder = desc
    for pattern, replacement in type_patterns:
        if desc_upper.startswith(pattern.upper()):
            txn_prefix = replacement
            remainder = desc[len(pattern):].strip()
            break

    merchant = remainder
    if payment_type:
        for processor in payment_processors:
            merchant = re.sub(rf'\b{processor}\b\s*', '', merchant,
                              flags=re.IGNORECASE)

    merchant = re.sub(r'^\*+\s*', '', merchant)
    merchant = merchant.strip()

    if not merchant or len(merchant) < 2:
        if memo:
            memo_merchant = memo
            memo_merchant = re.sub(r'^\*+\s*', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}US$', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}$', '', memo_merchant)
            memo_merchant = re.sub(r'\s*\d{7,}', '', memo_merchant)
            parts = re.split(
                r'\s+(\d{2,}\s+(?:ST|AVE|RD|DR|BLVD|HWY|PKWY|N\s|S\s|E\s|W\s|'
                r'SW\s|NW\s|SE\s|NE\s|CANAL|MAIN|STATE))',
                memo_merchant, maxsplit=1, flags=re.IGNORECASE
            )
            if parts:
                memo_merchant = parts[0].strip()
            memo_merchant = re.sub(r'\s+\d[\d\s]*$', '', memo_merchant)
            merchant = memo_merchant.strip()

    if merchant.upper() in ['DEPOSIT', 'WITHDRAWAL', '']:
        if memo:
            memo_merchant = memo
            memo_merchant = re.sub(r'^\*+\s*', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}US$', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}$', '', memo_merchant)
            memo_merchant = re.sub(r'\s*\d{7,}', '', memo_merchant)
            parts = re.split(r'\s+\d{2,}\s+', memo_merchant, maxsplit=1)
            if parts:
                memo_merchant = parts[0].strip()
            memo_merchant = re.sub(r'\s+\d[\d\s]*$', '', memo_merchant)
            merchant = memo_merchant.strip()

    if 'Mobile Deposit' in txn_prefix:
        location = re.sub(r'\s+[A-Z]{2}$', '', memo).strip() if memo else ''
        merchant = location if location else ''

    if payment_type:
        if not merchant or len(merchant) < 2:
            if memo:
                memo_clean = re.sub(r'^\*+\s*', '', memo)
                memo_clean = re.sub(r'\s+\d{3,}.*$', '', memo_clean)
                memo_clean = re.sub(r'\s+[A-Z]{2}US$', '', memo_clean)
                memo_clean = re.sub(r'\s+[A-Z]{2}$', '', memo_clean)
                merchant = memo_clean.strip()
        merchant = re.sub(r'\s+\d{3,}.*$', '', merchant)
        merchant = merchant.strip()
        if txn_prefix and 'OD' in txn_prefix:
            result = f"{txn_prefix} {payment_type}: {merchant}"
        else:
            result = f"{payment_type}: {merchant}"
    elif txn_prefix:
        result = f"{txn_prefix} {merchant}"
    else:
        result = merchant if merchant else desc

    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r':\s*:', ':', result)
    result = re.sub(r':\s*$', '', result)
    result = result.strip(': -')

    if len(result) > 50:
        result = result[:47] + '...'

    return result if result else desc


def clean_description_usaa(description: str, original_desc: str) -> str:
    desc = description.strip().strip('"')

    if desc == 'Defense Finance and Accounting Service':
        return 'DFAS Salary'
    if desc == 'Social Security':
        return 'SSA'
    if desc == 'Mobile Deposit':
        return 'Mobile Deposit'
    if desc == 'ATM Fee Rebate':
        return 'ATM Fee Rebate'
    if 'UNSECURED FIXED RATE LOAN' in desc.upper():
        return 'USAA Loan Payment'

    if len(desc) > 100:
        desc = desc[:97] + '...'
    return desc


class SunmarkParser:
    """Parser for Sunmark CSV exports — dedup by transaction number."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.account_id = ACCOUNT_IDS['sunmark']
        self.transactions = []

    def parse(self) -> list:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 5:
            print("File too short - no data rows")
            return []

        for line in lines[4:]:
            line = line.strip()
            if not line:
                continue

            reader = csv.reader([line])
            try:
                row = next(reader)
            except:
                continue

            if len(row) < 7:
                continue

            txn_num = row[0].strip('"')
            date_str = row[1].strip('"')
            description = row[2]
            memo = row[3] if len(row) > 3 else ''
            debit = row[4] if len(row) > 4 else ''
            credit = row[5] if len(row) > 5 else ''
            balance = row[6] if len(row) > 6 else ''

            clean_desc = clean_description_sunmark(description, memo)
            original_desc = f"{description}|{memo}"

            debit_amt = parse_decimal(debit)
            credit_amt = parse_decimal(credit)

            if debit_amt != 0:
                amount = -abs(debit_amt)
            elif credit_amt != 0:
                amount = abs(credit_amt)
            else:
                continue

            try:
                parsed_date = parse_date(date_str)
            except ValueError as e:
                print(f"Skipping row with bad date: {e}")
                continue

            balance_amt = parse_decimal(balance) if balance else None

            # Hash includes txn_num — unique per Sunmark row
            raw = f"{self.account_id}|{parsed_date}|{amount}|{original_desc}|txn_{txn_num}"
            hash_id = hashlib.sha256(raw.encode()).hexdigest()[:16]

            self.transactions.append({
                'account_id': self.account_id,
                'transaction_date': parsed_date,
                'description': clean_desc,
                'original_description': original_desc,
                'amount': amount,
                'balance': balance_amt,
                'bank_transaction_id': txn_num,
                'is_pending': False,
                'hash_id': hash_id,
            })

        return self.transactions

    def get_current_balance(self) -> Decimal:
        if not self.transactions:
            return None
        return self.transactions[0].get('balance')


class USAAParser:
    """Parser for USAA CSV exports — overlap detection, no content dedup."""

    def __init__(self, filepath: str, known_balance: Decimal = None):
        self.filepath = filepath
        self.account_id = ACCOUNT_IDS['usaa']
        self.known_balance = known_balance
        self.transactions = []
        self.pending_transactions = []

    def parse(self) -> list:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return []

        for row in rows:
            date_str = row.get('Date', '').strip()
            description = row.get('Description', '').strip()
            original_desc = row.get('Original Description', '').strip()
            category = row.get('Category', '').strip()
            amount_str = row.get('Amount', '').strip()
            status = row.get('Status', '').strip()

            try:
                parsed_date = parse_date(date_str)
            except ValueError:
                continue

            amount = parse_decimal(amount_str)
            if amount == 0:
                continue

            clean_desc = clean_description_usaa(description, original_desc)

            txn = {
                'account_id': self.account_id,
                'transaction_date': parsed_date,
                'description': clean_desc,
                'original_description': original_desc or description,
                'amount': amount,
                'balance': None,
                'category_primary': category if category != 'Category Pending' else None,
                'bank_transaction_id': None,
                'is_pending': False,
                'hash_id': None,  # assigned during overlap detection
            }

            if 'Pending' in status or 'Scheduled' in status:
                txn['is_pending'] = True
                self.pending_transactions.append(txn)
                continue

            self.transactions.append(txn)

        return self.transactions

    def get_current_balance(self) -> Decimal:
        return self.known_balance


class Importer:
    """Database importer with overlap detection for USAA, txn-number dedup for Sunmark."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.conn = None
        self.cur = None
        self.categorizer = None

    def connect(self):
        if not self.dry_run:
            self.conn = get_db_connection()
            self.cur = self.conn.cursor()
            self.categorizer = Categorizer(conn=self.conn)
            if self.verbose:
                print(f"Loaded {self.categorizer.mapping_count} category mappings")
        else:
            self.categorizer = Categorizer()
            if self.verbose:
                print(f"Loaded {self.categorizer.mapping_count} category mappings")

    def close(self):
        if self.conn:
            self.conn.close()

    def _find_new_usaa_transactions(self, transactions: list) -> list:
        """
        Overlap detection for USAA.
        For each unique (date, amount, original_description) tuple,
        count occurrences in the file vs the DB. Import only the extras.
        """
        if not transactions:
            return []

        # Count each tuple in the incoming file
        file_counter = Counter()
        file_by_key = {}
        for txn in transactions:
            key = (txn['transaction_date'], str(txn['amount']),
                   txn['original_description'])
            file_counter[key] += 1
            if key not in file_by_key:
                file_by_key[key] = []
            file_by_key[key].append(txn)

        # Get date range from file
        dates = [t['transaction_date'] for t in transactions]
        min_date = min(dates)
        max_date = max(dates)

        # Count each tuple in the DB for this date range
        db_counter = Counter()
        if not self.dry_run:
            self.cur.execute("""
                SELECT transaction_date::text, amount::text, original_description,
                       COUNT(*) as cnt
                FROM transactions
                WHERE account_id = %s
                  AND transaction_date >= %s
                  AND transaction_date <= %s
                GROUP BY transaction_date, amount, original_description
            """, (ACCOUNT_IDS['usaa'], min_date, max_date))

            for row in self.cur.fetchall():
                key = (row['transaction_date'], row['amount'],
                       row['original_description'])
                db_counter[key] = row['cnt']

        # Find new transactions: file count - db count = new ones
        new_transactions = []
        for key, file_count in file_counter.items():
            db_count = db_counter.get(key, 0)
            new_count = file_count - db_count

            if new_count > 0:
                # Take the last N from the file's list for this key
                # (they're all identical content-wise, order doesn't matter)
                candidates = file_by_key[key]
                for i, txn in enumerate(candidates[-new_count:]):
                    # Assign hash with sequence = db_count + i
                    # This ensures stable hashes: if DB has 2 and we add 1,
                    # the new one gets sequence=2
                    seq = db_count + i
                    txn['hash_id'] = make_hash(
                        txn['account_id'], txn['transaction_date'],
                        txn['amount'], txn['original_description'], seq
                    )
                    new_transactions.append(txn)

        if self.verbose:
            total_file = len(transactions)
            total_new = len(new_transactions)
            print(f"  Overlap detection: {total_file} in file, "
                  f"{total_file - total_new} already in DB, "
                  f"{total_new} new")

        return new_transactions

    def _find_new_sunmark_transactions(self, transactions: list) -> list:
        """
        Sunmark dedup by bank transaction number.
        If the txn number exists in DB, skip. Otherwise import.
        """
        if not transactions or self.dry_run:
            return transactions

        txn_nums = [t['bank_transaction_id'] for t in transactions
                    if t.get('bank_transaction_id')]

        if not txn_nums:
            return transactions

        self.cur.execute("""
            SELECT bank_transaction_id
            FROM transactions
            WHERE account_id = %s
              AND bank_transaction_id = ANY(%s)
        """, (ACCOUNT_IDS['sunmark'], txn_nums))

        existing = {row['bank_transaction_id'] for row in self.cur.fetchall()}

        new_txns = [t for t in transactions
                    if t.get('bank_transaction_id') not in existing]

        if self.verbose:
            print(f"  Sunmark dedup: {len(transactions)} in file, "
                  f"{len(existing)} already in DB, "
                  f"{len(new_txns)} new")

        return new_txns

    def import_transactions(self, transactions: list, source_file: str,
                            bank: str) -> dict:
        results = {
            'total': len(transactions),
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'categorized': 0,
            'uncategorized': 0,
            'failed': [],
        }

        if not transactions:
            return results

        # --- Overlap / dedup detection ---
        if bank == 'usaa':
            new_txns = self._find_new_usaa_transactions(transactions)
        elif bank == 'sunmark':
            new_txns = self._find_new_sunmark_transactions(transactions)
        else:
            new_txns = transactions

        results['skipped'] = len(transactions) - len(new_txns)

        # --- Categorize ---
        if self.verbose:
            print(f"\nCategorizing {len(new_txns)} new transactions...")

        for txn in new_txns:
            if self.categorizer:
                cat_result = self.categorizer.categorize_transaction(txn)
                if cat_result:
                    results['categorized'] += 1
                else:
                    if not txn.get('category_primary'):
                        results['uncategorized'] += 1
                    else:
                        results['categorized'] += 1

        # --- Dry run output ---
        if self.dry_run:
            print(f"\nWould import {len(new_txns)} transactions:")
            for txn in new_txns[:15]:
                cat = txn.get('category_primary', '?')
                print(f"  {txn['transaction_date']} | {txn['amount']:>10.2f} | "
                      f"{cat:15} | {txn['description'][:35]}")
            if len(new_txns) > 15:
                print(f"  ... and {len(new_txns) - 15} more")
            results['imported'] = len(new_txns)
            return results

        # --- Insert ---
        for t in new_txns:
            try:
                self.cur.execute(
                    """
                    INSERT INTO transactions (
                        account_id, transaction_date, description,
                        original_description, amount, balance,
                        category_primary, category_secondary,
                        merchant_name, bank_transaction_id,
                        hash_id, is_pending, source_file
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        t['account_id'], t['transaction_date'],
                        t['description'], t.get('original_description'),
                        t['amount'], t.get('balance'),
                        t.get('category_primary'), t.get('category_secondary'),
                        t.get('merchant_name'), t.get('bank_transaction_id'),
                        t['hash_id'], t.get('is_pending', False), source_file,
                    )
                )
                self.conn.commit()
                results['imported'] += 1
            except Exception as e:
                self.conn.rollback()
                results['failed'].append({
                    'transaction': t, 'reason': str(e)
                })
                results['errors'] += 1

        if results['failed'] and self.verbose:
            print(f"\n⚠️  {len(results['failed'])} transactions failed:")
            for fail in results['failed'][:5]:
                t = fail['transaction']
                print(f"    {t.get('transaction_date', '?')} | "
                      f"{t.get('description', '?')[:30]} - {fail['reason']}")
            if len(results['failed']) > 5:
                print(f"    ... and {len(results['failed']) - 5} more")

        return results

    def update_account_balance(self, account_id: int, balance: Decimal):
        if self.dry_run:
            print(f"\nWould update account {account_id} balance to ${balance:.2f}")
            return
        self.cur.execute(
            "UPDATE accounts SET current_balance = %s, "
            "balance_updated_at = NOW() WHERE id = %s",
            (balance, account_id)
        )
        self.conn.commit()
        if self.verbose:
            print(f"\nUpdated account balance to ${balance:.2f}")

    def log_import(self, account_id: int, source_file: str, filepath: str,
                   file_hash: str, results: dict, date_range: tuple = None):
        """Log the import to import_logs table."""
        if self.dry_run:
            return

        min_date = date_range[0] if date_range else None
        max_date = date_range[1] if date_range else None

        self.cur.execute(
            """
            INSERT INTO import_logs (
                account_id, source_file, file_path,
                total_rows, imported_count, skipped_count, error_count,
                date_range_start, date_range_end,
                imported_by, file_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                account_id, source_file, filepath,
                results['total'], results['imported'],
                results['skipped'], results['errors'],
                min_date, max_date,
                'auto-import', file_hash,
            )
        )
        self.conn.commit()


def archive_file(filepath: str, bank: str):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = Path(filepath).suffix
    archive_name = f"{bank}_{timestamp}{ext}"
    archive_path = ARCHIVE_DIR / archive_name
    shutil.copy2(filepath, archive_path)
    return archive_path


def recalc_balances(conn, account_id: int, anchor: Decimal,
                    verbose: bool = False) -> int:
    """
    Recalculate running balances for all transactions of an account.
    anchor = the known real balance AFTER the most recent transaction in the DB.
    Algorithm:
      - Fetch all transactions ordered by transaction_date ASC, id ASC
        (id as tiebreaker = stable same-date ordering by insertion order)
      - Walk backwards from anchor:
          balance[last] = anchor
          balance[n-1]  = balance[n] - amount[n]
      - Write computed balance back to every transaction row
      - Update accounts.current_balance = anchor
    Returns number of rows updated.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amount
        FROM transactions
        WHERE account_id = %s
        ORDER BY transaction_date ASC, id ASC
    """, (account_id,))
    rows = cur.fetchall()

    if not rows:
        if verbose:
            print(f"  No transactions found for account {account_id}")
        return 0

    n = len(rows)
    balances = [Decimal('0')] * n
    balances[n - 1] = anchor

    for i in range(n - 2, -1, -1):
        balances[i] = balances[i + 1] - rows[i + 1]['amount']

    update_data = [(balances[i], rows[i]['id']) for i in range(n)]
    cur.executemany(
        "UPDATE transactions SET balance = %s WHERE id = %s",
        update_data
    )

    cur.execute(
        "UPDATE accounts SET current_balance = %s, "
        "balance_updated_at = NOW() WHERE id = %s",
        (anchor, account_id)
    )
    conn.commit()

    if verbose:
        print(f"  Recalculated {n} transactions. "
              f"Current balance: ${anchor:,.2f}")

    return n


def main():
    parser = argparse.ArgumentParser(description='Import bank CSV files')
    parser.add_argument('bank', choices=['sunmark', 'usaa'], help='Bank type')
    parser.add_argument('file', help='CSV file path')
    parser.add_argument('--balance', type=float,
                        help='Current balance (required for USAA)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be imported without committing')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--no-archive', action='store_true',
                        help='Do not archive the file')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    if args.bank == 'usaa' and args.balance is None:
        print("USAA imports require --balance argument")
        sys.exit(1)

    print(f"Parsing {args.bank.upper()} file: {args.file}")

    # Hash file contents for import log
    file_hash = hash_file_contents(args.file)

    # Parse
    if args.bank == 'sunmark':
        bank_parser = SunmarkParser(args.file)
    else:
        bank_parser = USAAParser(args.file, Decimal(str(args.balance)))

    transactions = bank_parser.parse()
    current_balance = bank_parser.get_current_balance()

    print(f"Found {len(transactions)} transactions")
    if current_balance:
        print(f"Current balance: ${current_balance:.2f}")

    # Report pending if USAA
    if args.bank == 'usaa' and hasattr(bank_parser, 'pending_transactions'):
        pending = bank_parser.pending_transactions
        if pending:
            print(f"⏳ {len(pending)} pending transactions (not imported):")
            for p in pending:
                print(f"    {p['transaction_date']} | {p['amount']:>10.2f} | "
                      f"{p['description'][:40]}")

    if args.verbose and transactions:
        print("\nSample transactions:")
        for txn in transactions[:5]:
            bal = (f"${txn['balance']:.2f}"
                   if txn.get('balance') else "N/A")
            print(f"  {txn['transaction_date']} | {txn['amount']:>10.2f} | "
                  f"{bal:>12} | {txn['description'][:35]}")

    importer = Importer(dry_run=args.dry_run, verbose=args.verbose)
    importer.connect()

    try:
        results = importer.import_transactions(
            transactions, Path(args.file).name, bank=args.bank
        )

        print(f"\nResults:")
        print(f"  Total:        {results['total']}")
        print(f"  Imported:     {results['imported']}")
        print(f"  Skipped:      {results['skipped']} (overlap)")
        print(f"  Categorized:  {results['categorized']}")
        print(f"  Uncategorized:{results['uncategorized']}")
        if results['errors']:
            print(f"  Errors:       {results['errors']}")

        # Update balance
        if current_balance and results['imported'] > 0:
            importer.update_account_balance(
                bank_parser.account_id, current_balance
            )

        # Recalc USAA balances if we have an anchor
        if (args.bank == 'usaa' and current_balance
                and results['imported'] > 0 and not args.dry_run):
            print("\nRecalculating USAA balances...")
            recalc_balances(
                importer.conn, ACCOUNT_IDS['usaa'],
                current_balance, verbose=args.verbose
            )

        # Log the import
        if results['imported'] > 0 or results['skipped'] > 0:
            dates = [t['transaction_date'] for t in transactions]
            date_range = (min(dates), max(dates)) if dates else None
            importer.log_import(
                bank_parser.account_id, Path(args.file).name,
                str(args.file), file_hash, results, date_range
            )

        # Archive
        if not args.dry_run and not args.no_archive:
            archive_path = archive_file(args.file, args.bank)
            print(f"\nArchived to: {archive_path}")

        # Post-import analysis
        if not args.dry_run and results['imported'] > 0:
            try:
                from post_import_analyzer import PostImportAnalyzer
                analyzer = PostImportAnalyzer()
                report = analyzer.analyze_import(
                    bank=args.bank,
                    imported_count=results['imported'],
                    skipped_count=results['skipped'],
                    source_file=Path(args.file).name,
                    prompt_balance=(args.bank == 'usaa'
                                   and args.balance is not None),
                )
                print(f"\n📋 Bill matching: {len(report['bill_matches'])} "
                      f"matched, {len(report['unpaid_bills'])} unpaid "
                      f"this month")
                for m in report['bill_matches']:
                    print(f"  ✓ {m['bill_name']:25} ${m['actual']:>8.2f}")
                analyzer.send_telegram_report(report)
                print("  → Telegram report sent")
                analyzer.close()
            except Exception as e:
                print(f"\n⚠️  Post-import analysis failed (non-fatal): {e}")

    finally:
        importer.close()

    print("\nDone!")


if __name__ == '__main__':
    main()
