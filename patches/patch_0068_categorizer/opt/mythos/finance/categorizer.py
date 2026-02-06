#!/usr/bin/env python3
"""
Mythos Finance - Transaction Categorizer
/opt/mythos/finance/categorizer.py

Loads category_mappings from PostgreSQL and applies them to transactions.
Used by:
  - importer.py (inline during import)
  - Telegram /categorize command (retroactive)
  - Standalone CLI (bulk re-categorize)

Matching logic:
  1. Load all active mappings, sorted by priority (lower = higher priority)
  2. For each transaction, check description against patterns
  3. pattern_type 'contains' = case-insensitive substring match
  4. First match wins (by priority, then by longest pattern)

Usage:
    # As module
    from categorizer import Categorizer
    cat = Categorizer()  # loads from DB
    cat = Categorizer(conn=existing_connection)
    category, merchant = cat.categorize("STEWART'S SHOP")
    
    # Standalone - re-categorize all uncategorized transactions
    python categorizer.py
    python categorizer.py --all  # re-categorize everything, even already categorized
    python categorizer.py --dry-run
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


class Categorizer:
    """
    Transaction categorizer using category_mappings table.
    
    Loads mappings once, applies to many transactions.
    Thread-safe for read operations (mappings are immutable after load).
    """
    
    def __init__(self, conn=None):
        """Load mappings from database"""
        self.mappings = []
        self._load_mappings(conn)
    
    def _load_mappings(self, conn=None):
        """Load active mappings sorted by priority then pattern length (longest first)"""
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT pattern, pattern_type, category_primary, category_secondary, merchant_name, priority
                FROM category_mappings
                WHERE is_active = true
                ORDER BY priority ASC, LENGTH(pattern) DESC
            """)
            self.mappings = cur.fetchall()
        finally:
            if close_conn:
                conn.close()
    
    def categorize(self, description: str, original_description: str = None) -> dict:
        """
        Categorize a transaction based on description.
        
        Checks description first, then original_description as fallback.
        Returns dict with category_primary, category_secondary, merchant_name.
        Returns empty dict if no match found.
        """
        if not description:
            return {}
        
        # Try matching against description first, then original_description
        texts_to_check = [description]
        if original_description and original_description != description:
            texts_to_check.append(original_description)
        
        for text in texts_to_check:
            text_upper = text.upper()
            
            for mapping in self.mappings:
                pattern = mapping['pattern']
                pattern_type = mapping['pattern_type'] or 'contains'
                
                matched = False
                
                if pattern_type == 'contains':
                    matched = pattern.upper() in text_upper
                elif pattern_type == 'starts_with':
                    matched = text_upper.startswith(pattern.upper())
                elif pattern_type == 'exact':
                    matched = text_upper == pattern.upper()
                elif pattern_type == 'ends_with':
                    matched = text_upper.endswith(pattern.upper())
                
                if matched:
                    result = {
                        'category_primary': mapping['category_primary'],
                    }
                    if mapping['category_secondary']:
                        result['category_secondary'] = mapping['category_secondary']
                    if mapping['merchant_name']:
                        result['merchant_name'] = mapping['merchant_name']
                    return result
        
        return {}
    
    def categorize_transaction(self, txn: dict) -> dict:
        """
        Categorize a transaction dict in-place.
        
        If the transaction already has a category_primary set, skip it
        (unless the caller explicitly clears it first).
        
        Returns the categorization result (or empty dict if already categorized).
        """
        # Don't override existing categorization
        if txn.get('category_primary'):
            return {}
        
        result = self.categorize(
            txn.get('description', ''),
            txn.get('original_description', '')
        )
        
        if result:
            txn['category_primary'] = result.get('category_primary')
            if 'category_secondary' in result:
                txn['category_secondary'] = result['category_secondary']
            if 'merchant_name' in result:
                txn['merchant_name'] = result['merchant_name']
        
        return result
    
    @property
    def mapping_count(self):
        return len(self.mappings)


def recategorize_db(all_transactions: bool = False, dry_run: bool = False, verbose: bool = False):
    """
    Re-categorize transactions in the database.
    
    Args:
        all_transactions: If True, re-categorize even already categorized ones
        dry_run: If True, don't commit changes
        verbose: If True, print details
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cat = Categorizer(conn=conn)
    print(f"Loaded {cat.mapping_count} category mappings")
    
    # Get transactions to categorize
    if all_transactions:
        cur.execute("""
            SELECT id, description, original_description, category_primary
            FROM transactions
            WHERE description != 'Balance checkpoint'
            ORDER BY transaction_date DESC
        """)
    else:
        cur.execute("""
            SELECT id, description, original_description, category_primary
            FROM transactions
            WHERE category_primary IS NULL
              AND description != 'Balance checkpoint'
            ORDER BY transaction_date DESC
        """)
    
    rows = cur.fetchall()
    print(f"Found {len(rows)} transactions to process")
    
    updated = 0
    skipped = 0
    unmatched = []
    
    for row in rows:
        result = cat.categorize(row['description'], row['original_description'])
        
        if result:
            if not dry_run:
                update_fields = ["category_primary = %s"]
                update_values = [result['category_primary']]
                
                if 'category_secondary' in result:
                    update_fields.append("category_secondary = %s")
                    update_values.append(result['category_secondary'])
                
                if 'merchant_name' in result:
                    update_fields.append("merchant_name = %s")
                    update_values.append(result['merchant_name'])
                
                update_values.append(row['id'])
                
                cur.execute(
                    f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = %s",
                    update_values
                )
            
            updated += 1
            if verbose:
                print(f"  ✓ {row['description'][:35]:35} → {result['category_primary']}")
        else:
            skipped += 1
            if row['description'] not in [u['desc'] for u in unmatched]:
                unmatched.append({
                    'desc': row['description'],
                    'original': row['original_description'],
                })
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    print(f"\nResults:")
    print(f"  Categorized: {updated}")
    print(f"  No match:    {skipped}")
    
    if unmatched:
        print(f"\nUnmatched descriptions ({len(unmatched)}):")
        for u in unmatched[:20]:
            print(f"  - {u['desc']}")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched) - 20} more")
    
    return {'updated': updated, 'skipped': skipped, 'unmatched': len(unmatched)}


def main():
    parser = argparse.ArgumentParser(description='Re-categorize transactions')
    parser.add_argument('--all', action='store_true', help='Re-categorize all transactions, not just uncategorized')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without committing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show each categorization')
    
    args = parser.parse_args()
    
    recategorize_db(
        all_transactions=args.all,
        dry_run=args.dry_run,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()
