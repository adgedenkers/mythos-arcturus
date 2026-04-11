# eval/results/query_routines/20260305_091358/pass05_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Documentation for `eval/results/query_routines/20260305_091358/pass05_attempt05.py`

#### 1. Purpose
This file contains a class `QueryRoutinesSkill` that queries the PostgreSQL database to retrieve and summarize daily, weekly, and monthly routines along with their completion status for the current day. It formats the results and builds a summary to be returned as a `SkillResponse`.

#### 2. Architecture
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase` and implements methods to execute the query, format results, and build a summary.
- **Methods**:
  - `execute`: Main method that orchestrates the query, formatting, and summary building.
  - `_query_routines_today`: Queries the database for routines applicable today.
  - `_format_results`: Formats the raw query results into a more readable structure.
  - `_build_summary`: Builds a summary of the routines and their completion status.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.

#### 3. Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it ensures a single database connection is established.
- **Factory**: The `execute` method could be seen as a factory method that produces a `SkillResponse` object.

#### 4. Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `dotenv`, `engine.base`
- **Database Tables**: `routines`, `routine_completions`

#### 5. Interfaces
- **Exposed Methods**: `execute` is the primary method exposed to other parts of the system.
- **Exposed Classes**: `QueryRoutinesSkill` is the main class that other parts of the system interact with.

#### 6. Database
- **Tables**: `routines`, `routine_completions`
- **Queries**: The `_query_routines_today` method performs a LEFT JOIN query on `routines` and `routine_completions` to fetch routines applicable for the current day along with their completion status.

#### 7. Configuration
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **Configuration Files**: `.env` file is loaded using `dotenv.load_dotenv()` to set environment variables.

#### 8. Key Logic
- **Query Execution**: The `_query_routines_today` method constructs a SQL query to fetch routines based on their frequency and the current date.
- **Result Formatting**: The `_format_results` method converts the raw query results into a more structured format, including completion status.
- **Summary Building**: The `_build_summary` method generates a summary of the routines, indicating how many are completed and which ones are still pending.

#### 9. Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method returns a `SkillResponse` object, which is likely used by other parts of the system to handle the response.
- **Database Connection**: The `_get_conn` function is used to establish a database connection, which is a critical integration point with the PostgreSQL database.

### Detailed Explanation

#### Class: `QueryRoutinesSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Define metadata about the skill.
- **Methods**:
  - `execute`: The main method that handles the execution of the skill. It queries routines, formats the results, builds a summary, and returns a `SkillResponse`.
  - `_query_routines_today`: Queries the database for routines applicable today and returns the results.
  - `_format_results`: Formats the raw query results into a more structured format.
  - `_build_summary`: Builds a summary of the routines and their completion status.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Database Operations
- **_query_routines_today**: Performs a LEFT JOIN query on `routines` and `routine_completions` to fetch routines applicable for the current day along with their completion status.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

#### Integration
- **SkillBase**: The class integrates with the broader Mythos system's skill framework through inheritance and the use of `SkillRequest` and `SkillResponse` objects.

This file is a critical component of the Mythos system, providing a structured way to query and summarize daily routines and their completion status.
