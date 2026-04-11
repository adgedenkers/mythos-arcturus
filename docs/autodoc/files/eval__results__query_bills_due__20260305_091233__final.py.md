# eval/results/query_bills_due/20260305_091233/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 175

---

### Documentation for `eval/results/query_bills_due/20260305_091233/final.py`

#### Purpose
This file contains the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due within a specified number of days from the Mythos PostgreSQL database. It processes user messages to determine the lookahead period, queries the database for relevant bills, and formats the results into a summary.

#### Architecture
- **Class**: `QueryBillsDueSkill` inherits from `SkillBase` and contains methods for executing the skill, detecting the number of days to look ahead, querying the database for bills, formatting the results, and building a summary.
- **Functions**: `_get_conn` is a top-level function to establish a database connection. Other top-level functions like `execute`, `_detect_days`, `_query_bills`, `_format_results`, and `_build_summary` are defined but not used within the class.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connections.
- **Factory**: The `execute` method acts as a factory to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `datetime`, `timedelta`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method exposed to other parts of the system.
- **SkillBase Inheritance**: The class inherits from `SkillBase`, which likely defines a common interface for skills in the Mythos system.

#### Database
- **Tables**: `recurring_bills`, `bill_overrides`.
- **Queries**: The `_query_bills` method queries the `recurring_bills` table and performs a LEFT JOIN with `bill_overrides` to check if bills are already paid.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables.
- **dotenv**: `load_dotenv()` is used to load environment variables from a `.env` file.

#### Key Logic
- **Detect Days**: `_detect_days` method parses the user message to determine the number of days to look ahead. It handles keywords like 'week', 'month', 'today', and 'tomorrow'.
- **Query Bills**: `_query_bills` method constructs a SQL query to retrieve bills due within the specified number of days, considering month wraparound.
- **Format Results**: `_format_results` method formats the raw query results into a more readable structure.
- **Build Summary**: `_build_summary` method generates a summary of the bills due, including the total number and amount.

#### Integration Points
- **SkillBase**: The class integrates with the `SkillBase` class, which likely provides a common framework for skills in the Mythos system.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to retrieve bill information.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, which is likely used by the Mythos system to handle and present the results.

### Summary
The `QueryBillsDueSkill` class in `final.py` is designed to query upcoming bills due within a specified number of days from the Mythos PostgreSQL database. It processes user messages to determine the lookahead period, queries the database for relevant bills, formats the results, and builds a summary. The class integrates with the `SkillBase` framework and uses environment variables for database configuration.
