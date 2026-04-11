# finance/bill_matcher.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 333

---

### File: finance/bill_matcher.py

#### Purpose
This file contains the `BillMatcher` class, which matches imported transactions against recurring bills to track payments. It provides methods to load bills, match transactions, and retrieve unpaid bills.

#### Architecture
The `BillMatcher` class is the primary component of this file. It contains methods for initializing the class, loading bills, determining billing months, matching single transactions, matching multiple transactions, getting unpaid bills, and closing the database connection. The class is designed to be instantiated and used as a module or run as a standalone script.

#### Patterns
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern as it ensures a single database connection is used throughout the class.
- **Factory**: The `BillMatcher` class acts as a factory for matching transactions to bills.

#### Dependencies
- **Imports**: `os`, `sys`, `argparse`, `logging`, `datetime`, `decimal`, `pathlib`, `dotenv`, `psycopg2`
- **Database**: PostgreSQL (`recurring_bills`, `transactions`, `bill_payments` tables)

#### Interfaces
- **Public Methods**:
  - `__init__(self, conn=None)`: Initializes the `BillMatcher` instance with a database connection.
  - `match_single_transaction(self, txn)`: Matches a single transaction to a bill.
  - `match_transactions(self, transaction_ids=None, month=None, dry_run=False)`: Matches multiple transactions to bills and records payments.
  - `get_unpaid_bills(self, month=None)`: Retrieves unpaid bills for a given month.
  - `close(self)`: Closes the database connection.

#### Database
- **Tables**:
  - `recurring_bills`: Stores information about recurring bills.
  - `transactions`: Stores transaction data.
  - `bill_payments`: Stores records of matched transactions and their associated bills.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
1. **Loading Bills**: The `_load_bills` method loads active recurring bills with merchant patterns from the `recurring_bills` table.
2. **Matching Transactions**:
   - `_determine_billing_month`: Determines the billing month for a transaction based on the transaction date and bill due date.
   - `match_single_transaction`: Checks if a transaction matches any bill based on the description and amount.
   - `match_transactions`: Matches multiple transactions against bills and records the payments in the `bill_payments` table.
3. **Getting Unpaid Bills**: The `get_unpaid_bills` method retrieves bills that have not been paid for a given month.

#### Integration Points
- **Importer**: The `BillMatcher` class is called after importing transactions to identify which bills have been paid.
- **Database**: The class interacts with PostgreSQL to load bills, match transactions, and record payments.
- **Logging**: Uses the `logging` module to log errors and information.

### Detailed Documentation

#### Classes
- **BillMatcher**
  - **Methods**:
    - `__init__(self, conn=None)`: Initializes the `BillMatcher` instance with a database connection.
    - `_load_bills(self)`: Loads active recurring bills with merchant patterns.
    - `_determine_billing_month(self, txn_date, bill)`: Determines the billing month for a transaction.
    - `match_single_transaction(self, txn)`: Matches a single transaction to a bill.
    - `match_transactions(self, transaction_ids=None, month=None, dry_run=False)`: Matches multiple transactions to bills and records payments.
    - `get_unpaid_bills(self, month=None)`: Retrieves unpaid bills for a given month.
    - `close(self)`: Closes the database connection.

#### Top-level Functions
- **get_db_connection()**: Returns a PostgreSQL database connection.
- **main()**: Main function for running the `BillMatcher` as a standalone script.

#### Key Logic
1. **Loading Bills**:
   ```python
   def _load_bills(self):
       cur = self.conn.cursor()
       cur.execute("""
           SELECT id, merchant_name, merchant_pattern, expected_amount, 
                  amount_variance, frequency, expected_day, category_primary, notes
           FROM recurring_bills
           WHERE is_active = true
             AND merchant_pattern IS NOT NULL
             AND merchant_pattern != ''
           ORDER BY id
       """)
       self.bills = cur.fetchall()
   ```

2. **Matching Transactions**:
   ```python
   def match_single_transaction(self, txn):
       desc = (txn.get('description') or '').upper()
       orig = (txn.get('original_description') or '').upper()
       amount = abs(Decimal(str(txn.get('amount', 0))))
       
       # Skip income transactions
       if txn.get('amount', 0) > 0:
           return None
       
       for bill in self.bills:
           pattern = bill['merchant_pattern'].upper()
           
           # Check pattern match against description or original_description
           if pattern not in desc and pattern not in orig:
               continue
           
           # Check amount within variance
           expected = abs(Decimal(str(bill['expected_amount'])))
           variance = Decimal(str(bill['amount_variance'] or 5))
           
           # For bills marked as varying significantly (high variance in notes),
           # be more lenient — just confirm it's a debit, pattern matches
           notes = (bill.get('notes') or '').lower()
           is_variable = any(word in notes for word in ['varies', 'variable', 'ext:'])
           
           if is_variable:
               # Variable bills: just need pattern match + it's a debit
               pass
           else:
               # Fixed bills: check amount is within variance
               if abs(amount - expected) > variance:
                   continue
           
           return {
               'bill_id': bill['id'],
               'bill_name': bill['merchant_name'],
               'expected_amount': expected,
               'actual_amount': amount,
               'matched_pattern': bill['merchant_pattern'],
           }
       
       return None
   ```

3. **Getting Unpaid Bills**:
   ```python
   def get_unpaid_bills(self, month=None):
       if not month:
           month = date.today().strftime('%Y-%m')
       
       cur = self.conn.cursor()
       cur.execute("""
           SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day, 
                  rb.frequency, rb.notes
           FROM recurring_bills rb
           WHERE rb.is_active = true
             AND rb.frequency = 'monthly'
             AND rb.id NOT IN (
                 SELECT bill_id FROM bill_payments WHERE billing_month = %s
             )
           ORDER BY rb.expected_day
       """, (month,))
       
       return cur.fetchall()
   ```

This file is crucial for the Mythos system's finance module, ensuring that transactions are accurately matched to recurring bills and that unpaid bills are tracked effectively.
