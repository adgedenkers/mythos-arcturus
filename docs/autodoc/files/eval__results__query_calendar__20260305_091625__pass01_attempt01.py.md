# eval/results/query_calendar/20260305_091625/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 53

---

### File: `eval/results/query_calendar/20260305_091625/pass01_attempt01.py`

#### Purpose
This file defines a class `QueryCalendarSkill` that implements a skill to query calendar events based on user input. It detects the date range from the user's message, queries the database for events within that range, formats the results, and builds a summary.

#### Architecture
The file contains a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that orchestrates the process of detecting the date range, querying events, formatting results, and building a summary.
- `_detect_range`: Detects the date range from the user's message.
- `_query_events`: Queries the database for events within the specified date range.
- `_format_results`: Formats the raw query results.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential direct invocation.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The database connection could be managed as a singleton to ensure a single connection is used throughout the application.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method that other parts of the system will call to use this skill.
- **Private Methods**: `_detect_range`, `_query_events`, `_format_results`, `_build_summary` are helper methods used internally by `execute`.

#### Database
- **Tables/Labels**: The file references the `calendar_events` table in PostgreSQL for querying events.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `QueryCalendarSkill` class.

#### Key Logic
1. **Date Range Detection**: The `_detect_range` method parses the user's message to determine the start and end dates for the query.
2. **Database Query**: The `_query_events` method queries the `calendar_events` table for events within the detected date range.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form.
4. **Summary Building**: The `_build_summary` method creates a summary of the formatted results.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, indicating it integrates with a broader skill management system.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database, which is used by the `_query_events` method.
- **Request/Response**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the request-response model of the Mythos system.

### Summary
This file implements a calendar query skill that processes user requests to retrieve and summarize calendar events. It leverages PostgreSQL for data storage and retrieval, and integrates with the broader Mythos system through the `SkillBase` class and request-response model.
