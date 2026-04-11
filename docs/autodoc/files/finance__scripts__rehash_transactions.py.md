# finance/scripts/rehash_transactions.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 190

---

### File: finance/scripts/rehash_transactions.py

#### Purpose
This script is designed to clean up and rehash transactions in the Mythos system. It removes duplicate transactions based on specific criteria and rehashes all transactions using a new deterministic hash algorithm. The script can be run in dry-run mode to simulate the process without making actual changes.

#### Architecture
The script consists of three main functions:
1. **`get_db_connection`**: Establishes a connection to the PostgreSQL database.
2. **`make_hash_v4`**: Generates a new hash for a transaction based on account ID, date, amount, and original description.
3. **`run`**: The main function that orchestrates the entire process of finding and removing duplicates, rehashing transactions, and providing final counts.

#### Patterns
- **Singleton Pattern**: The database connection is established once and reused throughout the script.
- **Command Pattern**: The script can be run in dry-run mode, which simulates the process without making changes.

#### Dependencies
- **`os`**: For environment variable access.
- **`sys`**: For command-line argument parsing.
- **`hashlib`**: For generating hash values.
- **`psycopg2`**: For PostgreSQL database interaction.
- **`dotenv`**: For loading environment variables from a `.env` file.

#### Interfaces
- The script is designed to be run from the command line and accepts a `--dry-run` flag.
- It exposes the `run` function, which can be called with a `dry_run` parameter to control whether changes are made.

#### Database
- **Tables**: 
  - `transactions`: Read and written to for finding duplicates, rehashing, and final counts.
  - `accounts`: Read for final counts.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in the `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Finding Duplicates**:
   - Queries the `transactions` table to find groups of transactions with the same account ID, transaction date, amount, and original description but different hash IDs.
   - Removes all but one transaction from each duplicate group.

2. **Rehashing Transactions**:
   - Iterates over all transactions, generating a new hash using the `make_hash_v4` function.
   - Updates the `hash_id` field for each transaction with the new hash.
   - Detects and handles conflicts where the new hash already exists for another transaction.

3. **Final Counts**:
   - Provides counts of transactions per account and the total number of transactions with unique hashes.

#### Integration Points
- **Database Integration**: The script interacts with the PostgreSQL database to read and write transaction data.
- **Environment Configuration**: The script reads environment variables from a `.env` file to configure the database connection.

### Detailed Analysis

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `os`, `psycopg2`.
- **Database**: Uses `psycopg2` to connect to the `transactions` and `accounts` tables.

#### `make_hash_v4`
- **Purpose**: Generates a new deterministic hash for a transaction based on account ID, date, amount, and original description.
- **Dependencies**: `hashlib`.
- **Key Logic**: Concatenates the input parameters and generates a SHA-256 hash, truncating it to 16 characters.

#### `run`
- **Purpose**: Orchestrates the entire process of finding and removing duplicates, rehashing transactions, and providing final counts.
- **Dependencies**: `get_db_connection`, `make_hash_v4`.
- **Database**: Reads and writes to the `transactions` table, reads from the `accounts` table.
- **Key Logic**:
  - **Step 1**: Finds and removes duplicate transactions.
  - **Step 2**: Rehashes all transactions and handles conflicts.
  - **Step 3**: Provides final counts and statistics.

### Example Usage
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/finance/scripts/rehash_transactions.py
/opt/mythos/.venv/bin/python3 /opt/mythos/finance/scripts/rehash_transactions.py --dry-run
```

This script is designed to be run once after deploying a specific patch but is idempotent and can be safely run multiple times.
