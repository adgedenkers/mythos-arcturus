# eval/results/query_routines/20260305_091358/pass05_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Purpose
The `pass05_attempt04.py` file contains the `QueryRoutinesSkill` class, which is responsible for querying and summarizing daily, weekly, and monthly routines from a PostgreSQL database, along with their completion status for the current day.

### Architecture
The file is structured around a single class `QueryRoutinesSkill` that inherits from `SkillBase`. It contains several methods:
- `execute`: The main entry point that orchestrates the querying, formatting, and summarizing of routines.
- `_query_routines_today`: Queries the database for routines applicable for today.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the routines and their completion status.

Additionally, there are two top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential use outside the class context.

### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **Database**: PostgreSQL tables `routines` and `routine_completions`

### Interfaces
- **Public Methods**: `execute` (async method)
- **Internal Methods**: `_query_routines_today`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

### Database
- **Tables**: `routines`, `routine_completions`
- **Queries**: 
  - Selects routines based on their frequency (daily, weekly, monthly) and their completion status for the current day.
  - Joins `routines` with `routine_completions` to get the completion status.

### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

### Key Logic
1. **Querying Routines**: The `_query_routines_today` method queries the database for routines that are active and applicable for today based on their frequency (daily, weekly, monthly).
2. **Formatting Results**: The `_format_results` method formats the raw query results into a more structured format, including completion status.
3. **Building Summary**: The `_build_summary` method constructs a summary of the routines, indicating how many are completed and which ones remain.

### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the broader Mythos system through the `execute` method, which returns a `SkillResponse` object.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, ensuring seamless integration with the database layer.
- **Environment Configuration**: Relies on environment variables for database connection details, allowing for easy configuration and deployment.

### Summary
The `QueryRoutinesSkill` class in `pass05_attempt04.py` is designed to query and summarize daily routines from a PostgreSQL database, providing a structured summary of completion status. It integrates with the Mythos system through the `SkillBase` class and uses environment variables for configuration, ensuring flexibility and ease of deployment.
