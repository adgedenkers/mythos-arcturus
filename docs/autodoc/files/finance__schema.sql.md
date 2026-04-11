# finance/schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Finance System
**Lines:** 377

---

### File: finance/schema.sql

#### Purpose
This SQL file defines the PostgreSQL schema for the Mythos Finance subsystem, including tables for managing bank accounts, transactions, import logs, category mappings, and recurring bills. It also includes default data and indexes for efficient querying.

#### Architecture
The file is structured into several sections, each defining a specific table and its constraints. The tables include `accounts`, `transactions`, `import_logs`, `category_mappings`, and `recurring_bills`. Each table has a set of columns with appropriate data types and constraints. The file also includes default data insertion and index creation for performance optimization.

#### Patterns
No specific design patterns are used in this SQL file as it is primarily focused on defining the database schema and initial data.

#### Dependencies
This file depends on PostgreSQL and the existence of the `finance` schema within the database. It does not import any external libraries or modules.

#### Interfaces
This file does not expose any interfaces directly. Instead, it defines the structure and initial data for the Mythos Finance subsystem, which can be accessed and manipulated through SQL queries or ORM (Object-Relational Mapping) tools.

#### Database
The file creates and populates the following tables:
- `accounts`: Tracks bank accounts.
- `transactions`: Stores transaction details.
- `import_logs`: Logs transaction import activities.
- `category_mappings`: Stores rules for auto-categorizing transactions.
- `recurring_bills`: Tracks expected recurring transactions.

#### Configuration
This file does not use any configuration files or environment variables directly. However, it assumes the existence of a PostgreSQL database and the `finance` schema.

#### Key Logic
- **Accounts Table**: Manages bank account details with fields like `bank_name`, `account_name`, `account_number`, `account_type`, and `current_balance`.
- **Transactions Table**: Stores transaction details with fields like `account_id`, `transaction_date`, `post_date`, `description`, `amount`, `balance`, `category_primary`, `category_secondary`, and `transaction_type`.
- **Import Logs Table**: Tracks transaction import activities with fields like `account_id`, `source_file`, `file_path`, `total_rows`, `imported_count`, `skipped_count`, `error_count`, and `imported_at`.
- **Category Mappings Table**: Stores rules for auto-categorizing transactions with fields like `pattern`, `pattern_type`, `category_primary`, `category_secondary`, and `merchant_name`.
- **Recurring Bills Table**: Tracks expected recurring transactions with fields like `account_id`, `merchant_name`, `expected_amount`, `frequency`, and `expected_day`.

#### Integration Points
This file integrates with other parts of the Mythos system by defining the schema and initial data for the finance subsystem. It is used by other components such as transaction processors, import managers, and reporting tools to manage and query financial data.

### Detailed Breakdown

#### Accounts Table
- **Columns**: `id`, `bank_name`, `account_name`, `account_number`, `account_type`, `current_balance`, `is_active`, `notes`, `created_at`, `updated_at`
- **Indexes**: None directly defined, but can be queried efficiently.

#### Transactions Table
- **Columns**: `id`, `account_id`, `transaction_date`, `post_date`, `description`, `original_description`, `merchant_name`, `amount`, `balance`, `category_primary`, `category_secondary`, `transaction_type`, `is_pending`, `is_recurring`, `bank_transaction_id`, `hash_id`, `source_file`, `imported_by`, `notes`, `created_at`, `updated_at`
- **Indexes**: `idx_transactions_date`, `idx_transactions_account`, `idx_transactions_hash`, `idx_transactions_category`, `idx_transactions_merchant`

#### Import Logs Table
- **Columns**: `id`, `account_id`, `source_file`, `file_path`, `total_rows`, `imported_count`, `skipped_count`, `error_count`, `date_range_start`, `date_range_end`, `imported_by`, `imported_at`, `notes`

#### Category Mappings Table
- **Columns**: `id`, `pattern`, `pattern_type`, `category_primary`, `category_secondary`, `merchant_name`, `priority`, `is_active`, `created_at`
- **Indexes**: `idx_category_mappings_pattern`

#### Recurring Bills Table
- **Columns**: `id`, `account_id`, `merchant_name`, `expected_amount`, `amount_variance`, `frequency`, `expected_day`, `category_primary`, `is_active`, `notes`, `created_at`

### Default Data
- **Accounts**: Two default accounts are inserted with IDs 1 and 2.
- **Category Mappings**: A comprehensive set of mappings for various categories and merchants is inserted.

### Indexes
- **Transactions**: Indexes on `transaction_date`, `account_id`, `hash_id`, `category_primary`, and `merchant_name`.
- **Category Mappings**: Index on `pattern`.

This schema provides a robust foundation for managing financial transactions and related data within the Mythos system.
