# eval/results/query_routines/20260305_091634/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 84

---

### File: `eval/results/query_routines/20260305_091634/pass02_attempt01.py`

#### Purpose
This file contains the `QueryRoutinesSkill` class, which is responsible for querying the database to retrieve and format daily, weekly, and monthly routines along with their completion status for the current day. It integrates with the PostgreSQL database to fetch routine data and completion statuses.

#### Architecture
The file defines a single class `QueryRoutinesSkill` that inherits from `SkillBase`. This class contains several methods:
- `execute`: The main entry point for executing the skill.
- `_query_routines_today`: Queries the database for active routines applicable today.
- `_format_results`: Formats the retrieved routine data.
- `_build_summary`: Builds a summary of the routine completion status.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` method could be considered a form of singleton pattern for database connections, as it ensures a single connection is used throughout the class.
- **Factory**: The `_get_conn` method can be seen as a factory method for creating database connections.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `request` and returns a `SkillResponse`.
- **Private Methods**:
  - `_query_routines_today`: Queries the database for today's routines.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the routines.
  - `_get_conn`: Establishes a database connection.

#### Database
- **Tables/Labels**:
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion status of routines.
  - `datetime`: Used for date and time operations.
  - `psycopg2`: PostgreSQL database operations.
  - `dotenv`: Environment variable handling.
  - `engine`: Base skill class.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Hostname of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port number for the PostgreSQL database.

#### Key Logic
- **_query_routines_today**:
  - Queries the `routines` table and `routine_completions` table for active routines applicable today based on frequency (daily, weekly, monthly).
  - Uses a LEFT JOIN to include completion status for today's date.
  - Filters routines by active status and frequency.
  - Orders the results by sort order and title.

- **_format_results**:
  - Formats the query results into a more readable and structured form.

- **_build_summary**:
  - Builds a summary string indicating the number of completed routines and what remains to be done.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, which provides a base structure for skills.
- **Database**: Connects to the PostgreSQL database to fetch routine data and completion statuses.
- **Environment Variables**: Uses environment variables for database connection details.
- **Logging**: Uses the `logging` module to log errors.

### Summary
This file is a crucial component of the Mythos system, handling the retrieval and formatting of daily routines and their completion statuses. It integrates with the PostgreSQL database to fetch and process data, and it is designed to be part of a larger skill-based system.
