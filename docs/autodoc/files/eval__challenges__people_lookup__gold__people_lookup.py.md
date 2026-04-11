# eval/challenges/people_lookup/gold/people_lookup.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 187

---

### Documentation for `people_lookup.py`

#### Purpose
The `people_lookup.py` file implements a skill for the Mythos system that allows searching the people registry stored in PostgreSQL by name, nickname, or ID. It returns matching person records with birth data and notes.

#### Architecture
The file contains a single class `PeopleLookupSkill` that inherits from `SkillBase`. This class has methods for executing the skill (`execute`), extracting search terms (`_extract_search_term`), formatting names (`_format_name`), and formatting birth locations (`_format_birth_location`). Additionally, there are top-level functions `_get_conn` and `execute` that handle database connection and skill execution respectively.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the input request.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `typing`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Internal Methods**: `_extract_search_term`, `_format_name`, `_format_birth_location`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `people`
- **Operations**: 
  - `SELECT COUNT(*) as total FROM people` (to get total count of people)
  - `SELECT ... FROM people WHERE ...` (to search for people by name, nickname, or ID)

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.
- **Configuration File**: `.env` located at `/opt/mythos/.env`

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method cleans the input message to extract a search term.
- **Database Query**: The `execute` method constructs and executes a SQL query to search the `people` table based on the extracted search term.
- **Response Construction**: The `execute` method formats the query results into a structured response and builds a summary string.

#### Integration Points
- **SkillBase Class**: The `PeopleLookupSkill` class inherits from `SkillBase`, indicating integration with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos request/response framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

### Detailed Breakdown

#### Classes
- **PeopleLookupSkill**
  - **Inheritance**: `SkillBase`
  - **Methods**:
    - `execute`: Asynchronous method that handles the skill execution, including database connection, query execution, and response construction.
    - `_extract_search_term`: Extracts the search term from the input message.
    - `_format_name`: Formats the full name from the database row.
    - `_format_birth_location`: Formats the birth location from the database row.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**: This top-level function is not used within the file and seems redundant given the class method with the same name.

#### Key Methods
- **_extract_search_term**: Cleans the input message to extract a meaningful search term by removing common phrases.
- **_format_name**: Constructs a full name from the parts stored in the database row.
- **_format_birth_location**: Constructs a birth location string from the city, state, and country parts.

#### Database Operations
- The `execute` method constructs a SQL query to search the `people` table based on the extracted search term. It handles both exact and partial matches for first name, last name, and known aliases.

#### Configuration and Environment
- The database connection details are loaded from environment variables using `dotenv`, ensuring that the connection is configured correctly for the running environment.

#### Error Handling
- The `execute` method includes error handling to log any exceptions and return an error response if the database query fails.

This documentation provides a comprehensive overview of the `people_lookup.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, and key logic.
