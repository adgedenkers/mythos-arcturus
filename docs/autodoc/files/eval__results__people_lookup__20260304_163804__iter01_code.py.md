# eval/results/people_lookup/20260304_163804/iter01_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 195

---

### Documentation for `iter01_code.py`

#### Purpose
This file implements a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted from the request, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**: 
  - `_get_conn`: A utility function to establish a connection to the PostgreSQL database.
  - `execute`: An asynchronous function that processes the request and performs the database operations.
- **Data Flow**: 
  - The `execute` method processes the incoming request, extracts the search term, and queries the database to retrieve matching records or the total count of people.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it returns a database connection, which is typically a singleton resource.
- **Factory**: The `execute` method acts as a factory to produce `SkillResponse` objects based on the query results.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that processes the request and returns a `SkillResponse` object.

#### Database
- **Tables**: 
  - `people`: The table from which the skill retrieves data based on the search term or returns the total count.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured using `dotenv` to connect to the PostgreSQL database.
- **Files**: 
  - `.env`: Contains the environment variables for the PostgreSQL connection.

#### Key Logic
- **Search Term Extraction**: 
  - The `execute` method parses the incoming message to extract a search term based on specific keywords like "who is", "find person", "lookup", etc.
- **Database Query**: 
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, or `known_as` fields.
  - If no search term is found, it retrieves the total count of records in the `people` table.
- **Result Formatting**: 
  - Formats the results into a human-readable summary and structured data format.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, indicating it integrates with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response model.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, integrating with the Mythos database layer.

### Summary
This file implements a skill that searches the Mythos people table based on various search terms extracted from the request message. It handles database connections, query execution, and result formatting, integrating with the Mythos skill framework and database layer.
