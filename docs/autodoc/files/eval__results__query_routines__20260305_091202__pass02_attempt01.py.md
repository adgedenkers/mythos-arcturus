# eval/results/query_routines/20260305_091202/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 81

---

### Documentation for `eval/results/query_routines/20260305_091202/pass02_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryRoutinesSkill`) that queries the database for daily, weekly, and monthly routines and their completion status for the current day. It formats the results and builds a summary to be returned to the user.

#### Architecture
The file defines a single class `QueryRoutinesSkill` that inherits from `SkillBase`. The class contains several methods:
- `execute`: The main entry point for the skill, which orchestrates the querying, formatting, and summarizing of the routines.
- `_query_routines_today`: Queries the database for routines applicable today.
- `_format_results`: Formats the query results.
- `_build_summary`: Builds a summary of the routines and their completion status.
- `_get_conn`: Establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton Pattern**: The `_get_conn` method ensures that a database connection is established only once and reused.
- **Factory Method Pattern**: The `_get_conn` method can be seen as a factory method that creates and returns a database connection object.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging purposes.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- `execute`: Exposed method that takes a `SkillRequest` and returns a `SkillResponse`.
- `_query_routines_today`, `_format_results`, `_build_summary`, `_get_conn`: Private methods used internally by the class.

#### Database
- **Tables/Labels**: 
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion status of routines.
  - `datetime`: Used for date and time operations.
  - `psycopg2`: PostgreSQL database connection.
  - `dotenv`: Environment variables for database connection details.
  - `engine`: Base module for skill operations.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port for the PostgreSQL database.

#### Key Logic
- **_query_routines_today**: 
  - Queries the `routines` table for routines that are active and applicable for today based on their frequency (daily, weekly, monthly).
  - Left joins the `routine_completions` table to check the completion status for today.
  - Returns a list of dictionaries containing routine details and completion status.
- **_format_results**: 
  - Formats the raw query results into a more user-friendly format.
- **_build_summary**: 
  - Constructs a summary string indicating the number of completed routines and the remaining ones.

#### Integration Points
- **SkillBase**: The `QueryRoutinesSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database**: Uses PostgreSQL for querying routines and their completion status.
- **Environment Variables**: Relies on environment variables for database connection details, loaded via `dotenv`.

### Summary
This file implements a skill that queries the PostgreSQL database for daily routines and their completion status, formats the results, and builds a summary. It integrates with the Mythos skill system and uses environment variables for database configuration.
