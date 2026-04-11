# eval/results/people_lookup/20260304_141455/iter03_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 183

---

### File: `eval/results/people_lookup/20260304_141455/iter03_code.py`

#### Purpose
This file implements a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest` to extract a search term.
  - It then queries the PostgreSQL database to find matching records or the total count of people.
  - The results are formatted into a `SkillResponse` object and returned.

#### Patterns
- **Singleton**: The `_get_conn()` function can be considered a singleton pattern as it provides a single connection instance.
- **Factory**: The `SkillResponse` object creation can be seen as a factory method pattern.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type annotations.
  - `psycopg2` and `psycopg2.extras`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: Processes a skill request and returns a skill response.

#### Database
- **Tables/Labels**:
  - **PostgreSQL Table**: `people` (reads from this table to fetch records based on search terms or to get the total count).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**:
  - The method checks for specific keywords in the request message to extract a search term.
- **Database Query**:
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, or `known_as` fields.
  - If no search term is found, it queries the total count of people in the `people` table.
- **Result Formatting**:
  - The results are formatted into a `SkillResponse` object, including a summary and detailed data.

#### Integration Points
- **Mythos Subsystems**:
  - **Engine**: Integrates with the `SkillBase` class and uses `SkillRequest` and `SkillResponse` for request and response handling.
  - **Database**: Connects to the PostgreSQL database to fetch people records.
  - **Logging**: Uses the logging module to log errors.

### Summary
This file implements a skill that searches the Mythos people table based on various name fields and returns matching records or the total count of people. It integrates with the Mythos engine and PostgreSQL database, using environment variables for configuration and logging for error handling.
