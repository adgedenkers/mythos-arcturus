#!/usr/bin/env python3
"""
Mythos Finance - Transaction Importer
/opt/mythos/finance/import_transactions.py

Import bank CSV files into PostgreSQL with deduplication and auto-categorization.

Usage:
    python import_transactions.py <csv_file> --account-id <id> [--parser <n>] [--dry-run]

Examples:
    python import_transactions.py accounts/usaa_2026_01.csv --account-id 2
    python import_transactions.py accounts/sunmark_2026_01.csv --account-id 1 --dry-run
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from parsers import Transaction, detect_parser, get_parser

# Load environment
load_dotenv('/opt/mythos/.env')


class TransactionImporter:
    """Import transactions into PostgreSQL with deduplication"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'mythos'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_existing_hashes(self, hashes: List[str]) -> set:
        """Get set of hashes that already exist in database"""
        if not hashes:
            return set()
        
        self.cursor.execute(
            "SELECT hash_id FROM transactions WHERE hash_id = ANY(%s)",
            (hashes,)
        )
        return {row[0] for row in self.cursor.fetchall()}
    
    def apply_category_mappings(self, transactions: List[Transaction]) -> List[Transaction]:
        """Apply category mappings to transactions that don't have categories"""
        # Get all active mappings ordered by priority
        self.cursor.execute("""
            SELECT pattern, pattern_type, category_primary, category_secondary, merchant_name
            FROM category_mappings
            WHERE is_active = true
            ORDER BY priority DESC
        """)
        mappings = self.cursor.fetchall()
        
        for trans in transactions:
            # Skip if already categorized
            if trans.category_primary and trans.category_primary != 'Category Pending':
                continue
            
            # Try each mapping
            desc_upper = trans.original_description.upper()
            for pattern, pattern_type, cat_primary, cat_secondary, merchant in mappings:
                matched = False
                
                if pattern_type == 'contains':
                    matched = pattern.upper() in desc_upper
                elif pattern_type == 'starts_with':
                    matched = desc_upper.startswith(pattern.upper())
                elif pattern_type == 'regex':
                    import re
                    matched = bool(re.search(pattern, trans.original_description, re.IGNORECASE))
                
                if matched:
                    trans.category_primary = cat_primary
                    trans.category_secondary = cat_secondary
                    if merchant and not trans.merchant_name:
                        trans.merchant_name = merchant
                    break
        
        return transactions
    
    def import_transactions(
        self,
        transactions: List[Transaction],
        account_id: int,
        source_file: str,
        imported_by: str = 'system'
    ) -> Tuple[int, int, int]:
        """
        Import transactions into database
        
        Returns:
            Tuple of (imported_count, skipped_count, error_count)
        """
        if not transactions:
            return 0, 0, 0
        
        # Get existing hashes for deduplication
        all_hashes = [t.hash_id for t in transactions]
        existing_hashes = self.get_existing_hashes(all_hashes)
        
        # Filter out duplicates
        new_transactions = [t for t in transactions if t.hash_id not in existing_hashes]
        skipped = len(transactions) - len(new_transactions)
        
        if self.dry_run:
            print(f"\n[DRY RUN] Would import {len(new_transactions)} transactions")
            print(f"[DRY RUN] Would skip {skipped} duplicates")
            print("\nSample transactions:")
            for t in new_transactions[:10]:
                cat = t.category_primary or 'Uncategorized'
                print(f"  {t.transaction_date.date()} | {t.amount:>10.2f} | {cat:<20} | {t.description[:40]}")
            if len(new_transactions) > 10:
                print(f"  ... and {len(new_transactions) - 10} more")
            return len(new_transactions), skipped, 0
        
        if not new_transactions:
            return 0, skipped, 0
        
        # Prepare data for bulk insert - matches clean schema.sql
        values = []
        for t in new_transactions:
            values.append((
                account_id,
                t.transaction_date.date(),
                t.transaction_date.date(),  # post_date
                t.description,
                t.original_description,
                t.merchant_name,
                t.amount,
                t.balance,
                t.category_primary,
                t.category_secondary,
                t.transaction_type,
                t.is_pending,
                False,  # is_recurring
                t.bank_transaction_id,
                t.hash_id,
                source_file,
                imported_by,
            ))
        
        # Bulk insert
        try:
            execute_values(
                self.cursor,
                """
                INSERT INTO transactions (
                    account_id, transaction_date, post_date,
                    description, original_description, merchant_name,
                    amount, balance,
                    category_primary, category_secondary,
                    transaction_type, is_pending, is_recurring,
                    bank_transaction_id, hash_id, source_file, imported_by
                ) VALUES %s
                ON CONFLICT (hash_id) DO NOTHING
                """,
                values
            )
            self.conn.commit()
            imported = self.cursor.rowcount
            return imported, skipped, 0
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Database error during import: {e}")
            return 0, skipped, len(new_transactions)
    
    def log_import(
        self,
        account_id: int,
        source_file: str,
        file_path: Path,
        total_rows: int,
        imported: int,
        skipped: int,
        errors: int,
        date_range: Tuple[datetime, datetime],
        imported_by: str
    ):
        """Log the import to import_logs table"""
        if self.dry_run:
            return
        
        try:
            self.cursor.execute(
                """
                INSERT INTO import_logs (
                    account_id, source_file, file_path, total_rows,
                    imported_count, skipped_count, error_count,
                    date_range_start, date_range_end, imported_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    account_id, source_file, str(file_path), total_rows,
                    imported, skipped, errors,
                    date_range[0].date(), date_range[1].date(), imported_by
                )
            )
            self.conn.commit()
        except Exception as e:
            print(f"Warning: Failed to log import: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Import bank CSV files into PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s accounts/usaa_2026_01.csv --account-id 2
    %(prog)s accounts/sunmark_2026_01.csv --account-id 1 --dry-run

Account IDs:
    1 = Sunmark Primary Checking
    2 = USAA Simple Checking
        """
    )
    parser.add_argument('csv_file', type=Path, help='Path to CSV file')
    parser.add_argument('--account-id', type=int, required=True, help='Account ID (1=Sunmark, 2=USAA)')
    parser.add_argument('--parser', choices=['usaa', 'sunmark'], help='Force specific parser')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    parser.add_argument('--imported-by', default='adge', help='User performing import')
    
    args = parser.parse_args()
    
    # Resolve file path
    file_path = args.csv_file
    if not file_path.is_absolute():
        file_path = Path('/opt/mythos/finance') / file_path
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Detect or use specified parser
    parser_type = args.parser
    if not parser_type:
        parser_type = detect_parser(file_path)
        if not parser_type:
            print("Error: Could not auto-detect bank format. Please specify --parser usaa or --parser sunmark")
            sys.exit(1)
        print(f"Auto-detected parser: {parser_type}")
    
    # Parse the file
    print(f"Parsing {file_path.name} with {parser_type} parser...")
    bank_parser = get_parser(parser_type)
    transactions = bank_parser.parse_file(file_path, f"account_{args.account_id}")
    
    if not transactions:
        print("No transactions found in file")
        sys.exit(0)
    
    print(f"Parsed {len(transactions)} transactions")
    
    # Get date range
    dates = [t.transaction_date for t in transactions]
    date_range = (min(dates), max(dates))
    print(f"Date range: {date_range[0].date()} to {date_range[1].date()}")
    
    # Import
    importer = TransactionImporter(dry_run=args.dry_run)
    
    try:
        importer.connect()
        
        # Apply category mappings
        transactions = importer.apply_category_mappings(transactions)
        
        # Show category summary
        categorized = sum(1 for t in transactions if t.category_primary)
        print(f"Categorized: {categorized}/{len(transactions)} transactions")
        
        # Import transactions
        imported, skipped, errors = importer.import_transactions(
            transactions,
            args.account_id,
            file_path.name,
            args.imported_by
        )
        
        # Log the import
        importer.log_import(
            args.account_id,
            file_path.name,
            file_path,
            len(transactions),
            imported,
            skipped,
            errors,
            date_range,
            args.imported_by
        )
        
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Import complete:")
        print(f"  Imported: {imported}")
        print(f"  Skipped (duplicates): {skipped}")
        print(f"  Errors: {errors}")
        
        if not args.dry_run and imported > 0:
            print(f"\nView results:")
            print(f"  python reports.py summary")
        
    finally:
        importer.close()


if __name__ == "__main__":
    main()
