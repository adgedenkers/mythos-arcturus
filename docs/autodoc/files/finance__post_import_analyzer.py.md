# finance/post_import_analyzer.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 340

---

### File: finance/post_import_analyzer.py

#### Purpose
This file contains the `PostImportAnalyzer` class, which analyzes newly imported financial transactions, generates a comprehensive report, and sends the report via Telegram.

#### Architecture
The `PostImportAnalyzer` class is designed to handle the entire process of analyzing imported transactions, formatting the report, and sending it via Telegram. It includes methods for initializing the database connection, analyzing the imported transactions, formatting the report as Telegram HTML, sending the report, and closing the database connection.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function ensures a single database connection is established and reused.
- **Factory Method**: The `PostImportAnalyzer` class acts as a factory for creating and sending reports.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `logging`, `argparse`, `subprocess`, `datetime`, `decimal`, `pathlib`, `dotenv`
- **External Libraries**: `psycopg2` for PostgreSQL database interactions
- **Internal Modules**: `bill_matcher` for bill matching logic

#### Interfaces
- **Public Methods**:
  - `analyze_import`: Analyzes imported transactions and builds a report.
  - `format_telegram_html`: Formats the report as Telegram HTML.
  - `send_telegram_report`: Sends the formatted report via Telegram.
  - `close`: Closes the database connection.
- **Top-level Functions**:
  - `get_db_connection`: Establishes a PostgreSQL database connection.
  - `main`: Entry point for command-line usage.

#### Database
- **PostgreSQL Tables**:
  - `transactions`: Stores transaction data.
  - `accounts`: Stores account information.
  - `patch`: Likely used for tracking patches or updates.
  - `post_import_analyzer`: Likely a table for storing analysis results or metadata.
  - `bill_matcher`: Likely a table for storing bill matching data.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details.
  - `TELEGRAM_ID_KA`, `TELEGRAM_ID_SERAPHE`: Telegram user IDs for sending notifications.
- **Configuration Files**:
  - `.env`: Loaded using `dotenv` for environment variables.

#### Key Logic
- **Transaction Analysis**:
  - Retrieves the most recent transactions from the `transactions` table.
  - Filters and categorizes transactions.
  - Matches transactions against recurring bills using the `BillMatcher` class.
- **Report Generation**:
  - Summarizes transaction counts, categorizations, and bill matches.
  - Formats the report into a structured HTML message for Telegram.
- **Telegram Notification**:
  - Sends the formatted report via a Telegram bot script.

#### Integration Points
- **Database Integration**:
  - Connects to PostgreSQL to retrieve and analyze transaction data.
- **Bill Matching Integration**:
  - Uses the `BillMatcher` class to match transactions against recurring bills.
- **Telegram Integration**:
  - Sends the report via a Telegram bot script located at `/opt/mythos/telegram_bot/send_notification.py`.

### Detailed Documentation

#### Class: `PostImportAnalyzer`
- **Methods**:
  - `__init__`: Initializes the database connection.
  - `analyze_import`: Analyzes imported transactions and builds a report.
  - `format_telegram_html`: Formats the report as Telegram HTML.
  - `send_telegram_report`: Sends the formatted report via Telegram.
  - `_send_telegram`: Sends a message via the Telegram notification script.
  - `close`: Closes the database connection.

#### Top-level Functions
- `get_db_connection`: Establishes a PostgreSQL database connection.
- `main`: Entry point for command-line usage, allowing re-analysis of recent imports or running bill matching.

#### Key Business Logic
- **Transaction Retrieval and Filtering**:
  - Retrieves the most recent transactions from the `transactions` table.
  - Filters out skipped transactions to focus on newly imported ones.
- **Bill Matching**:
  - Uses the `BillMatcher` class to match transactions against recurring bills.
- **Category Summary**:
  - Aggregates transactions by category, calculating counts and totals.
- **Telegram Report Formatting**:
  - Formats the report into a structured HTML message, including transaction counts, bill matches, category summaries, and uncategorized transactions.
- **Telegram Notification**:
  - Sends the formatted report via a Telegram bot script, handling exceptions and logging errors.

This file is a critical component of the Mythos system, ensuring that newly imported financial transactions are analyzed, summarized, and reported in a timely and structured manner.
