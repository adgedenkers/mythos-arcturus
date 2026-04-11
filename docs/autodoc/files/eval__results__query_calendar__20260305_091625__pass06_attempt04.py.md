# eval/results/query_calendar/20260305_091625/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 169

---

### File: eval/results/query_calendar/20260305_091625/pass06_attempt04.py

#### Purpose
This file contains the `QueryCalendarSkill` class, which is responsible for querying the PostgreSQL database for calendar events based on a user's message and returning a formatted summary of the events within the specified date range.

#### Architecture
- **Class**: `QueryCalendarSkill` extends `SkillBase` and contains methods for detecting date ranges, querying events, formatting results, and building summaries.
- **Top-level Functions**: `_get_conn`, `execute`, `_detect_range`, `_query_events`, `_format_results`, `_build_summary`.
- **Data Flow**: The class processes user messages to determine the date range, queries the database for events within that range, formats the results, and builds a summary to return.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection to the database.
- **Factory**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_detect_range`, `_query_events`, `_format_results`, `_build_summary`.
- **Exposed**: The `execute` method is the main entry point for processing user requests and returning a formatted response.

#### Database
- **Tables**: `calendar_events` (PostgreSQL).
- **Operations**: Reads from `calendar_events` to fetch events within a specified date range.

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL database connection.
- **Dotenv**: Loads environment variables from a `.env` file.

#### Key Logic
1. **Date Range Detection**: `_detect_range` parses the user message to determine the start and end dates for the query.
2. **Event Querying**: `_query_events` constructs and executes a SQL query to fetch events from the `calendar_events` table.
3. **Result Formatting**: `_format_results` formats the raw query results into a more readable structure.
4. **Summary Building**: `_build_summary` aggregates and summarizes the formatted results, providing a concise summary of events.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Utilizes `SkillRequest` and `SkillResponse` from `engine.base` to handle request and response objects.

### Detailed Documentation

#### Classes
- **QueryCalendarSkill**
  - **Inherits**: `SkillBase`
  - **Attributes**:
    - `name`: 'query_calendar'
    - `version`: '1.0'
    - `category`: 'data'
    - `description`: 'Show calendar events for today or upcoming days'
    - `triggers`: List of keywords that trigger this skill
    - `cache_ttl`: 300 seconds
  - **Methods**:
    - `execute`: Main method to process the user request and return a formatted response.
    - `_detect_range`: Determines the date range based on the user message.
    - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
    - `_format_results`: Formats the query results into a more readable structure.
    - `_build_summary`: Aggregates and summarizes the formatted results.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database.
- **execute**: Processes the user request and returns a formatted response.
- **_detect_range**: Determines the date range based on the user message.
- **_query_events**: Queries the `calendar_events` table for events within the specified date range.
- **_format_results**: Formats the query results into a more readable structure.
- **_build_summary**: Aggregates and summarizes the formatted results.

#### Dependencies
- **os**: Used to access environment variables.
- **logging**: Used for logging errors.
- **re**: Used for regular expression matching.
- **datetime**: Used for date and time operations.
- **psycopg2**: Used to connect to and query the PostgreSQL database.
- **dotenv**: Used to load environment variables from a `.env` file.
- **engine.base**: Provides the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Hostname of the PostgreSQL server.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASS`: Password for the PostgreSQL database.
  - `DB_PORT`: Port number for the PostgreSQL server.

#### Key Logic
1. **Date Range Detection**:
   - `_detect_range` parses the user message to determine the start and end dates for the query.
   - Supports keywords like 'tomorrow', 'this week', 'this month', and 'next N days'.

2. **Event Querying**:
   - `_query_events` constructs and executes a SQL query to fetch events from the `calendar_events` table.
   - Filters events based on the `is_active` flag and the specified date range.

3. **Result Formatting**:
   - `_format_results` formats the raw query results into a more readable structure.
   - Converts date and time formats and handles 'all day' events.

4. **Summary Building**:
   - `_build_summary` aggregates and summarizes the formatted results.
   - Groups events by date and provides a concise summary of up to 5 events.

#### Integration Points
- **SkillBase**: Integrates with the Mythos skill framework by inheriting from `SkillBase`.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Utilizes `SkillRequest` and `SkillResponse` to handle request and response objects.
