# finance/weekly_review.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 563

---

### File: finance/weekly_review.py

#### Purpose
This file contains functions to generate a comprehensive weekly financial review, including account balances, transactions, spending by category, income, bills, and large transactions. It also calculates the financial runway based on current balances and spending patterns.

#### Architecture
The file is organized into several top-level functions and a custom JSON encoder class `DecimalEncoder`. The functions are designed to fetch specific financial data from a PostgreSQL database and perform calculations to generate a detailed financial review. The `DecimalEncoder` class is used to handle `Decimal` and `datetime` objects when converting data to JSON.

#### Patterns
- **Custom JSON Encoder**: The `DecimalEncoder` class extends `json.JSONEncoder` to handle `Decimal` and `datetime` objects.
- **Database Connection**: The `get_connection` function uses environment variables to establish a connection to the PostgreSQL database.

#### Dependencies
- `argparse`: For command-line argument parsing.
- `json`: For JSON encoding.
- `sys`: For system-specific parameters and functions.
- `psycopg2`: For PostgreSQL database interaction.
- `psycopg2.extras`: For additional PostgreSQL-specific features.
- `os`: For interacting with the operating system.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- **Top-level Functions**:
  - `get_connection()`: Establishes a connection to the PostgreSQL database.
  - `get_week_bounds(start_date)`: Returns the start and end dates for the review week.
  - `get_month_bounds()`: Returns the start and end dates for the current month.
  - `fetch_account_balances(cur)`: Fetches current balances across all active accounts.
  - `fetch_week_transactions(cur, week_start, week_end)`: Fetches all transactions for the review week.
  - `fetch_week_spending_by_category(cur, week_start, week_end)`: Fetches spending grouped by category for the week.
  - `fetch_month_spending_by_category(cur, month_start, month_end)`: Fetches spending grouped by category for the full month so far.
  - `fetch_income_this_month(cur, month_start)`: Fetches income received so far this month.
  - `fetch_expected_income(cur)`: Fetches expected monthly income from recurring income sources.
  - `fetch_bills_status(cur, month_start)`: Fetches bills due this month and their payment status.
  - `fetch_large_transactions(cur, week_start, week_end, threshold)`: Fetches transactions over a specified threshold.
  - `fetch_cash_withdrawals(cur, month_start)`: Fetches cash withdrawals this month.
  - `fetch_fast_food_spending(cur, month_start)`: Fetches fast food spending this month.
  - `calculate_runway(balances, bills_remaining, daily_avg_discretionary)`: Calculates the financial runway.
  - `generate_review(week_start_str)`: Generates the complete weekly financial review.
  - `print_terminal_review(review)`: Prints a clean terminal-friendly review.

#### Database
- **Tables Referenced**:
  - `accounts`: For fetching account balances and details.
  - `transactions`: For fetching transactions, spending by category, income, and large transactions.
  - `recurring_income`: For fetching expected monthly income.
  - `recurring_bills`: For fetching bills due this month.
  - `bill_overrides`: For fetching bill payment overrides.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details loaded from `/opt/mythos/.env`.

#### Key Logic
- **Account Balances**: Fetches and aggregates balances for different account types.
- **Weekly Transactions**: Fetches all transactions within the specified week.
- **Spending by Category**: Aggregates spending by category for both the week and the month.
- **Income**: Fetches income received so far this month.
- **Expected Income**: Fetches expected monthly income from recurring income sources.
- **Bills Status**: Fetches and categorizes bills due this month into paid, upcoming, and overdue.
- **Large Transactions**: Fetches transactions over a specified threshold.
- **Cash Withdrawals**: Fetches cash withdrawals this month.
- **Fast Food Spending**: Fetches fast food spending this month.
- **Runway Calculation**: Calculates the financial runway based on current balances and spending patterns.

#### Integration Points
- **Database Integration**: Connects to the PostgreSQL database to fetch financial data.
- **Command-line Interface**: Parses command-line arguments to generate the review for a specific week or in JSON format.
- **JSON Encoding**: Uses the `DecimalEncoder` class to handle `Decimal` and `datetime` objects when converting data to JSON.
- **Terminal Output**: Provides a clean terminal-friendly output for the weekly review.

This file is a critical component of the Mythos system, providing a structured financial review that helps in decision-making based on current financial status and trends.
