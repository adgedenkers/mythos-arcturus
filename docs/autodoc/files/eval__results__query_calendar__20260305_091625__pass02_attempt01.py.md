# eval/results/query_calendar/20260305_091625/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 74

---

### File: `eval/results/query_calendar/20260305_091625/pass02_attempt01.py`

#### Purpose
This file contains the implementation of a calendar query skill (`QueryCalendarSkill`) that processes user requests to retrieve and summarize calendar events within a specified date range. It interacts with a PostgreSQL database to fetch event data and formats the results for presentation.

#### Architecture
The file is structured around a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class contains several methods to handle different aspects of the calendar query process:
- `_detect_range`: Detects the date range from the user's message.
- `_query_events`: Queries the database for events within the detected range.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, which orchestrates the query process.

#### Patterns
- **Factory Method**: The `_get_conn` function can be considered a factory method for creating database connections.
- **Singleton**: The database connection could be implemented as a singleton to ensure only one connection is used throughout the application.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Internal Methods**: `_detect_range`, `_query_events`, `_format_results`, `_build_summary`

#### Database
- **Tables/Labels**: `calendar_events` (PostgreSQL table)
- **Operations**: Reads from `calendar_events` to fetch events within a specified date range.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are used to configure the database connection.
- **Dotenv**: `.env` file is loaded to provide environment variables.

#### Key Logic
1. **Date Range Detection**: The `_detect_range` method parses the user message to determine the date range for the query. It supports various keywords like "tomorrow," "this week," "next N days," etc.
2. **Database Query**: The `_query_events` method is intended to query the `calendar_events` table for events within the detected date range.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form.
4. **Summary Building**: The `_build_summary` method creates a summary of the formatted results.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, indicating it integrates with a broader skill management system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_query_events` method.
- **Request Handling**: The `execute` method processes incoming requests and interacts with other methods to produce a response.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `psycopg2`, `os.getenv`
- **Configuration**: Uses environment variables for database connection details.

#### `QueryCalendarSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Main entry point for the skill. It orchestrates the process of detecting the date range, querying events, formatting results, and building a summary.
  - `_detect_range`: Parses the user message to determine the date range.
  - `_query_events`: Queries the database for events within the detected date range.
  - `_format_results`: Formats the raw query results.
  - `_build_summary`: Builds a summary of the formatted results.

#### Top-Level Functions
- **`_detect_range`**: Parses the user message to determine the date range.
- **`_query_events`**: Queries the database for events within the detected date range.
- **`_format_results`**: Formats the raw query results.
- **`_build_summary`**: Builds a summary of the formatted results.

### Example Usage
```python
# Example usage of QueryCalendarSkill
skill = QueryCalendarSkill()
request = SkillRequest(message="What's on this week?")
response = skill.execute(request)
print(response.summary)
```

This example demonstrates how the `QueryCalendarSkill` can be instantiated and used to process a user request, returning a summary of calendar events for the current week.
