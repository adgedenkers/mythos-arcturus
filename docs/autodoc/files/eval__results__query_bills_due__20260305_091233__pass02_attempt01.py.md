# eval/results/query_bills_due/20260305_091233/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 181

---

### Documentation for `eval/results/query_bills_due/20260305_091233/pass02_attempt01.py`

#### Purpose
This file contains the implementation of the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due in the next N days from the Mythos database. It processes user messages to determine the number of days to look ahead, queries the database for relevant bills, formats the results, and builds a summary response.

#### Architecture
The file is structured around the `QueryBillsDueSkill` class, which inherits from `SkillBase`. The class contains several methods:
- `execute`: The main method that orchestrates the bill query process.
- `_detect_days`: Detects the number of days to look ahead based on the user message.
- `_query_bills`: Queries the database for bills due in the next N days.
- `_format_results`: Formats the query results into a list of dictionaries.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: A top-level function that is likely a helper or alternative entry point for testing.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection is created and reused.
- **Factory Method**: The `_build_summary` method can be seen as a factory method that creates a summary string based on the results.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: 
  - `_detect_days`: Detects the number of days to look ahead.
  - `_query_bills`: Queries the database for bills due in the next N days.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the formatted results.

#### Database
- **Tables/Labels**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores overrides for bill payments.
- **Operations**:
  - The `_query_bills` method performs a `LEFT JOIN` between `recurring_bills` and `bill_overrides` to check if bills are already paid.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configuration for the PostgreSQL database connection.

#### Key Logic
- **Detecting Days**: The `_detect_days` method parses the user message to determine the number of days to look ahead. It checks for keywords like 'week', 'month', 'today', and 'tomorrow', and uses regular expressions to find numeric values.
- **Querying Bills**: The `_query_bills` method constructs a SQL query to retrieve bills due in the next N days. It handles cases where the query spans across months.
- **Formatting Results**: The `_format_results` method converts the raw query results into a list of dictionaries with specific fields.
- **Building Summary**: The `_build_summary` method generates a summary string that includes the number of bills due, the total amount, and details of unpaid bills.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class extends `SkillBase`, integrating with the Mythos skill system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_query_bills` method.
- **Environment Configuration**: The `dotenv` library is used to load environment variables, which are then used to configure the database connection.

This file is a critical component of the Mythos system, enabling users to query and receive summaries of upcoming bills due in the next N days.
