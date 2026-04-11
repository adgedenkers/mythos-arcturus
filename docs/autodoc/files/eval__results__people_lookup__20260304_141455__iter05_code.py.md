# eval/results/people_lookup/20260304_141455/iter05_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 188

---

### File: `eval/results/people_lookup/20260304_141455/iter05_code.py`

#### Purpose
This file defines a skill (`PeopleLookupSkill`) that searches the Mythos people table for records based on a search term extracted from a user message. It returns matching records with birth data or the total count of people if no search term is found.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest` to extract a search term.
  - It then queries the PostgreSQL database to find matching records or the total count of people.
  - The results are formatted into a `SkillResponse` object, which is returned to the caller.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it establishes a database connection, which is a common resource.
- **Factory Method**: The `SkillResponse` object is created based on the outcome of the database query.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes the `SkillRequest` and returns a `SkillResponse` object.

#### Database
- **Tables**:
  - `people`: The table from which the records are queried. It contains fields such as `first_name`, `last_name`, `known_as`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_zip`, and `birth_country`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection parameters.
- **Files**:
  - `.env`: Configuration file located at `/opt/mythos/.env` used to load environment variables.

#### Key Logic
- **Search Term Extraction**: The `execute` method parses the incoming message to extract a search term based on specific keywords or heuristics.
- **Database Query**: The method constructs and executes a SQL query to search for people matching the extracted search term in the `first_name`, `last_name`, or `known_as` fields.
- **Result Formatting**: If records are found, the method formats the results into a human-readable summary and a structured data format.

#### Integration Points
- **SkillBase Interface**: The `PeopleLookupSkill` class integrates with the broader Mythos system through the `SkillBase` interface, which handles the execution of skills and the response format.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to execute queries and retrieve results.
- **Logging**: Errors are logged using the `logging` module, which integrates with the Mythos logging infrastructure.

### Summary
This file implements a skill for searching the Mythos people table based on a user-provided search term. It handles database connections, query execution, and result formatting, integrating with the Mythos system through the `SkillBase` interface and logging errors for troubleshooting.
