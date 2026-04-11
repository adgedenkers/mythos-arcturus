# eval/results/people_lookup/20260304_163804/iter04_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 180

---

### File: `eval/results/people_lookup/20260304_163804/iter04_code.py`

#### Purpose
This file defines a skill (`PeopleLookupSkill`) that searches the Mythos people table by name or alias and returns birth data. It handles user messages to extract search terms and formats the results for display.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and contains methods for extracting search terms, formatting names and birth locations, and executing the skill.
- **Functions**: 
  - `_get_conn`: Establishes a PostgreSQL connection.
  - `_extract_search_term`: Extracts a search term from the user message.
  - `_format_name`: Formats a person's name for display.
  - `_format_birth_location`: Formats the birth location for display.
  - `execute`: Asynchronous method to execute the skill, handling the database query and response formatting.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern for database connections, though it does not explicitly enforce a single instance.
- **Factory**: The `execute` method acts as a factory for `SkillResponse` objects based on the query results.

#### Dependencies
- **Imports**: 
  - `os`, `logging`, `re`, `psycopg2`, `typing`, `dotenv`, `engine.base` (SkillBase, SkillRequest, SkillResponse).
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**: 
  - `_extract_search_term`, `_format_name`, `_format_birth_location`.

#### Database
- **Tables**: 
  - `people`: Used for querying and fetching person records.

#### Configuration
- **Environment Variables**: 
  - Database connection details are loaded from environment variables using `dotenv`.
- **Logging**: 
  - Uses `logging` to log errors.

#### Key Logic
- **Search Term Extraction**: 
  - `_extract_search_term` removes common trigger phrases and trims the message to extract a search term.
- **Database Query**: 
  - The `execute` method constructs a SQL query to search the `people` table for matches based on `first_name`, `last_name`, or `known_as`.
- **Result Formatting**: 
  - `_format_name` and `_format_birth_location` methods format the person's name and birth location for display.
- **Response Construction**: 
  - The `execute` method constructs a `SkillResponse` object with the search results or a summary message.

#### Integration Points
- **SkillBase**: 
  - Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **Database Connection**: 
  - Uses `_get_conn` to establish a PostgreSQL connection, which is used to query the `people` table.
- **SkillRequest and SkillResponse**: 
  - Uses `SkillRequest` to receive input and `SkillResponse` to return output, integrating with the Mythos skill execution pipeline.

### Summary
This file implements a skill for searching and retrieving person records from the Mythos people table. It handles user input to extract search terms, performs database queries, and formats the results for display. The skill integrates with the Mythos skill execution framework and uses PostgreSQL for data retrieval.
