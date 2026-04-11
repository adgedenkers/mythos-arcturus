# finance/scripts/backfill_balances.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 173

---

### Documentation for `finance/scripts/backfill_balances.py`

#### Purpose
This script is designed to backfill NULL balances for transactions in the Mythos finance system. It identifies transactions with missing balance fields and calculates the correct balance by walking forward from the last known balance for each account.

#### Architecture
The script consists of several functions:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `backfill_account`: Backfills NULL balances for a single account by walking forward from the last known balance.
- `backfill_all`: Backfills NULL balances across all active accounts.
- `main`: Entry point for the script, which parses command-line arguments and calls `backfill_all`.

#### Patterns
- **Singleton Pattern**: The database connection is established once and reused.
- **Command Line Interface (CLI)**: Uses `argparse` to handle command-line arguments.

#### Dependencies
- `os`: For environment variable access.
- `sys`: For system-specific parameters and functions.
- `argparse`: For parsing command-line arguments.
- `logging`: For logging messages.
- `psycopg2`: For PostgreSQL database interactions.
- `decimal`: For precise decimal arithmetic.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- **Command-line Interface**: The script can be run from the command line with options like `--dry-run`.
- **Database Interface**: Interacts with PostgreSQL to read and write transaction and account data.

#### Database
- **Tables**:
  - `transactions`: Contains transaction data, including balance fields.
  - `accounts`: Contains account data, including current balance.

#### Configuration
- **Environment Variables**: The script reads PostgreSQL connection details from environment variables loaded via `dotenv`.
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **Backfilling Balances**:
  1. **Finding the Anchor**: The script identifies the last transaction with a non-NULL balance for each account.
  2. **Walking Forward**: It then processes all subsequent transactions, calculating the running balance.
  3. **Updating Balances**: It updates any NULL balance fields with the calculated balance.
  4. **Updating Account Balance**: Finally, it updates the `current_balance` field in the `accounts` table with the final calculated balance.

#### Integration Points
- **Database Connection**: The script establishes a connection to the PostgreSQL database to read and write transaction and account data.
- **Logging**: Uses the Python `logging` module to log informational and warning messages.
- **Command-line Interface**: Integrates with the command-line interface to accept user input and provide feedback.

### Detailed Analysis

#### `get_db`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses `psycopg2.connect` with environment variables for database credentials and sets `RealDictCursor` as the cursor factory.

#### `backfill_account`
- **Purpose**: Backfills NULL balances for a single account.
- **Logic**:
  1. Finds the last transaction with a non-NULL balance (the anchor).
  2. Retrieves all transactions after the anchor, ordered by date and ID.
  3. Walks forward, calculating the running balance.
  4. Updates any NULL balance fields.
  5. Updates the `current_balance` field in the `accounts` table.

#### `backfill_all`
- **Purpose**: Backfills NULL balances across all active accounts.
- **Logic**:
  1. Retrieves active accounts with NULL balances.
  2. Calls `backfill_account` for each account.
  3. Commits changes to the database if not in dry-run mode.

#### `main`
- **Purpose**: Entry point for the script.
- **Logic**:
  1. Parses command-line arguments.
  2. Sets up logging.
  3. Calls `backfill_all` with the `dry_run` flag based on command-line input.

This script ensures that transaction balances are accurately calculated and updated, maintaining data integrity in the Mythos finance system.
