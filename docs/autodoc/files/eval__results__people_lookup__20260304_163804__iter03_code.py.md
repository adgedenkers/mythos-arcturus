# eval/results/people_lookup/20260304_163804/iter03_code.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### File: eval/results/people_lookup/20260304_163804/iter03_code.py

#### Purpose
This file contains the implementation of a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**: 
  - `_get_conn`: A helper function to establish a PostgreSQL database connection.
  - `execute`: An asynchronous function that processes the request and returns a `SkillResponse` object.
- **Data Flow**: 
  - The `execute` method processes the incoming `SkillRequest`, extracts search terms, queries the database, and constructs a `SkillResponse` object with the results.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connection management.
- **Factory**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable handling.
  - `logging`: For logging errors and information.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Exposed to the system for processing skill requests.
- **Exposed Classes**: 
  - `PeopleLookupSkill`: Exposed as a skill that can be invoked by the system.

#### Database
- **Tables**: 
  - `people`: The table from which the skill retrieves data based on the search term.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env` for database connection settings.

#### Key Logic
- **Search Term Extraction**: 
  - The `execute` method parses the incoming message to extract a search term based on predefined phrases like "who is", "find person", "lookup", etc.
- **Database Query**: 
  - If a search term is found, it performs a case-insensitive LIKE match on `first_name`, `last_name`, and `known_as` fields.
  - If no search term is found, it returns the total count of people in the registry.
- **Result Formatting**: 
  - The results are formatted into a summary and structured data for the `SkillResponse` object.

#### Integration Points
- **SkillBase**: 
  - The `PeopleLookupSkill` class inherits from `SkillBase`, integrating with the skill execution framework.
- **SkillRequest**: 
  - The `execute` method processes `SkillRequest` objects, which are part of the Mythos skill execution pipeline.
- **SkillResponse**: 
  - The `execute` method returns `SkillResponse` objects, which are used by the system to handle the results of the skill execution.

### Summary
This file implements a skill that performs a database query on the `people` table based on extracted search terms from a message. It handles both specific search queries and a fallback to return the total count of people if no search term is found. The skill integrates with the Mythos skill execution framework by inheriting from `SkillBase` and using `SkillRequest` and `SkillResponse` objects for request and response handling.
