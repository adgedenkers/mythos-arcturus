#!/usr/bin/env python3
"""
Mythos Finance - Bank-Specific CSV Parsers
/opt/mythos/finance/parsers.py

Handles different CSV formats from various banks.
"""

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from abc import ABC, abstractmethod


@dataclass
class Transaction:
    """Normalized transaction record"""
    transaction_date: datetime
    description: str
    original_description: str
    amount: float
    balance: Optional[float]
    category_primary: Optional[str]
    category_secondary: Optional[str]
    merchant_name: Optional[str]
    transaction_type: str  # debit, credit, transfer
    is_pending: bool
    bank_transaction_id: Optional[str]
    hash_id: str
    
    @staticmethod
    def compute_hash(account_id: int, date: datetime, amount: float, description: str) -> str:
        """Generate deduplication hash"""
        data = f"{account_id}|{date.strftime('%Y-%m-%d')}|{amount:.2f}|{description}"
        return hashlib.sha256(data.encode()).hexdigest()


class BaseParser(ABC):
    """Base class for bank parsers"""
    
    @abstractmethod
    def parse_file(self, file_path: Path, account_identifier: str) -> List[Transaction]:
        """Parse a CSV file and return normalized transactions"""
        pass
    
    @abstractmethod
    def detect(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file"""
        pass


class USAAParser(BaseParser):
    """
    Parser for USAA bank exports
    
    Format:
    - First 3 lines are header metadata (account name, number, date range)
    - Columns: Transaction Number,Date,Description,Memo,Amount Debit,Amount Credit,Balance,Check Number
    - Separate debit/credit columns
    - Has transaction numbers for deduplication
    """
    
    def detect(self, file_path: Path) -> bool:
        """Detect USAA format by looking for account header"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                return 'Account Name' in first_line or 'Simple Checking' in first_line
        except Exception:
            return False
    
    def parse_file(self, file_path: Path, account_identifier: str) -> List[Transaction]:
        """Parse USAA CSV export"""
        transactions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip header lines (usually 3: Account Name, Account Number, Date Range)
        # Find the actual CSV header row
        header_row_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('Transaction Number') or 'Transaction Number' in line:
                header_row_idx = i
                break
        
        # Parse from header row onwards
        csv_content = ''.join(lines[header_row_idx:])
        reader = csv.DictReader(csv_content.splitlines())
        
        for row in reader:
            try:
                # Skip empty rows
                if not row.get('Date'):
                    continue
                
                # Parse date (MM/DD/YYYY format)
                date_str = row['Date'].strip()
                trans_date = datetime.strptime(date_str, '%m/%d/%Y')
                
                # Get amount (debit is negative, credit is positive)
                debit = row.get('Amount Debit', '').strip()
                credit = row.get('Amount Credit', '').strip()
                
                if debit:
                    amount = -abs(float(debit.replace(',', '').replace('$', '')))
                    trans_type = 'debit'
                elif credit:
                    amount = abs(float(credit.replace(',', '').replace('$', '')))
                    trans_type = 'credit'
                else:
                    continue  # Skip if no amount
                
                # Get description
                description = row.get('Description', '').strip()
                memo = row.get('Memo', '').strip()
                original_desc = f"{description} {memo}".strip() if memo else description
                
                # Clean up description for display
                clean_desc = self._clean_description(description)
                
                # Get balance if available
                balance_str = row.get('Balance', '').strip()
                balance = float(balance_str.replace(',', '').replace('$', '')) if balance_str else None
                
                # Transaction ID from bank
                bank_trans_id = row.get('Transaction Number', '').strip() or None
                
                # Compute hash for deduplication (use bank ID if available)
                if bank_trans_id:
                    hash_id = hashlib.sha256(f"usaa|{bank_trans_id}".encode()).hexdigest()
                else:
                    hash_id = Transaction.compute_hash(
                        hash(account_identifier),
                        trans_date,
                        amount,
                        original_desc
                    )
                
                transactions.append(Transaction(
                    transaction_date=trans_date,
                    description=clean_desc,
                    original_description=original_desc,
                    amount=amount,
                    balance=balance,
                    category_primary=None,  # Will be set by categorizer
                    category_secondary=None,
                    merchant_name=self._extract_merchant(description),
                    transaction_type=trans_type,
                    is_pending=False,
                    bank_transaction_id=bank_trans_id,
                    hash_id=hash_id
                ))
                
            except Exception as e:
                print(f"Error parsing row: {row} - {e}")
                continue
        
        return transactions
    
    def _clean_description(self, desc: str) -> str:
        """Clean up USAA description for display"""
        # Remove location codes and extra whitespace
        desc = re.sub(r'\s{2,}', ' ', desc)
        # Remove state codes at end
        desc = re.sub(r'\s+[A-Z]{2}US$', '', desc)
        return desc.strip()
    
    def _extract_merchant(self, desc: str) -> Optional[str]:
        """Try to extract merchant name from description"""
        # Common patterns
        patterns = [
            r'^(?:Point Of Sale Withdrawal|External Withdrawal)\s+(.+?)(?:\s+[A-Z]{2}US)?$',
            r'^(.+?)\s+#\d+',
        ]
        for pattern in patterns:
            match = re.match(pattern, desc, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None


class SunmarkParser(BaseParser):
    """
    Parser for Sunmark/Plaid-style exports
    
    Format:
    - Columns: Date,Description,Original Description,Category,Amount,Status
    - Single amount column (negative = debit)
    - Pre-categorized
    - Has pending status
    """
    
    def detect(self, file_path: Path) -> bool:
        """Detect Sunmark format by looking for specific columns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                return 'Original Description' in first_line and 'Status' in first_line
        except Exception:
            return False
    
    def parse_file(self, file_path: Path, account_identifier: str) -> List[Transaction]:
        """Parse Sunmark/Plaid CSV export"""
        transactions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Skip empty rows
                    if not row.get('Date'):
                        continue
                    
                    # Parse date (YYYY-MM-DD format)
                    date_str = row['Date'].strip()
                    trans_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    # Get amount
                    amount_str = row.get('Amount', '0').strip()
                    amount = float(amount_str.replace(',', '').replace('$', ''))
                    
                    # Determine transaction type
                    if amount < 0:
                        trans_type = 'debit'
                    else:
                        trans_type = 'credit'
                    
                    # Get descriptions
                    description = row.get('Description', '').strip()
                    original_desc = row.get('Original Description', description).strip()
                    
                    # Get category from bank
                    category = row.get('Category', '').strip()
                    if category == 'Category Pending' or not category:
                        category = None
                    
                    # Check pending status
                    status = row.get('Status', 'Posted').strip()
                    is_pending = status.lower() == 'pending'
                    
                    # Compute hash for deduplication
                    hash_id = Transaction.compute_hash(
                        hash(account_identifier),
                        trans_date,
                        amount,
                        original_desc
                    )
                    
                    transactions.append(Transaction(
                        transaction_date=trans_date,
                        description=description,
                        original_description=original_desc,
                        amount=amount,
                        balance=None,  # Not provided in this format
                        category_primary=category,
                        category_secondary=None,
                        merchant_name=description if description != original_desc else None,
                        transaction_type=trans_type,
                        is_pending=is_pending,
                        bank_transaction_id=None,
                        hash_id=hash_id
                    ))
                    
                except Exception as e:
                    print(f"Error parsing row: {row} - {e}")
                    continue
        
        return transactions


# Parser registry
PARSERS = {
    'usaa': USAAParser(),
    'sunmark': SunmarkParser(),
}


def detect_parser(file_path: Path) -> Optional[str]:
    """Auto-detect which parser to use for a file"""
    for name, parser in PARSERS.items():
        if parser.detect(file_path):
            return name
    return None


def get_parser(parser_name: str) -> BaseParser:
    """Get parser by name"""
    if parser_name not in PARSERS:
        raise ValueError(f"Unknown parser: {parser_name}. Available: {list(PARSERS.keys())}")
    return PARSERS[parser_name]
