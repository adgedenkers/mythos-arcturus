#!/usr/bin/env python3
"""
Mythos Finance — Backfill Transaction Balances
/opt/mythos/finance/scripts/backfill_balances.py

Finds all transactions with NULL balance fields and calculates them
by walking forward from the last known balance per account.

Can be run standalone or called after any import.

Usage:
    backfill-balances              # backfill all accounts
    backfill-balances --dry-run    # show what would change without writing
"""
import os
import sys
import argparse
import logging
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)


def get_db():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def backfill_account(cur, account_id, abbreviation, dry_run=False):
    """
    Backfill NULL balances for a single account.

    Strategy:
    1. Find the last transaction with a non-NULL balance (the anchor)
    2. Get all transactions after the anchor, ordered by date + id
    3. Walk forward, calculating running balance
    4. Update any NULL balance fields
    5. Update accounts.current_balance to the final balance

    Returns count of updated transactions.
    """
    # Find anchor: last transaction with a balance
    cur.execute("""
        SELECT id, transaction_date, balance
        FROM transactions
        WHERE account_id = %s AND balance IS NOT NULL
        ORDER BY transaction_date DESC, id DESC
        LIMIT 1
    """, (account_id,))
    anchor = cur.fetchone()

    if not anchor:
        logger.warning(f"  {abbreviation}: No transactions with balance found — cannot backfill")
        return 0

    anchor_balance = Decimal(str(anchor['balance']))
    anchor_date = anchor['transaction_date']
    anchor_id = anchor['id']

    # Get all transactions from anchor onward (including anchor for ordering)
    cur.execute("""
        SELECT id, transaction_date, amount, balance
        FROM transactions
        WHERE account_id = %s
          AND (transaction_date > %s OR (transaction_date = %s AND id >= %s))
        ORDER BY transaction_date, id
    """, (account_id, anchor_date, anchor_date, anchor_id))
    rows = cur.fetchall()

    if not rows:
        return 0

    running = None
    updated = 0

    for row in rows:
        if row['id'] == anchor_id:
            # This is the anchor — use its known balance
            running = anchor_balance
            continue

        amount = Decimal(str(row['amount']))
        running = running + amount

        if row['balance'] is None:
            if dry_run:
                print(f"  [DRY RUN] {abbreviation} txn {row['id']} ({row['transaction_date']}): "
                      f"would set balance = {running}")
            else:
                cur.execute(
                    "UPDATE transactions SET balance = %s WHERE id = %s",
                    (running, row['id'])
                )
            updated += 1
        else:
            # Transaction already has a balance — use it as new anchor
            # (in case there are gaps)
            running = Decimal(str(row['balance']))

    # Update account balance to match the final calculated balance
    if running is not None and not dry_run:
        cur.execute("""
            UPDATE accounts
            SET current_balance = %s, balance_updated_at = NOW()
            WHERE id = %s
        """, (running, account_id))
        logger.info(f"  {abbreviation}: accounts.current_balance → {running}")

    return updated


def backfill_all(dry_run=False):
    """Backfill NULL balances across all active accounts."""
    conn = get_db()
    cur = conn.cursor()

    # Find accounts with NULL balances
    cur.execute("""
        SELECT a.id, a.abbreviation,
               COUNT(*) FILTER (WHERE t.balance IS NULL) as null_count,
               COUNT(*) as total_count
        FROM accounts a
        JOIN transactions t ON t.account_id = a.id
        WHERE a.is_active = true
        GROUP BY a.id, a.abbreviation
        HAVING COUNT(*) FILTER (WHERE t.balance IS NULL) > 0
        ORDER BY a.id
    """)
    accounts = cur.fetchall()

    if not accounts:
        print("✓ All transaction balances are populated — nothing to backfill")
        conn.close()
        return 0

    total_updated = 0
    for acct in accounts:
        print(f"  {acct['abbreviation']}: {acct['null_count']} NULL out of {acct['total_count']} transactions")
        count = backfill_account(cur, acct['id'], acct['abbreviation'], dry_run=dry_run)
        total_updated += count
        print(f"  {acct['abbreviation']}: {'would update' if dry_run else 'updated'} {count} balances")

    if not dry_run:
        conn.commit()
        print(f"\n✓ Backfilled {total_updated} transaction balances")
    else:
        print(f"\n[DRY RUN] Would backfill {total_updated} transaction balances")

    conn.close()
    return total_updated


def main():
    parser = argparse.ArgumentParser(description='Backfill NULL transaction balances')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    backfill_all(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
