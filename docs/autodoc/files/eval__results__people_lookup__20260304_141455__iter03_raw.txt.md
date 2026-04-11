# eval/results/people_lookup/20260304_141455/iter03_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 189

---

### File: `eval/results/people_lookup/20260304_141455/iter03_raw.txt`

#### Purpose
This file contains the implementation of a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The skill receives a `SkillRequest` object containing the message to be processed.
  - The message is parsed to extract a search term.
  - The search term is used to query the `people` table in the PostgreSQL database.
  - The results are formatted into a `SkillResponse` object and returned.

#### Patterns
- **Singleton**: The database connection is managed within the `_get_conn` function, ensuring a single connection is established and reused.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database interaction.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Interfaces**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: The main method that processes the request and returns a response.

#### Database
- **Tables/Labels**:
  - `people`: The table in the PostgreSQL database that stores people records.
  - **Columns queried**:
    - `id`, `prefix`, `first_name`, `middle_name`, `last_name`, `suffix`, `known_as`, `display_text`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_zip`, `birth_country`, `date_of_death`, `notes`, `canonical_id`, `created_at`, `updated_at`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details.
- **Config Files**:
  - `.env`: Loaded from `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**:
  - The message is parsed to extract a search term based on specific keywords like "who is", "find person", "lookup", "born", "birthday", "birth data".
- **Database Query**:
  - If a search term is found, it is used to query the `people` table using a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as`.
  - If no search term is found, the total count of people in the registry is returned.
- **Result Formatting**:
  - The results are formatted into a list of dictionaries containing the relevant fields.
  - A summary is created to provide a human-readable response.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Connects to the PostgreSQL database to query the `people` table.
  - **Skill System**: Integrates with the Mythos skill system by inheriting from `SkillBase` and implementing the `execute` method.
  - **Logging**: Uses the logging system to log errors.

This file is a critical component of the Mythos system, providing a robust mechanism for searching and retrieving people data based on various search criteria.
