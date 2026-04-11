# eval/results/people_lookup/20260304_163804/best.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### Documentation for `eval/results/people_lookup/20260304_163804/best.py`

#### Purpose
This file contains the `PeopleLookupSkill` class, which is designed to search the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and return matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**: 
  - `_get_conn`: A utility function to establish a connection to the PostgreSQL database.
  - `execute`: A top-level asynchronous function that handles the execution of the skill.
- **Data Flow**: 
  - The `execute` method processes the incoming `SkillRequest`, extracts the search term, and queries the PostgreSQL database to retrieve matching records or the total count of people.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is established.
- **Observer**: The `logger` object is used to log errors, which can be considered an observer pattern.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that processes the `SkillRequest` and returns a `SkillResponse` object.

#### Database
- **Tables**: 
  - `people`: The primary table used for querying people records.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in the `.env` file and used to establish the database connection.

#### Key Logic
- **Search Term Extraction**: 
  - The method extracts search terms from the message using keywords like "who is", "find person", "lookup", "born", "birthday", and "birth data".
- **Query Execution**: 
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as` fields.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**: 
  - Formats the results into a human-readable summary and structured data.

#### Integration Points
- **SkillBase**: 
  - The `PeopleLookupSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill system.
- **SkillRequest and SkillResponse**: 
  - The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating it integrates with the request-response mechanism of the Mythos system.
- **Database Connection**: 
  - Uses `_get_conn` to establish a connection to the PostgreSQL database, indicating it integrates with the database layer of the Mythos system.

### Summary
This file implements a skill for the Mythos system that allows searching the people table in the PostgreSQL database based on various name-related fields. It handles both search term extraction and total count retrieval, and it integrates with the broader Mythos skill architecture through the `SkillBase` class and the `SkillRequest`/`SkillResponse` objects.
