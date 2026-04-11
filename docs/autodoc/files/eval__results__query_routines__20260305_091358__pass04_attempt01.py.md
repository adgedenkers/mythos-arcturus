# eval/results/query_routines/20260305_091358/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 123

---

### Documentation for `eval/results/query_routines/20260305_091358/pass04_attempt01.py`

#### Purpose
This file defines a skill (`QueryRoutinesSkill`) that queries the database to retrieve and summarize the user's daily, weekly, and monthly routines along with their completion status for the current day.

#### Architecture
The file contains a single class `QueryRoutinesSkill` that inherits from `SkillBase`. It includes methods for executing the query, formatting results, and building a summary. There are also top-level functions for establishing a database connection and executing the query.

- **Classes**:
  - `QueryRoutinesSkill`: Inherits from `SkillBase` and contains methods to execute the query, format results, and build a summary.
  
- **Methods**:
  - `execute`: Main method that orchestrates the query, formatting, and summary building.
  - `_query_routines_today`: Queries the database for today's routines and their completion status.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the routines and their completion status.

- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential external use.

#### Patterns
- **Singleton**: Not explicitly used, but `_get_conn` could be modified to act as a singleton to ensure a single database connection is reused.
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `RealDictCursor`: For fetching results as dictionaries.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `request` and returns a `SkillResponse` object containing the query results and summary.

#### Database
- **Tables/Labels**:
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion status for routines.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Hostname of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.

#### Key Logic
1. **Query Execution**:
   - `_query_routines_today`: Queries the database for routines that are active and applicable for today (daily, weekly, or monthly) along with their completion status.
   
2. **Result Formatting**:
   - `_format_results`: Converts the raw query results into a more readable format, including completion status and timestamps.

3. **Summary Building**:
   - `_build_summary`: Constructs a summary of the routines, indicating how many are completed and which ones are still pending.

#### Integration Points
- **SkillBase Integration**:
  - The `QueryRoutinesSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database Integration**:
  - Uses PostgreSQL for querying routines and their completion status.
- **Environment Configuration**:
  - Relies on environment variables for database connection details, loaded via `dotenv`.

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines, which can be integrated into various user interfaces or automated processes within the system.
