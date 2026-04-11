# eval/results/query_calendar/20260305_091625/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 165

---

### File: eval/results/query_calendar/20260305_091625/final.py

#### Purpose
This file implements a calendar query skill (`QueryCalendarSkill`) that allows users to retrieve and summarize calendar events for specified date ranges. It processes user messages to determine the date range, queries the PostgreSQL database for events, formats the results, and builds a summary.

#### Architecture
The file contains a single class `QueryCalendarSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the query process:
- `_detect_range`: Detects the date range from the user message.
- `_query_events`: Queries the PostgreSQL database for events within the detected date range.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, coordinating the other methods.

#### Patterns
- **Factory Method**: `_get_conn` can be seen as a factory method for creating database connections.
- **Singleton**: The database connection could be considered a singleton pattern, although it is not explicitly implemented as such.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For error logging.
- `re`: For regular expression operations.
- `datetime`: For date and time manipulations.
- `psycopg2`: For PostgreSQL database interactions.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- `execute`: Exposed method that takes a `SkillRequest` and returns a `SkillResponse`.
- `_detect_range`, `_query_events`, `_format_results`, `_build_summary`: Internal methods used by `execute` to process the request.

#### Database
- **PostgreSQL Tables**: 
  - `calendar_events`: Table from which events are queried.
  - `dotenv`: Configuration table for environment variables.
  - `engine`: Configuration table for the database engine.
  - `message`: Table for storing messages.
  - `datetime`: Table for date and time operations.

#### Configuration
- Environment variables:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details.
- `.env` file: Loaded using `dotenv.load_dotenv()` to set environment variables.

#### Key Logic
1. **Date Range Detection**:
   - `_detect_range` parses the user message to determine the date range (e.g., today, this week, next N days).
   
2. **Event Querying**:
   - `_query_events` constructs and executes a PostgreSQL query to retrieve events within the detected date range.
   
3. **Result Formatting**:
   - `_format_results` formats the raw query results into a more readable form, converting times and dates into strings.
   
4. **Summary Building**:
   - `_build_summary` groups events by date and formats them into a summary string, limiting the number of events displayed.

#### Integration Points
- **Mythos System**:
  - The `QueryCalendarSkill` class integrates with the Mythos skill system via the `SkillBase` class, which likely handles the overall skill execution and response framework.
  - The `execute` method is the primary integration point, receiving `SkillRequest` objects and returning `SkillResponse` objects.
- **Database**:
  - The `_get_conn` function connects to the PostgreSQL database, which is used to query the `calendar_events` table.
- **Environment Configuration**:
  - The `.env` file and environment variables are used to configure the PostgreSQL connection details, ensuring the skill can connect to the correct database.

This file is a critical component of the Mythos system, enabling users to interact with calendar events through natural language queries, and it integrates seamlessly with the broader Mythos infrastructure.
