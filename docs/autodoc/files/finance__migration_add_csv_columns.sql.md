# finance/migration_add_csv_columns.sql

**Language:** sql
**Stream:** SYS
**Module:** Finance System
**Lines:** 134

---

### Documentation for `finance/migration_add_csv_columns.sql`

#### Purpose
This SQL file is a migration script designed to add new columns to the `accounts` and `transactions` tables in the Mythos finance schema. The additions are necessary for supporting CSV import functionality while maintaining compatibility with the existing Plaid schema.

#### Architecture
The script is structured into several sections, each handling a specific aspect of the migration:
1. **Accounts Table Modifications**: Adds new columns and populates them with existing data.
2. **Transactions Table Modifications**: Adds new columns and populates them with existing data.
3. **Indexes and Constraints**: Adds indexes and a unique constraint on the `hash_id` column.
4. **Default Accounts Insertion**: Inserts default accounts if they do not already exist.
5. **Verification**: Verifies the migration's success by checking the presence of required columns.

#### Patterns
- **Conditional Execution**: Uses `IF NOT EXISTS` and `COALESCE` to ensure that operations are only performed when necessary.
- **Transaction Management**: Implicitly uses transactions for each block of operations to ensure atomicity.

#### Dependencies
- **PostgreSQL**: The script is written for PostgreSQL and relies on its schema and table management features.
- **Plaid Integration**: References existing columns and data structures from the Plaid integration.

#### Interfaces
- **Database Schema**: Modifies the `accounts` and `transactions` tables.
- **Indexes and Constraints**: Adds indexes and a unique constraint to the `transactions` table.

#### Database
- **Tables and Columns**:
  - `accounts`: Adds `bank_name`, `account_name`, `account_number`, and `notes`.
  - `transactions`: Adds `description`, `original_description`, `balance`, `category_primary`, `category_secondary`, `bank_transaction_id`, `hash_id`, `source_file`, `imported_by`, and `created_at`.

#### Configuration
- **Environment Variables**: None.
- **Configuration Files**: None.

#### Key Logic
- **Column Population**: Populates new columns with existing data from related columns.
- **Hash Generation**: Generates a `hash_id` for each transaction using a SHA-256 hash of concatenated transaction details.
- **Unique Constraint**: Ensures that `hash_id` is unique across all transactions.

#### Integration Points
- **CSV Import**: Supports the CSV import process by adding necessary columns and ensuring data integrity.
- **Plaid Integration**: Maintains compatibility with the existing Plaid schema by mapping and populating new columns with existing data.

### Detailed Analysis

#### Accounts Table Modifications
- **Columns Added**:
  - `bank_name`: Maps from `name` via the `institutions` table.
  - `account_name`: Maps from `official_name` or `name`.
  - `account_number`: Maps from `mask`.
  - `notes`: A text field for additional notes.

- **Data Population**:
  - Populates `bank_name` from `name` if `bank_name` is `NULL`.
  - Populates `account_name` from `official_name` or `name` if `account_name` is `NULL`.

#### Transactions Table Modifications
- **Columns Added**:
  - `description`: Maps from `name`.
  - `original_description`: Maps from `name`.
  - `balance`: Tracks the balance.
  - `category_primary`: Maps from `primary_category`.
  - `category_secondary`: A secondary category field.
  - `bank_transaction_id`: Maps from `plaid_transaction_id`.
  - `hash_id`: A unique hash for deduplication.
  - `source_file`: Tracks the source CSV file.
  - `imported_by`: Tracks the user who imported the transaction.
  - `created_at`: Tracks the creation timestamp.

- **Data Population**:
  - Populates `description` and `original_description` from `name` if `NULL`.
  - Populates `category_primary` from `primary_category` if `NULL`.
  - Populates `bank_transaction_id` from `plaid_transaction_id` if `NULL`.
  - Generates `hash_id` for existing transactions using a SHA-256 hash of concatenated transaction details.

#### Indexes and Constraints
- **Indexes**:
  - `idx_transactions_hash`: Index on `hash_id`.
  - `idx_transactions_source`: Index on `source_file`.

- **Unique Constraint**:
  - `transactions_hash_id_key`: Ensures `hash_id` is unique across all transactions.

#### Default Accounts Insertion
- Inserts default accounts for `Sunmark` and `USAA` if they do not already exist.
- Resets the sequence for the `accounts` table to ensure the next `id` is greater than the maximum existing `id`.

#### Verification
- Verifies the migration's success by checking the presence of required columns in the `transactions` table.

This script ensures that the Mythos finance schema is ready for CSV import while maintaining compatibility with the existing Plaid schema and ensuring data integrity through unique constraints and indexes.
