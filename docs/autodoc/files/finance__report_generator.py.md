# finance/report_generator.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 300

---

### Purpose
The `report_generator.py` file is responsible for generating a detailed HTML financial report for a specified number of months. The report includes recurring bills, spending breakdown by category, and income/expense totals.

### Architecture
The file consists of several functions and a custom JSON encoder class:
- **Classes**: 
  - `DecimalEncoder`: A custom JSON encoder to handle `Decimal` and `datetime` types.
- **Functions**:
  - `get_db_connection`: Establishes a connection to the PostgreSQL database.
  - `get_current_balances`: Retrieves current account balances.
  - `get_recurring_bills`: Retrieves all active recurring bills.
  - `match_bill_to_transactions`: Matches a recurring bill to a transaction within a specified month.
  - `build_month_data`: Builds complete data for one month, including bills and category breakdowns.
  - `generate_report`: Generates the full HTML report.
  - `main`: Entry point for the script, handling command-line arguments.

### Patterns
- **Factory Method**: The `get_db_connection` function acts as a factory method to create a database connection.
- **Singleton**: The `DecimalEncoder` class can be considered a singleton as it is used to encode JSON data consistently throughout the report generation process.

### Dependencies
- **Imports**: 
  - `os`, `sys`, `json`, `argparse`, `datetime`, `decimal`, `calendar`, `pathlib`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL tables (`accounts`, `transactions`, `recurring_bills`)

### Interfaces
- **Exposed Functions**: 
  - `generate_report`: Generates the full HTML report.
  - `main`: Entry point for the script, handling command-line arguments.

### Database
- **Tables/Labels**: 
  - `accounts`: Used to retrieve account balances.
  - `transactions`: Used to retrieve transaction data.
  - `recurring_bills`: Used to retrieve recurring bill data.

### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` (loaded from `.env` file)
- **Constants**: 
  - `TEMPLATE_PATH`: Path to the HTML template.
  - `DEFAULT_OUTPUT`: Default output directory for the report.

### Key Logic
- **get_current_balances**: Retrieves account balances by querying the `accounts` and `transactions` tables.
- **get_recurring_bills**: Retrieves recurring bills by querying the `recurring_bills` and `accounts` tables.
- **match_bill_to_transactions**: Matches a recurring bill to a transaction within a specified month by comparing merchant names and transaction descriptions.
- **build_month_data**: Aggregates data for one month, including bills and category breakdowns.
- **generate_report**: Orchestrates the report generation process by fetching data, building month data, and rendering the HTML template.

### Integration Points
- **Database**: Connects to PostgreSQL to fetch account balances, transactions, and recurring bills.
- **Environment**: Uses environment variables for database connection details.
- **File System**: Reads the HTML template and writes the generated report to the file system.

### Detailed Analysis

#### `DecimalEncoder`
- **Purpose**: Custom JSON encoder to handle `Decimal` and `datetime` types.
- **Methods**: 
  - `default`: Encodes `Decimal` and `datetime` objects to JSON-compatible formats.

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses environment variables to configure the connection.

#### `get_current_balances`
- **Purpose**: Retrieves current account balances.
- **Logic**: Queries the `accounts` and `transactions` tables to get the latest balances for active accounts.

#### `get_recurring_bills`
- **Purpose**: Retrieves all active recurring bills.
- **Logic**: Queries the `recurring_bills` and `accounts` tables to get active recurring bills.

#### `match_bill_to_transactions`
- **Purpose**: Matches a recurring bill to a transaction within a specified month.
- **Logic**: Compares merchant names and transaction descriptions to find a match.

#### `build_month_data`
- **Purpose**: Builds complete data for one month, including bills and category breakdowns.
- **Logic**: Aggregates transaction data, matches bills, and categorizes transactions.

#### `generate_report`
- **Purpose**: Generates the full HTML report.
- **Logic**: Fetches data, builds month data, and renders the HTML template with the aggregated data.

#### `main`
- **Purpose**: Entry point for the script, handling command-line arguments.
- **Logic**: Parses command-line arguments and calls `generate_report` with the specified parameters.

This file is a critical component of the Mythos system, responsible for generating comprehensive financial reports based on data from the PostgreSQL database.
