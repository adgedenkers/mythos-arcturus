# skills/data/query_calendar.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 165

---

### File: `skills/data/query_calendar.py`

#### Purpose
This file implements a calendar query skill (`QueryCalendarSkill`) that processes user requests to retrieve and summarize calendar events from a PostgreSQL database based on specified date ranges.

#### Architecture
The file contains a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class includes methods for executing the skill, detecting date ranges from user messages, querying the database for events, formatting the results, and building a summary. Additionally, there is a top-level function `_get_conn` for establishing a database connection.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a consistent connection setup using environment variables.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_detect_range`, `_query_events`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `calendar_events`
- **Operations**: Reads from `calendar_events` to fetch events based on date ranges.

#### Configuration
- **Environment Variables**: Database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`)
- **Configuration Files**: `.env` file loaded using `dotenv.load_dotenv()`

#### Key Logic
1. **Date Range Detection**: `_detect_range` parses the user message to determine the date range (e.g., today, this week, next N days).
2. **Database Query**: `_query_events` fetches events from the `calendar_events` table within the specified date range.
3. **Result Formatting**: `_format_results` formats the raw database rows into a more readable structure.
4. **Summary Building**: `_build_summary` creates a human-readable summary of the events, grouping them by date.

#### Integration Points
- **SkillBase Integration**: The `QueryCalendarSkill` class extends `SkillBase` and integrates with the Mythos skill engine.
- **Database Integration**: Uses `psycopg2` to connect to and query the PostgreSQL database.
- **Logging**: Uses `logging` to log errors during execution.

### Detailed Analysis

#### Class: `QueryCalendarSkill`
- **Attributes**:
  - `name`: 'query_calendar'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show calendar events for today or upcoming days'
  - `triggers`: List of keywords that trigger this skill
  - `cache_ttl`: 300 seconds (5 minutes)

- **Methods**:
  - `execute`: Main method that processes the user request, detects the date range, queries the database, formats the results, and builds a summary.
  - `_detect_range`: Parses the user message to determine the date range.
  - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
  - `_format_results`: Formats the raw database rows into a more readable structure.
  - `_build_summary`: Creates a human-readable summary of the events.

#### Top-level Functions
- **`_get_conn`**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Key Business Logic
1. **Date Range Detection**:
   - Parses the user message to determine the date range (e.g., today, this week, next N days).
   - Uses regular expressions to identify specific date ranges like "next N days".

2. **Database Query**:
   - Connects to the PostgreSQL database using `psycopg2`.
   - Executes a query to fetch events from the `calendar_events` table within the specified date range.

3. **Result Formatting**:
   - Converts the raw database rows into a more readable format, including handling `start_time` and `end_time` fields.

4. **Summary Building**:
   - Groups events by date and formats them into a human-readable summary.
   - Limits the summary to the first 5 events and indicates if there are more.

#### Integration with Mythos System
- **SkillBase Integration**: The `QueryCalendarSkill` class extends `SkillBase` and integrates with the Mythos skill engine.
- **Database Integration**: Uses `psycopg2` to connect to and query the PostgreSQL database.
- **Logging**: Uses `logging` to log errors during execution.

This file is a critical component of the Mythos system, providing a robust and flexible way to query and summarize calendar events based on user requests.
