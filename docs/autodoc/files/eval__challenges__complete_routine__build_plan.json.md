# eval/challenges/complete_routine/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 35

---

### Documentation for `eval/challenges/complete_routine/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a skill in the Mythos system that marks a routine as completed for the current day. It includes detailed instructions, patterns, and test cases to guide the implementation.

#### Architecture
The JSON file is structured into several key sections:
- **plan_id**: Identifies the plan.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the plan.
- **pattern**: Indicates the type of skill (action_skill).
- **model_hint**: Suggests a model to use (qwen3-coder:30b).
- **context**: Contains detailed information about the database schema, class structure, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Provides test cases to validate the implementation.

#### Patterns
- **Factory Method**: The `_get_conn` function is a factory method for creating database connections.
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection instance.
- **Observer**: The `SkillBase` class could be part of an observer pattern where the skill observes user actions and responds accordingly.

#### Dependencies
- **Imports**: The file specifies imports such as `os`, `logging`, `datetime`, `psycopg2`, `RealDictCursor`, `dotenv`, and `engine.base`.
- **Environment Variables**: Uses environment variables for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Interfaces
- **Class**: `CompleteRoutineSkill` extends `SkillBase` and implements methods like `execute`, `_find_routine`, and `_mark_complete`.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object with specific attributes (`skill_name`, `data`, `summary`, `confidence`, `sources`, `error`).

#### Database
- **Tables**: 
  - `routines`: Contains columns `id`, `title`, and `is_active`.
  - `routine_completions`: Contains columns `id`, `routine_id`, `due_date`, `status`, `completed_at`, `completed_by`, and `notes`.
- **Operations**: 
  - `_find_routine` queries the `routines` table to find an active routine by title.
  - `_mark_complete` inserts or updates the `routine_completions` table to mark a routine as completed.

#### Configuration
- **Environment Variables**: The `_get_conn` function uses environment variables for database connection details.
- **ASCII Only**: Comments and strings are restricted to ASCII characters.

#### Key Logic
- **_find_routine**: Cleans the input message, removes trigger phrases, and queries the `routines` table to find a matching routine by title.
- **_mark_complete**: Inserts or updates the `routine_completions` table to mark a routine as completed for the current day.
- **execute**: Coordinates the process by calling `_find_routine` and `_mark_complete`, and returns a `SkillResponse` object.

#### Integration Points
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
- **SkillResponse**: Returns `SkillResponse` objects to communicate with the Mythos system.

### Detailed Breakdown

#### `context` Section
- **system_context**: Provides details about the database and required imports.
- **table_schema**: Describes the structure of the `routines` and `routine_completions` tables.
- **scaffold**: Outlines the class structure and methods for `CompleteRoutineSkill`.
- **mandatory_patterns**: Specifies critical patterns such as `_get_conn`, connection cleanup, ASCII-only comments, and specific column names.

#### `build_plan` Section
- **Pass 1**: Write the file skeleton with required imports and class structure.
- **Pass 2**: Implement `_find_routine` to find the matching routine by title.
- **Pass 3**: Implement `_mark_complete` to insert or update the completion status.
- **Pass 4**: Implement `execute` to coordinate the routine completion process.
- **Pass 5**: Review and ensure all critical patterns and requirements are met.

#### `test_cases` Section
- Provides test cases to validate the implementation, ensuring correct behavior for different input messages.

This JSON file serves as a comprehensive guide for developing the `CompleteRoutineSkill` in the Mythos system, ensuring consistency, correctness, and integration with the existing infrastructure.
