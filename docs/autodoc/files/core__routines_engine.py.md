# core/routines_engine.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 614

---

### File: core/routines_engine.py

#### Purpose
This file contains the core logic for managing recurring routines and generating daily briefings in the Mythos system. It handles the creation and tracking of routine completion records, fetching overdue routines, and assembling various components of the daily briefing.

#### Architecture
The file consists of several top-level functions that interact with a PostgreSQL database to manage and retrieve routine data. Each function is designed to perform a specific task, such as checking if a date is a specific occurrence of a weekday, fetching routines due today, marking routines as completed or skipped, and generating daily briefings.

#### Patterns
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory**: The `generate_daily_briefing` function acts as a factory method, assembling various components to create a complete daily briefing.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `decimal`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL tables such as `routines`, `routine_completions`, `idea_backlog`, `recurring_bills`, `accounts`, `bill_overrides`, `calendar_events`, `checkin_log`

#### Interfaces
- **Public Functions**: 
  - `_is_nth_weekday(target_date, day_of_week, week_of_month)`
  - `get_db_connection()`
  - `get_routines_due_today(conn)`
  - `get_overdue_routines(conn)`
  - `ensure_today_instances(conn)`
  - `complete_routine(routine_id, notes, completed_by, conn)`
  - `skip_routine(routine_id, reason, conn)`
  - `get_open_tasks(conn, limit)`
  - `get_upcoming_bills(conn, days_ahead)`
  - `get_calendar_events_today(conn)`
  - `get_account_balances_summary(conn)`
  - `get_last_checkin(conn)`
  - `log_checkin(checkin_type, summary, conn)`
  - `generate_daily_briefing()`
  - `format_briefing_telegram(briefing)`

#### Database
- **Tables**: `routines`, `routine_completions`, `idea_backlog`, `recurring_bills`, `accounts`, `bill_overrides`, `calendar_events`, `checkin_log`
- **Neo4j Labels**: None

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Config Files**: `.env` file located at `/opt/mythos/.env`

#### Key Logic
- **Routine Due Date Calculation**: Functions like `get_routines_due_today` and `ensure_today_instances` calculate and create completion records for routines based on their frequency (daily, weekly, monthly, etc.).
- **Completion Status Management**: Functions like `complete_routine` and `skip_routine` manage the status of routine completions.
- **Daily Briefing Assembly**: `generate_daily_briefing` and `format_briefing_telegram` assemble and format the daily briefing for the user.

#### Integration Points
- **Database Interaction**: All functions interact with the PostgreSQL database to fetch or update routine data.
- **Other Subsystems**: 
  - **Iris**: `generate_daily_briefing` is used by Iris for the daily checkin.
  - **Telegram**: `format_briefing_telegram` formats the briefing for Telegram.
  - **Cron/Service**: `ensure_today_instances` can be called by a cron job or service to ensure today's routine instances are created.

### Detailed Function Descriptions

1. **_is_nth_weekday(target_date, day_of_week, week_of_month)**
   - **Purpose**: Determines if a given date is the Nth occurrence of a specific weekday in its month.
   - **Logic**: Checks if the target date matches the specified weekday and occurrence.

2. **get_db_connection()**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Logic**: Loads environment variables from `.env` and creates a database connection.

3. **get_routines_due_today(conn)**
   - **Purpose**: Fetches routines that are due today based on their frequency.
   - **Logic**: Queries the `routines` and `routine_completions` tables to find routines due today and their completion status.

4. **get_overdue_routines(conn)**
   - **Purpose**: Retrieves routines that were due in the past 7 days but were never completed.
   - **Logic**: Queries the `routines` and `routine_completions` tables to find overdue routines.

5. **ensure_today_instances(conn)**
   - **Purpose**: Ensures that completion records for today's routines are created if they don't exist.
   - **Logic**: Inserts new records into `routine_completions` for routines due today.

6. **complete_routine(routine_id, notes, completed_by, conn)**
   - **Purpose**: Marks a routine as completed for today.
   - **Logic**: Updates the `routine_completions` table to mark the routine as completed.

7. **skip_routine(routine_id, reason, conn)**
   - **Purpose**: Marks a routine as skipped for today.
   - **Logic**: Updates the `routine_completions` table to mark the routine as skipped.

8. **get_open_tasks(conn, limit)**
   - **Purpose**: Fetches open one-off tasks from the `idea_backlog`.
   - **Logic**: Queries the `idea_backlog` table to find open tasks.

9. **get_upcoming_bills(conn, days_ahead)**
   - **Purpose**: Retrieves bills due in the next N days.
   - **Logic**: Queries the `recurring_bills` and `bill_overrides` tables to find upcoming bills.

10. **get_calendar_events_today(conn)**
    - **Purpose**: Fetches today's calendar events.
    - **Logic**: Queries the `calendar_events` table to find events for today.

11. **get_account_balances_summary(conn)**
    - **Purpose**: Provides a quick balance summary for account checkin.
    - **Logic**: Queries the `accounts` table to get account balances.

12. **get_last_checkin(conn)**
    - **Purpose**: Retrieves the most recent checkin.
    - **Logic**: Queries the `checkin_log` table to find the last checkin.

13. **log_checkin(checkin_type, summary, conn)**
    - **Purpose**: Logs a checkin event.
    - **Logic**: Inserts a new record into the `checkin_log` table.

14. **generate_daily_briefing()**
    - **Purpose**: Assembles the complete daily briefing.
    - **Logic**: Calls various functions to gather data and assemble the briefing.

15. **format_briefing_telegram(briefing)**
    - **Purpose**: Formats the daily briefing for Telegram.
    - **Logic**: Takes the assembled briefing and formats it for Telegram.

This file is a critical component of the Mythos system, providing the backbone for managing daily routines and generating the daily briefing for the user.
