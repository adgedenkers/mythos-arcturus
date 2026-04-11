# finance/categorizer.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 273

---

### File: finance/categorizer.py

#### Purpose
This file contains the `Categorizer` class and related functions to categorize financial transactions based on predefined mappings stored in a PostgreSQL database. It provides methods to load mappings, categorize transactions, and re-categorize transactions in the database.

#### Architecture
- **Classes**: 
  - `Categorizer`: Manages transaction categorization logic.
- **Functions**:
  - `get_db_connection`: Establishes a connection to the PostgreSQL database.
  - `recategorize_db`: Re-categorizes transactions in the database.
  - `main`: Entry point for command-line interface to re-categorize transactions.

#### Patterns
- **Singleton**: The `Categorizer` class can be considered a singleton-like pattern as it loads mappings once and reuses them for categorization.
- **Factory**: The `get_db_connection` function acts as a factory method to create database connections.

#### Dependencies
- **Imports**: `os`, `sys`, `argparse`, `pathlib`, `dotenv`, `psycopg2`, `psycopg2.extras`
- **Database**: PostgreSQL

#### Interfaces
- **Public Methods**:
  - `Categorizer.__init__(conn=None)`: Initializes the `Categorizer` with an optional database connection.
  - `Categorizer.categorize(description, original_description=None)`: Categorizes a transaction based on its description.
  - `Categorizer.categorize_transaction(txn)`: Categorizes a transaction dictionary in-place.
  - `Categorizer.mapping_count`: Returns the number of loaded mappings.
- **Functions**:
  - `get_db_connection()`: Returns a database connection.
  - `recategorize_db(all_transactions=False, dry_run=False, verbose=False)`: Re-categorizes transactions in the database.
  - `main()`: Command-line interface entry point.

#### Database
- **Tables**:
  - `category_mappings`: Stores category mappings with patterns, types, and priorities.
  - `transactions`: Stores transaction data including descriptions and categories.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details.
- **Dotenv**: Loads environment variables from `.env` file.

#### Key Logic
- **Mapping Loading**:
  - `Categorizer._load_mappings(conn)`: Loads active mappings from the `category_mappings` table, sorted by priority and pattern length.
- **Transaction Categorization**:
  - `Categorizer.categorize(description, original_description)`: Matches transaction descriptions against loaded mappings to determine categories.
- **Database Re-categorization**:
  - `recategorize_db(all_transactions, dry_run, verbose)`: Retrieves transactions from the `transactions` table, categorizes them, and updates the database if not in dry-run mode.

#### Integration Points
- **Importer**: Used by `importer.py` to categorize transactions during import.
- **Telegram**: Used by Telegram bot commands to categorize transactions.
- **CLI**: Standalone command-line interface to re-categorize transactions in bulk.

### Detailed Documentation

#### Classes
- **Categorizer**
  - **Attributes**:
    - `mappings`: List of loaded category mappings.
  - **Methods**:
    - `__init__(self, conn=None)`: Initializes the `Categorizer` and loads mappings from the database.
    - `_load_mappings(self, conn=None)`: Loads mappings from the `category_mappings` table.
    - `categorize(self, description, original_description=None)`: Categorizes a transaction based on its description.
    - `categorize_transaction(self, txn)`: Categorizes a transaction dictionary in-place.
    - `mapping_count(self)`: Returns the number of loaded mappings.

#### Functions
- **get_db_connection()**
  - Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **recategorize_db(all_transactions=False, dry_run=False, verbose=False)**
  - Retrieves transactions from the `transactions` table, categorizes them using the `Categorizer`, and updates the database if not in dry-run mode.
- **main()**
  - Command-line interface entry point to re-categorize transactions using `recategorize_db`.

#### Usage
- **As a Module**:
  ```python
  from categorizer import Categorizer
  cat = Categorizer()
  category, merchant = cat.categorize("STEWART'S SHOP")
  ```
- **Standalone CLI**:
  ```bash
  python categorizer.py
  python categorizer.py --all  # re-categorize everything
  python categorizer.py --dry-run
  ```

This file is a critical component of the Mythos system, providing robust transaction categorization capabilities that integrate seamlessly with the PostgreSQL database and other subsystems.
