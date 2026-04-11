# eval/results/query_calendar/20260305_091625/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 173

---

### File: `eval/results/query_calendar/20260305_091625/pass06_attempt02.py`

#### Purpose
This file contains the implementation of a calendar query skill (`QueryCalendarSkill`) that fetches and formats calendar events based on a user's query. It interacts with a PostgreSQL database to retrieve event data and provides a formatted summary of events within a specified date range.

#### Architecture
The file is structured around a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class contains methods for executing the skill, detecting date ranges from user messages, querying the database, formatting results, and building a summary. Additionally, there are top-level functions for establishing a database connection and executing the skill.

- **Class**: `QueryCalendarSkill`
  - **Methods**: `execute`, `_detect_range`, `_query_events`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection is established.
- **Factory**: The `SkillBase` class likely follows a factory pattern to instantiate different skill classes.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Internal Methods**: `_detect_range`, `_query_events`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `calendar_events`
- **Operations**: 
  - **Read**: `SELECT` from `calendar_events` to fetch events within a specified date range.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` (used to establish a database connection)
- **Configuration Files**: `.env` (loaded using `dotenv.load_dotenv()`)

#### Key Logic
1. **Date Range Detection**: `_detect_range` method parses the user message to determine the date range for the query (e.g., today, next N days, this week).
2. **Database Query**: `_query_events` method queries the `calendar_events` table to fetch events within the detected date range.
3. **Result Formatting**: `_format_results` method formats the fetched events into a more readable structure.
4. **Summary Building**: `_build_summary` method creates a summary of the events, grouping them by date and limiting the number of events displayed.

#### Integration Points
- **Skill Execution**: The `execute` method is called by the Mythos system to handle user requests related to calendar events.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, which is required for querying events.
- **Skill Base Class**: The `QueryCalendarSkill` class inherits from `SkillBase`, which likely provides common functionality for different skills in the Mythos system.

### Detailed Breakdown

#### `QueryCalendarSkill` Class
- **Attributes**:
  - `name`: 'query_calendar'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show calendar events for today or upcoming days'
  - `triggers`: List of keywords that trigger this skill
  - `cache_ttl`: Time-to-live for caching results (300 seconds)

- **Methods**:
  - `execute`: Main method that processes the user request, detects the date range, queries the database, formats the results, and builds a summary.
  - `_detect_range`: Parses the user message to determine the date range for the query.
  - `_query_events`: Queries the `calendar_events` table to fetch events within the specified date range.
  - `_format_results`: Formats the fetched events into a more readable structure.
  - `_build_summary`: Creates a summary of the events, grouping them by date and limiting the number of events displayed.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- `execute`: Async function that processes the user request and returns a `SkillResponse` object.

### Summary
This file implements a calendar query skill that interacts with a PostgreSQL database to fetch and format calendar events based on user queries. It follows a modular design with clear separation of concerns, using environment variables for configuration and leveraging the `SkillBase` class for common skill functionality.
