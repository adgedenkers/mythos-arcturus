# eval/results/query_routines/20260305_091358/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### Documentation for `eval/results/query_routines/20260305_091358/pass03_attempt01.py`

#### Purpose
This file defines a skill (`QueryRoutinesSkill`) that queries the database for daily, weekly, and monthly routines applicable for today, checks their completion status, formats the results, and builds a summary of completed and remaining tasks.

#### Architecture
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Main method that orchestrates the query, formatting, and summarization.
  - `_query_routines_today`: Queries the database for routines applicable today.
  - `_format_results`: Formats the raw query results into a more readable form.
  - `_build_summary`: Builds a summary of the completed and remaining tasks.
- **Functions**:
  - `_get_conn`: Establishes a database connection.
  - `execute`: Top-level function that wraps the `QueryRoutinesSkill`'s `execute` method.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is established.
- **Factory**: The `QueryRoutinesSkill` class can be seen as a factory for creating instances that handle routine queries and summarization.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `request` and returns a `SkillResponse` object containing the summary and formatted results.
- **Top-level Functions**:
  - `_get_conn`: Returns a database connection.
  - `execute`: Wraps the `QueryRoutinesSkill`'s `execute` method.

#### Database
- **Tables**:
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion status of routines.
- **Queries**:
  - Queries `routines` and `routine_completions` to fetch routines applicable for today and their completion status.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Host for the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.

#### Key Logic
- **Query Logic**:
  - Queries routines with frequencies of 'daily', 'weekly', and 'monthly' that are applicable for today.
  - Uses a LEFT JOIN to include completion status from `routine_completions`.
- **Formatting Logic**:
  - Converts raw query results into a list of dictionaries with formatted fields.
- **Summary Logic**:
  - Counts completed and remaining tasks.
  - Builds a summary string indicating the number of completed tasks and lists the titles of completed and remaining tasks.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Uses PostgreSQL to query routines and their completion status.
  - **Skill System**: Integrates with the Mythos skill system by inheriting from `SkillBase` and implementing the `execute` method.
  - **Environment Configuration**: Uses environment variables for database connection details.

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines, which can be integrated into various user interfaces or automated workflows within the Mythos platform.
