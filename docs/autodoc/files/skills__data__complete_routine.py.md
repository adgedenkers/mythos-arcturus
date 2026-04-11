# skills/data/complete_routine.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 134

---

### File: `skills/data/complete_routine.py`

#### Purpose
This file contains the `CompleteRoutineSkill` class, which is responsible for marking a routine as completed in the Mythos system based on user input. It connects to a PostgreSQL database to find and update routine completion records.

#### Architecture
- **Classes**: 
  - `CompleteRoutineSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the main logic of finding and marking a routine as completed.
- **Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `_find_routine`: Finds the routine based on the message content.
  - `_mark_complete`: Marks the routine as completed in the database.
- **Data Flow**:
  - The `execute` method processes the user message, uses `_find_routine` to identify the routine, and then `_mark_complete` to update the database.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it ensures a single connection is created and reused.
- **Factory**: The `SkillBase` class could be seen as a factory for creating different skill instances.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `datetime`: For date and time operations.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: The main method that processes the user request and returns a `SkillResponse`.
  - `_find_routine`: A helper method to find the routine based on the message content.
  - `_mark_complete`: A helper method to mark the routine as completed in the database.

#### Database
- **Tables/Labels**:
  - `routines`: Stores routine information.
  - `routine_completions`: Stores completion records for routines.
  - `datetime`: Used for date and time operations.
  - `message`: Likely used for storing or processing user messages.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
- **Main Logic**:
  - **Finding the Routine**: The `_find_routine` method cleans the user message, removes trigger phrases, and queries the `routines` table to find a matching routine.
  - **Marking as Complete**: The `_mark_complete` method inserts or updates the `routine_completions` table to mark the routine as completed for the current date.
  - **Error Handling**: Both `_find_routine` and `_mark_complete` handle exceptions and log errors appropriately.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Connects to the PostgreSQL database to query and update routine and completion records.
  - **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
  - **SkillRequest/SkillResponse**: Uses these classes to handle and return skill responses.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, `os.getenv` for environment variables.
- **Usage**: Called by `_find_routine` and `_mark_complete` to get a database connection.

#### `CompleteRoutineSkill`
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Define the skill metadata.
- **Methods**:
  - `execute`: Processes the user request, finds the routine, and marks it as completed.
  - `_find_routine`: Queries the `routines` table to find a matching routine based on the message content.
  - `_mark_complete`: Updates the `routine_completions` table to mark the routine as completed.

#### `_find_routine`
- **Logic**:
  - Cleans the message by removing trigger phrases and normalizing whitespace.
  - Queries the `routines` table to find a matching routine using ILIKE for case-insensitive matching.
  - Returns the first matching routine or `None` if no match is found.

#### `_mark_complete`
- **Logic**:
  - Inserts or updates the `routine_completions` table to mark the routine as completed for the current date.
  - Uses `ON CONFLICT` to update the record if it already exists.
  - Returns the ID of the completion record.

### Conclusion
The `complete_routine.py` file is a crucial component of the Mythos system, handling the logic for marking routines as completed based on user input. It integrates with the PostgreSQL database to query and update routine and completion records, ensuring that user actions are accurately reflected in the system.
