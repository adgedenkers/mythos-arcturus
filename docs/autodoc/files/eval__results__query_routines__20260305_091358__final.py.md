# eval/results/query_routines/20260305_091358/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 123

---

### Documentation for `eval/results/query_routines/20260305_091358/final.py`

#### Purpose
This file contains the `QueryRoutinesSkill` class, which is responsible for querying and summarizing daily, weekly, and monthly routines from a PostgreSQL database and their completion status for the current day.

#### Architecture
- **Class Structure**: The `QueryRoutinesSkill` class extends `SkillBase` and includes methods for executing the query, formatting results, and building a summary.
- **Methods**:
  - `execute`: The main entry point that orchestrates the query, formatting, and summary building.
  - `_query_routines_today`: Queries the database for routines applicable today.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the routines and their completion status.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  1. The `execute` method is called with a request.
  2. `_query_routines_today` is called to fetch routines and their completion status.
  3. `_format_results` formats the fetched data.
  4. `_build_summary` generates a summary of the results.
  5. The `execute` method constructs and returns a `SkillResponse` object with the formatted results and summary.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it ensures a single database connection is established.
- **Factory**: The `SkillBase` class might be part of a factory pattern to create different types of skills.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `RealDictCursor`: For fetching results as dictionaries.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute`: Exposed to other parts of the system for executing the routine query.
- **Private Methods**:
  - `_query_routines_today`: For internal use to query routines.
  - `_format_results`: For internal use to format query results.
  - `_build_summary`: For internal use to build a summary of the results.

#### Database
- **Tables/Labels**:
  - `routines`: Contains routine information.
  - `routine_completions`: Contains completion status for routines.
  - `datetime`: Used for date and time operations.
  - `psycopg2`: PostgreSQL connection and cursor operations.
  - `dotenv`: Environment variable handling.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Database host.
  - `DB_NAME`: Database name.
  - `DB_USER`: Database user.
  - `DB_PASSWORD`: Database password.

#### Key Logic
- **Query Execution**:
  - The `_query_routines_today` method constructs a SQL query to fetch routines based on their frequency (daily, weekly, monthly) and their completion status for the current day.
- **Result Formatting**:
  - The `_format_results` method converts the raw query results into a more structured format, including completion status and timestamps.
- **Summary Building**:
  - The `_build_summary` method generates a summary of the routines, indicating how many are completed and which ones are still pending.

#### Integration Points
- **Mythos Subsystems**:
  - **Database Layer**: Uses PostgreSQL to fetch routine and completion data.
  - **Skill Engine**: Integrates with the skill engine to execute the query and return the results.
  - **Logging**: Uses the `logging` module to log errors and debug information.
  - **Environment Configuration**: Uses `dotenv` to load configuration from environment variables.

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines and their completion status, ensuring that users can easily track their tasks and progress.
