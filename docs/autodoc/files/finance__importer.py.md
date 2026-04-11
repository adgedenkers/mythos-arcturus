# finance/importer.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 868

---

### File: finance/importer.py

#### Purpose
This file contains the logic for importing financial transactions from CSV files exported by Sunmark and USAA banks into a PostgreSQL database. It includes parsers for each bank's CSV format, deduplication logic, and transaction import functionality.

#### Architecture
The file is structured around three main classes:
- `SunmarkParser`: Parses Sunmark CSV files and deduplicates transactions based on transaction numbers.
- `USAAParser`: Parses USAA CSV files and detects overlaps based on transaction details.
- `Importer`: Manages the database connection, transaction import, and balance updates.

Additionally, there are several top-level functions for utility tasks such as hashing file contents, parsing dates and decimals, and cleaning transaction descriptions.

#### Patterns
- **Factory Method**: The `Importer` class uses factory methods to instantiate the appropriate parser based on the bank type.
- **Singleton**: The `get_db_connection` function can be considered a singleton as it returns a single database connection instance.

#### Dependencies
- `os`, `sys`, `csv`, `hashlib`, `argparse`, `shutil`, `re`, `psycopg2`: Standard Python libraries for file handling, argument parsing, hashing, and database connection.
- `dotenv`: For loading environment variables.
- `categorizer`: For categorizing transactions (not fully implemented in the provided code).

#### Interfaces
- `SunmarkParser` and `USAAParser` expose `parse` and `get_current_balance` methods.
- `Importer` exposes methods for connecting to the database, importing transactions, updating account balances, and logging imports.
- Top-level functions such as `hash_file_contents`, `make_hash`, `parse_decimal`, `parse_date`, `clean_description_sunmark`, and `clean_description_usaa` are used for utility tasks.

#### Database
- **Tables**: `transactions`, `accounts`, `import_logs`.
- **Labels**: None (since this is a PostgreSQL-based system, no Neo4j labels are involved).

#### Configuration
- Environment variables: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- Constants: `ACCOUNT_IDS`, `ARCHIVE_DIR`.

#### Key Logic
- **Deduplication**:
  - `SunmarkParser`: Deduplicates transactions based on unique transaction numbers.
  - `USAAParser`: Detects overlaps by counting occurrences of transaction details in the file and database.
- **Transaction Parsing**:
  - `SunmarkParser.parse`: Parses CSV lines, cleans descriptions, and constructs transaction dictionaries.
  - `USAAParser.parse`: Parses CSV lines, cleans descriptions, and constructs transaction dictionaries.
- **Import Logic**:
  - `Importer.import_transactions`: Imports new transactions into the database, ensuring deduplication.
  - `Importer.update_account_balance`: Updates the account balance based on the imported transactions.
  - `Importer.log_import`: Logs the import process and file details.

#### Integration Points
- **Database**: Connects to PostgreSQL to insert transactions, update account balances, and log imports.
- **File System**: Reads CSV files and archives processed files.
- **Environment Variables**: Uses environment variables for database connection details.

### Detailed Documentation

#### Classes

1. **SunmarkParser**
   - **Purpose**: Parses Sunmark CSV exports and deduplicates transactions based on transaction numbers.
   - **Methods**:
     - `__init__`: Initializes the parser with the file path and account ID.
     - `parse`: Parses the CSV file and returns a list of transaction dictionaries.
     - `get_current_balance`: Returns the current balance from the parsed transactions.

2. **USAAParser**
   - **Purpose**: Parses USAA CSV exports and detects overlaps based on transaction details.
   - **Methods**:
     - `__init__`: Initializes the parser with the file path, account ID, and known balance.
     - `parse`: Parses the CSV file and returns a list of transaction dictionaries.
     - `get_current_balance`: Returns the current balance from the parsed transactions.

3. **Importer**
   - **Purpose**: Manages the database connection, transaction import, and balance updates.
   - **Methods**:
     - `__init__`: Initializes the importer with dry-run and verbose flags.
     - `connect`: Establishes a database connection.
     - `close`: Closes the database connection.
     - `_find_new_usaa_transactions`: Detects new USAA transactions based on overlap.
     - `_find_new_sunmark_transactions`: Detects new Sunmark transactions based on transaction numbers.
     - `import_transactions`: Imports new transactions into the database.
     - `update_account_balance`: Updates the account balance.
     - `log_import`: Logs the import process.

#### Top-Level Functions

1. **get_db_connection**
   - **Purpose**: Returns a database connection using psycopg2.
   - **Dependencies**: `psycopg2`, `os.getenv`.

2. **hash_file_contents**
   - **Purpose**: Generates a SHA256 hash of a file's contents for exact re-import detection.
   - **Arguments**: `filepath`.

3. **make_hash**
   - **Purpose**: Creates a hash for transaction details, including a sequence number.
   - **Arguments**: `account_id`, `date_str`, `amount`, `original_description`, `sequence`.

4. **parse_decimal**
   - **Purpose**: Converts a string to a Decimal, handling invalid formats.
   - **Arguments**: `value`.

5. **parse_date**
   - **Purpose**: Converts a date string to a standardized format.
   - **Arguments**: `date_str`.

6. **clean_description_sunmark**
   - **Purpose**: Cleans and standardizes Sunmark transaction descriptions.
   - **Arguments**: `description`, `memo`.

7. **clean_description_usaa**
   - **Purpose**: Cleans and standardizes USAA transaction descriptions.
   - **Arguments**: `description`, `original_desc`.

8. **archive_file**
   - **Purpose**: Archives a processed file.
   - **Arguments**: `filepath`, `bank`.

9. **recalc_balances**
   - **Purpose**: Recalculates running balances for all transactions of an account.
   - **Arguments**: `conn`, `account_id`, `anchor`, `verbose`.

10. **main**
    - **Purpose**: Entry point for the script, handling command-line arguments and invoking the import process.

### Usage
The script can be invoked from the command line to import transactions from CSV files:
```bash
python importer.py sunmark /path/to/file.CSV
python importer.py usaa /path/to/file.csv --balance 1243.19
python importer.py usaa /path/to/file.csv --balance 1243.19 --dry-run
python importer.py sunmark /path/to/file.CSV --dry-run
```

### Conclusion
This file provides a robust mechanism for importing financial transactions from CSV files into a PostgreSQL database, with deduplication and overlap detection tailored to the specific formats of Sunmark and USAA banks. The architecture is modular and well-structured, making it easy to extend or modify for other bank formats or additional features.
