# telegram_bot/handlers/finance_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 1144

---

### File: `telegram_bot/handlers/finance_handler.py`

#### Purpose
This file contains the handlers for various financial commands in the Mythos Telegram bot, such as `/balance`, `/finance`, `/spending`, `/report`, and `/setbalance`. These handlers interact with the PostgreSQL database to retrieve financial data and format it for display in Telegram messages.

#### Architecture
The file consists of several top-level functions, each handling a specific command. Each function is designed to:
1. Establish a database connection.
2. Execute SQL queries to retrieve relevant financial data.
3. Format the retrieved data into a human-readable format.
4. Send the formatted data back to the user via Telegram.

The functions are asynchronous (`async def`) to handle the I/O operations efficiently.

#### Patterns
- **Singleton**: The database connection is established using a function (`get_db_connection`) that can be considered a singleton pattern, as it ensures a single connection is used for each query.
- **Factory**: The `format_currency` and `fmt_right` functions can be seen as simple factory methods that produce formatted currency strings.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `decimal`, `telegram`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL tables (`accounts`, `transactions`, `recurring_bills`, `recurring_income`)

#### Interfaces
- **Telegram Bot API**: The functions interact with the Telegram bot API via `Update` and `ContextTypes.DEFAULT_TYPE` to receive and send messages.
- **Database**: The functions interact with the PostgreSQL database to retrieve financial data.

#### Database
- **Tables**: `accounts`, `transactions`, `recurring_bills`, `recurring_income`
- **Queries**: The file contains multiple SQL queries to retrieve balances, spending data, and financial summaries.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **Balance Command**: Retrieves and formats the most recent balances for active accounts.
- **Finance Command**: Provides a comprehensive financial summary including account balances, this month's income and expenses, and recent transactions.
- **Spending Command**: Shows spending by category for the current month.
- **Report Command**: Generates a full financial status report, including balances, upcoming bills, and expected income.

#### Integration Points
- **Telegram Bot**: This file integrates with the Telegram bot to handle financial commands and send responses.
- **Database**: It integrates with the PostgreSQL database to retrieve financial data.
- **Environment Configuration**: It integrates with the environment configuration to load database connection details.

### Detailed Analysis of Functions

1. **`get_db_connection`**
   - **Purpose**: Establishes a database connection.
   - **Dependencies**: `psycopg2`, `os`, `dotenv`
   - **Database**: PostgreSQL

2. **`format_currency`**
   - **Purpose**: Formats a given amount as a currency string.
   - **Dependencies**: `decimal`

3. **`fmt_right`**
   - **Purpose**: Formats a given amount as a right-aligned currency string.
   - **Dependencies**: `decimal`

4. **`balance_command`**
   - **Purpose**: Handles the `/balance` command to show current account balances.
   - **Dependencies**: `psycopg2`, `telegram`, `datetime`
   - **Database**: `accounts`, `transactions`
   - **Logic**: Retrieves the most recent balance for each active account and formats the data into a readable message.

5. **`finance_command`**
   - **Purpose**: Handles the `/finance` command to provide a comprehensive financial summary.
   - **Dependencies**: `psycopg2`, `telegram`, `datetime`
   - **Database**: `accounts`, `transactions`
   - **Logic**: Retrieves account balances, this month's income and expenses, and recent transactions, and formats the data into a readable message.

6. **`spending_command`**
   - **Purpose**: Handles the `/spending` command to show spending by category.
   - **Dependencies**: `psycopg2`, `telegram`, `datetime`
   - **Database**: `transactions`
   - **Logic**: Retrieves spending data by category for the current month and formats the data into a readable message.

7. **`report_command`**
   - **Purpose**: Handles the `/report` command to generate a full financial status report.
   - **Dependencies**: `psycopg2`, `telegram`, `datetime`
   - **Database**: `accounts`, `transactions`, `recurring_bills`, `recurring_income`
   - **Logic**: Retrieves balances, upcoming bills, and expected income for the next 14 days and formats the data into a readable message.

8. **`setbalance_command`**
   - **Purpose**: Handles the `/setbalance` command to set the current balance for an account.
   - **Dependencies**: `psycopg2`, `telegram`
   - **Database**: `accounts`, `transactions`
   - **Logic**: Updates the balance for a specified account.

9. **`get_category_icon`**
   - **Purpose**: Retrieves an emoji icon for a given category.
   - **Dependencies**: None

10. **`spend_command`**
    - **Purpose**: Handles the `/spend` command to show spending breakdown by category.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves spending data by category for a specified month and formats the data into a readable message.

11. **`monthly_command`**
    - **Purpose**: Handles the `/monthly` command to show a month-by-month spending trend.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves spending data for each month and formats the data into a readable message.

12. **`compare_command`**
    - **Purpose**: Handles the `/compare` command to compare spending between this month and the previous month.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves spending data for the current and previous months and formats the data into a readable message.

13. **`top_command`**
    - **Purpose**: Handles the `/top` command to show top merchants by spending.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves spending data by merchant and formats the data into a readable message.

14. **`txn_command`**
    - **Purpose**: Handles the `/txn` command to list transactions (paginated).
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves transaction data for a specified category and formats the data into a readable message.

15. **`next_command`**
    - **Purpose**: Handles the `/next` command to show the next page of results.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves the next page of transaction data and formats the data into a readable message.

16. **`back_command`**
    - **Purpose**: Handles the `/back` command to show the previous page of results.
    - **Dependencies**: `psycopg2`, `telegram`, `datetime`
    - **Database**: `transactions`
    - **Logic**: Retrieves the previous page of transaction data and formats the data into a readable message.

### Summary
This file is a critical component of the Mythos Telegram bot, providing financial insights to users through various commands. It integrates with the PostgreSQL database to retrieve and format financial data, ensuring that users receive timely and accurate financial information via Telegram.
