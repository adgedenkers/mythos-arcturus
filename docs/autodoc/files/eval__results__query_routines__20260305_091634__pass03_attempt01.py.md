# eval/results/query_routines/20260305_091634/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 115

---

### Documentation for `eval/results/query_routines/20260305_091634/pass03_attempt01.py`

#### Purpose
This file defines a `QueryRoutinesSkill` class that queries the PostgreSQL database for daily, weekly, and monthly routines and their completion status for the current day. It formats the results and provides a summary of completed and pending routines.

#### Architecture
The file contains a single class `QueryRoutinesSkill` which inherits from `SkillBase`. The class has several methods:
- `execute`: The main entry point for the skill, which orchestrates the querying, formatting, and summarizing of routines.
- `_query_routines_today`: Queries the database for routines applicable today.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the routine completion status.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton Pattern**: The `_get_conn` method can be considered a form of singleton pattern as it ensures a single database connection is established and reused.
- **Factory Method**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `dotenv`
- **External Libraries**: `psycopg2` for PostgreSQL database operations, `dotenv` for environment variable loading.

#### Interfaces
- **Public Methods**: `execute` is the primary public method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**: `_query_routines_today`, `_format_results`, `_build_summary`, `_get_conn` are internal methods used by `execute`.

#### Database
- **Tables**: `routines`, `routine_completions`
- **Operations**: 
  - `routines`: SELECT operations to fetch routines based on frequency and active status.
  - `routine_completions`: LEFT JOIN to fetch completion status for today.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.

#### Key Logic
- **Query Logic**: The `_query_routines_today` method constructs a SQL query to fetch routines applicable for today based on their frequency (daily, weekly, monthly) and their completion status.
- **Result Formatting**: The `_format_results` method transforms the raw query results into a more structured format, including completion status.
- **Summary Building**: The `_build_summary` method generates a summary of the completion status, indicating how many routines are complete and which ones remain.

#### Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, indicating it integrates with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request-response model.
- **Database Connection**: The `_get_conn` method establishes a connection to the PostgreSQL database, integrating with the Mythos database layer.

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines and their completion status, which can be integrated into various user-facing interfaces or automated processes within the Mythos platform.
