# telegram_bot/handlers/snapshot_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 363

---

### File: telegram_bot/handlers/snapshot_handler.py

#### Purpose
This file contains the logic for handling two Telegram bot commands: `/snapshot` and `/setbal`. The `/snapshot` command generates a financial snapshot report, while the `/setbal` command allows users to quickly update account balances.

#### Architecture
The file consists of four top-level functions:
1. `get_db_connection`: Establishes a connection to the PostgreSQL database.
2. `fmt`: Formats currency values for display.
3. `snapshot_command`: Handles the `/snapshot` command, generating a financial snapshot report.
4. `setbal_command`: Handles the `/setbal` command, updating account balances.

#### Patterns
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Command Pattern**: The `snapshot_command` and `setbal_command` functions act as commands that execute specific operations based on user input.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors and information.
- `psycopg2`: For PostgreSQL database operations.
- `datetime`: For date and time manipulation.
- `decimal`: For precise decimal arithmetic.
- `telegram`: For interacting with the Telegram bot API.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `snapshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Exposes the `/snapshot` command to the Telegram bot.
- `setbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Exposes the `/setbal` command to the Telegram bot.

#### Database
- **Tables/Labels**:
  - `accounts`: Used to retrieve and update account balances.
  - `recurring_bills`: Used to retrieve upcoming payments.
  - `recurring_income`: Used to retrieve expected income.

#### Configuration
- Uses environment variables loaded from `/opt/mythos/.env` for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Key Logic
1. **`snapshot_command`**:
   - Retrieves account balances, categorizes them by type (checking, credit, loan).
   - Calculates total cash, total debt, and net worth.
   - Retrieves and formats upcoming payments and expected income.
   - Builds and sends a formatted report to the user.

2. **`setbal_command`**:
   - Validates user input for account abbreviation and amount.
   - Updates the account balance in the `accounts` table.

#### Integration Points
- **Telegram Bot API**: The functions interact with the Telegram bot API to receive commands and send responses.
- **PostgreSQL Database**: The functions interact with the PostgreSQL database to retrieve and update financial data.

### Detailed Breakdown

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses environment variables to configure the connection and returns a `psycopg2` connection object.

#### `fmt`
- **Purpose**: Formats currency values for display.
- **Logic**: Converts the amount to a `Decimal`, formats it with a currency symbol, and right-aligns it.

#### `snapshot_command`
- **Purpose**: Generates a financial snapshot report.
- **Logic**:
  - Retrieves account balances and categorizes them.
  - Calculates totals for cash, debt, and net worth.
  - Retrieves upcoming payments and expected income.
  - Builds a formatted report and sends it to the user.

#### `setbal_command`
- **Purpose**: Updates account balances.
- **Logic**:
  - Validates user input for account abbreviation and amount.
  - Updates the account balance in the `accounts` table.
  - Sends a confirmation message to the user.

### Example Usage
- **`/snapshot`**: Generates a financial snapshot report with account balances, upcoming payments, and expected income.
- **`/setbal <ACCT> <amount>`**: Updates the balance for a specified account.

### Error Handling
- Both commands handle exceptions and log errors using the `logging` module.
- Errors are communicated back to the user via the Telegram bot.

This file is a critical component of the Mythos system, providing users with real-time financial insights and the ability to quickly update their account balances.
