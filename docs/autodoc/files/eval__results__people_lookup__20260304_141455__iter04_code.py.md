# eval/results/people_lookup/20260304_141455/iter04_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 199

---

### File: eval/results/people_lookup/20260304_141455/iter04_code.py

#### Purpose
This file implements a skill (`PeopleLookupSkill`) that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inheriting from `SkillBase`, this class implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest` message, extracts the search term, and queries the database.
  - The results are formatted and returned as a `SkillResponse`.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a connection to the database, which can be considered a singleton pattern for the connection.
- **Factory**: The `SkillResponse` object is created based on the query results and error handling.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Interfaces**:
  - `PeopleLookupSkill.execute`: Processes the request and returns a `SkillResponse` object.

#### Database
- **Tables/Labels**:
  - `people`: The table is queried for matching records based on `first_name`, `last_name`, or `known_as`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Used to configure the PostgreSQL connection.
- **Config Files**:
  - `.env` file located at `/opt/mythos/.env` is loaded to access the environment variables.

#### Key Logic
- **Search Term Extraction**:
  - The search term is extracted from the message based on specific keywords like "who is", "find person", "lookup", "born", "birthday", and "birth data".
- **Database Query**:
  - If a search term is found, a case-insensitive LIKE query is executed to find matching records.
  - If no search term is found, the total count of people in the registry is returned.
- **Result Formatting**:
  - The results are formatted into a summary and structured data format for the `SkillResponse`.

#### Integration Points
- **Mythos Subsystems**:
  - This skill integrates with the `engine.base` module for the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.
  - It interacts with the PostgreSQL database to query the `people` table.

### Summary
The `PeopleLookupSkill` class in this file provides a robust mechanism to search for people in the Mythos system based on various name-related fields. It handles both successful and error scenarios, ensuring that the system can provide meaningful responses to user queries. The skill is designed to be part of a larger Mythos system, integrating with the database and other subsystems through well-defined interfaces and configurations.
