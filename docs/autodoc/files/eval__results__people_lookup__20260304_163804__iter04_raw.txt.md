# eval/results/people_lookup/20260304_163804/iter04_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 182

---

### Documentation for `eval/results/people_lookup/20260304_163804/iter04_raw.txt`

#### Purpose
This file contains the implementation of a skill named `PeopleLookupSkill` that performs a search on the Mythos people table based on first name, last name, or known alias. It returns matching records with birth data or the total count of people in the registry if no search term is provided.

#### Architecture
The file is structured as follows:
- **Imports**: Necessary modules and libraries are imported.
- **Connection Function**: `_get_conn()` establishes a connection to the PostgreSQL database.
- **Class Definition**: `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to perform the search.
- **Helper Methods**: `_extract_search_term`, `_format_name`, and `_format_birth_location` are helper methods used within the `execute` method.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The database connection is managed within the `_get_conn` function, ensuring a consistent connection setup.
- **Observer**: The logging mechanism observes and logs errors during execution.

#### Dependencies
- **Imports**: 
  - `os`, `logging`, `re`, `typing`
  - `psycopg2`, `psycopg2.extras`
  - `dotenv` for environment variable loading
  - `engine.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`

#### Interfaces
- **SkillBase Inheritance**: The class `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object.

#### Database
- **Tables**: The `people` table is queried for records based on the search term.
- **Queries**: 
  - `SELECT COUNT(*) as count FROM people` to get the total count of people.
  - `SELECT ... FROM people WHERE LOWER(first_name) LIKE LOWER(%s) OR LOWER(last_name) LIKE LOWER(%s) OR LOWER(known_as) LIKE LOWER(%s)` to find matching records.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.
- **Configuration File**: `/opt/mythos/.env` is used to load environment variables.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method cleans and extracts the search term from the user message.
- **Database Query Execution**: The `execute` method constructs and executes the SQL query to find matching records or count all records.
- **Result Formatting**: The `_format_name` and `_format_birth_location` methods format the person's name and birth location for display.
- **Error Handling**: Errors are logged, and a `SkillResponse` with an error message is returned.

#### Integration Points
- **SkillBase**: The `PeopleLookupSkill` class integrates with the Mythos skill framework by inheriting from `SkillBase` and implementing the `execute` method.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to perform queries.
- **Environment Variables**: The file integrates with the environment configuration to load database connection details.

### Summary
The `PeopleLookupSkill` class provides a robust mechanism to search the Mythos people table based on various criteria and returns formatted results or a count of all people. It integrates with the Mythos skill framework and PostgreSQL database, ensuring efficient and reliable data retrieval and processing.
