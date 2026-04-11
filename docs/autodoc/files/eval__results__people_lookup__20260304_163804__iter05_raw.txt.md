# eval/results/people_lookup/20260304_163804/iter05_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 204

---

### File: eval/results/people_lookup/20260304_163804/iter05_raw.txt

#### Purpose
This file contains the implementation of the `PeopleLookupSkill` class, which is responsible for searching the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returning matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
The file is structured around the `PeopleLookupSkill` class, which inherits from `SkillBase`. The class contains:
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, and `cache_ttl`.
- **Methods**: `execute`, which processes the incoming `SkillRequest` and returns a `SkillResponse`.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connection management.
- **Factory**: The `SkillResponse` object is created based on the execution logic.

#### Dependencies
- **Imports**: `os`, `logging`, `typing`, `psycopg2`, `psycopg2.extras`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Exposed Methods**: `execute` method, which takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Exposed Classes**: `PeopleLookupSkill` class.

#### Database
- **Tables**: `people` table.
- **Operations**: Reads from the `people` table using `LIKE` queries for `first_name`, `last_name`, and `known_as`.

#### Configuration
- **Config Files**: `.env` file located at `/opt/mythos/.env`.
- **Environment Variables**: Used to configure the PostgreSQL connection.

#### Key Logic
- **Search Term Extraction**: Extracts search terms from the message using keywords like "who is", "find person", "lookup", "born", "birthday", and "birth data".
- **Database Query**: Executes a `LIKE` query on `first_name`, `last_name`, and `known_as` fields to find matching records.
- **Result Formatting**: Formats the results into a structured data format and a summary string.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for input and output.
- **Database Connection**: Uses `_get_conn` to manage database connections, integrating with the PostgreSQL database.

### Detailed Documentation

#### Classes
- **PeopleLookupSkill**
  - **Attributes**:
    - `name`: "people_lookup"
    - `version`: "1.0"
    - `category`: "data"
    - `description`: "Searches the Mythos people table by name or alias, returning birth data."
    - `triggers`: List of keywords that trigger this skill.
    - `cache_ttl`: Cache time-to-live in seconds (600 seconds).
  - **Methods**:
    - `execute(request: SkillRequest) -> SkillResponse`: Processes the request and returns a response.

#### Functions
- **_get_conn()**
  - **Purpose**: Establishes a connection to the PostgreSQL database.
  - **Returns**: A `psycopg2` connection object.

#### Key Logic Flow
1. **Connection Setup**: Establishes a connection to the PostgreSQL database using `_get_conn`.
2. **Search Term Extraction**: Extracts the search term from the request message using predefined keywords.
3. **Query Execution**:
   - If no search term is found, queries the total count of people in the registry.
   - If a search term is found, performs a `LIKE` query on `first_name`, `last_name`, and `known_as` fields.
4. **Result Formatting**: Formats the query results into a structured data format and a summary string.
5. **Response Construction**: Constructs and returns a `SkillResponse` object with the results and summary.

#### Error Handling
- **Exception Handling**: Catches any exceptions during execution, logs the error, and returns a `SkillResponse` with an error message.
- **Resource Cleanup**: Ensures that the database cursor and connection are closed in the `finally` block.

This file is a critical component of the Mythos system, enabling efficient and flexible querying of the people registry based on various search criteria.
