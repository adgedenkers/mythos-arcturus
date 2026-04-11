# eval/results/query_calendar/20260305_091625/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 165

---

### File: `eval/results/query_calendar/20260305_091625/temp_skill/test_skill.py`

#### Purpose
This file defines a skill (`QueryCalendarSkill`) that queries the calendar events from a PostgreSQL database based on user input and formats the results into a summary.

#### Architecture
- **Class**: `QueryCalendarSkill` inherits from `SkillBase`.
- **Methods**: 
  - `execute`: Main method to execute the skill, handling the entire process from detecting the date range to formatting the results.
  - `_detect_range`: Detects the date range from the user's message.
  - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
  - `_format_results`: Formats the raw query results into a more readable format.
  - `_build_summary`: Builds a summary of the events for the specified date range.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that is likely used for testing or standalone execution.

#### Patterns
- **Factory Method**: `_get_conn` can be seen as a factory method for creating database connections.
- **Singleton**: The connection to the database is created and managed within `_get_conn`, which can be seen as a singleton pattern for database connections.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.

#### Interfaces
- **Exposed Methods**: `execute` is the primary method exposed to other parts of the system for executing the skill.
- **SkillBase Integration**: Inherits from `SkillBase` and implements the `execute` method to integrate with the Mythos skill system.

#### Database
- **Tables**: `calendar_events` (PostgreSQL table).
- **Operations**: Reads from `calendar_events` to fetch events based on the specified date range.

#### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`) are loaded from environment variables using `dotenv`.

#### Key Logic
- **Date Range Detection**: `_detect_range` parses the user message to determine the date range for querying events.
- **Event Querying**: `_query_events` constructs and executes a SQL query to fetch events from the `calendar_events` table.
- **Result Formatting**: `_format_results` formats the raw query results into a more user-friendly format.
- **Summary Building**: `_build_summary` aggregates and summarizes the events, providing a concise overview.

#### Integration Points
- **SkillBase**: Integrates with the `SkillBase` class, which is part of the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, which is a core component of the Mythos system.
- **Logging**: Uses `logging` to log errors and other important information, which is a standard practice in the Mythos system for debugging and monitoring.

### Detailed Breakdown

#### `QueryCalendarSkill` Class
- **Attributes**:
  - `name`: 'query_calendar'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show calendar events for today or upcoming days'
  - `triggers`: List of keywords that trigger this skill
  - `cache_ttl`: Cache time-to-live in seconds (300 seconds)

- **Methods**:
  - `execute`: Main method that orchestrates the skill execution.
    - **Steps**:
      1. Detects the date range from the user message.
      2. Queries the database for events within the detected range.
      3. Formats the query results.
      4. Builds a summary of the events.
      5. Returns a `SkillResponse` object with the formatted results and summary.
  - `_detect_range`: Parses the user message to determine the date range.
  - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
  - `_format_results`: Formats the raw query results into a more readable format.
  - `_build_summary`: Aggregates and summarizes the events, providing a concise overview.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- `execute`: A top-level function that is likely used for testing or standalone execution.

### Conclusion
This file is a crucial component of the Mythos system, providing a skill to query and summarize calendar events based on user input. It integrates with the PostgreSQL database and follows a structured approach to handle the entire process from parsing user input to providing a formatted summary of events.
