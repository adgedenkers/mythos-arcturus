#!/usr/bin/env python3
"""
Mythos Finance — Full Account Reimport
/opt/mythos/finance/scripts/reimport_account.py

Wipes all transactions for an account and reimports from a complete CSV.
Verifies calculated running balances match bank-provided balances.
Updates accounts.current_balance to the final balance.
Runs the categorizer on all imported transactions.

Usage:
    reimport-account sunmark ~/Downloads/sunmark-archive.CSV
    reimport-account usaa ~/Downloads/usaa-archive.csv
    reimport-account usaa ~/Downloads/usaa-archive.csv --dry-run
    reimport-account sunmark ~/Downloads/sunmark.CSV --no-wipe   # append mode, hash dedup
"""
import os
import sys
import csv
import hashlib
import argparse
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

import psycopg2
from psycopg2.extras import RealDictCursor

# Add paths for categorizer
sys.path.insert(0, '/opt/mythos/finance')
from categorizer import Categorizer

logger = logging.getLogger(__name__)

ACCOUNT_MAP = {
    'usaa': {'id': 2, 'abbreviation': 'USAA', 'parser': 'usaa'},
    'sunmark': {'id': 1, 'abbreviation': 'SUN', 'parser': 'sunmark'},
    'sun': {'id': 1, 'abbreviation': 'SUN', 'parser': 'sunmark'},
}


def get_db():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def compute_hash(account_id, date_str, amount, description):
    """Generate deduplication hash matching existing parser logic."""
    data = f"{hash(str(account_id))}|{date_str}|{amount:.2f}|{description}"
    return hashlib.sha256(data.encode()).hexdigest()


def parse_usaa_csv(file_path):
    """
    Parse USAA CSV.
    Columns: Date,Description,Original Description,Category,Amount,Status,Bal-Calc
    Skips pending transactions.
    Returns rows sorted chronologically (oldest first).
    """
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Date'):
                continue

            status = (row.get('Status') or '').strip()
            if status.lower() == 'pending':
                continue

            date_str = row['Date'].strip()
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print(f"  ⚠ Skipping bad date: {date_str}")
                continue

            amount_str = (row.get('Amount') or '0').strip()
            amount = float(amount_str.replace(',', '').replace('$', ''))

            description = (row.get('Description') or '').strip()
            original_desc = (row.get('Original Description') or description).strip()
            category = (row.get('Category') or '').strip()
            if category in ('Category Pending', ''):
                category = None

            # Balance column
            bal_str = (row.get('Bal-Calc') or row.get('Balance') or '').strip()
            balance = None
            if bal_str:
                try:
                    balance = float(bal_str.replace(',', '').replace('$', ''))
                except ValueError:
                    pass

            # Hash for dedup
            hash_id = compute_hash(2, dt.strftime('%Y-%m-%d'), amount, original_desc)

            rows.append({
                'transaction_date': dt.date(),
                'description': description,
                'original_description': original_desc,
                'amount': Decimal(str(amount)),
                'balance': Decimal(str(round(balance, 2))) if balance is not None else None,
                'category_primary': category,
                'merchant_name': description if description != original_desc else None,
                'transaction_type': 'debit' if amount < 0 else 'credit',
                'is_pending': False,
                'bank_transaction_id': None,
                'hash_id': hash_id,
            })

    # USAA CSV is newest-first, reverse to oldest-first
    rows.reverse()
    return rows


def parse_sunmark_csv(file_path):
    """
    Parse Sunmark CSV.
    3 header lines, then:
    Transaction Number,Date,Description,Memo,Amount Debit,Amount Credit,Balance,Check Number
    Returns rows sorted chronologically (oldest first).
    """
    rows = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find header row
    header_idx = 0
    for i, line in enumerate(lines):
        if 'Transaction Number' in line:
            header_idx = i
            break

    csv_content = ''.join(lines[header_idx:])
    reader = csv.DictReader(csv_content.splitlines())

    for row in reader:
        if not row.get('Date'):
            continue

        date_str = row['Date'].strip()
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            print(f"  ⚠ Skipping bad date: {date_str}")
            continue

        debit = (row.get('Amount Debit') or '').strip()
        credit = (row.get('Amount Credit') or '').strip()

        if debit:
            amount = Decimal(debit.replace(',', '').replace('$', ''))
            # Sunmark debit column is already negative
            if amount > 0:
                amount = -amount
            trans_type = 'debit'
        elif credit:
            amount = Decimal(credit.replace(',', '').replace('$', ''))
            if amount < 0:
                amount = abs(amount)
            trans_type = 'credit'
        else:
            continue

        description_raw = (row.get('Description') or '').strip()
        memo = (row.get('Memo') or '').strip()
        original_desc = f"{description_raw} {memo}".strip() if memo else description_raw

        # Use memo as primary description if it has merchant info
        description = memo if memo else description_raw

        bal_str = (row.get('Balance') or '').strip()
        balance = None
        if bal_str:
            try:
                balance = Decimal(bal_str.replace(',', '').replace('$', ''))
            except Exception:
                pass

        bank_txn_id = (row.get('Transaction Number') or '').strip().strip('"') or None

        if bank_txn_id:
            hash_id = hashlib.sha256(f"sunmark|{bank_txn_id}".encode()).hexdigest()
        else:
            hash_id = compute_hash(1, dt.strftime('%Y-%m-%d'), float(amount), original_desc)

        rows.append({
            'transaction_date': dt.date(),
            'description': description,
            'original_description': original_desc,
            'amount': amount,
            'balance': balance,
            'category_primary': None,  # Will be set by categorizer
            'merchant_name': None,
            'transaction_type': trans_type,
            'is_pending': False,
            'bank_transaction_id': bank_txn_id,
            'hash_id': hash_id,
        })

    # Sunmark CSV is newest-first (highest txn number first), reverse
    rows.reverse()
    return rows


