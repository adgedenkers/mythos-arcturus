# telegram_bot/handlers/calendar_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 211

---

### Documentation for `telegram_bot/handlers/calendar_handler.py`

#### Purpose
This file handles calendar-related commands for a Telegram bot, allowing users to view events for today, this week, or this month, and to quickly add new events.

#### Architecture
The file consists of several functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `handle_calendar`: Main handler for the `/calendar` command, which routes the request to the appropriate sub-function based on the provided arguments.
- `_show_today`, `_show_week`, `_show_month`: Functions to display the calendar for today, this week, and this month, respectively.
- `_quick_add`: Handles the quick addition of new events to the calendar.
- `_looks_like_time`, `_parse_time`, `_parse_date`: Helper functions for parsing time and date strings.

#### Patterns
- **Factory Method**: `_get_conn` acts as a factory method to create and return a database connection.
- **Facade**: `handle_calendar` acts as a facade, simplifying the interface for handling various calendar-related commands.

#### Dependencies
- `os`, `sys`, `logging`: Standard Python libraries for environment variables, system operations, and logging.
- `psycopg2`: PostgreSQL database adapter for Python.
- `re`: Regular expression operations.
- `telegram`: Telegram bot framework.
- `calendar_formatter`: Custom module for formatting calendar views.

#### Interfaces
- `handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Main entry point for handling `/calendar` commands.
- `_show_today(update: Update)`, `_show_week(update: Update)`, `_show_month(update: Update)`: Functions to display calendar views.
- `_quick_add(update: Update, args: list)`: Function to add new events to the calendar.

#### Database
- **Tables**: 
  - `calendar_events`: Table for storing calendar events.
  - `datetime`: Table for storing date and time information.
  - `telegram`: Table for storing Telegram-related data.
  - `dotenv`: Table for storing environment variables.
  - `calendar_formatter`: Table for storing calendar formatting information.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: PostgreSQL database connection details loaded from `.env` file.

#### Key Logic
- **Event Addition**: `_quick_add` parses the provided date and time strings, determines the person associated with the event, and inserts the event into the `calendar_events` table.
- **Date Parsing**: `_parse_date` handles various date formats, including relative dates like "today", "tomorrow", and specific dates like "2/20".
- **Time Parsing**: `_parse_time` handles various time formats, including AM/PM and 24-hour formats.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot framework to handle user commands and send responses.
- **Database**: Connects to the PostgreSQL database to retrieve and store calendar events.
- **Calendar Formatter**: Uses the `calendar_formatter` module to format the calendar views for display.

### Detailed Analysis

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables.
- **Dependencies**: `psycopg2`, `dotenv`.
- **Database**: Connects to the `calendar_events` table.

#### `handle_calendar`
- **Purpose**: Routes the `/calendar` command to the appropriate sub-function based on the provided arguments.
- **Dependencies**: `telegram`, `calendar_formatter`.
- **Database**: Uses `_get_conn` to connect to the database.

#### `_show_today`, `_show_week`, `_show_month`
- **Purpose**: Display the calendar for today, this week, and this month, respectively.
- **Dependencies**: `calendar_formatter`.
- **Database**: Uses `_get_conn` to connect to the database.

#### `_quick_add`
- **Purpose**: Quickly add a new event to the calendar.
- **Dependencies**: `calendar_formatter`, `psycopg2`.
- **Database**: Inserts new events into the `calendar_events` table.

#### `_looks_like_time`, `_parse_time`, `_parse_date`
- **Purpose**: Helper functions for parsing time and date strings.
- **Dependencies**: `re`.
- **Database**: None.

This file is a crucial part of the Mythos system, providing a user-friendly interface for managing calendar events through a Telegram bot.
