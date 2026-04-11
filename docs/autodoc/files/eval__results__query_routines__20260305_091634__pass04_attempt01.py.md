# eval/results/query_routines/20260305_091634/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 133

---

### File: eval/results/query_routines/20260305_091634/pass04_attempt01.py

#### Purpose
This file contains the `QueryRoutinesSkill` class, which is responsible for querying the database for daily routines and their completion status, formatting the results, and providing a summary of the routines for the current day.

#### Architecture
The file is structured around the `QueryRoutinesSkill` class, which inherits from `SkillBase`. The class contains several methods:
- `execute`: The main method that orchestrates the querying, formatting, and summarizing of routines.
- `_query_routines_today`: Queries the database for routines applicable today.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the routines, indicating how many are completed and which ones remain.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` method ensures that a connection is established only once and reused, which is a form of the Singleton pattern.
- **Factory**: The `SkillResponse` object is created based on the processed data, which can be seen as a factory method.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the public method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**: `_query_routines_today`, `_format_results`, `_build_summary`, `_get_conn` are internal methods used by `execute`.

#### Database
- **Tables**: `routines`, `routine_completions`.
- **Queries**: 
  - `_query_routines_today` queries the `routines` table and left joins `routine_completions` to get the completion status for today.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
1. **Query Execution**: The `_query_routines_today` method queries the database for routines applicable today, including daily, weekly, and monthly routines, and their completion status.
2. **Result Formatting**: The `_format_results` method formats the query results into a more user-friendly structure, indicating whether each routine is completed.
3. **Summary Building**: The `_build_summary` method creates a summary of the routines, indicating how many are completed and which ones remain.

#### Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **Database**: The `_get_conn` method connects to the PostgreSQL database, integrating with the database subsystem.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, integrating with the response handling subsystem.

### Detailed Documentation

#### Class: `QueryRoutinesSkill`
- **Inheritance**: `SkillBase`
- **Attributes**:
  - `name`: 'query_routines'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show routines and their completion status for today'
  - `triggers`: List of strings that trigger this skill
  - `cache_ttl`: 300 seconds

- **Methods**:
  - `execute`: Asynchronous method that executes the skill, querying routines, formatting results, and building a summary.
  - `_query_routines_today`: Queries the database for routines applicable today.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the routines, indicating how many are completed and which ones remain.
  - `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Top-Level Functions
- **execute**: Asynchronous function that orchestrates the querying, formatting, and summarizing of routines.
- **_query_routines_today**: Queries the database for routines applicable today.
- **_format_results**: Formats the raw query results into a more readable structure.
- **_build_summary**: Builds a summary of the routines, indicating how many are completed and which ones remain.
- **_get_conn**: Establishes a connection to the PostgreSQL database.

### Example Usage
```python
# Example usage of QueryRoutinesSkill
skill = QueryRoutinesSkill()
response = await skill.execute(request)
print(response.summary)
```

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines and their completion status.
