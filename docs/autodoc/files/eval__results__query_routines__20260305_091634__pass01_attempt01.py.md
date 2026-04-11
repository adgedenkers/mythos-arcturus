# eval/results/query_routines/20260305_091634/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: eval/results/query_routines/20260305_091634/pass01_attempt01.py

#### Purpose
This file defines a skill (`QueryRoutinesSkill`) for the Mythos system that queries and formats daily routines and their completion status for the current day. It handles requests to check what routines need to be done and provides a summary of completed and pending tasks.

#### Architecture
The file contains a single class `QueryRoutinesSkill` that inherits from `SkillBase`. The class includes methods for executing the skill, querying routines, formatting results, building a summary, and getting a database connection. There are also top-level functions that are not part of the class but are likely to be used within the class methods.

#### Patterns
- **Singleton**: The `_get_conn` method could be used to implement a singleton pattern for database connections, ensuring only one connection is active at a time.
- **Factory**: The `execute` method could be seen as a factory method that orchestrates the creation and processing of routine data.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `psycopg2`, `dotenv`
- **External Libraries**: `psycopg2` for PostgreSQL database operations, `dotenv` for loading environment variables from `.env` files.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_query_routines_today`: Queries routines for today.
  - `_format_results`: Formats the queried results.
  - `_build_summary`: Builds a summary of the results.
  - `_get_conn`: Establishes a database connection.

#### Database
- **Tables/Labels**:
  - `routine_completions`: Table used to check the completion status of routines.
  - `datetime`: Likely used for date and time operations.
  - `psycopg2`: PostgreSQL adapter used for database operations.
  - `dotenv`: Used for loading environment variables.
  - `engine`: Likely part of the Mythos system's core engine.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
1. **Querying Routines**: `_query_routines_today` retrieves active routines for the current day, including daily, weekly, and monthly routines, and checks their completion status.
2. **Formatting Results**: `_format_results` processes the raw query results to include completion indicators.
3. **Building Summary**: `_build_summary` creates a summary string indicating how many routines are complete and which ones are pending.
4. **Database Connection**: `_get_conn` establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos system's request-response model.
- **Database**: The `_get_conn` method integrates with the PostgreSQL database to fetch and process routine data.

### Detailed Documentation

#### Class: `QueryRoutinesSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'query_routines'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show routines and their completion status for today'
  - `triggers`: List of trigger phrases for invoking the skill.
  - `cache_ttl`: Time-to-live for caching results (300 seconds).

- **Methods**:
  - `execute`: Asynchronous method that orchestrates the querying, formatting, and summarizing of routines.
  - `_query_routines_today`: Queries routines for today, including completion status.
  - `_format_results`: Formats the queried results.
  - `_build_summary`: Builds a summary of the results.
  - `_get_conn`: Establishes a database connection.

#### Top-Level Functions
- **`execute`**: Asynchronous function that takes a `request` and returns a `SkillResponse`.
- **`_query_routines_today`**: Queries routines for today.
- **`_format_results`**: Formats the queried results.
- **`_build_summary`**: Builds a summary of the results.
- **`_get_conn`**: Establishes a database connection.

#### Database Operations
- **Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **Queries**: Likely queries the `routine_completions` table to check completion status.

#### Configuration
- **Environment Variables**: Uses `dotenv` to load database connection details from environment variables.

This file is a crucial part of the Mythos system, providing a structured way to query and summarize daily routines and their completion status.
