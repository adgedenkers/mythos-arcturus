# eval/results/query_calendar/20260305_091625/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 173

---

### Documentation for `eval/results/query_calendar/20260305_091625/pass06_attempt05.py`

#### Purpose
This file contains the `QueryCalendarSkill` class, which is responsible for querying calendar events from a PostgreSQL database based on user input and formatting the results for display. It handles detecting date ranges from user messages, querying the database for events within those ranges, formatting the results, and building a summary of the events.

#### Architecture
- **Class**: `QueryCalendarSkill` inherits from `SkillBase` and implements methods for executing the skill, detecting date ranges, querying events, formatting results, and building summaries.
- **Top-level Functions**: `_get_conn`, `execute`, `_detect_range`, `_query_events`, `_format_results`, `_build_summary`.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method for creating a database connection.
- **Singleton**: The `_get_conn` function ensures a consistent connection setup using environment variables and returns a connection object.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_detect_range`, `_query_events`, `_format_results`, `_build_summary`.
- **Exposed Interfaces**: `execute` method is exposed to other parts of the system for executing the skill.

#### Database
- **Tables**: `calendar_events` (PostgreSQL).
- **Operations**: Reads from `calendar_events` table to retrieve events based on date ranges.

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL connection details.
- **Dotenv**: Loads environment variables from a `.env` file.

#### Key Logic
1. **Date Range Detection**: `_detect_range` method parses the user message to determine the date range for querying events.
2. **Event Querying**: `_query_events` method queries the `calendar_events` table for events within the detected date range.
3. **Result Formatting**: `_format_results` method formats the query results into a more readable structure.
4. **Summary Building**: `_build_summary` method generates a summary of the events, grouping them by date and formatting the output.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for handling input and output.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, which is a critical integration point for data retrieval.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `psycopg2`, `os.getenv`.

#### `QueryCalendarSkill`
- **Purpose**: Implements the logic for querying and formatting calendar events based on user input.
- **Methods**:
  - `execute`: Main entry point for the skill, orchestrates the detection of date ranges, querying events, formatting results, and building a summary.
  - `_detect_range`: Parses the user message to determine the start and end dates for the query.
  - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
  - `_format_results`: Formats the query results into a more readable structure.
  - `_build_summary`: Generates a summary of the events, grouping them by date and formatting the output.

#### `_detect_range`
- **Purpose**: Determines the date range for querying events based on the user message.
- **Logic**: Uses regex and string matching to identify specific date ranges like "tomorrow", "this week", "next N days", etc.

#### `_query_events`
- **Purpose**: Queries the `calendar_events` table for events within the specified date range.
- **Logic**: Uses a PostgreSQL query to fetch active events within the given date range.

#### `_format_results`
- **Purpose**: Formats the raw query results into a more readable structure.
- **Logic**: Converts date and time fields to strings and formats them appropriately.

#### `_build_summary`
- **Purpose**: Generates a summary of the events, grouping them by date and formatting the output.
- **Logic**: Groups events by date, formats each event, and generates a summary string.

This file is a critical component of the Mythos system, enabling users to query and view their calendar events based on natural language input.
