# eval/challenges/query_routines/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### Documentation for `build_plan.json`

#### Purpose
This JSON file serves as a detailed build plan and configuration for the `QueryRoutinesSkill` class, which is designed to query and display today's routines and their completion status from a PostgreSQL database.

#### Architecture
The file is structured as a JSON object containing several key sections:
- **plan_id**: Identifies the plan.
- **version**: Version of the plan.
- **description**: Brief description of the plan's purpose.
- **pattern**: Indicates the type of skill (data query).
- **model_hint**: Specifies the model hint for the AI.
- **context**: Contains detailed information about the database schema, class structure, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Example test cases to validate the implementation.

#### Patterns
- **Singleton**: Not explicitly used, but `_get_conn` function ensures a single connection per call.
- **Factory**: Not used.
- **Observer**: Not used.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Class**: `QueryRoutinesSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Main method to query and format routines.
  - `_query_routines_today`: Queries today's routines and their completion status.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of completed and pending routines.

#### Database
- **Tables**:
  - `routines`: Contains routine information.
  - `routine_completions`: Contains completion status for each routine.
- **Columns**:
  - `routines`: `id`, `title`, `description`, `frequency`, `day_of_week`, `day_of_month`, `time_due`, `domain`, `priority`, `assigned_to`, `is_active`, `sort_order`.
  - `routine_completions`: `id`, `routine_id`, `due_date`, `status`, `completed_at`, `completed_by`, `notes`.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Key Logic
- **_query_routines_today**: Queries routines applicable today based on frequency and day of the week/month.
- **_format_results**: Formats the query results into a dictionary with routine details and completion status.
- **_build_summary**: Builds a summary string indicating the number of completed and pending routines.
- **execute**: Orchestrates the query, formatting, and summary building, returning a `SkillResponse` object.

#### Integration Points
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
- **SkillResponse**: Returns a `SkillResponse` object to the Mythos system, containing the formatted routines and summary.

### Detailed Breakdown of Build Plan Steps

1. **Write File Skeleton**:
   - Imports necessary modules.
   - Defines `_get_conn` function.
   - Skeleton of `QueryRoutinesSkill` class with all attributes and methods.

2. **Implement `_query_routines_today`**:
   - Connects to the database using `_get_conn`.
   - Queries today's routines and their completion status.
   - Ensures proper handling of connections and cursors.

3. **Implement `_format_results` and `_build_summary`**:
   - Formats query results into a dictionary.
   - Builds a summary string indicating completion status.

4. **Implement `execute`**:
   - Calls `_query_routines_today`.
   - Formats and summarizes the results.
   - Returns a `SkillResponse` object.

5. **Review and Finalize**:
   - Ensures all critical points are addressed.
   - Validates the implementation against test cases.

### Test Cases
- **"what are my routines today"**: Expects data containing "routines".
- **"have I done my daily tasks"**: Expects data containing "routines" and summary containing "Routine".
- **"checklist"**: Expects a valid response.

This JSON file provides a comprehensive guide for implementing the `QueryRoutinesSkill`, ensuring all aspects of the skill are covered from database interaction to final response formatting.
