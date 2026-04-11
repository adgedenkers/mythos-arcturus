# eval/results/complete_routine/20260305_092840/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 106

---

### File: eval/results/complete_routine/20260305_092840/pass03_attempt01.py

#### 1. Purpose
This file contains the implementation of a skill (`CompleteRoutineSkill`) that marks a routine as completed for the current day based on user input. It interacts with a PostgreSQL database to find and update routine completion records.

#### 2. Architecture
The file consists of a single class `CompleteRoutineSkill` that inherits from `SkillBase`. The class includes methods for executing the skill (`execute`), finding a routine based on user input (`_find_routine`), and marking a routine as complete (`_mark_complete`). Additionally, there is a top-level function `_get_conn` for establishing a database connection.

#### 3. Patterns
- **Factory Pattern**: The `_get_conn` function acts as a factory method to create and return a database connection.
- **Singleton Pattern**: The `_get_conn` function ensures a consistent connection setup by using environment variables for configuration.

#### 4. Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `dotenv`
- **Database**: PostgreSQL (`psycopg2`)

#### 5. Interfaces
- **Public Methods**:
  - `execute(request)`: Asynchronous method to execute the skill based on the provided request.
  - `_find_routine(message)`: Synchronous method to find a routine based on the user message.
  - `_mark_complete(routine_id, routine_title)`: Synchronous method to mark a routine as completed.

#### 6. Database
- **Tables**:
  - `routines`: Table to store routine information.
  - `routine_completions`: Table to store routine completion records.
  - `message`: Table to store messages (possibly for logging or auditing).
  - `datetime`: Table or function to handle date and time operations.
  - `today`: Table or function to handle today's date.

#### 7. Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### 8. Key Logic
- **Finding a Routine**:
  - The `_find_routine` method cleans the user message by removing trigger phrases and normalizing whitespace.
  - It then queries the `routines` table to find a matching routine based on the cleaned message.
  - If no exact match is found, it tries to match individual words from the cleaned message.

- **Marking a Routine as Complete**:
  - The `_mark_complete` method inserts a new record into the `routine_completions` table or updates an existing one if the routine is already marked as completed for the day.
  - It uses an `ON CONFLICT` clause to handle potential conflicts and updates the status accordingly.

#### 9. Integration Points
- **SkillBase Class**: The `CompleteRoutineSkill` class inherits from `SkillBase`, which likely provides a framework for defining and executing skills.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, which is a core component of the Mythos system.
- **Environment Variables**: The file uses environment variables to configure the database connection, which is a common practice for managing configuration in a self-hosted system like Mythos.
- **Logging**: The file uses the `logging` module to log errors, which helps in debugging and monitoring the system.

### Summary
This file implements a skill that allows users to mark routines as completed based on their input. It interacts with a PostgreSQL database to find and update routine completion records, using environment variables for configuration and logging for error handling. The skill is designed to be part of a larger system, integrating with the `SkillBase` class and the Mythos infrastructure.
