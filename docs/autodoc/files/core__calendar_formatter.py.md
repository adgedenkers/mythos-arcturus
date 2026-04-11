# core/calendar_formatter.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 302

---

### File: core/calendar_formatter.py

#### Purpose
This file provides functions to format calendar views for a specific day, week, or month, integrating events, bills, and routines into a unified timeline view. The formatted views are intended for display in a Telegram bot.

#### Architecture
The file consists of several top-level functions that handle different aspects of calendar formatting:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `_get_events`, `_get_bills`, `_get_routines_for_day`: Retrieve events, bills, and routines from the database.
- `_format_time`, `_format_event_line`, `_format_bill_line`, `_format_routine_line`: Format individual components for display.
- `format_day_view`, `format_week_view`, `format_month_view`: Generate formatted views for a day, week, or month, respectively.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is used throughout the file.
- **Factory**: The `_get_events`, `_get_bills`, and `_get_routines_for_day` functions can be seen as factory methods that produce lists of events, bills, and routines.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `typing`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL tables (`calendar_events`, `recurring_bills`, `bill_overrides`, `routines`, `routine_completions`)

#### Interfaces
- **Public Functions**:
  - `format_day_view(target_date: date = None, conn=None) -> str`: Formats a single day's view.
  - `format_week_view(start_date: date = None) -> str`: Formats a full week view.
  - `format_month_view(target_date: date = None) -> str`: Formats a month view with days that have events or bills.

#### Database
- **Tables/Labels**:
  - `calendar_events`: Stores calendar events.
  - `recurring_bills`: Stores recurring bills.
  - `bill_overrides`: Stores overrides for bills.
  - `routines`: Stores routines.
  - `routine_completions`: Stores completions for routines.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` are loaded from a `.env` file using `dotenv`.

#### Key Logic
- **_get_conn**: Establishes a database connection using environment variables.
- **_get_events**: Retrieves active calendar events within a specified date range.
- **_get_bills**: Retrieves active bills due within a specified date range, including payment status.
- **_get_routines_for_day**: Retrieves routines scheduled for a specific day, considering frequency and completion status.
- **_format_time**: Formats a time object for display.
- **_format_event_line**: Formats a single event as a line.
- **_format_bill_line**: Formats a single bill as a line.
- **_format_routine_line**: Formats a single routine as a line.
- **format_day_view**: Combines events, bills, and routines for a single day into a formatted view.
- **format_week_view**: Combines views for each day of the week into a formatted week view.
- **format_month_view**: Combines views for days with events or bills into a formatted month view.

#### Integration Points
- **Database Integration**: Connects to PostgreSQL to fetch events, bills, and routines.
- **Telegram Integration**: The formatted views are intended for display in a Telegram bot, though the actual integration with Telegram is not handled in this file.
- **Dependency Injection**: The `format_day_view` function accepts a database connection as an argument, allowing for dependency injection and easier testing.

This file serves as a crucial component of the Mythos system, providing a unified and formatted view of calendar events, bills, and routines for users through a Telegram interface.
