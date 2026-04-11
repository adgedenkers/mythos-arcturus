# finance/scripts/reimport_account.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 472

---

### File: finance/scripts/reimport_account.py

#### Purpose
This script is designed to reimport financial transactions for a specified account from a CSV file into the Mythos system. It supports parsing CSV files from USAA and Sunmark, verifies the calculated running balances against the bank-provided balances, and updates the account's transactions in the database.

#### Architecture
The script consists of several top-level functions:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `compute_hash`: Generates a hash for deduplication.
- `parse_usaa_csv`: Parses a USAA CSV file and returns a list of transaction rows.
- `parse_sunmark_csv`: Parses a Sunmark CSV file and returns a list of transaction rows.
- `verify_balances`: Verifies the calculated running balances against the bank-provided balances.
- `reimport_account`: Orchestrates the full reimport process for an account.
- `main`: Entry point for the script, parses command-line arguments and calls `reimport_account`.

#### Patterns
- **Factory Pattern**: The `reimport_account` function uses a factory-like approach to select the appropriate CSV parser based on the account type.
- **Singleton Pattern**: The `get_db` function could be considered a singleton as it establishes a database connection that could be reused.

#### Dependencies
- `os`, `sys`, `csv`, `hashlib`, `argparse`, `logging`, `datetime`, `decimal`, `pathlib`, `dotenv`, `psycopg2`, `categorizer`

#### Interfaces
- The script exposes a command-line interface via the `main` function, which accepts arguments for the account type, CSV file path, and optional flags for dry run and no-wipe modes.
- The `reimport_account` function is the primary interface for the reimport process, accepting parameters for account key, CSV path, dry run, and no-wipe.

#### Database
- The script interacts with the PostgreSQL database to:
  - Retrieve and update account information.
  - Insert new transactions.
  - Verify balances against existing transactions.

#### Configuration
- The script uses environment variables loaded via `dotenv` for database connection details.
- Configuration files: `.env` located at `/opt/mythos/.env`.

#### Key Logic
- **CSV Parsing**: The script parses CSV files from USAA and Sunmark, handling different formats and extracting relevant transaction details.
- **Balance Verification**: The `verify_balances` function ensures that the calculated running balances match the bank-provided balances, allowing for a small rounding tolerance.
- **Transaction Deduplication**: The `compute_hash` function generates a unique hash for each transaction to prevent duplicates during reimport.

#### Integration Points
- **Database Integration**: The script connects to the PostgreSQL database to retrieve account information and insert new transactions.
- **Categorizer Integration**: The script uses the `categorizer` module to categorize transactions after parsing the CSV.
- **Command-Line Interface**: The script integrates with the command-line interface to accept user input and provide feedback on the reimport process.

### Detailed Documentation

#### Functions

1. **get_db**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Dependencies**: `psycopg2`, `os`
   - **Database**: Connects to the PostgreSQL database using environment variables.

2. **compute_hash**
   - **Purpose**: Generates a deduplication hash for a transaction.
   - **Arguments**: `account_id`, `date_str`, `amount`, `description`
   - **Dependencies**: `hashlib`

3. **parse_usaa_csv**
   - **Purpose**: Parses a USAA CSV file and returns a list of transaction rows.
   - **Arguments**: `file_path`
   - **Dependencies**: `csv`, `datetime`, `decimal`
   - **Key Logic**: Skips pending transactions, parses date and amount, and generates a hash for each transaction.

4. **parse_sunmark_csv**
   - **Purpose**: Parses a Sunmark CSV file and returns a list of transaction rows.
   - **Arguments**: `file_path`
   - **Dependencies**: `csv`, `datetime`, `decimal`
   - **Key Logic**: Handles different date formats, parses debit and credit amounts, and generates a hash for each transaction.

5. **verify_balances**
   - **Purpose**: Verifies that the calculated running balances match the bank-provided balances.
   - **Arguments**: `rows`, `account_name`
   - **Dependencies**: `decimal`
   - **Key Logic**: Walks through the transactions to calculate running balances and compares them with the bank-provided balances.

6. **reimport_account**
   - **Purpose**: Orchestrates the full reimport process for an account.
   - **Arguments**: `account_key`, `csv_path`, `dry_run`, `no_wipe`
   - **Dependencies**: `ACCOUNT_MAP`, `parse_usaa_csv`, `parse_sunmark_csv`, `verify_balances`, `categorizer`
   - **Key Logic**: Selects the appropriate CSV parser, verifies balances, and categorizes transactions.

7. **main**
   - **Purpose**: Entry point for the script, parses command-line arguments and calls `reimport_account`.
   - **Dependencies**: `argparse`, `sys`

### Example Usage
```sh
reimport-account usaa ~/Downloads/usaa-archive.csv
reimport-account sunmark ~/Downloads/sunmark-archive.CSV --dry-run
```

This script is a critical component of the Mythos system, ensuring that financial transactions are accurately imported and verified, maintaining the integrity of the financial data within the system.
