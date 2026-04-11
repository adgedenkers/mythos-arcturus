# eval/results/people_lookup/20260304_141455/iter02_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### File: eval/results/people_lookup/20260304_141455/iter02_code.py

#### 1. Purpose
This file implements a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### 2. Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest` to extract a search term.
  - It then queries the PostgreSQL database to find matching records or the total count if no search term is found.
  - The results are formatted and returned as a `SkillResponse`.

#### 3. Patterns
- **Singleton**: The database connection `_get_conn()` can be considered a singleton pattern as it ensures a single connection is used throughout the execution.
- **Factory**: The `SkillResponse` object is created based on the outcome of the database query.

#### 4. Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors and information.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### 5. Interfaces
- **Exposed Methods**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: Processes the request and returns a response with search results or error details.

#### 6. Database
- **Tables/Lables**:
  - `people`: Table in the PostgreSQL database containing person records with fields like `first_name`, `last_name`, `known_as`, `date_of_birth`, etc.

#### 7. Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### 8. Key Logic
- **Search Term Extraction**:
  - The method checks for specific keywords in the request message to extract a search term.
- **Database Query**:
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, or `known_as`.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**:
  - Formats the search results into a human-readable summary and structured data format.

#### 9. Integration Points
- **SkillBase Inheritance**:
  - The `PeopleLookupSkill` class inherits from `SkillBase`, which provides a framework for handling skill requests and responses.
- **Database Connection**:
  - Uses `_get_conn()` to connect to the PostgreSQL database, which is part of the Mythos infrastructure.
- **Skill Request/Response**:
  - Integrates with the Mythos skill system by accepting `SkillRequest` and returning `SkillResponse`.

This file is a critical component of the Mythos system, enabling efficient and flexible searching of person records within the PostgreSQL database.
