# eval/results/people_lookup/20260304_163804/iter02_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 177

---

### Documentation for `eval/results/people_lookup/20260304_163804/iter02_code.py`

#### Purpose
This file contains the implementation of a skill (`PeopleLookupSkill`) for the Mythos system, which allows users to search for people in the Mythos people table by name or alias and retrieve their birth data.

#### Architecture
The file is structured around a single class, `PeopleLookupSkill`, which inherits from `SkillBase`. The class contains several methods:
- `_extract_search_term`: Extracts a search term from the user message.
- `_format_name`: Formats a person's name for display.
- `_format_birth_location`: Formats a person's birth location for display.
- `execute`: The main method that processes the request, performs the database query, and formats the results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `_extract_search_term`: A top-level function that mirrors the class method.
- `_format_name`: A top-level function that mirrors the class method.
- `_format_birth_location`: A top-level function that mirrors the class method.
- `execute`: A top-level function that mirrors the class method.

#### Patterns
- **Factory Method**: The `_get_conn` function can be considered a factory method for creating database connections.
- **Singleton**: The database connection (`_get_conn`) could be implemented as a singleton to ensure only one connection is created per request.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors and information.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**: 
  - `execute`: Processes the request and returns a `SkillResponse` object.
- **Top-Level Functions**: 
  - `_get_conn`: Establishes a database connection.
  - `_extract_search_term`: Extracts a search term from the user message.
  - `_format_name`: Formats a person's name for display.
  - `_format_birth_location`: Formats a person's birth location for display.

#### Database
- **Tables**: 
  - `people`: The table from which the skill retrieves data.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for the PostgreSQL database connection.
- **Configuration File**: 
  - `.env`: Loaded from `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method removes common trigger phrases and extracts a valid search term from the user message.
- **Database Query**: The `execute` method constructs and executes a PostgreSQL query to search for people by first name, last name, or known alias.
- **Result Formatting**: The `_format_name` and `_format_birth_location` methods format the retrieved data for display.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, which likely provides a framework for handling skill requests and responses.
- **SkillRequest and SkillResponse**: The `execute` method processes a `SkillRequest` and returns a `SkillResponse`, indicating integration with the Mythos skill execution framework.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

### Summary
This file implements a skill for the Mythos system that allows users to search for people in the `people` table by name or alias and retrieve their birth data. It uses PostgreSQL for data retrieval and provides formatted results through a well-defined interface. The skill integrates with the Mythos skill execution framework and uses environment variables for configuration.
