# eval/results/query_bills_due/20260305_091107/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 199

---

### Documentation for `eval/results/query_bills_due/20260305_091107/pass06_attempt01.py`

#### Purpose
This file contains the implementation of a skill named `QueryBillsDueSkill` that queries upcoming bills due in the next N days from a PostgreSQL database and formats the results for presentation.

#### Architecture
The file contains a single class `QueryBillsDueSkill` that inherits from `SkillBase`. This class has several methods:
- `execute`: The main entry point for the skill, which orchestrates the entire process.
- `_detect_days`: Detects the number of days to look ahead based on the input message.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the query results into a list of dictionaries.
- `_build_summary`: Builds a summary of the results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that is not used within the class but might be for testing or external use.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it ensures that only one database connection is established per call.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the input request.

#### Dependencies
The file imports the following modules:
- `os`: For environment variable access.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
The `QueryBillsDueSkill` class exposes the following methods:
- `execute`: The main method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- `_detect_days`: Detects the number of days to look ahead based on the input message.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the query results into a list of dictionaries.
- `_build_summary`: Builds a summary of the results.

#### Database
The file interacts with the following PostgreSQL tables:
- `recurring_bills`: Stores information about recurring bills.
- `bill_overrides`: Stores overrides for specific bills, such as payment status.

#### Configuration
The file uses environment variables for database connection details:
- `POSTGRES_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_PORT`

#### Key Logic
1. **Detecting Days**: The `_detect_days` method parses the input message to determine the number of days to look ahead. It checks for keywords like 'week', 'month', 'today', and 'tomorrow', and also looks for numerical values.
2. **Querying Bills**: The `_query_bills` method constructs a SQL query to fetch bills due in the next N days. It handles month wraparound by splitting the query into two parts if the lookahead period crosses into the next month.
3. **Formatting Results**: The `_format_results` method converts the raw query results into a more readable format.
4. **Building Summary**: The `_build_summary` method creates a summary string that includes the number of bills due, the total amount due, and details of each bill.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, which likely provides a framework for skill execution and response handling.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos system's request-response mechanism.

### Summary
This file implements a skill that queries upcoming bills due in the next N days from a PostgreSQL database. It handles parsing the input message, querying the database, formatting the results, and building a summary. The skill integrates with the Mythos system's framework for skill execution and response handling.
