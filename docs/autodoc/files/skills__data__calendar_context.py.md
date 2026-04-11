# skills/data/calendar_context.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 186

---

### File: skills/data/calendar_context.py

#### Purpose
This file defines the `CalendarContextSkill` class, which is responsible for retrieving and summarizing today's calendar events, routine completion status, and upcoming events from the PostgreSQL database. It provides a structured output for the Mythos system.

#### Architecture
- **Classes**: 
  - `CalendarContextSkill` inherits from `SkillBase` and implements the `execute` method to fetch and process calendar and routine data.
- **Functions**:
  - `_get_conn`: A helper function to establish a connection to the PostgreSQL database.
  - `execute`: An asynchronous method that processes the request and returns a `SkillResponse` object with the summarized data.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of connection to the database.
- **Factory**: The `SkillResponse` object is created and returned based on the processed data.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object containing the summarized calendar and routine data.

#### Database
- **Tables/Labels**:
  - `calendar_events`: Used to fetch today's and upcoming events.
  - `routines`: Used to fetch today's routines.
  - `routine_completions`: Used to fetch the completion status of today's routines.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for connecting to the PostgreSQL database.
- **Files**:
  - `.env`: Loaded using `dotenv` to provide database connection details.

#### Key Logic
- **Event Retrieval**:
  - Fetches today's events from `calendar_events` where `event_date` matches today and `is_active` is true.
- **Upcoming Events**:
  - Fetches upcoming events from `calendar_events` for the next 3 days.
- **Routine Retrieval**:
  - Fetches today's routines from `routines` and their completion status from `routine_completions` based on various frequency conditions.
- **Data Summarization**:
  - Summarizes the events and routines into a human-readable format and constructs a `SkillResponse` object with the summarized data and confidence level.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Connects to the PostgreSQL database to fetch calendar events and routine data.
  - **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
  - **Logging**: Uses the `logging` module to log errors and information.
  - **Environment Configuration**: Uses `dotenv` to load environment variables for database connection details.

This file is a critical component of the Mythos system, providing structured and summarized calendar and routine data to other parts of the system.
