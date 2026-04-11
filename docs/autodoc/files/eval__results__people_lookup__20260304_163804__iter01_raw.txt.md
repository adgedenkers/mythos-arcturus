# eval/results/people_lookup/20260304_163804/iter01_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### Documentation for `eval/results/people_lookup/20260304_163804/iter01_raw.txt`

#### Purpose
This file contains the implementation of a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**: 
  - `_get_conn()`: Establishes a connection to the PostgreSQL database.
- **Data Flow**: 
  - The `execute` method processes the incoming `SkillRequest` to extract a search term.
  - It then queries the PostgreSQL database to find matching records or the total count of people.
  - The results are formatted and returned as a `SkillResponse`.

#### Patterns
- **Singleton**: The database connection is managed within the `_get_conn` function, ensuring a single connection per invocation.
- **Factory**: The `SkillResponse` object is created based on the query results.

#### Dependencies
- **Imports**: 
  - `os`, `logging`, `typing`: Standard Python libraries.
  - `psycopg2`, `psycopg2.extras`: PostgreSQL database interaction.
  - `dotenv`: For loading environment variables.
  - `engine.base`: Contains `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Processes the `SkillRequest` and returns a `SkillResponse`.

#### Database
- **Tables**: 
  - `people`: The table containing person records, queried for `first_name`, `last_name`, `known_as`, and other fields.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**: 
  - The search term is extracted from the `SkillRequest.message` using predefined triggers like "who is", "find person", etc.
- **Database Query**: 
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as`.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**: 
  - Results are formatted into a summary and structured data for the `SkillResponse`.

#### Integration Points
- **Mythos Engine**: 
  - This skill integrates with the Mythos engine through the `SkillBase` class, which handles the request and response lifecycle.
- **Database Layer**: 
  - Connects to the PostgreSQL database to retrieve person records.
- **Environment Configuration**: 
  - Uses environment variables for database connection details, loaded via `dotenv`.

### Summary
The `PeopleLookupSkill` class provides a robust mechanism to search and retrieve person records from the Mythos people table based on various search terms. It handles both case-insensitive searches and total count retrieval, ensuring comprehensive and accurate responses to user queries.
