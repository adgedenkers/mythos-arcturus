# eval/results/query_calendar/20260305_091625/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 174

---

### File: `eval/results/query_calendar/20260305_091625/pass06_attempt01.py`

#### Purpose
This file contains the `QueryCalendarSkill` class, which is responsible for querying the PostgreSQL database for calendar events based on a user's message and returning a formatted summary of the events.

#### Architecture
The file is structured around the `QueryCalendarSkill` class, which inherits from `SkillBase`. The class contains several methods to handle the execution of the skill, including detecting the date range from the user's message, querying the database for events, formatting the results, and building a summary.

- **Classes**: 
  - `QueryCalendarSkill`: Inherits from `SkillBase` and contains methods for executing the skill, detecting date ranges, querying events, formatting results, and building summaries.

- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: The main entry point for the skill, which orchestrates the execution of the other methods.
  - `_detect_range`: Detects the date range from the user's message.
  - `_query_events`: Queries the database for events within a specified date range.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the events.

#### Patterns
- **Singleton**: The `_get_conn` function acts as a singleton for database connections.
- **Factory**: The `execute` method can be seen as a factory method that produces a `SkillResponse` object.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `datetime`: For date and time manipulations.
  - `psycopg2`: For PostgreSQL database interactions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: The main method that processes the request and returns a `SkillResponse` object.
  - `_detect_range`, `_query_events`, `_format_results`, `_build_summary`: Helper methods used internally by `execute`.

#### Database
- **Tables/Labels**: 
  - `calendar_events`: The PostgreSQL table from which events are queried.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Used to establish a connection to the PostgreSQL database.

#### Key Logic
1. **Date Range Detection**: The `_detect_range` method parses the user's message to determine the date range for querying events. It supports phrases like "today", "tomorrow", "this week", "this month", and "next N days".
2. **Database Query**: The `_query_events` method constructs and executes a SQL query to retrieve events from the `calendar_events` table within the specified date range.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a more readable structure, including handling times and locations.
4. **Summary Building**: The `_build_summary` method generates a summary of the events, grouping them by date and formatting them into a readable string.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, which provides a framework for skill execution.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the broader Mythos system's request/response model.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch calendar events, using environment variables for configuration.

This file is a key component of the Mythos system, enabling users to query their calendar events through natural language inputs and receive structured, summarized responses.
