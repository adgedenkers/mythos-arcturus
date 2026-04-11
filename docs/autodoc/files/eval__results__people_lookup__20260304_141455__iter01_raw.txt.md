# eval/results/people_lookup/20260304_141455/iter01_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### Documentation for `eval/results/people_lookup/20260304_141455/iter01_raw.txt`

#### Purpose
This file contains the implementation of the `PeopleLookupSkill` class, which is responsible for searching the Mythos people table by first name, last name, or known alias (case-insensitive LIKE match) and returning matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the input message to extract a search term.
  - It then queries the PostgreSQL database to find matching records or the total count if no search term is found.
  - The results are formatted and returned in a `SkillResponse` object.

#### Patterns
- **Singleton**: The database connection is established and closed within the `execute` method, ensuring that each invocation has its own connection.
- **Factory**: The `SkillBase` class is used as a base class, and `PeopleLookupSkill` is a concrete implementation of this base class.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `re`: For regular expression matching.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database interaction.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Processes the request and returns a response with search results or error messages.

#### Database
- **Tables/Labels**:
  - `people`: The table in the PostgreSQL database that stores person records. The query searches this table for matching records based on `first_name`, `last_name`, or `known_as`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for connecting to the PostgreSQL database.
- **Files**:
  - `/opt/mythos/.env`: Contains environment variables loaded using `dotenv`.

#### Key Logic
- **Search Term Extraction**: The `execute` method uses regular expressions to extract a search term from the input message based on specific keywords like "who is", "find person", and "lookup".
- **Database Query**: The method constructs a SQL query to search the `people` table for records matching the extracted search term in `first_name`, `last_name`, or `known_as`.
- **Result Formatting**: The method formats the query results into a structured response, including a summary and detailed data.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, which provides a framework for handling skill requests and responses.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos skill execution system.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

This file is a critical component of the Mythos system, enabling efficient and flexible searching of person records based on various criteria.
