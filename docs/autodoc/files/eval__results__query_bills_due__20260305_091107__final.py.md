# eval/results/query_bills_due/20260305_091107/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 199

---

### Documentation for `eval/results/query_bills_due/20260305_091107/final.py`

#### Purpose
This file contains the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due in the next N days from a PostgreSQL database and formatting the results into a summary.

#### Architecture
- **Class**: `QueryBillsDueSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Main method that orchestrates the bill query process.
  - `_detect_days`: Detects the number of days ahead from the input message.
  - `_query_bills`: Queries the database for bills due within the specified days.
  - `_format_results`: Formats the query results into a list of dictionaries.
  - `_build_summary`: Builds a summary of the results.
- **Top-level Functions**:
  - `_get_conn`: Establishes a database connection.
  - `execute`: A top-level function that wraps the `execute` method of `QueryBillsDueSkill`.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection is established and closed properly.
- **Factory**: The `SkillBase` class likely acts as a factory for creating skill instances.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Public method to execute the skill.
- **Exposed Functions**:
  - `_get_conn`: Public function to get a database connection.

#### Database
- **Tables and Labels**:
  - `recurring_bills`: Table containing recurring bill information.
  - `bill_overrides`: Table containing overrides for specific bill payments.
  - `dotenv`: Configuration table for environment variables.
  - `engine`: Configuration table for the database engine.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: PostgreSQL host.
  - `DB_NAME`: Database name.
  - `DB_USER`: Database user.
  - `DB_PASSWORD`: Database password.
  - `DB_PORT`: Database port.

#### Key Logic
- **_detect_days**: Detects the number of days ahead from the input message using regular expressions and keyword matching.
- **_query_bills**: Queries the PostgreSQL database for bills due within the specified days, handling month wraparound scenarios.
- **_format_results**: Formats the query results into a list of dictionaries.
- **_build_summary**: Builds a summary string of the results, ensuring ASCII encoding.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, which provides a base structure for skills.
- **SkillRequest and SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **Environment Variables**: Loads environment variables using `dotenv` for database connection details.

### Detailed Analysis

#### Class: `QueryBillsDueSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: Name of the skill.
  - `version`: Version of the skill.
  - `category`: Category of the skill.
  - `description`: Description of the skill.
  - `triggers`: List of trigger phrases for the skill.
  - `cache_ttl`: Time-to-live for cache.

#### Methods
- **execute**:
  - **Purpose**: Main method to execute the skill.
  - **Logic**:
    1. Detects the number of days ahead from the input message.
    2. Queries the database for bills due within the specified days.
    3. Formats the query results.
    4. Builds a summary of the results.
    5. Returns a `SkillResponse` object with the formatted results and summary.

- **_detect_days**:
  - **Purpose**: Detects the number of days ahead from the input message.
  - **Logic**:
    - Checks for keywords like 'week', 'month', 'today', 'tomorrow'.
    - Uses regular expressions to find numeric values in the message.
    - Defaults to 7 days if no keywords or numbers are found.

- **_query_bills**:
  - **Purpose**: Queries the database for bills due within the specified days.
  - **Logic**:
    - Establishes a database connection.
    - Calculates the end day of the month.
    - Handles month wraparound by splitting the query into two parts if the end day exceeds the current month's days.
    - Executes the query and fetches the results.
    - Closes the database connection.

- **_format_results**:
  - **Purpose**: Formats the query results into a list of dictionaries.
  - **Logic**:
    - Converts the query results into a list of dictionaries with specific keys.

- **_build_summary**:
  - **Purpose**: Builds a summary string of the results.
  - **Logic**:
    - Calculates the total amount and count of unpaid bills.
    - Formats the list of bills into a summary string.
    - Ensures ASCII encoding for the summary.

#### Top-level Functions
- **_get_conn**:
  - **Purpose**: Establishes a database connection.
  - **Logic**:
    - Loads environment variables for database connection details.
    - Establishes a connection using `psycopg2.connect`.
    - Closes the connection if an error occurs.

- **execute**:
  - **Purpose**: Wraps the `execute` method of `QueryBillsDueSkill`.
  - **Logic**:
    - Calls the `execute` method of `QueryBillsDueSkill` with the provided request.

### Conclusion
This file is a crucial component of the Mythos system, responsible for querying and summarizing upcoming bills due within a specified number of days. It leverages PostgreSQL for data retrieval and provides a structured response through the `SkillResponse` object.
