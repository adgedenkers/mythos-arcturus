#!/usr/bin/env python3
"""
Mythos Finance Importer v3
/opt/mythos/finance/importer.py
Clean import system for bank CSVs with proper parsing and inline categorization.

Banks supported:
- Sunmark (has balance column, 3 header lines, separate debit/credit)
- USAA (no balance, calculates from known endpoint, single amount column)

Changes in v3:
- Inline categorization using category_mappings table
- merchant_name populated from mappings
- Categorizer loaded once, applied per transaction

Usage:
    python importer.py sunmark /path/to/file.CSV
    python importer.py usaa /path/to/file.csv --balance 1243.19
    python importer.py sunmark /path/to/file.CSV --dry-run
    
Testing:
    python importer.py sunmark /path/to/file.CSV --dry-run --verbose
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
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

# Import categorizer
from categorizer import Categorizer

# Account IDs (from database)
ACCOUNT_IDS = {
    'sunmark': 1,  # SUN
    'usaa': 2,     # USAA
}
ARCHIVE_DIR = Path('/opt/mythos/finance/archive/imports')
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
def make_hash(date_str: str, amount: Decimal, description: str, account_id: int) -> str:
    """Create unique hash for transaction deduplication"""
    raw = f"{account_id}|{date_str}|{amount}|{description}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
def parse_decimal(value: str) -> Decimal:
    """Parse a string to Decimal, handling various formats"""
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
    """Parse date string to YYYY-MM-DD format"""
    date_str = date_str.strip().strip('"')
    
    # Try MM/DD/YYYY format (Sunmark)
    try:
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Try YYYY-MM-DD format (USAA)
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    raise ValueError(f"Cannot parse date: {date_str}")
def clean_description_sunmark(description: str, memo: str) -> str:
    """
    Clean Sunmark description by removing verbose prefixes and extracting merchant.
    
    Logic:
    1. Strip transaction type prefix from description
    2. What remains in description is usually the merchant
    3. If nothing remains, extract merchant from memo (before address junk)
    4. Payment processors (PayPal, Venmo) become transaction type prefix
    
    Examples:
        "Point Of Sale Withdrawal", "WALMART.COM 800 702..." → "Walmart.com"
        "Point Of Sale Withdrawal PAYPAL", "*DISNEY 7700..." → "PayPal: Disney"
        "Point Of Sale Withdrawal DUNKIN", "#358342 155 KINGSTON..." → "Dunkin"
        "Point Of Sale Deposit", "ENTERPRISE RENT 5051..." → "Enterprise Rent"
        "External Withdrawal Blueox", "Corporati 264..." → "EXT: Blueox"
        "Overdraft Fee PAYPAL *DISNEY", "7700..." → "OD Fee: PayPal: Disney"
        "Deposit Shared Branch Mobile", "Latham MD" → "Mobile Deposit: Latham"
        "Point Of Sale Withdrawal Amazon", "web serv 440..." → "Amazon"
    """
    desc = description.strip().strip('"')
    memo = memo.strip().strip('"') if memo else ''
    
    # Payment processors - these become the transaction type
    payment_processors = ['PAYPAL', 'VENMO', 'ZELLE', 'CASHAPP', 'CASH APP']
    payment_type = None
    
    # Check description for payment processor
    desc_upper = desc.upper()
    for processor in payment_processors:
        if processor in desc_upper:
            payment_type = processor.title()
            if processor == 'CASHAPP' or processor == 'CASH APP':
                payment_type = 'CashApp'
            break
    
    # Transaction type prefixes - order matters (longer/specific first)
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
    
    # Extract merchant from remainder (what's left in description after prefix)
    merchant = remainder
    
    # Remove payment processor from merchant (it becomes the type prefix)
    if payment_type:
        for processor in payment_processors:
            merchant = re.sub(rf'\b{processor}\b\s*', '', merchant, flags=re.IGNORECASE)
    
    # Clean up merchant
    merchant = re.sub(r'^\*+\s*', '', merchant)  # Remove leading asterisks
    merchant = merchant.strip()
    
    # If merchant is empty or too short, extract from memo
    if not merchant or len(merchant) < 2:
        if memo:
            memo_merchant = memo
            memo_merchant = re.sub(r'^\*+\s*', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}US$', '', memo_merchant)
            memo_merchant = re.sub(r'\s+[A-Z]{2}$', '', memo_merchant)
            memo_merchant = re.sub(r'\s*\d{7,}', '', memo_merchant)
            
            parts = re.split(r'\s+(\d{2,}\s+(?:ST|AVE|RD|DR|BLVD|HWY|PKWY|N\s|S\s|E\s|W\s|SW\s|NW\s|SE\s|NE\s|CANAL|MAIN|STATE))', memo_merchant, maxsplit=1, flags=re.IGNORECASE)
            if parts:
                memo_merchant = parts[0].strip()
            
            memo_merchant = re.sub(r'\s+\d[\d\s]*$', '', memo_merchant)
            merchant = memo_merchant.strip()
    
    # Special case: "Deposit" or "Withdrawal" alone means we need memo
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
    
    # Special case: Mobile Deposit uses memo for location
    if 'Mobile Deposit' in txn_prefix:
        location = re.sub(r'\s+[A-Z]{2}$', '', memo).strip() if memo else ''
        merchant = location if location else ''
    
    # Build final result
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
    
    # Final cleanup
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r':\s*:', ':', result)
    result = re.sub(r':\s*$', '', result)
    result = result.strip(': -')
    
    if len(result) > 50:
        result = result[:47] + '...'
    
    return result if result else desc
def clean_description_usaa(description: str, original_desc: str) -> str:
    """
    Clean USAA description - usually already clean, just minor fixes.
    """
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
    """Parser for Sunmark CSV exports"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.account_id = ACCOUNT_IDS['sunmark']
        self.transactions = []
    
    def parse(self) -> list:
        """Parse Sunmark CSV file"""
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
            
            txn = {
                'account_id': self.account_id,
                'transaction_date': parsed_date,
                'description': clean_desc,
                'original_description': original_desc,
                'amount': amount,
                'balance': balance_amt,
                'bank_transaction_id': txn_num,
                'is_pending': False,
                'hash_id': make_hash(parsed_date, amount, f"{original_desc}|{txn_num}", self.account_id),
            }
            self.transactions.append(txn)
        
        return self.transactions
    
    def get_current_balance(self) -> Decimal:
        """Get the most recent balance from parsed transactions"""
        if not self.transactions:
            return None
        return self.transactions[0].get('balance')
