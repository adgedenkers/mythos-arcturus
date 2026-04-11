# eval/results/query_routines/20260305_091634/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 136

---

### Documentation for `eval/results/query_routines/20260305_091634/pass05_attempt01.py`

#### Purpose
This file contains the `QueryRoutinesSkill` class, which is responsible for querying and summarizing daily routines and their completion status from a PostgreSQL database. It provides an asynchronous `execute` method to handle incoming requests and generate a response with detailed routine information and completion status.

#### Architecture
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase` and contains methods for executing the query, formatting results, building summaries, and managing database connections.
- **Methods**:
  - `execute`: Asynchronous method to handle the request and return a `SkillResponse` object.
  - `_query_routines_today`: Fetches routines and their completion status for the current day.
  - `_format_results`: Formats the raw query results into a more user-friendly structure.
  - `_build_summary`: Constructs a summary of the routines and their completion status.
  - `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` method ensures a single connection is used throughout the class, though it does not explicitly implement a singleton pattern.
- **Factory**: The `SkillResponse` object is constructed based on the results of the query and formatting methods.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `RealDictCursor`, `load_dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: Uses `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` to configure the database connection.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Internal Methods**: `_query_routines_today`, `_format_results`, `_build_summary`, `_get_conn` are used internally to perform specific tasks.

#### Database
- **Tables**: `routines`, `routine_completions`.
- **Queries**: 
  - Fetches active routines with their completion status for the current day, considering daily, weekly, and monthly frequencies.
  - Uses a `LEFT JOIN` to include completion status from `routine_completions`.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `load_dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined to configure the skill.

#### Key Logic
- **Query Execution**: The `_query_routines_today` method constructs and executes a SQL query to fetch routines and their completion status for the current day.
- **Result Formatting**: The `_format_results` method transforms the raw query results into a more readable format, including completion status.
- **Summary Building**: The `_build_summary` method generates a summary of the routines and their completion status, providing a concise overview.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request handling and response generation.
- **Database**: Connects to the PostgreSQL database to fetch routine and completion data.

### Summary
The `QueryRoutinesSkill` class in this file is designed to query and summarize daily routines and their completion status from a PostgreSQL database. It handles incoming requests, executes database queries, formats results, and builds summaries, all while integrating with the Mythos skill system through the `SkillBase` class.
