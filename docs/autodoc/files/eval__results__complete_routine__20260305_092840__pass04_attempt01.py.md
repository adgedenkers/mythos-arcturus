# eval/results/complete_routine/20260305_092840/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 134

---

### Documentation for `eval/results/complete_routine/20260305_092840/pass04_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`CompleteRoutineSkill`) that marks a specified routine as completed for the current day based on user input. It interacts with a PostgreSQL database to find and update routine completion records.

#### Architecture
- **Classes**: 
  - `CompleteRoutineSkill`: Inherits from `SkillBase` and implements the `execute` method to process user requests and update the database.
- **Functions**: 
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Top-level function to handle the skill execution.
  - `_find_routine`: Helper function to find the routine based on the user message.
  - `_mark_complete`: Helper function to mark the routine as completed.

#### Patterns
- **Singleton**: The database connection is established using a helper function `_get_conn`, which can be considered a form of singleton pattern for database connections.
- **Factory**: The `SkillResponse` object is created based on the outcome of the routine completion process.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database interactions.
  - `datetime`: For date and time operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**: 
  - `execute`: Takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Helper Methods**: 
  - `_find_routine`: Takes a message string and returns a dictionary or `None`.
  - `_mark_complete`: Takes a routine ID and title, and returns an integer (completion ID).

#### Database
- **Tables/Labels**: 
  - `routines`: Used to find the routine based on the user message.
  - `routine_completions`: Used to mark a routine as completed.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configured for the PostgreSQL database connection.

#### Key Logic
1. **Routine Extraction**: The `execute` method extracts the routine name from the user message by removing trigger phrases and normalizing the string.
2. **Routine Search**: The `_find_routine` method queries the `routines` table to find a matching routine based on the cleaned message.
3. **Completion Marking**: The `_mark_complete` method inserts or updates the `routine_completions` table to mark the routine as completed for the current day.

#### Integration Points
- **Mythos Subsystems**: 
  - **Database Layer**: Interacts with PostgreSQL to read from `routines` and write to `routine_completions`.
  - **Skill Engine**: Integrates with the skill engine to process user requests and return responses.

### Detailed Explanation

#### Classes
- **CompleteRoutineSkill**:
  - **Attributes**: 
    - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Define the skill metadata.
  - **Methods**:
    - `execute`: Processes the user request, finds the routine, marks it as completed, and returns a response.
    - `_find_routine`: Searches for the routine based on the user message.
    - `_mark_complete`: Marks the routine as completed in the database.

#### Functions
- **_get_conn**:
  - Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**:
  - Handles the main logic of the skill, including extracting the routine from the message, finding the routine, and marking it as completed.
- **_find_routine**:
  - Cleans the user message, removes trigger phrases, and queries the `routines` table to find a matching routine.
- **_mark_complete**:
  - Inserts or updates the `routine_completions` table to mark the routine as completed for the current day.

#### Database Operations
- **routines Table**: 
  - Used to find the routine based on the user message.
- **routine_completions Table**: 
  - Used to mark the routine as completed for the current day.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configured for the PostgreSQL database connection.

#### Key Logic
1. **Routine Extraction**: The `execute` method processes the user message to extract the routine name.
2. **Routine Search**: The `_find_routine` method queries the `routines` table to find a matching routine.
3. **Completion Marking**: The `_mark_complete` method updates the `routine_completions` table to mark the routine as completed.

#### Integration Points
- **Database Layer**: Interacts with PostgreSQL to read from `routines` and write to `routine_completions`.
- **Skill Engine**: Integrates with the skill engine to process user requests and return responses.

This documentation provides a comprehensive overview of the `pass04_attempt01.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
