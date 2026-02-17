#!/usr/bin/env python3
"""
Patch 0086 - Finance Hash Rehash & Dedup Cleanup
/opt/mythos/finance/scripts/rehash_transactions.py

This script:
1. Removes duplicate transactions (same account/date/amount/description, different hash)
2. Rehashes all existing transactions using the new deterministic hash algorithm
3. Reports what was cleaned up

Run ONCE after deploying patch 0086. Safe to run multiple times (idempotent).

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/finance/scripts/rehash_transactions.py
    /opt/mythos/.venv/bin/python3 /opt/mythos/finance/scripts/rehash_transactions.py --dry-run
"""
import os
import sys
import hashlib
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def make_hash_v4(account_id: int, date_str: str, amount, original_description: str) -> str:
    """New deterministic hash — account_id|date|amount|original_description"""
    raw = f"{account_id}|{date_str}|{amount}|{original_description}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def run(dry_run=False):
    conn = get_db_connection()
    cur = conn.cursor()

    print("=" * 60)
    print("Patch 0086: Transaction Hash Rehash & Dedup Cleanup")
    print("DRY RUN" if dry_run else "LIVE RUN")
    print("=" * 60)

    # ----------------------------------------------------------------
    # Step 1: Find duplicates
    # Duplicates = same account_id, transaction_date, amount, original_description
    # but different hash_id (imported via different code paths)
    # ----------------------------------------------------------------
    print("\n[1] Scanning for duplicates...")

    cur.execute("""
        SELECT 
            account_id,
            transaction_date,
            amount,
            original_description,
            COUNT(*) as cnt,
            array_agg(id ORDER BY id) as ids,
            array_agg(hash_id ORDER BY id) as hashes
        FROM transactions
        WHERE original_description IS NOT NULL
        GROUP BY account_id, transaction_date, amount, original_description
        HAVING COUNT(*) > 1
        ORDER BY transaction_date DESC
    """)
    dupes = cur.fetchall()

    if not dupes:
        print("  No duplicates found.")
    else:
        total_removed = 0
        print(f"  Found {len(dupes)} duplicate groups:")
        for d in dupes:
            keep_id = d['ids'][0]
            remove_ids = d['ids'][1:]
            print(f"  [{d['transaction_date']}] acct={d['account_id']} "
                  f"amt={d['amount']} desc={str(d['original_description'])[:40]}")
            print(f"    keep id={keep_id}, remove ids={remove_ids}")

            if not dry_run:
                cur.execute("DELETE FROM transactions WHERE id = ANY(%s)", (remove_ids,))
                conn.commit()
                total_removed += len(remove_ids)

        if dry_run:
            print(f"\n  Would remove {sum(len(d['ids'])-1 for d in dupes)} duplicate rows")
        else:
            print(f"\n  Removed {total_removed} duplicate rows")

    # ----------------------------------------------------------------
    # Step 2: Rehash all transactions using v4 algorithm
    # New hash: account_id | date | amount | original_description
    # ----------------------------------------------------------------
    print("\n[2] Rehashing all transactions to v4 algorithm...")

    cur.execute("""
        SELECT id, account_id, transaction_date, amount, original_description, description, hash_id
        FROM transactions
        ORDER BY id
    """)
    all_txns = cur.fetchall()
    print(f"  Total transactions: {len(all_txns)}")

    changed = 0
    conflicts = 0
    errors = 0

    for txn in all_txns:
        date_str = txn['transaction_date'].strftime('%Y-%m-%d')
        orig_desc = txn['original_description'] or txn['description'] or ''
        
        new_hash = make_hash_v4(
            txn['account_id'],
            date_str,
            txn['amount'],
            orig_desc
        )

        if new_hash == txn['hash_id']:
            continue  # already correct

        # Check if new hash already exists (another row owns it)
        cur.execute("SELECT id FROM transactions WHERE hash_id = %s AND id != %s", 
                    (new_hash, txn['id']))
        existing = cur.fetchone()
        if existing:
            conflicts += 1
            print(f"  CONFLICT: id={txn['id']} new_hash={new_hash} already owned by id={existing['id']}")
            if not dry_run:
                # This is a true duplicate — remove current row
                cur.execute("DELETE FROM transactions WHERE id = %s", (txn['id'],))
                conn.commit()
            continue

        changed += 1
        if not dry_run:
            try:
                cur.execute("UPDATE transactions SET hash_id = %s WHERE id = %s",
                            (new_hash, txn['id']))
                conn.commit()
            except Exception as e:
                conn.rollback()
                errors += 1
                print(f"  ERROR updating id={txn['id']}: {e}")

    print(f"  Hashes updated: {changed}")
    print(f"  Conflicts (true dupes, removed): {conflicts}")
    if errors:
        print(f"  Errors: {errors}")

    # ----------------------------------------------------------------
    # Step 3: Final counts
    # ----------------------------------------------------------------
    print("\n[3] Final state:")
    cur.execute("""
        SELECT a.abbreviation, COUNT(t.id) as cnt, MIN(t.transaction_date) as earliest, MAX(t.transaction_date) as latest
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id
        GROUP BY a.id, a.abbreviation
        ORDER BY a.id
    """)
    for row in cur.fetchall():
        print(f"  {row['abbreviation']:<10} {row['cnt']:>5} txns  "
              f"{str(row['earliest'] or '-'):>12} → {str(row['latest'] or '-'):>12}")

    cur.execute("SELECT COUNT(*) as total, COUNT(DISTINCT hash_id) as unique_hashes FROM transactions")
    totals = cur.fetchone()
    print(f"\n  Total: {totals['total']} transactions, {totals['unique_hashes']} unique hashes")
    if totals['total'] != totals['unique_hashes']:
        print(f"  ⚠️  WARNING: {totals['total'] - totals['unique_hashes']} hash collisions remain!")
    else:
        print(f"  ✓ All hashes unique")

    conn.close()
    print("\nDone." + (" (DRY RUN — no changes made)" if dry_run else ""))


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    run(dry_run=dry_run)
