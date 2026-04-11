# eval/results/people_lookup/20260304_141455/iter05_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 192

---

### Documentation for `eval/results/people_lookup/20260304_141455/iter05_raw.txt`

#### Purpose
This file contains the implementation of a skill (`PeopleLookupSkill`) that searches the Mythos people table by first_name, last_name, or known_as, returning birth data. If no search term is found, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to perform the search.
- **Functions**:
  - `_get_conn()`: Establishes a connection to the PostgreSQL database using environment variables.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest` message to extract a search term.
  - It then queries the PostgreSQL database for matching records or the total count if no search term is found.
  - The results are formatted into a `SkillResponse` object and returned.

#### Patterns
- **Singleton**: The database connection is managed within the `_get_conn` function, ensuring a single connection per invocation.
- **Factory**: The `SkillResponse` object is created based on the query results.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes the incoming `SkillRequest` and returns a `SkillResponse` object.
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Define the skill's metadata.

#### Database
- **Tables/Labels**:
  - `people`: The table from which the skill queries data. It contains fields such as `id`, `first_name`, `last_name`, `known_as`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_zip`, `birth_country`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Used to establish a connection to the PostgreSQL database.
- **Config Files**:
  - `.env`: Loaded from `/opt/mythos/.env` to provide database connection details.

#### Key Logic
- **Search Term Extraction**:
  - The skill attempts to extract a search term from the `SkillRequest` message using keywords like "who is", "find person", "lookup", "born", "birthday", "birth data".
- **Database Query**:
  - If a search term is found, the skill queries the `people` table for records matching the term in `first_name`, `last_name`, or `known_as` fields.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**:
  - The skill formats the query results into a human-readable summary and a structured data object.

#### Integration Points
- **Mythos Subsystems**:
  - **Engine**: The skill integrates with the Mythos engine through the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.
  - **Database**: The skill connects to the PostgreSQL database to query the `people` table.
  - **Logging**: Errors are logged using the `logging` module.

This documentation provides a comprehensive overview of the `PeopleLookupSkill` implementation, detailing its purpose, architecture, dependencies, and integration points within the Mythos system.
