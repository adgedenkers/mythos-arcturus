# finance/update_sunmark_descriptions.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 131

---

### File: finance/update_sunmark_descriptions.py

#### Purpose
This file contains a script to update the descriptions and merchant names of existing Sunmark transactions in the PostgreSQL database using new cleaning logic. It can operate in dry-run mode to preview changes without applying them.

#### Architecture
The file consists of two main functions:
1. `update_descriptions(dry_run: bool = False)`: This function handles the core logic of fetching transactions, applying the new cleaning logic, and updating the database.
2. `main()`: This function parses command-line arguments and calls `update_descriptions` with the appropriate parameters.

The script uses the `argparse` module to handle command-line arguments and the `psycopg2` module to interact with the PostgreSQL database. It also imports the `SunmarkParser` class from the `parsers` module to apply the new cleaning logic.

#### Patterns
- **Singleton Pattern**: The database connection is established once and reused throughout the function.
- **Command Line Interface (CLI) Pattern**: The script uses `argparse` to handle command-line arguments.

#### Dependencies
- `argparse`: For parsing command-line arguments.
- `os`: For accessing environment variables.
- `sys`: For system-specific parameters and functions.
- `psycopg2`: For PostgreSQL database interaction.
- `dotenv`: For loading environment variables from a `.env` file.
- `parsers.SunmarkParser`: For the cleaning logic.

#### Interfaces
- `update_descriptions(dry_run: bool = False)`: Exposes the core logic for updating transaction descriptions.
- `main()`: Entry point for the script, which parses command-line arguments and calls `update_descriptions`.

#### Database
- **Tables**: `transactions`
- **Operations**: 
  - **Read**: Fetches transactions with `account_id = 1` from the `transactions` table.
  - **Write**: Updates the `description` and `merchant_name` fields in the `transactions` table.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`
- **Dotenv File**: `/opt/mythos/.env`

#### Key Logic
1. **Fetching Transactions**: The script fetches all Sunmark transactions (`account_id = 1`) from the `transactions` table.
2. **Cleaning Logic**: Uses the `SunmarkParser` class to apply new cleaning logic to the `original_description` field.
3. **Dry Run Mode**: If `dry_run` is `True`, the script only prints the changes without updating the database.
4. **Updating Transactions**: If `dry_run` is `False`, the script updates the `description` and `merchant_name` fields in the `transactions` table.

#### Integration Points
- **Parsers Module**: The script uses the `SunmarkParser` class from the `parsers` module to apply the new cleaning logic.
- **Database Connection**: The script connects to the PostgreSQL database using environment variables and the `psycopg2` module.

### Detailed Breakdown

#### `update_descriptions(dry_run: bool = False)`
- **Purpose**: Updates the descriptions and merchant names of Sunmark transactions.
- **Flow**:
  1. Connects to the PostgreSQL database.
  2. Fetches all Sunmark transactions (`account_id = 1`).
  3. Applies the new cleaning logic to each transaction's `original_description`.
  4. If `dry_run` is `True`, prints the changes.
  5. If `dry_run` is `False`, updates the `description` and `merchant_name` fields in the database.
- **Database Operations**:
  - **Read**: `SELECT id, original_description, description, merchant_name FROM transactions WHERE account_id = 1 ORDER BY transaction_date DESC`
  - **Write**: `UPDATE transactions SET description = %s, merchant_name = COALESCE(%s, merchant_name), updated_at = CURRENT_TIMESTAMP WHERE id = %s`

#### `main()`
- **Purpose**: Entry point for the script, handles command-line arguments.
- **Flow**:
  1. Parses command-line arguments using `argparse`.
  2. Calls `update_descriptions` with the `dry_run` argument based on the command-line input.

### Example Usage
```sh
python update_sunmark_descriptions.py --dry-run
```
This command runs the script in dry-run mode, previewing the changes without applying them to the database.
