# eval/results/people_lookup/20260304_163804/iter05_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### File: `eval/results/people_lookup/20260304_163804/iter05_code.py`

#### Purpose
This file defines a skill (`PeopleLookupSkill`) that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` (inherits from `SkillBase`):
    - **Methods**: `execute`
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Asynchronous function to handle the execution of the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection to the database.
- **Factory**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors and information.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**:
  - `PeopleLookupSkill.execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Top-level Functions**:
  - `_get_conn`: Returns a PostgreSQL database connection.
  - `execute`: Asynchronous function to handle the execution of the skill.

#### Database
- **Tables**:
  - `people`: PostgreSQL table used for searching and retrieving people records.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### Key Logic
1. **Connection Establishment**: `_get_conn` function establishes a connection to the PostgreSQL database.
2. **Search Term Extraction**: The `execute` method extracts a search term from the request message based on specific keywords.
3. **Database Query Execution**:
   - If no search term is found, it queries the total count of people in the `people` table.
   - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as` fields.
4. **Result Formatting**: Formats the search results into a structured data format and a summary string.
5. **Error Handling**: Catches exceptions and logs errors, returning a `SkillResponse` with an error message if an exception occurs.

#### Integration Points
- **SkillBase Class**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **SkillRequest and SkillResponse**: Uses `SkillRequest` and `SkillResponse` objects to handle input and output of the skill.
- **Database Connection**: Uses `psycopg2` to interact with the PostgreSQL database, which is part of the Mythos infrastructure.

This file is a critical component of the Mythos system, providing a robust and flexible way to search and retrieve people records from the database based on various search criteria.
