# eval/results/complete_routine/20260305_092840/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 44

---

### File: `eval/results/complete_routine/20260305_092840/pass01_attempt01.py`

#### Purpose
This file defines the `CompleteRoutineSkill` class, which is responsible for marking a routine as completed based on user input. It interacts with a PostgreSQL database to find and update routine completion records.

#### Architecture
- **Classes**: 
  - `CompleteRoutineSkill` inherits from `SkillBase` and implements methods for executing the skill, finding routines, and marking them as complete.
- **Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Asynchronous method to handle the skill execution.
  - `_find_routine`: Finds a routine based on the provided message.
  - `_mark_complete`: Marks a routine as completed in the database.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object.
- **Factory Method**: The `execute` method can be seen as a factory method that orchestrates the process of finding and marking routines.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging purposes.
  - `psycopg2`: For PostgreSQL database interaction.
  - `RealDictCursor`: For cursor factory to return dictionary-like rows.
  - `dotenv`: For loading environment variables from `.env` files.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `request` and returns a `SkillResponse`.
  - `_find_routine`: Takes a `message` and returns a dictionary or `None`.
  - `_mark_complete`: Takes `routine_id` and `routine_title` and returns an integer.

#### Database
- **Tables**:
  - `routine_completions`: Used to insert or update completion records.
  - `message`: Likely used to store or retrieve messages for processing.
  - `pass`: Possibly used for storing pass-related information.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the database connection.

#### Key Logic
- **`execute` Method**:
  1. Extracts the routine from the user message.
  2. Finds the matching routine using `_find_routine`.
  3. Marks the routine as completed using `_mark_complete`.
  4. Returns a confirmation response.

- **`_find_routine` Method**:
  - Queries the database to find an active routine that matches the message using a fuzzy match.

- **`_mark_complete` Method**:
  - Inserts a new record or updates an existing one in the `routine_completions` table to mark the routine as completed.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Interacts with PostgreSQL to read and write routine completion records.
  - **SkillBase**: Inherits from `SkillBase` to integrate with the skill execution framework.
  - **Environment**: Uses environment variables for database configuration.
  - **Logging**: Uses logging to track execution and errors.

### Summary
This file provides the logic for marking routines as completed based on user input. It integrates with the Mythos system through the `SkillBase` class and interacts with a PostgreSQL database to manage routine completion records. The key methods handle the extraction of routine information from user messages, finding the appropriate routine, and marking it as completed.
