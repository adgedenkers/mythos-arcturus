# finance/scripts/manual_transaction_import.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 82

---

### File: `finance/scripts/manual_transaction_import.py`

#### Purpose
This script imports transaction data from a CSV file into the PostgreSQL `transactions` table, ensuring that duplicate transactions are not inserted by using a hash-based uniqueness check.

#### Architecture
The script consists of two primary functions:
1. `compute_hash(row)`: Computes a unique hash for a transaction row based on its date, amount, description, and account ID.
2. `import_csv(csv_path, account_id, source_file, imported_by)`: Reads a CSV file, computes hashes for each transaction, and inserts new transactions into the PostgreSQL `transactions` table.

#### Patterns
- **No explicit design patterns**: The script is a straightforward procedural implementation without any design patterns like factory, singleton, or observer.

#### Dependencies
- **Python Standard Libraries**: `csv`, `hashlib`, `sys`, `datetime`, `pathlib`
- **External Libraries**: `psycopg2` for PostgreSQL database operations

#### Interfaces
- **Functions**:
  - `compute_hash(row)`: Computes a unique hash for a transaction row.
  - `import_csv(csv_path, account_id, source_file, imported_by)`: Imports transaction data from a CSV file into the PostgreSQL database.

#### Database
- **PostgreSQL Tables**:
  - `transactions`: Reads existing transactions to check for duplicates and inserts new transactions.

#### Configuration
- **Environment Variables**: None
- **Configuration**: `DB_CONFIG` dictionary containing database connection details.

#### Key Logic
1. **Hash Computation**: A unique hash is computed for each transaction to ensure uniqueness.
2. **CSV Parsing**: The script reads a CSV file using `csv.DictReader` and processes each row.
3. **Database Operations**:
   - Connects to the PostgreSQL database using `psycopg2`.
   - Checks for existing transactions by comparing hashes.
   - Inserts new transactions into the `transactions` table.

#### Integration Points
- **Database Integration**: The script interacts with the PostgreSQL database to read existing transactions and insert new ones.
- **Command Line Interface**: The script can be executed from the command line, taking CSV file path, account ID, and source file name as arguments.

### Detailed Documentation

#### `compute_hash(row)`
- **Purpose**: Computes a unique hash for a transaction based on its date, amount, description, and account ID.
- **Parameters**:
  - `row`: A dictionary containing transaction details.
- **Logic**:
  - Constructs a key string from the transaction details.
  - Uses `hashlib.sha256` to compute the hash of the key string.

#### `import_csv(csv_path, account_id, source_file, imported_by)`
- **Purpose**: Imports transaction data from a CSV file into the PostgreSQL `transactions` table, ensuring no duplicates.
- **Parameters**:
  - `csv_path`: Path to the CSV file containing transaction data.
  - `account_id`: ID of the account to which the transactions belong.
  - `source_file`: Name of the source file from which the transactions are imported.
  - `imported_by`: Identifier for the user or system importing the transactions (default is "manual").
- **Logic**:
  - Connects to the PostgreSQL database using `psycopg2`.
  - Reads the CSV file using `csv.DictReader`.
  - Computes a hash for each transaction to ensure uniqueness.
  - Checks for existing transactions with the same hash.
  - Inserts new transactions into the `transactions` table.
  - Commits the transaction and closes the database connection.

#### Command Line Execution
- **Usage**: The script can be executed from the command line with the following arguments:
  - `<csv_file>`: Path to the CSV file.
  - `<account_id>`: ID of the account.
  - `<source_file_name>`: Name of the source file.

#### Example Command
```bash
python manual_transaction_import.py /path/to/transactions.csv 12345 source_file.csv
```

This script is a critical component of the Mythos system for manually importing transaction data into the PostgreSQL database, ensuring data integrity through hash-based uniqueness checks.