def verify_balances(rows, account_name):
    """
    Verify that calculated running balances match bank-provided balances.
    Returns (verified_count, mismatch_count, mismatches).
    """
    if not rows:
        return 0, 0, []

    # Find first row with a balance to use as anchor
    anchor_idx = None
    for i, row in enumerate(rows):
        if row['balance'] is not None:
            anchor_idx = i
            break

    if anchor_idx is None:
        print(f"  ⚠ {account_name}: No bank balances to verify against")
        return 0, 0, []

    # Calculate what the balance before the anchor should be
    anchor_balance = rows[anchor_idx]['balance']

    # Walk forward from anchor, checking balances
    running = anchor_balance - rows[anchor_idx]['amount']  # balance before this txn
    verified = 0
    mismatches = []

    for i in range(anchor_idx, len(rows)):
        row = rows[i]
        running = running + row['amount']
        running = running.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if row['balance'] is not None:
            bank_bal = row['balance'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            diff = abs(running - bank_bal)
            if diff > Decimal('0.02'):  # Allow 2 cent rounding tolerance
                mismatches.append({
                    'date': row['transaction_date'],
                    'desc': row['description'][:40],
                    'amount': row['amount'],
                    'expected': running,
                    'bank_says': bank_bal,
                    'diff': running - bank_bal,
                })
            else:
                verified += 1

        # Store calculated balance (overwrite bank balance with our calc)
        row['calc_balance'] = running

    # Also walk backward from anchor to fill earlier rows
    running_back = anchor_balance - rows[anchor_idx]['amount']
    for i in range(anchor_idx - 1, -1, -1):
        row = rows[i]
        # running_back is the balance AFTER this transaction
        row['calc_balance'] = running_back
        running_back = running_back - row['amount']
        running_back = running_back.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if row['balance'] is not None:
            bank_bal = row['balance'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            diff = abs(row['calc_balance'] - bank_bal)
            if diff > Decimal('0.02'):
                mismatches.append({
                    'date': row['transaction_date'],
                    'desc': row['description'][:40],
                    'amount': row['amount'],
                    'expected': row['calc_balance'],
                    'bank_says': bank_bal,
                    'diff': row['calc_balance'] - bank_bal,
                })
            else:
                verified += 1

    return verified, len(mismatches), mismatches


def reimport_account(account_key, csv_path, dry_run=False, no_wipe=False):
    """Full reimport for an account."""

    acct = ACCOUNT_MAP.get(account_key.lower())
    if not acct:
        print(f"❌ Unknown account: {account_key}")
        print(f"   Available: {', '.join(ACCOUNT_MAP.keys())}")
        return False

    account_id = acct['id']
    abbrev = acct['abbreviation']
    parser_name = acct['parser']

    csv_path = Path(csv_path).expanduser()
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return False

    print(f"\n{'=' * 60}")
    print(f"  REIMPORT: {abbrev} (account_id={account_id})")
    print(f"  CSV: {csv_path}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'WIPE + IMPORT' if not no_wipe else 'APPEND (hash dedup)'}")
    print(f"{'=' * 60}\n")

    # ── 1. Parse CSV ────────────────────────────────────────
    print(f"  Parsing {parser_name} CSV...")
    if parser_name == 'usaa':
        rows = parse_usaa_csv(csv_path)
    elif parser_name == 'sunmark':
        rows = parse_sunmark_csv(csv_path)
    else:
        print(f"❌ Unknown parser: {parser_name}")
        return False

    print(f"  ✓ Parsed {len(rows)} transactions ({rows[0]['transaction_date']} → {rows[-1]['transaction_date']})")

    # ── 2. Verify balances ──────────────────────────────────
    print(f"\n  Verifying balances...")
    verified, mismatch_count, mismatches = verify_balances(rows, abbrev)
    print(f"  ✓ Verified: {verified} balances match")
    if mismatch_count > 0:
        print(f"  ⚠ Mismatches: {mismatch_count}")
        for m in mismatches[:5]:
            print(f"    {m['date']} {m['desc']}: calc={m['expected']} bank={m['bank_says']} diff={m['diff']}")
        if mismatch_count > 5:
            print(f"    ... and {mismatch_count - 5} more")

    # ── 3. Categorize ───────────────────────────────────────
    print(f"\n  Running categorizer...")
    conn = get_db()
    cat = Categorizer(conn=conn)
    categorized = 0
    for row in rows:
        if not row.get('category_primary'):
            result = cat.categorize(
                row.get('description', ''),
                row.get('original_description', '')
            )
            if result:
                row['category_primary'] = result.get('category_primary')
                if 'merchant_name' in result:
                    row['merchant_name'] = result['merchant_name']
                categorized += 1
    print(f"  ✓ Categorized {categorized} transactions ({cat.mapping_count} rules)")

    if dry_run:
        print(f"\n  [DRY RUN] Would wipe {abbrev} transactions and insert {len(rows)}")
        final_bal = rows[-1].get('calc_balance') or rows[-1].get('balance')
        if final_bal:
            print(f"  [DRY RUN] Final balance would be: {final_bal}")
        conn.close()
        return True

    cur = conn.cursor()

    # ── 4. Wipe existing transactions ───────────────────────
    if not no_wipe:
        # Delete bill_payments references first
        cur.execute("""
            DELETE FROM bill_payments
            WHERE transaction_id IN (
                SELECT id FROM transactions WHERE account_id = %s
            )
        """, (account_id,))
        bp_deleted = cur.rowcount

        cur.execute("DELETE FROM transactions WHERE account_id = %s", (account_id,))
        deleted = cur.rowcount
        print(f"\n  ✓ Wiped {deleted} existing transactions (+ {bp_deleted} bill_payment refs)")
    else:
        print(f"\n  ⏭ No-wipe mode — will skip existing hashes")

    # ── 5. Insert transactions ──────────────────────────────
    inserted = 0
    skipped = 0

    for row in rows:
        # Use calculated balance if available, else bank balance
        balance = row.get('calc_balance') or row.get('balance')

        if no_wipe:
            # Check for existing hash
            cur.execute("SELECT id FROM transactions WHERE hash_id = %s", (row['hash_id'],))
            if cur.fetchone():
                skipped += 1
                continue

        cur.execute("""
            INSERT INTO transactions (
                account_id, transaction_date, description, original_description,
                amount, balance, category_primary, merchant_name,
                transaction_type, is_pending, bank_transaction_id, hash_id,
                source_file, imported_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            account_id,
            row['transaction_date'],
            row['description'],
            row['original_description'],
            float(row['amount']),
            float(balance) if balance is not None else None,
            row.get('category_primary'),
            row.get('merchant_name'),
            row['transaction_type'],
            row['is_pending'],
            row.get('bank_transaction_id'),
            row['hash_id'],
            str(csv_path.name),
            'reimport',
        ))
        inserted += 1

    print(f"  ✓ Inserted {inserted} transactions" + (f" (skipped {skipped} existing)" if skipped else ""))

    # ── 6. Update account balance ───────────────────────────
    final_balance = rows[-1].get('calc_balance') or rows[-1].get('balance')
    if final_balance is not None:
        cur.execute("""
            UPDATE accounts
            SET current_balance = %s, balance_updated_at = NOW()
            WHERE id = %s
        """, (float(final_balance), account_id))
        print(f"  ✓ Account balance → ${float(final_balance):,.2f}")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"  ✅ {abbrev} reimport complete: {inserted} transactions")
    print(f"  📅 {rows[0]['transaction_date']} → {rows[-1]['transaction_date']}")
    if final_balance:
        print(f"  💰 Final balance: ${float(final_balance):,.2f}")
    print(f"{'=' * 60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(description='Full account reimport from CSV')
    parser.add_argument('account', choices=['usaa', 'sunmark', 'sun'],
                        help='Account to reimport')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse and verify without writing')
    parser.add_argument('--no-wipe', action='store_true',
                        help='Append mode — skip existing hashes instead of wiping')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    reimport_account(args.account, args.csv_file, dry_run=args.dry_run, no_wipe=args.no_wipe)


if __name__ == '__main__':
    main()
