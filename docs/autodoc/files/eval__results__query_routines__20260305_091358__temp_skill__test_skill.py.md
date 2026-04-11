# eval/results/query_routines/20260305_091358/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 123

---

### File: `eval/results/query_routines/20260305_091358/temp_skill/test_skill.py`

#### Purpose
This file contains a class `QueryRoutinesSkill` that queries PostgreSQL to retrieve daily, weekly, and monthly routines along with their completion status for the current day. It formats the results and builds a summary to provide a comprehensive overview of the routines and their completion status.

#### Architecture
The file contains a single class `QueryRoutinesSkill` which inherits from `SkillBase`. The class has the following methods:
- `execute`: Main method that orchestrates the querying, formatting, and summarizing of routines.
- `_query_routines_today`: Queries the PostgreSQL database to retrieve routines and their completion status for the current day.
- `_format_results`: Formats the raw query results into a more readable and structured format.
- `_build_summary`: Builds a summary string based on the formatted results.

Additionally, there is a top-level function `_get_conn` that establishes a connection to the PostgreSQL database.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it provides a single point of connection to the database.
- **Facade**: The `execute` method acts as a facade, abstracting the complex operations of querying, formatting, and summarizing into a single method call.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `psycopg2`: For connecting to and querying the PostgreSQL database.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- `execute`: Exposes an asynchronous method that takes a `request` and returns a `SkillResponse` object containing the formatted routines and a summary.
- `_query_routines_today`: Internal method that queries the database and returns the raw results.
- `_format_results`: Internal method that formats the raw results into a more structured format.
- `_build_summary`: Internal method that builds a summary string from the formatted results.

#### Database
- **Tables/Labels**: 
  - `routines`: Contains the routine details.
  - `routine_completions`: Contains the completion status of routines.
  - `datetime`: Used to determine the current date and day of the week/month.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.

#### Key Logic
1. **Querying Routines**: The `_query_routines_today` method constructs a SQL query to retrieve routines and their completion status for the current day. It filters routines based on their frequency (daily, weekly, monthly) and joins with the `routine_completions` table to get the completion status.
2. **Formatting Results**: The `_format_results` method transforms the raw query results into a more readable format, including the completion status and time due.
3. **Building Summary**: The `_build_summary` method generates a summary string that includes the total number of routines, the number of completed routines, and lists the titles of completed and remaining routines.

#### Integration Points
- **SkillBase Integration**: The `QueryRoutinesSkill` class extends `SkillBase` and integrates with the Mythos system through the `execute` method, which is called when a skill is triggered.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_query_routines_today` method to execute the query.

This file is a crucial component of the Mythos system, providing a structured and summarized view of daily routines and their completion status, which can be used for user notifications, task management, and other integrations within the Mythos platform.
