# eval/results/people_lookup/20260304_141455/iter02_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 208

---

### Documentation for `eval/results/people_lookup/20260304_141455/iter02_raw.txt`

#### Purpose
This file contains a Python script that defines a skill (`PeopleLookupSkill`) for searching the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match). It returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: A class that inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The script processes a `SkillRequest` to extract a search term.
  - It then queries the PostgreSQL database for matching records or the total count of people.
  - The results are formatted and returned as a `SkillResponse`.

#### Patterns
- **Singleton**: The database connection is managed within the `_get_conn` function, which can be considered a singleton pattern for database connections.
- **Observer**: The logging mechanism (`logger`) acts as an observer to log errors.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `psycopg2.extras`: For using `RealDictCursor`.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Interfaces**:
  - `execute`: A method that processes a `SkillRequest` and returns a `SkillResponse`.

#### Database
- **Tables/Labels**:
  - **PostgreSQL Table**: `people` (columns: `id`, `prefix`, `first_name`, `middle_name`, `last_name`, `suffix`, `known_as`, `display_text`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_zip`, `birth_country`, `date_of_death`, `notes`, `canonical_id`, `created_at`, `updated_at`).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**:
  - The script attempts to extract a search term from the request message using specific keywords like "who is", "find person", "lookup", etc.
- **Database Query**:
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as` fields.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**:
  - The script formats the results into a human-readable summary and structured data format.

#### Integration Points
- **Mythos Subsystems**:
  - **Skill Engine**: The `PeopleLookupSkill` integrates with the Mythos skill engine, which handles the `SkillRequest` and `SkillResponse`.
  - **Database Layer**: It interacts with the PostgreSQL database to fetch people records.
  - **Logging**: It uses the logging subsystem to log errors and other important information.

### Summary
This script provides a robust mechanism for searching and retrieving people records from the Mythos database based on various search terms and conditions. It integrates seamlessly with the Mythos skill engine and database layer, ensuring efficient and accurate data retrieval and processing.
