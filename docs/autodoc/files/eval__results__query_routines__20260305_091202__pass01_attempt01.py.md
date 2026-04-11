# eval/results/query_routines/20260305_091202/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/query_routines/20260305_091202/pass01_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryRoutinesSkill`) that queries and formats the completion status of daily routines for the current day. It interacts with a PostgreSQL database to retrieve and process routine data.

#### Architecture
The file defines a single class `QueryRoutinesSkill` that inherits from `SkillBase`. The class includes several methods:
- `execute`: The main entry point for the skill, which orchestrates the querying, formatting, and summarizing of routine data.
- `_query_routines_today`: Queries the database for today's routines and their completion status.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary string indicating the number of completed routines and what remains.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` method could be considered a singleton pattern as it manages a single database connection.
- **Facade**: The `execute` method acts as a facade, abstracting the complex operations of querying, formatting, and summarizing into a single method.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging purposes.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- `execute`: Exposes an asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- `_query_routines_today`, `_format_results`, `_build_summary`, `_get_conn`: These methods are internal and not exposed to other parts of the system.

#### Database
- **Tables**: 
  - `routine_completions`: Used to check the completion status of routines.
  - `datetime`: Likely used for date-related operations.
  - `engine`: Possibly a table or schema related to the engine.
- **Neo4j Labels**: Not used in this file.

#### Configuration
- Uses environment variables loaded via `dotenv` for database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

#### Key Logic
- **Querying Routines**: The `_query_routines_today` method queries the database for today's routines and their completion status.
- **Formatting Results**: The `_format_results` method formats the raw query results into a more readable form.
- **Building Summary**: The `_build_summary` method creates a summary string indicating the number of completed routines and what remains.
- **Database Connection**: The `_get_conn` method establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **Database**: Connects to the PostgreSQL database to retrieve and process routine data.
- **Environment Variables**: Uses environment variables for database configuration, which are loaded via `dotenv`.

### Detailed Documentation

#### Class: `QueryRoutinesSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'query_routines'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show routines and their completion status for today'
  - `triggers`: List of strings that trigger this skill.
  - `cache_ttl`: Cache time-to-live in seconds.
- **Methods**:
  - `execute`: Asynchronous method that orchestrates the querying, formatting, and summarizing of routine data.
  - `_query_routines_today`: Queries the database for today's routines and their completion status.
  - `_format_results`: Formats the raw query results into a more readable form.
  - `_build_summary`: Builds a summary string indicating the number of completed routines and what remains.
  - `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Top-level Functions
- **`execute`**: Asynchronous function that takes a `request` and returns a `SkillResponse`. It orchestrates the querying, formatting, and summarizing of routine data.
- **`_query_routines_today`**: Queries the database for today's routines and their completion status.
- **`_format_results`**: Formats the raw query results into a more readable form.
- **`_build_summary`**: Builds a summary string indicating the number of completed routines and what remains.
- **`_get_conn`**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

### Example Usage
```python
# Example usage of QueryRoutinesSkill
skill = QueryRoutinesSkill()
response = await skill.execute(request)
```

This file is a crucial component of the Mythos system, providing the functionality to query and summarize daily routines and their completion status, and it integrates seamlessly with the system's skill framework and database infrastructure.