class USAAParser:
    """Parser for USAA CSV exports"""
    
    def __init__(self, filepath: str, known_balance: Decimal):
        self.filepath = filepath
        self.account_id = ACCOUNT_IDS['usaa']
        self.known_balance = known_balance
        self.transactions = []
    
    def parse(self) -> list:
        """Parse USAA CSV file and calculate running balance"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return []
        
        raw_txns = []
        for row in rows:
            date_str = row.get('Date', '').strip()
            description = row.get('Description', '').strip()
            original_desc = row.get('Original Description', '').strip()
            category = row.get('Category', '').strip()
            amount_str = row.get('Amount', '').strip()
            status = row.get('Status', '').strip()
            
            if 'Pending' in status or 'Scheduled' in status:
                continue
            
            try:
                parsed_date = parse_date(date_str)
            except ValueError:
                continue
            
            amount = parse_decimal(amount_str)
            if amount == 0:
                continue
            
            clean_desc = clean_description_usaa(description, original_desc)
            
            raw_txns.append({
                'date': parsed_date,
                'description': clean_desc,
                'original_description': original_desc or description,
                'category': category,
                'amount': amount,
                'status': status,
            })
        
        running_balance = self.known_balance
        
        for txn in raw_txns:
            balance_after = running_balance
            
            self.transactions.append({
                'account_id': self.account_id,
                'transaction_date': txn['date'],
                'description': txn['description'],
                'original_description': txn['original_description'],
                'amount': txn['amount'],
                'balance': balance_after,
                'category_primary': txn['category'] if txn['category'] != 'Category Pending' else None,
                'bank_transaction_id': None,
                'is_pending': False,
                'hash_id': make_hash(txn['date'], txn['amount'], f"{txn['original_description']}|{balance_after}", self.account_id),
            })
            
            running_balance = running_balance - txn['amount']
        
        return self.transactions
    
    def get_current_balance(self) -> Decimal:
        """Get the most recent balance"""
        return self.known_balance
class Importer:
    """Database importer for parsed transactions with inline categorization"""
    
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
            # Load categorizer using same connection
            self.categorizer = Categorizer(conn=self.conn)
            if self.verbose:
                print(f"Loaded {self.categorizer.mapping_count} category mappings")
        else:
            # Still load categorizer for dry-run display
            self.categorizer = Categorizer()
            if self.verbose:
                print(f"Loaded {self.categorizer.mapping_count} category mappings")
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def import_transactions(self, transactions: list, source_file: str) -> dict:
        """Import transactions to database with inline categorization"""
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
        
        if self.verbose:
            print(f"\nProcessing {len(transactions)} transactions...")
        
        # Apply categorization to all transactions
        for txn in transactions:
            if self.categorizer:
                cat_result = self.categorizer.categorize_transaction(txn)
                if cat_result:
                    results['categorized'] += 1
                else:
                    if not txn.get('category_primary'):
                        results['uncategorized'] += 1
                    else:
                        # Already had a category (e.g. from USAA)
                        results['categorized'] += 1
        
        if self.dry_run:
            for txn in transactions[:10]:
                cat = txn.get('category_primary', '?')
                merch = txn.get('merchant_name', '')
                print(f"  {txn['transaction_date']} | {txn['amount']:>10.2f} | {cat:15} | {txn['description'][:35]}")
            if len(transactions) > 10:
                print(f"  ... and {len(transactions) - 10} more")
            results['imported'] = len(transactions)
            return results
        
        # Check for existing hashes
        hashes = [t['hash_id'] for t in transactions]
        self.cur.execute(
            "SELECT hash_id FROM transactions WHERE hash_id = ANY(%s)",
            (hashes,)
        )
        existing = {row['hash_id'] for row in self.cur.fetchall()}
        
        new_txns = [t for t in transactions if t['hash_id'] not in existing]
        results['skipped'] = len(transactions) - len(new_txns)
        
        if self.verbose:
            print(f"  {results['skipped']} already exist, {len(new_txns)} new")
        
        if not new_txns:
            return results
        
        # Insert one at a time
        for t in new_txns:
            try:
                self.cur.execute(
                    """
                    INSERT INTO transactions (
                        account_id, transaction_date, description, original_description,
                        amount, balance, category_primary, category_secondary,
                        merchant_name, bank_transaction_id,
                        hash_id, is_pending, source_file
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (hash_id) DO NOTHING
                    """,
                    (
                        t['account_id'],
                        t['transaction_date'],
                        t['description'],
                        t.get('original_description'),
                        t['amount'],
                        t.get('balance'),
                        t.get('category_primary'),
                        t.get('category_secondary'),
                        t.get('merchant_name'),
                        t.get('bank_transaction_id'),
                        t['hash_id'],
                        t.get('is_pending', False),
                        source_file,
                    )
                )
                self.conn.commit()
                results['imported'] += 1
            except Exception as e:
                self.conn.rollback()
                results['failed'].append({
                    'transaction': t,
                    'reason': str(e)
                })
                results['errors'] += 1
        
        if results['failed'] and self.verbose:
            print(f"\n⚠️  {len(results['failed'])} transactions failed:")
            for fail in results['failed'][:5]:
                t = fail['transaction']
                print(f"    {t.get('transaction_date', '?')} | {t.get('description', '?')[:30]} - {fail['reason']}")
            if len(results['failed']) > 5:
                print(f"    ... and {len(results['failed']) - 5} more")
        
        return results
    
    def update_account_balance(self, account_id: int, balance: Decimal):
        """Update the account's current_balance"""
        if self.dry_run:
            print(f"\nWould update account {account_id} balance to ${balance:.2f}")
            return
        
        self.cur.execute(
            """
            UPDATE accounts 
            SET current_balance = %s, balance_updated_at = NOW()
            WHERE id = %s
            """,
            (balance, account_id)
        )
        self.conn.commit()
        if self.verbose:
            print(f"\nUpdated account balance to ${balance:.2f}")
def archive_file(filepath: str, bank: str):
    """Archive the imported file"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = Path(filepath).suffix
    archive_name = f"{bank}_{timestamp}{ext}"
    archive_path = ARCHIVE_DIR / archive_name
    
    shutil.copy2(filepath, archive_path)
    return archive_path
def main():
    parser = argparse.ArgumentParser(description='Import bank CSV files')
    parser.add_argument('bank', choices=['sunmark', 'usaa'], help='Bank type')
    parser.add_argument('file', help='CSV file path')
    parser.add_argument('--balance', type=float, help='Current balance (required for USAA)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without committing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-archive', action='store_true', help='Do not archive the file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)
    
    if args.bank == 'usaa' and args.balance is None:
        print("USAA imports require --balance argument")
        print("Check your USAA account and provide current balance")
        sys.exit(1)
    
    # Parse
    print(f"Parsing {args.bank.upper()} file: {args.file}")
    
    if args.bank == 'sunmark':
        bank_parser = SunmarkParser(args.file)
    else:
        bank_parser = USAAParser(args.file, Decimal(str(args.balance)))
    
    transactions = bank_parser.parse()
    current_balance = bank_parser.get_current_balance()
    
    print(f"Found {len(transactions)} transactions")
    if current_balance:
        print(f"Current balance: ${current_balance:.2f}")
    
    if args.verbose and transactions:
        print("\nSample transactions:")
        for txn in transactions[:5]:
            bal = f"${txn['balance']:.2f}" if txn.get('balance') else "N/A"
            print(f"  {txn['transaction_date']} | {txn['amount']:>10.2f} | {bal:>12} | {txn['description'][:35]}")
    
    # Import
    importer = Importer(dry_run=args.dry_run, verbose=args.verbose)
    importer.connect()
    
    try:
        results = importer.import_transactions(transactions, Path(args.file).name)
        
        print(f"\nResults:")
        print(f"  Total:        {results['total']}")
        print(f"  Imported:     {results['imported']}")
        print(f"  Skipped:      {results['skipped']} (duplicates)")
        print(f"  Categorized:  {results['categorized']}")
        print(f"  Uncategorized:{results['uncategorized']}")
        if results['errors']:
            print(f"  Errors:       {results['errors']}")
        
        # Update account balance
        if current_balance and results['imported'] > 0:
            importer.update_account_balance(bank_parser.account_id, current_balance)
        
        # Archive
        if not args.dry_run and not args.no_archive:
            archive_path = archive_file(args.file, args.bank)
            print(f"\nArchived to: {archive_path}")
        
    finally:
        importer.close()
    
    print("\nDone!")
if __name__ == '__main__':
    main()
