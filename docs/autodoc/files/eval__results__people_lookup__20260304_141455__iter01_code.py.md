# eval/results/people_lookup/20260304_141455/iter01_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 207

---

### File: `eval/results/people_lookup/20260304_141455/iter01_code.py`

#### Purpose
This file defines a `PeopleLookupSkill` class that implements a skill to search the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: A subclass of `SkillBase` that provides the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn()`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest`, extracts the search term from the message, and queries the PostgreSQL database to retrieve matching records or the total count of people.
  - The results are formatted into a `SkillResponse` object, which is returned to the caller.

#### Patterns
- **Singleton**: The database connection is established using a helper function `_get_conn()`, but it does not enforce a singleton pattern.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `re`: For regular expression matching.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database connection and querying.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: Processes the request and returns a response containing the search results or total count.

#### Database
- **Tables/Labels**:
  - `people`: The PostgreSQL table from which the search is performed. It contains fields like `first_name`, `last_name`, `known_as`, `date_of_birth`, `birth_city`, etc.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for connecting to the PostgreSQL database.
- **Files**:
  - `/opt/mythos/.env`: Environment variables file loaded using `dotenv`.

#### Key Logic
- **Search Term Extraction**:
  - The function uses regular expressions to extract the search term from the message based on specific triggers like "who is", "find person", "lookup", etc.
- **Database Query**:
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as` fields.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**:
  - The results are formatted into a structured `data` dictionary and a human-readable `summary` string.

#### Integration Points
- **SkillBase Class**:
  - The `PeopleLookupSkill` class inherits from `SkillBase`, which likely provides a framework for handling skills in the Mythos system.
- **SkillRequest and SkillResponse**:
  - The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos skill execution pipeline.

This file is a critical component of the Mythos system, enabling efficient and flexible searching of the people registry based on various criteria.
