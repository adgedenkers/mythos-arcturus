# eval/results/people_lookup/20260304_141455/best.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 199

---

### Documentation for `eval/results/people_lookup/20260304_141455/best.py`

#### 1. Purpose
This Python file implements a skill (`PeopleLookupSkill`) that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### 2. Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest`, extracts a search term from the message, and queries the database to find matching records. The results are then formatted and returned as a `SkillResponse`.

#### 3. Patterns
- **Singleton**: The `_get_conn()` function can be considered a singleton pattern as it ensures a single database connection is created and reused.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### 4. Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### 5. Interfaces
- **Exposed Methods**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: Processes the incoming request and returns a `SkillResponse` object containing the search results or error information.

#### 6. Database
- **Tables/Labels**:
  - `people`: The table in the PostgreSQL database that stores people records. The query searches this table for matching records based on `first_name`, `last_name`, or `known_as`.

#### 7. Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for the PostgreSQL database connection.
- **Files**:
  - `/opt/mythos/.env`: Contains environment variables used to configure the database connection.

#### 8. Key Logic
- **Search Term Extraction**:
  - The search term is extracted from the message based on specific keywords like "who is", "find person", "lookup", "born", "birthday", and "birth data".
- **Database Query**:
  - The query searches the `people` table for records where `first_name`, `last_name`, or `known_as` match the search term (case-insensitive).
- **Result Formatting**:
  - The results are formatted into a structured format and a summary string for the `SkillResponse`.

#### 9. Integration Points
- **Subsystems**:
  - **Database**: Connects to the PostgreSQL database to retrieve people records.
  - **Skill Engine**: Integrates with the Mythos skill engine via the `SkillBase` class and interacts with `SkillRequest` and `SkillResponse` objects.
  - **Environment Configuration**: Uses environment variables and `.env` file for configuration.

This file is a critical component of the Mythos system, providing a robust and flexible way to search and retrieve information from the people registry.
