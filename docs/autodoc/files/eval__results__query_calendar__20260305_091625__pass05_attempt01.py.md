# eval/results/query_calendar/20260305_091625/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 165

---

### Documentation for `eval/results/query_calendar/20260305_091625/pass05_attempt01.py`

#### Purpose
This file implements a calendar query skill (`QueryCalendarSkill`) that retrieves and formats calendar events from a PostgreSQL database based on user-specified date ranges.

#### Architecture
The file contains a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the query process:
- `execute`: The main method that orchestrates the query process.
- `_detect_range`: Detects the date range from the user message.
- `_query_events`: Queries the database for events within the detected range.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the events for the specified date range.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that wraps the class method for execution.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function could be considered a singleton pattern if the connection is reused, though it is not explicitly implemented as such in this file.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `datetime`: For date and time manipulations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- `execute`: Exposes the main execution method to other parts of the system, taking a `SkillRequest` object and returning a `SkillResponse` object.
- `_detect_range`, `_query_events`, `_format_results`, `_build_summary`: These methods are internal and are not directly exposed to other parts of the system but are used within the `execute` method.

#### Database
- **Tables/Labels**: 
  - `calendar_events`: PostgreSQL table from which calendar events are queried.
  - `dotenv`: Used to load environment variables for database connection.
  - `engine`: Likely a reference to the database engine configuration.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
- **Date Range Detection**: The `_detect_range` method parses the user message to determine the date range for querying events. It supports keywords like "tomorrow," "this week," "next N days," and defaults to today if no specific range is mentioned.
- **Database Query**: The `_query_events` method constructs and executes a PostgreSQL query to retrieve events within the specified date range.
- **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form, including handling of time formats and event descriptions.
- **Summary Building**: The `_build_summary` method generates a summary of the events, grouping them by date and formatting them for display.

#### Integration Points
- **SkillBase**: The `QueryCalendarSkill` class inherits from `SkillBase`, indicating that it integrates with a broader skill management system.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the system's request-response model.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database, establishing a connection and ensuring proper resource management.

This file is a critical component of the Mythos system, providing a robust and flexible way to query and present calendar events based on user input.
