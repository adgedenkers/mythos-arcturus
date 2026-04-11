# eval/results/people_lookup/20260304_141455/iter04_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 205

---

### File: `eval/results/people_lookup/20260304_141455/iter04_raw.txt`

#### Purpose
This file contains a Python script that defines a `PeopleLookupSkill` class, which is responsible for searching the Mythos people table by first name, last name, or known alias (case-insensitive LIKE match) and returning matching records with birth data. If no search term can be extracted from the request, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest`, extracts a search term from the request message, and queries the database to find matching records or return the total count of people.

#### Patterns
- **Singleton**: The database connection `_get_conn()` can be considered a singleton pattern as it ensures a single connection is established and reused.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database connection.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Processes the request and returns a `SkillResponse` object containing the search results or error information.

#### Database
- **Tables/Labels**:
  - **people**: The table is queried to retrieve records based on `first_name`, `last_name`, or `known_as` fields.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured for the PostgreSQL database connection.
- **Files**:
  - `.env`: Loaded from `/opt/mythos/.env` to configure database connection settings.

#### Key Logic
- **Search Term Extraction**: The script extracts a search term from the request message based on specific keywords like "who is", "find person", "lookup", "born", "birthday", "birth data".
- **Database Query**: If a search term is found, it performs a case-insensitive LIKE query on the `people` table to find matching records. If no search term is found, it returns the total count of people.
- **Result Formatting**: The script formats the results into a human-readable summary and structured data for further processing.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, which likely provides a framework for handling skill requests and responses.
- **SkillRequest/SkillResponse**: The script interacts with `SkillRequest` and `SkillResponse` classes to process incoming requests and return formatted responses.
- **Database Connection**: The script integrates with the PostgreSQL database to perform queries and retrieve data.

### Summary
This script is a critical component of the Mythos system, designed to handle people lookup requests by searching a PostgreSQL database and returning structured results or error messages. It leverages environment variables for configuration and integrates with the broader Mythos infrastructure through the `SkillBase` framework.
