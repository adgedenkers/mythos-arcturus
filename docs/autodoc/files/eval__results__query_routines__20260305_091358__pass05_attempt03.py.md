# eval/results/query_routines/20260305_091358/pass05_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Documentation for `eval/results/query_routines/20260305_091358/pass05_attempt03.py`

#### Purpose
This file defines a skill (`QueryRoutinesSkill`) that queries the database to retrieve and summarize the user's daily, weekly, and monthly routines along with their completion status for the current day.

#### Architecture
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase` and contains methods for executing the query, formatting results, and building a summary.
- **Methods**:
  - `execute`: Main method that orchestrates the query, formatting, and summary building.
  - `_query_routines_today`: Queries the database for routines applicable today.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the routines, indicating which are completed and which remain.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern for database connection management, although it is not explicitly implemented as a singleton class.
- **Facade**: The `QueryRoutinesSkill` class acts as a facade, abstracting the complex database interactions and result processing into a simple `execute` method.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database interactions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From `engine.base` for skill framework.

#### Interfaces
- **Exposed Methods**:
  - `execute(request)`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse` containing the formatted routines and summary.

#### Database
- **Tables/Labels**:
  - `routines`: Stores routine definitions.
  - `routine_completions`: Stores completion status for routines.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Hostname for the PostgreSQL database.
  - `DB_NAME`: Name of the database.
  - `DB_USER`: Username for database access.
  - `DB_PASSWORD`: Password for database access.

#### Key Logic
- **Execution Flow**:
  1. **Query Routines**: `_query_routines_today` retrieves routines applicable for today, including daily, weekly, and monthly routines.
  2. **Format Results**: `_format_results` processes the raw query results into a more readable format.
  3. **Build Summary**: `_build_summary` creates a summary of completed and remaining routines.
  4. **Return Response**: The `execute` method constructs and returns a `SkillResponse` object with the formatted routines and summary.

- **Database Query**:
  - The query in `_query_routines_today` fetches routines based on their frequency and the current date, joining with `routine_completions` to get the completion status.

#### Integration Points
- **Skill Execution**: The `execute` method is designed to be called by the Mythos skill execution framework, which handles the request and response lifecycle.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, which is a critical integration point for data retrieval and processing.

This file is a crucial component of the Mythos system, providing a structured way to retrieve and summarize daily routines, which can be integrated into various user-facing interfaces for task management and tracking.
