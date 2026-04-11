# eval/results/complete_routine/20260305_092840/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 134

---

### Documentation for `eval/results/complete_routine/20260305_092840/final.py`

#### Purpose
This file contains the implementation of a skill (`CompleteRoutineSkill`) that marks a specified routine as completed for the current day. It interacts with a PostgreSQL database to find and update routine completion records.

#### Architecture
- **Class**: `CompleteRoutineSkill` inherits from `SkillBase` and implements the `execute` method to handle the skill execution.
- **Methods**:
  - `execute`: The main method that processes the request, finds the routine, and marks it as completed.
  - `_find_routine`: Helper method to find the routine from the message.
  - `_mark_complete`: Helper method to mark the routine as completed in the database.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential direct execution.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connections, ensuring a single connection is created and reused.
- **Factory**: The `SkillResponse` object creation can be seen as a factory method pattern, producing responses based on the outcome of the routine completion process.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `RealDictCursor`: For fetching results as dictionaries.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed for skill execution, taking a `SkillRequest` and returning a `SkillResponse`.
- **Top-level Functions**:
  - `_get_conn`: Exposed for database connection management.
  - `execute`: Exposed for direct execution of the skill.

#### Database
- **Tables/Labels**:
  - `routines`: Used to find active routines.
  - `routine_completions`: Used to insert or update completion records.
  - `today`: Used to determine the current date for completion records.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configured for database connection.
- **Config Files**:
  - `.env`: Loaded using `dotenv` for environment variables.

#### Key Logic
1. **Routine Identification**:
   - The `_find_routine` method processes the message to identify the routine by removing trigger phrases and querying the `routines` table.
2. **Routine Completion**:
   - The `_mark_complete` method inserts or updates the `routine_completions` table to mark the routine as completed for the current day.
3. **Error Handling**:
   - Proper error handling and logging are implemented to manage exceptions and ensure database transactions are rolled back on failure.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Interacts with PostgreSQL to query and update routine and completion records.
  - **Skill Engine**: Integrates with the skill engine via `SkillBase` and `SkillResponse` for request and response handling.
  - **Environment Configuration**: Uses environment variables and `.env` for configuration.

This file is a critical component of the Mythos system, enabling users to mark routines as completed and updating the system's state accordingly.
