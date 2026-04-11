# eval/results/people_lookup/20260304_163804/iter02_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 179

---

### Documentation for `eval/results/people_lookup/20260304_163804/iter02_raw.txt`

#### Purpose
This file contains the implementation of the `PeopleLookupSkill` class, which is designed to search the Mythos people table by `first_name`, `last_name`, or `known_as` (case-insensitive LIKE match) and return matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**:
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `_extract_search_term`: Extracts a search term from the user message by removing common trigger phrases.
  - `_format_name`: Formats a person's name for display.
  - `_format_birth_location`: Formats the birth location for display.
- **Data Flow**:
  - The `execute` method processes the user message to extract a search term.
  - It then queries the PostgreSQL database to find matching records.
  - The results are formatted and returned in a `SkillResponse` object.

#### Patterns
- **Singleton**: The database connection is managed within the `_get_conn` function, which could be considered a singleton pattern for database connections.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- **Imports**:
  - `os`, `logging`, `re`, `typing` from the Python standard library.
  - `psycopg2` and `psycopg2.extras` for PostgreSQL database interaction.
  - `dotenv` for loading environment variables.
  - `engine.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes a `SkillRequest` and returns a `SkillResponse` containing the search results or summary.

#### Database
- **Tables/Labels**:
  - `people`: The table in the PostgreSQL database that stores person records. The query retrieves fields such as `id`, `prefix`, `first_name`, `middle_name`, `last_name`, `suffix`, `known_as`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_zip`, `birth_country`, and `display_text`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env` for database connection.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method removes common trigger phrases and returns a valid search term.
- **Database Query**: The `execute` method constructs a SQL query to search the `people` table based on the extracted search term.
- **Result Formatting**: The `_format_name` and `_format_birth_location` methods format the retrieved data for display.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request-response framework.
- **Database Connection**: The `_get_conn` function manages the connection to the PostgreSQL database, integrating with the Mythos database infrastructure.

This documentation provides a comprehensive overview of the `PeopleLookupSkill` implementation, detailing its purpose, architecture, dependencies, interfaces, and integration points within the Mythos system.
