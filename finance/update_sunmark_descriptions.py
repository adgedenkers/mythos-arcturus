#!/usr/bin/env python3
"""
Mythos Finance - Update Sunmark Descriptions
/opt/mythos/finance/update_sunmark_descriptions.py

Re-processes existing Sunmark transactions to apply the new description
cleaning logic. Updates description and merchant_name fields.

Usage:
    python update_sunmark_descriptions.py [--dry-run]
"""

import argparse
import os
import sys
from typing import Tuple, Optional

import psycopg2
from dotenv import load_dotenv

# Load environment
load_dotenv('/opt/mythos/.env')

# Import the parser for its cleaning logic
from parsers import SunmarkParser


def update_descriptions(dry_run: bool = False):
    """Update all Sunmark transaction descriptions"""
    
    parser = SunmarkParser()
    
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    cursor = conn.cursor()
    
    try:
        # Get all Sunmark transactions (account_id = 1)
        cursor.execute("""
            SELECT id, original_description, description, merchant_name
            FROM transactions
            WHERE account_id = 1
            ORDER BY transaction_date DESC
        """)
        
        rows = cursor.fetchall()
        print(f"Found {len(rows)} Sunmark transactions to process")
        
        updates = []
        changed = 0
        
        for row_id, original_desc, current_desc, current_merchant in rows:
            if not original_desc:
                continue
            
            # Split original_description back into description and memo parts
            # The original format combines them with a space
            # We need to detect the prefix to know where the split is
            desc_part = original_desc
            memo_part = ""
            
            for prefix, _ in parser.TRANSACTION_PREFIXES:
                if original_desc.upper().startswith(prefix.upper()):
                    # Everything after the prefix is the "memo" content
                    desc_part = prefix
                    memo_part = original_desc[len(prefix):].strip()
                    break
            
            # Apply new cleaning logic
            new_desc, new_merchant = parser._clean_description(desc_part, memo_part)
            
            # Check if anything changed
            if new_desc != current_desc or (new_merchant and new_merchant != current_merchant):
                changed += 1
                updates.append((new_desc, new_merchant, row_id))
                
                if dry_run and changed <= 20:
                    print(f"\n[{row_id}] OLD: {current_desc}")
                    print(f"     NEW: {new_desc}")
                    if new_merchant != current_merchant:
                        print(f"     MERCHANT: {current_merchant} -> {new_merchant}")
        
        print(f"\n{changed} transactions would be updated")
        
        if dry_run:
            if changed > 20:
                print(f"(showing first 20 of {changed} changes)")
            return
        
        if changed == 0:
            print("No changes needed")
            return
        
        # Apply updates
        print(f"\nApplying {changed} updates...")
        
        for new_desc, new_merchant, row_id in updates:
            cursor.execute("""
                UPDATE transactions
                SET description = %s,
                    merchant_name = COALESCE(%s, merchant_name),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_desc, new_merchant, row_id))
        
        conn.commit()
        print(f"✓ Updated {changed} transactions")
        
    finally:
        cursor.close()
        conn.close()


def main():
    arg_parser = argparse.ArgumentParser(
        description='Update Sunmark transaction descriptions with new cleaning logic'
    )
    arg_parser.add_argument('--dry-run', action='store_true', 
                           help='Preview changes without applying')
    
    args = arg_parser.parse_args()
    update_descriptions(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
