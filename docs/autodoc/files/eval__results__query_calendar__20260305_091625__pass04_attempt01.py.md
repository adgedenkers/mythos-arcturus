# eval/results/query_calendar/20260305_091625/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 148

---

### Documentation for `eval/results/query_calendar/20260305_091625/pass04_attempt01.py`

#### Purpose
This file contains the implementation of a calendar query skill (`QueryCalendarSkill`) that processes user requests to retrieve and summarize calendar events from a PostgreSQL database based on specified date ranges.

#### Architecture
The file is structured around the `QueryCalendarSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the calendar query process:
- `execute`: The main entry point for processing a request.
- `_detect_range`: Determines the date range based on the user's message.
- `_query_events`: Queries the PostgreSQL database for events within the specified date range.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential external use.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The database connection is created and managed within `_get_conn`, ensuring a consistent connection setup.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` for database connection.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Top-Level Functions**: `_get_conn` and `execute` are available for external use, though they are primarily used internally.

#### Database
- **Tables**: `calendar_events` (PostgreSQL) is queried for events.
- **Labels**: None (the system does not use Neo4j for this module).

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are used to configure the database connection.
- **Dotenv**: `.env` file is loaded to provide environment variables.

#### Key Logic
- **Date Range Detection**: The `_detect_range` method parses the user message to determine the date range for the query.
- **Event Query**: The `_query_events` method constructs and executes a SQL query to retrieve events from the `calendar_events` table.
- **Result Formatting**: The `_format_results` method formats the raw query results into a more user-friendly form.
- **Summary Building**: The `_build_summary` method aggregates and summarizes the formatted results, providing a concise summary of events.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill framework.
- **Database Connection**: The `_get_conn` function provides a consistent way to connect to the PostgreSQL database, ensuring that the skill can interact with the database seamlessly.
- **Request/Response Handling**: The `execute` method processes incoming `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request/response handling system.

This file is a critical component of the Mythos system, enabling users to query and receive summaries of calendar events based on specified date ranges, integrating seamlessly with the PostgreSQL database and the broader Mythos skill framework.
