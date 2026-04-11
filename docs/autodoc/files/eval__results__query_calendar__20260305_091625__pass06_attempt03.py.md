# eval/results/query_calendar/20260305_091625/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 173

---

### Documentation for `eval/results/query_calendar/20260305_091625/pass06_attempt03.py`

#### Purpose
This file implements a skill (`QueryCalendarSkill`) that queries a PostgreSQL database to retrieve calendar events based on a user's message. It processes the message to determine the date range, queries the database for events within that range, formats the results, and builds a summary.

#### Architecture
The file contains a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class has several methods for executing the skill, detecting date ranges, querying events, formatting results, and building summaries. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the creation and processing of calendar event data.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (async), `_detect_range`, `_query_events`, `_format_results`, `_build_summary`
- **Exposed Classes**: `QueryCalendarSkill` (inherits from `SkillBase`)

#### Database
- **Tables**: `calendar_events` (PostgreSQL)
- **Labels**: None (only PostgreSQL tables are used)

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL database connection.
- **Config Files**: `.env` file loaded using `dotenv`.

#### Key Logic
1. **Date Range Detection**: `_detect_range` method parses the user message to determine the date range for querying events.
2. **Event Querying**: `_query_events` method queries the `calendar_events` table for events within the detected date range.
3. **Result Formatting**: `_format_results` method formats the raw query results into a more readable structure.
4. **Summary Building**: `_build_summary` method generates a summary of the events for the specified date range.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, integrating with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **Logging**: Uses `logging` for error handling and logging.
- **Environment Configuration**: Uses `dotenv` to load environment variables for database configuration.

### Detailed Analysis

#### Class `QueryCalendarSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'query_calendar'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show calendar events for today or upcoming days'
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Cache time-to-live in seconds.
- **Methods**:
  - `execute`: Main method that processes the user request, detects the date range, queries events, formats results, and builds a summary.
  - `_detect_range`: Parses the user message to determine the date range.
  - `_query_events`: Queries the `calendar_events` table for events within the specified date range.
  - `_format_results`: Formats the raw query results into a structured format.
  - `_build_summary`: Generates a summary of the events for the specified date range.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**: Asynchronous function to execute the skill, integrating with the Mythos skill framework.

#### Database Interaction
- The `_query_events` method constructs a SQL query to retrieve events from the `calendar_events` table based on the specified date range.
- The `_get_conn` function ensures a consistent connection to the PostgreSQL database, using `psycopg2` with a `RealDictCursor` for dictionary-like row access.

#### Configuration and Environment Variables
- The `.env` file is loaded using `dotenv` to configure the PostgreSQL database connection.
- Environment variables `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are used to establish the database connection.

This file is a critical component of the Mythos system, providing a robust and flexible way to query and present calendar events based on user input.
