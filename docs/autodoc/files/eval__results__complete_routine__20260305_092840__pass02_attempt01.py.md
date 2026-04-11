# eval/results/complete_routine/20260305_092840/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 83

---

### File: eval/results/complete_routine/20260305_092840/pass02_attempt01.py

#### Purpose
This file contains the implementation of a skill (`CompleteRoutineSkill`) that marks a routine as completed based on user input. It interacts with a PostgreSQL database to find and update routine completion records.

#### Architecture
The file consists of:
- A top-level function `_get_conn()` for establishing a database connection.
- A top-level asynchronous function `execute()` that handles the main execution logic.
- A class `CompleteRoutineSkill` that inherits from `SkillBase` and implements the `execute`, `_find_routine`, and `_mark_complete` methods.

#### Patterns
- **Factory Method**: The `_get_conn()` function acts as a factory method to create a database connection.
- **Singleton**: The database connection is managed within the `_get_conn()` function, ensuring a consistent connection setup.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: The main entry point for the skill, which processes the user request and marks a routine as completed.
  - `_find_routine(message: str) -> dict | None`: A helper method to find a routine based on the user message.
  - `_mark_complete(routine_id: int, routine_title: str) -> int`: A helper method to mark a routine as completed in the database.

#### Database
- **Tables**:
  - `routines`: Stores routine information.
  - `routine_completions`: Stores routine completion records.
  - `message`: Stores message data.
  - `datetime`: Stores date and time information.
  - `engine`: Stores engine-related data.
  - `pass`: Stores pass-related data.

#### Configuration
- Environment variables:
  - `DB_HOST`: Database host.
  - `DB_NAME`: Database name.
  - `DB_USER`: Database user.
  - `DB_PASSWORD`: Database password.
  - `DB_PORT`: Database port.

#### Key Logic
1. **_get_conn()**: Establishes a connection to the PostgreSQL database using environment variables.
2. **_find_routine(message: str) -> dict | None**: 
   - Cleans the user message by removing trigger phrases and normalizing whitespace.
   - Queries the `routines` table to find a matching routine based on the cleaned message.
   - Returns the routine details if found.
3. **_mark_complete(routine_id: int, routine_title: str) -> int**: 
   - Inserts or updates a record in the `routine_completions` table to mark the routine as completed.
4. **execute(request: SkillRequest) -> SkillResponse**: 
   - Extracts the routine from the user message.
   - Calls `_find_routine` to find the routine.
   - Calls `_mark_complete` to mark the routine as completed.
   - Returns a confirmation response.

#### Integration Points
- **SkillBase**: The `CompleteRoutineSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **Database**: The file interacts with the PostgreSQL database to retrieve and update routine information.
- **Environment Variables**: Uses environment variables to configure the database connection.
- **Logging**: Uses the `logging` module to log errors and debug information.

This file is a critical component of the Mythos system, enabling users to mark routines as completed and updating the database accordingly.
