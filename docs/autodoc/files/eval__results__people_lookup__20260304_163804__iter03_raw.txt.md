# eval/results/people_lookup/20260304_163804/iter03_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### Documentation for `eval/results/people_lookup/20260304_163804/iter03_raw.txt`

#### Purpose
This file contains the implementation of a skill named `PeopleLookupSkill` that searches the Mythos people table by first_name, last_name, or known_as (case-insensitive LIKE match) and returns matching records with birth data. If no search term can be extracted, it returns the total count of people in the registry.

#### Architecture
The file consists of:
- A helper function `_get_conn()` to establish a PostgreSQL connection.
- A class `PeopleLookupSkill` that inherits from `SkillBase`.
- The `execute` method within `PeopleLookupSkill` that processes the skill request and returns a `SkillResponse`.

#### Patterns
- **Singleton Pattern**: The connection to the PostgreSQL database is managed within the `_get_conn` function, ensuring a single connection per invocation.
- **Factory Method Pattern**: The `SkillResponse` object is created based on the results of the database query.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `typing`: For type annotations.
- `psycopg2`: For PostgreSQL database connection and query execution.
- `dotenv`: For loading environment variables from `.env` files.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: `execute(self, request: SkillRequest) -> SkillResponse`
- **Exposed Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`

#### Database
- **Tables/Labels**: `people` table in PostgreSQL.
- **Queries**: 
  - `SELECT COUNT(*) as total FROM people;` (to get the total count of people)
  - `SELECT ... FROM people WHERE LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s OR LOWER(known_as) LIKE %s;` (to search for matching people)

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Config Files**: `.env` file located at `/opt/mythos/.env`

#### Key Logic
1. **Search Term Extraction**: The function parses the input message to extract a search term based on specific keywords like "who is", "find person", "lookup", etc.
2. **Database Query Execution**: The extracted search term is used to query the `people` table for matching records.
3. **Result Formatting**: The matching records are formatted into a summary and structured data format.
4. **Error Handling**: The function logs any errors and returns a `SkillResponse` with an error message.

#### Integration Points
- **Mythos Engine**: The `PeopleLookupSkill` class extends `SkillBase` and integrates with the Mythos engine through the `execute` method, which processes `SkillRequest` and returns `SkillResponse`.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database, which is used to execute queries.
- **Logging**: Errors are logged using the `logger` from the `logging` module.

### Summary
The `PeopleLookupSkill` class provides a robust mechanism for searching the Mythos people table based on various search terms and returning detailed birth data. It integrates seamlessly with the Mythos engine and handles database connections and error logging effectively.
