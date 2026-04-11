# telegram_bot/handlers/pulse_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 330

---

### File: `telegram_bot/handlers/pulse_handler.py`

#### Purpose
This file contains functions and logic to handle the generation and sending of financial pulse messages to household members via a Telegram bot. It includes both on-demand command handling and scheduled weekly pulse messages.

#### Architecture
The file is structured around several top-level functions:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `format_currency`: Formats a given amount as a currency string.
- `generate_pulse_message`: Compiles the financial pulse message by querying the database and formatting the results.
- `pulse_command`: Handles the `/pulse` command to send the financial pulse message on demand.
- `send_weekly_pulse`: Sends the weekly financial pulse message to specified household members.
- `setup_pulse_scheduler`: Sets up a scheduler to send the weekly pulse message every Sunday at 6:00 PM EST.

#### Patterns
- **Singleton**: The database connection is created using a function (`get_db_connection`), which could be considered a singleton pattern if the connection is reused.
- **Factory**: The `generate_pulse_message` function can be seen as a factory method that produces a formatted message based on database queries.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `decimal`, `telegram`, `telegram.ext`, `psycopg2`, `psycopg2.extras`, `dotenv`
- **Database**: PostgreSQL tables `accounts`, `recurring_bills`, `recurring_income`, and `telegram`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`, `TELEGRAM_ID_KA`, `TELEGRAM_ID_SERAPHE`

#### Interfaces
- **Public Functions**:
  - `pulse_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/pulse` command.
  - `send_weekly_pulse(context: ContextTypes.DEFAULT_TYPE)`: Sends the weekly pulse message.
  - `setup_pulse_scheduler(application)`: Sets up the scheduler for the weekly pulse.

#### Database
- **Tables/Labels**:
  - `accounts`: Used to retrieve current balances and account information.
  - `recurring_bills`: Used to retrieve upcoming bills.
  - `recurring_income`: Used to retrieve upcoming income.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` for database connection.
  - `TELEGRAM_ID_KA`, `TELEGRAM_ID_SERAPHE` for Telegram user IDs.

#### Key Logic
1. **Database Connection**: Establishes a connection to the PostgreSQL database using `psycopg2`.
2. **Currency Formatting**: Converts numerical amounts into formatted currency strings.
3. **Message Generation**:
   - Queries the `accounts`, `recurring_bills`, and `recurring_income` tables to gather financial data.
   - Calculates totals for checking balances, upcoming bills, and income.
   - Formats the data into a structured message with emojis indicating financial status.
4. **Command Handling**: Sends the generated message in response to the `/pulse` command.
5. **Scheduled Messages**: Sends the weekly pulse message to specified household members via Telegram.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot framework to handle commands and send messages.
- **Scheduler**: Uses the `telegram.ext.Application` job queue to schedule the weekly pulse message.
- **Database**: Connects to the PostgreSQL database to retrieve financial data.

### Summary
This file is a crucial component of the Mythos system, providing financial visibility to household members through a Telegram bot. It handles both on-demand and scheduled message generation, integrating with the Telegram bot framework and PostgreSQL database to provide real-time financial updates.
