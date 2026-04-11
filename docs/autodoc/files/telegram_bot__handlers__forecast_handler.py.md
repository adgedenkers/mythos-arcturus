# telegram_bot/handlers/forecast_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 668

---

### File: `telegram_bot/handlers/forecast_handler.py`

#### Purpose
This file contains the logic for handling financial forecast and projection commands in the Mythos Telegram bot. It provides functionality to retrieve and format current balances, upcoming bills, and expected income, and to generate forecasts based on these data.

#### Architecture
The file consists of several functions that handle different aspects of the forecast and projection logic:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `fmt`: Formats currency values.
- `get_current_balances`: Retrieves current balances for active accounts.
- `get_upcoming_bills`: Fetches bills expected in the next N days.
- `get_upcoming_income`: Fetches income expected in the next N days.
- `parse_forecast_args`: Parses command arguments for the forecast command.
- `matches_filter`: Checks if a bill or income item matches the account filter.
- `build_forecast`: Builds the forecast data.
- `forecast_command`: Handles the `/forecast` command.
- `projection_command`: Handles the `/projection` command.
- `bills_command`: Handles the `/bills` command.
- `income_command`: Handles the `/income` command.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function can be considered a singleton pattern as it ensures a single connection to the database.
- **Factory Method Pattern**: The `parse_forecast_args` function acts as a factory method to parse and return the account filter and days based on the command arguments.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging.
- `datetime`, `timedelta`, `date`: For date and time manipulation.
- `decimal`: For handling decimal values.
- `calendar`: For month range calculations.
- `telegram`: For handling Telegram bot updates.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- Exposes several asynchronous command handlers (`forecast_command`, `projection_command`, `bills_command`, `income_command`) that are intended to be integrated with the Telegram bot framework.
- Provides utility functions (`get_current_balances`, `get_upcoming_bills`, `get_upcoming_income`, `build_forecast`) that can be reused within the system.

#### Database
- **PostgreSQL Tables**: The file interacts with multiple tables:
  - `accounts`: Retrieves account details and balances.
  - `transactions`: Retrieves transaction balances.
  - `recurring_bills`: Retrieves recurring bills.
  - `recurring_income`: Retrieves recurring income.

#### Configuration
- Uses environment variables loaded from `/opt/mythos/.env` for database connection details.

#### Key Logic
- **Balance Retrieval**: `get_current_balances` compares and selects the most recent balance between the account's current balance and the last transaction balance.
- **Forecast Building**: `build_forecast` calculates the running balance over a specified number of days, tracking the lowest balance and any negative balance occurrences.
- **Command Parsing**: `parse_forecast_args` parses command arguments to determine the account filter and number of days for the forecast.

#### Integration Points
- The file integrates with the Telegram bot framework through the `forecast_command`, `projection_command`, `bills_command`, and `income_command` functions, which are likely registered as handlers in the bot's main command processing loop.
- It also integrates with the PostgreSQL database for retrieving account, transaction, bill, and income data.

### Summary
This file is a critical component of the Mythos Telegram bot, responsible for handling financial forecast and projection commands. It retrieves and processes data from the PostgreSQL database to generate accurate financial forecasts and projections, providing valuable insights to users through the Telegram interface.
