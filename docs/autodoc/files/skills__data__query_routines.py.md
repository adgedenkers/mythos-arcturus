# skills/data/query_routines.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 136

---

### File: skills/data/query_routines.py

#### Purpose
This file contains the `QueryRoutinesSkill` class, which is responsible for querying and summarizing daily routines and their completion status from a PostgreSQL database. It is designed to provide a summary of today's routines and their completion status.

#### Architecture
The file consists of a single class `QueryRoutinesSkill` that inherits from `SkillBase`. The class contains several methods:
- `execute`: The main entry point for the skill, which orchestrates the querying, formatting, and summarizing of routines.
- `_query_routines_today`: Queries the database for today's routines and their completion status.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the routines, indicating how many are complete and which ones remain.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` method can be considered a form of singleton pattern, as it ensures a single database connection is established and reused.
- **Facade**: The `execute` method acts as a facade, abstracting the complex logic of querying, formatting, and summarizing routines.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module, which likely provides the base class and response structures for skills.

#### Interfaces
- `execute`: Exposes an asynchronous method that takes a `request` and returns a `SkillResponse` object containing the routines, their completion status, and a summary.

#### Database
- **Tables**: 
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion status for routines.
- **Queries**: The `_query_routines_today` method queries the `routines` table and performs a LEFT JOIN with `routine_completions` to get the completion status for today's routines.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to establish a connection to the PostgreSQL database.
- **Dotenv**: The `dotenv` module is used to load environment variables from a `.env` file.

#### Key Logic
- **Querying Routines**: The `_query_routines_today` method constructs a query to fetch routines that are active and applicable for today based on their frequency (daily, weekly, monthly).
- **Formatting Results**: The `_format_results` method converts the raw query results into a more readable format, including completion status and timestamps.
- **Building Summary**: The `_build_summary` method generates a summary of the routines, indicating how many are complete and which ones remain.

#### Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, indicating it integrates with the Mythos skill system.
- **Database Connection**: The `_get_conn` method establishes a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, which is likely used to integrate with the Mythos response handling system.

### Summary
The `QueryRoutinesSkill` class in `query_routines.py` is designed to query and summarize daily routines and their completion status from a PostgreSQL database. It integrates with the Mythos skill system and database infrastructure, providing a structured response that includes a summary of today's routines.
