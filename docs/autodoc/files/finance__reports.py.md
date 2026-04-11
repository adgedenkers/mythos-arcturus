# finance/reports.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 416

---

### File: finance/reports.py

#### Purpose
This file contains functions to generate various financial reports from the PostgreSQL database, including account summaries, monthly breakdowns, spending by category, top merchants, transaction searches, uncategorized transactions, and recurring transaction detection.

#### Architecture
The file is structured around several top-level functions, each responsible for a specific type of financial report. Each function connects to the PostgreSQL database, retrieves relevant data, formats it, and prints it in a tabular form. The `main` function uses `argparse` to parse command-line arguments and dispatches to the appropriate report function based on the provided command.

#### Patterns
- **Factory Method**: The `get_connection` function acts as a factory method to create a database connection.
- **Singleton**: The database connection is created and closed within each function, implying a singleton pattern for the connection lifecycle within each report generation.

#### Dependencies
- **Imports**: `argparse`, `os`, `sys`, `datetime`, `decimal`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL tables `accounts`, `transactions`, `import_logs`, `category_mappings`

#### Interfaces
- **Functions**: `get_connection`, `format_currency`, `print_table`, `cmd_summary`, `cmd_monthly`, `cmd_category`, `cmd_merchants`, `cmd_search`, `cmd_uncategorized`, `cmd_recurring`, `main`
- **Command-line Interface**: Uses `argparse` to handle command-line arguments and dispatch to the appropriate report function.

#### Database
- **Tables**: `accounts`, `transactions`, `import_logs`, `category_mappings`
- **Operations**: 
  - `cmd_summary`: Reads from `accounts`, `transactions`, `import_logs`
  - `cmd_monthly`: Reads from `transactions`
  - `cmd_category`: Reads from `transactions`
  - `cmd_merchants`: Reads from `transactions`
  - `cmd_search`: Reads from `transactions`
  - `cmd_uncategorized`: Reads from `transactions`
  - `cmd_recurring`: Reads from `transactions`

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` loaded from `.env` file.

#### Key Logic
- **get_connection**: Establishes a PostgreSQL database connection.
- **format_currency**: Converts a numeric amount into a formatted currency string.
- **print_table**: Formats and prints data in a tabular form.
- **cmd_summary**: Generates a comprehensive account summary including balances, recent transactions, and import history.
- **cmd_monthly**: Provides a monthly breakdown of income and expenses.
- **cmd_category**: Displays spending by category over a specified period.
- **cmd_merchants**: Lists top merchants based on spending.
- **cmd_search**: Searches transactions based on a given term.
- **cmd_uncategorized**: Lists uncategorized transactions.
- **cmd_recurring**: Detects recurring transactions based on frequency and variance.

#### Integration Points
- **Database Integration**: Uses `psycopg2` to interact with the PostgreSQL database.
- **Command-line Interface**: Uses `argparse` to handle command-line arguments and dispatch to the appropriate report function.
- **Environment Configuration**: Loads environment variables from `.env` to configure the database connection.

### Detailed Analysis of Functions

1. **get_connection**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Logic**: Uses `psycopg2.connect` with environment variables for database credentials and sets `RealDictCursor` as the cursor factory.

2. **format_currency**
   - **Purpose**: Formats a numeric amount into a currency string.
   - **Logic**: Checks if the amount is `None` and formats it accordingly.

3. **print_table**
   - **Purpose**: Prints a formatted table with headers and rows.
   - **Logic**: Calculates column widths, prints headers, and formats rows to align properly.

4. **cmd_summary**
   - **Purpose**: Generates a comprehensive account summary.
   - **Logic**: Retrieves and formats account balances, recent transactions, and import history.

5. **cmd_monthly**
   - **Purpose**: Provides a monthly breakdown of income and expenses.
   - **Logic**: Retrieves and formats monthly income and expenses over a specified period.

6. **cmd_category**
   - **Purpose**: Displays spending by category over a specified period.
   - **Logic**: Retrieves and formats spending by category, including total, count, and average amount.

7. **cmd_merchants**
   - **Purpose**: Lists top merchants based on spending.
   - **Logic**: Retrieves and formats top merchants based on total spending and transaction count.

8. **cmd_search**
   - **Purpose**: Searches transactions based on a given term.
   - **Logic**: Retrieves and formats transactions that match the search term.

9. **cmd_uncategorized**
   - **Purpose**: Lists uncategorized transactions.
   - **Logic**: Retrieves and formats uncategorized transactions.

10. **cmd_recurring**
    - **Purpose**: Detects recurring transactions based on frequency and variance.
    - **Logic**: Retrieves and formats transactions that meet the criteria for recurring transactions.

11. **main**
    - **Purpose**: Parses command-line arguments and dispatches to the appropriate report function.
    - **Logic**: Uses `argparse` to handle command-line arguments and calls the appropriate function based on the provided command.
