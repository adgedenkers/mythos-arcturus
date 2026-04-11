# eval/results/query_routines/20260305_091358/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 47

---

### File: `eval/results/query_routines/20260305_091358/pass01_attempt01.py`

#### Purpose
This file contains a class `QueryRoutinesSkill` that is responsible for querying and summarizing daily routines and their completion status from a PostgreSQL database. It is designed to be part of a larger skill-based system, likely integrated with a FastAPI service.

#### Architecture
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that orchestrates the querying and summarizing process.
  - `_query_routines_today`: Fetches routines and their completion status for the current day.
  - `_format_results`: Formats the raw query results into a more readable form.
  - `_build_summary`: Builds a summary of the routines and their completion status.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: An additional top-level function that might be used for testing or direct execution.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it creates a database connection, which is a common resource.
- **Factory**: The `execute` method acts as a factory for creating the final response by orchestrating other methods.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging purposes.
  - `psycopg2`: For PostgreSQL database interaction.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Public method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**:
  - `_query_routines_today`: Fetches routines and their completion status.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the routines.

#### Database
- **Tables/Labels**:
  - `routine_completions`: Table used to store the completion status of routines.
  - `datetime`: Likely used for date-related queries.
  - `engine`: Likely a reference to the database engine or connection pool.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Used to configure the PostgreSQL connection.

#### Key Logic
- **`execute` Method**:
  1. Queries active routines applicable today.
  2. Checks the completion status for today.
  3. Formats the results with done/not-done indicators.
  4. Summarizes the completion status (e.g., "N of M complete").
- **`_query_routines_today` Method**:
  - Fetches active daily routines, weekly routines for today's day, and monthly routines for today's date.
  - Performs a LEFT JOIN with `routine_completions` for today's date.
- **`_format_results` Method**:
  - Takes raw query results and formats them into a more readable form.
- **`_build_summary` Method**:
  - Constructs a summary string indicating the number of completed routines and what remains.

#### Integration Points
- **SkillBase Integration**:
  - The `QueryRoutinesSkill` class inherits from `SkillBase`, integrating with the broader skill-based system.
- **Database Integration**:
  - Uses `_get_conn` to establish a connection to the PostgreSQL database, likely integrating with other parts of the system that also use this database.
- **FastAPI Integration**:
  - The `execute` method is designed to be called from a FastAPI endpoint, handling incoming requests and returning responses.

### Summary
This file provides a modular and structured approach to querying and summarizing daily routines from a PostgreSQL database. It integrates well with the broader Mythos system, leveraging environment variables for configuration and following a clear separation of concerns through its methods and classes.
