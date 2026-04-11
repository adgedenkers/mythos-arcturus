# finance/migration_0051_credit_cards.sql

**Language:** sql
**Stream:** SYS
**Module:** Finance System
**Lines:** 51

---

### Purpose
The `finance/migration_0051_credit_cards.sql` file is a PostgreSQL migration script designed to add credit card account tracking to the `accounts` table. It introduces new columns for credit card-specific data and updates existing account balances.

### Architecture
The script is organized into several sections:
1. **Add Columns**: Adds new columns to the `accounts` table if they do not already exist.
2. **Add Credit Card Accounts**: Inserts new credit card accounts into the `accounts` table.
3. **Update Existing Account Balances**: Updates the `current_balance` and `balance_updated_at` fields for existing accounts.
4. **Add USAA Loan**: Inserts a new loan account into the `accounts` table.

### Patterns
- **Database Migration**: This script follows the database migration pattern, where changes to the database schema and data are applied in a controlled manner.

### Dependencies
- **PostgreSQL Database**: The script relies on the PostgreSQL database and the `accounts` table.
- **Environment**: The script should be run using the `postgres` user with the `mythos` database.

### Interfaces
- **SQL Commands**: The script exposes SQL commands for altering the `accounts` table and inserting/updating data.

### Database
- **Tables/Labels**: The script modifies the `accounts` table by adding columns and inserting/updating rows.
  - **Columns Added**: `current_balance`, `balance_updated_at`, `credit_limit`, `min_payment`, `payment_due_day`.
  - **Rows Inserted/Updated**: Rows for credit card accounts and a loan account.

### Configuration
- **Environment Variables**: No specific environment variables are used.
- **Configuration Files**: No configuration files are used.

### Key Logic
1. **Add Columns**: Ensures that the `accounts` table has the necessary columns for credit card tracking.
2. **Insert Credit Card Accounts**: Inserts new credit card accounts with specific details.
3. **Update Balances**: Updates the `current_balance` and `balance_updated_at` fields for existing accounts.
4. **Add Loan Account**: Inserts a new loan account with specific details.

### Integration Points
- **Accounts Table**: This script integrates with the `accounts` table to add new columns and insert/update rows.
- **PostgreSQL**: The script is run directly against the PostgreSQL database, typically as part of a larger database migration process.

### Detailed Breakdown

1. **Add Columns**:
   ```sql
   ALTER TABLE accounts ADD COLUMN IF NOT EXISTS current_balance NUMERIC(12,2) DEFAULT 0;
   ALTER TABLE accounts ADD COLUMN IF NOT EXISTS balance_updated_at TIMESTAMP;
   ALTER TABLE accounts ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(12,2);
   ALTER TABLE accounts ADD COLUMN IF NOT EXISTS min_payment NUMERIC(12,2);
   ALTER TABLE accounts ADD COLUMN IF NOT EXISTS payment_due_day INTEGER;
   ```
   - Adds columns to track credit card balances and related information.

2. **Add Credit Card Accounts**:
   ```sql
   INSERT INTO accounts (bank_name, account_name, account_type, abbreviation, current_balance, credit_limit, min_payment, payment_due_day, notes, is_active)
   VALUES 
       ('L.L.Bean', 'Mastercard', 'credit', 'LLBEAN', -8423.34, 14650.00, 308.00, 12, 'Rebecca login', true),
       ('Tractor Supply', 'Credit Card', 'credit', 'TSC', -2411.14, 10250.00, 0.00, 12, 'Rebecca login', true),
       ('Old Navy', 'Barclaycard', 'credit', 'OLDNAVY', -6125.72, 6800.00, 59.33, 12, 'rdenkers login', true),
       ('TJX Rewards', 'Mastercard', 'credit', 'TJX', -1.99, 2700.00, 0.00, 18, 'rdenkers login', true),
       ('American Express', 'Blue Cash', 'credit', 'AMEX', -870.83, 1000.00, 0.00, 27, 'Adge card - paid current', true)
   ON CONFLICT DO NOTHING;
   ```
   - Inserts new credit card accounts into the `accounts` table.

3. **Update Existing Account Balances**:
   ```sql
   UPDATE accounts SET current_balance = 976.47, balance_updated_at = NOW() WHERE abbreviation = 'SUN';
   UPDATE accounts SET current_balance = 1431.65, balance_updated_at = NOW() WHERE abbreviation = 'USAA';
   UPDATE accounts SET current_balance = 2086.00, balance_updated_at = NOW() WHERE abbreviation = 'SID';
   UPDATE accounts SET current_balance = 7000.00, balance_updated_at = NOW() WHERE abbreviation = 'NBT';
   UPDATE accounts SET current_balance = 758.00, balance_updated_at = NOW() WHERE abbreviation = 'DVA';
   ```
   - Updates the `current_balance` and `balance_updated_at` fields for existing accounts.

4. **Add USAA Loan**:
   ```sql
   INSERT INTO accounts (bank_name, account_name, account_type, abbreviation, current_balance, min_payment, payment_due_day, notes, is_active)
   VALUES 
       ('USAA', 'Personal Loan', 'loan', 'USAALOAN', -3531.31, 0.00, 13, 'Paid ahead - autopay on', true)
   ON CONFLICT DO NOTHING;
   ```
   - Inserts a new loan account into the `accounts` table.

5. **Show Results**:
   ```sql
   \echo ''
   \echo '=== UPDATED ACCOUNTS ==='
   SELECT abbreviation, bank_name, account_name, account_type, current_balance, credit_limit, min_payment, payment_due_day 
   FROM accounts 
   ORDER BY account_type, bank_name;
   ```
   - Displays the updated accounts for verification.

This migration script ensures that the `accounts` table is properly updated to include credit card and loan account details, facilitating better financial tracking within the Mythos system.
