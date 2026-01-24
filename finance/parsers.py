#!/usr/bin/env python3
"""
Mythos Finance - Bank-Specific CSV Parsers
/opt/mythos/finance/parsers.py

Handles different CSV formats from various banks.

USAA format:
  - Columns: Date,Description,Original Description,Category,Amount,Status
  - Single amount column (negative = debit)
  - Pre-categorized by bank
  - Has pending status

Sunmark format:
  - 3 header lines (Account Name, Account Number, Date Range)
  - Columns: Transaction Number,Date,Description,Memo,Amount Debit,Amount Credit,Balance,Check Number
  - Separate debit/credit columns
  - Has transaction numbers for deduplication
"""

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
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
    - Columns: Date,Description,Original Description,Category,Amount,Status
    - Single amount column (negative = debit)
    - Pre-categorized
    - Has pending status
    """
    
    def detect(self, file_path: Path) -> bool:
        """Detect USAA format by looking for specific columns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                return 'Original Description' in first_line and 'Status' in first_line
        except Exception:
            return False
    
    def parse_file(self, file_path: Path, account_identifier: str) -> List[Transaction]:
        """Parse USAA CSV export"""
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


class SunmarkParser(BaseParser):
    """
    Parser for Sunmark bank exports
    
    Format:
    - First 3 lines are header metadata (account name, number, date range)
    - Columns: Transaction Number,Date,Description,Memo,Amount Debit,Amount Credit,Balance,Check Number
    - Separate debit/credit columns
    - Has transaction numbers for deduplication
    """
    
    # Transaction type prefixes and their abbreviations
    TRANSACTION_PREFIXES = [
        ('Point Of Sale Withdrawal', 'POS'),
        ('Point Of Sale Deposit', 'POS DEP'),
        ('External Withdrawal', 'EXT'),
        ('External Deposit', 'DEP'),
        ('ATM Withdrawal', 'ATM'),
        ('Overdraft Fee', 'OD FEE'),
        ('Overdraft Protection Deposit', 'OD PROT'),
        ('Withdrawal', 'WD'),
    ]
    
    # State abbreviations for cleanup
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    def detect(self, file_path: Path) -> bool:
        """Detect Sunmark format by looking for account header"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                return 'Account Name' in first_line or 'Simple Checking' in first_line
        except Exception:
            return False
    
    def parse_file(self, file_path: Path, account_identifier: str) -> List[Transaction]:
        """Parse Sunmark CSV export"""
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
                
                # Get description and memo
                description = row.get('Description', '').strip()
                memo = row.get('Memo', '').strip()
                
                # Combine for original (used for categorization matching)
                original_desc = f"{description} {memo}".strip() if memo else description
                
                # Clean up description for display - use memo for merchant info
                clean_desc, extracted_merchant = self._clean_description(description, memo)
                
                # Get balance if available
                balance_str = row.get('Balance', '').strip()
                balance = float(balance_str.replace(',', '').replace('$', '')) if balance_str else None
                
                # Transaction ID from bank
                bank_trans_id = row.get('Transaction Number', '').strip().strip('"') or None
                
                # Compute hash for deduplication (use bank ID if available)
                if bank_trans_id:
                    hash_id = hashlib.sha256(f"sunmark|{bank_trans_id}".encode()).hexdigest()
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
                    merchant_name=extracted_merchant,
                    transaction_type=trans_type,
                    is_pending=False,
                    bank_transaction_id=bank_trans_id,
                    hash_id=hash_id
                ))
                
            except Exception as e:
                print(f"Error parsing row: {row} - {e}")
                continue
        
        return transactions
    
    def _clean_description(self, description: str, memo: str) -> Tuple[str, Optional[str]]:
        """
        Clean up Sunmark description for display.
        
        Transforms ugly bank descriptions like:
            "Point Of Sale Withdrawal STEWART'S SHOP 40 N CANAL ST OXFORD NYUS"
        Into clean display text like:
            "Stewart's Shop - Oxford NY (POS)"
        
        Returns:
            Tuple of (clean_description, merchant_name)
        """
        # Combine description and memo
        full_text = f"{description} {memo}".strip() if memo else description
        
        # Detect and strip transaction type prefix
        trans_type_abbrev = None
        merchant_part = full_text
        
        for prefix, abbrev in self.TRANSACTION_PREFIXES:
            if full_text.upper().startswith(prefix.upper()):
                trans_type_abbrev = abbrev
                merchant_part = full_text[len(prefix):].strip()
                break
        
        # If no prefix matched and it's just a generic withdrawal
        if not trans_type_abbrev and description.startswith('Withdrawal'):
            trans_type_abbrev = 'WD'
            # Try to extract amount or description after "Withdrawal"
            merchant_part = description[len('Withdrawal'):].strip()
        
        # Clean up the merchant part
        merchant_name, location = self._parse_merchant_location(merchant_part)
        
        # Build the clean description
        if merchant_name:
            if location:
                clean_desc = f"{merchant_name} - {location}"
            else:
                clean_desc = merchant_name
            
            if trans_type_abbrev:
                clean_desc = f"{clean_desc} ({trans_type_abbrev})"
        else:
            # Fallback to original if we couldn't parse
            clean_desc = description
            merchant_name = None
        
        return clean_desc, merchant_name
    
    def _parse_merchant_location(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse merchant name and location from transaction text.
        
        Input: "STEWART'S SHOP 40 N CANAL ST OXFORD NYUS"
        Output: ("Stewart's Shop", "Oxford NY")
        
        Returns:
            Tuple of (merchant_name, location)
        """
        if not text:
            return None, None
        
        # Remove trailing country code (US, USUS, etc.)
        text = re.sub(r'\s*(US)+\s*$', '', text, flags=re.IGNORECASE)
        
        # Try to find state code at the end
        location = None
        merchant_text = text
        
        # Pattern: ... CITY STATECODE (e.g., "OXFORD NY" or "SAN FRANCISCO CA")
        state_match = re.search(r'\s+([A-Za-z\s]+?)\s+([A-Z]{2})\s*$', text)
        if state_match:
            potential_city = state_match.group(1).strip()
            potential_state = state_match.group(2).upper()
            
            if potential_state in self.US_STATES:
                location = f"{potential_city.title()} {potential_state}"
                merchant_text = text[:state_match.start()].strip()
        
        # Clean up merchant name
        if merchant_text:
            # Remove store numbers (e.g., "#6366", "T-1056", "9909")
            merchant_text = re.sub(r'\s*[#T-]*\d{3,}\s*', ' ', merchant_text)
            # Remove address fragments (numbers followed by words)
            merchant_text = re.sub(r'\s+\d+\s+[A-Za-z]+(\s+[A-Za-z]+)*\s*$', '', merchant_text)
            # Clean up extra whitespace
            merchant_text = re.sub(r'\s{2,}', ' ', merchant_text).strip()
            
            # Title case the merchant name
            merchant_name = self._smart_title_case(merchant_text)
        else:
            merchant_name = None
        
        return merchant_name, location
    
    def _smart_title_case(self, text: str) -> str:
        """
        Smart title case that handles special cases.
        
        - Preserves apostrophes properly (Stewart's not Stewart'S)
        - Handles common abbreviations
        """
        if not text:
            return text
        
        # Special cases that should stay uppercase
        uppercase_words = {'ACH', 'ATM', 'LLC', 'INC', 'USA', 'US', 'NY', 'CA', 'TX'}
        
        words = text.split()
        result = []
        
        for word in words:
            upper = word.upper()
            if upper in uppercase_words:
                result.append(upper)
            elif "'" in word:
                # Handle apostrophes: "STEWART'S" -> "Stewart's"
                parts = word.split("'")
                titled = "'".join(p.capitalize() for p in parts)
                result.append(titled)
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)


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
