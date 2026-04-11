# eval/results/people_lookup/20260304_162447/iter01_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 89

---

### File: `eval/results/people_lookup/20260304_162447/iter01_code.py`

#### Purpose
This file contains the implementation of the `PeopleLookupSkill` class, which is responsible for searching for people in the Mythos registry based on first name, last name, or known as. It also provides a count of all people in the registry if no search term is provided.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the skill execution.
- **Functions**: 
  - `_get_conn`: A helper function to establish a PostgreSQL database connection.
  - `execute`: An asynchronous function that processes the request and returns a response.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connections, as it ensures a consistent way to connect to the database.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the input request.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging errors and information.
  - `psycopg2`: For PostgreSQL database interactions.
  - `typing`: For type hints.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: An asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.

#### Database
- **Tables/Labels**: 
  - `public.people`: The table where people data is stored. The `execute` method queries this table to retrieve people based on search terms.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: These variables are used to configure the PostgreSQL database connection.
- **Dotenv File**: 
  - `/opt/mythos/.env`: This file is loaded to provide the environment variables.

#### Key Logic
- **Search Logic**: 
  - The `execute` method processes the request message to extract a search term based on predefined triggers.
  - If a search term is found, it queries the `public.people` table to find people matching the search term in first name, last name, or known as fields.
  - If no search term is found, it returns the count of all people in the registry.
- **Response Construction**: 
  - The method constructs a summary based on the query results and returns a `SkillResponse` object with the summary and other metadata.

#### Integration Points
- **SkillBase Class**: 
  - The `PeopleLookupSkill` class inherits from `SkillBase`, which provides a framework for skill execution.
- **SkillRequest and SkillResponse**: 
  - The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos skill execution framework.
- **Database Connection**: 
  - The `_get_conn` function is used to establish a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

### Summary
This file implements a skill for searching people in the Mythos registry. It uses PostgreSQL for data retrieval and integrates with the Mythos skill execution framework through the `SkillBase` class and related interfaces. The key logic involves parsing the request message, querying the database, and constructing a response based on the query results.
