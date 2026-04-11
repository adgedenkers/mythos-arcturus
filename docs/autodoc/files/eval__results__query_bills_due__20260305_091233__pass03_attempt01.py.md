# eval/results/query_bills_due/20260305_091233/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 171

---

### File: `eval/results/query_bills_due/20260305_091233/pass03_attempt01.py`

#### Purpose
This file contains a skill (`QueryBillsDueSkill`) that queries upcoming bills due in the next N days using the Mythos database. It processes user messages to determine the number of days to look ahead, retrieves bill information, checks for payment overrides, and formats the results into a summary.

#### Architecture
- **Class**: `QueryBillsDueSkill` inherits from `SkillBase` and implements the `execute` method.
- **Methods**:
  - `execute`: Main method that processes the request, detects lookahead days, queries bills, formats results, and builds a summary.
  - `_detect_days`: Parses the message to determine the number of days to look ahead.
  - `_query_bills`: Queries the database for bills due in the next N days.
  - `_format_results`: Formats the query results into a list of dictionaries.
  - `_build_summary`: Builds a summary string from the formatted results.
- **Top-level Functions**:
  - `_get_conn`: Establishes a database connection.
  - `execute`: An asynchronous function that processes the request and returns a `SkillResponse`.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern for database connection management.
- **Factory**: The `QueryBillsDueSkill` class can be seen as a factory for creating bill query responses.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `datetime`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Exposed Methods**: `execute` method of `QueryBillsDueSkill` class.
- **SkillBase Integration**: Implements the `SkillBase` interface, which likely includes methods for handling skill execution and response generation.

#### Database
- **Tables**: `recurring_bills`, `bill_overrides`.
- **Queries**: 
  - Queries `recurring_bills` and `bill_overrides` to retrieve bills due in the next N days.
  - Uses `LEFT JOIN` to check for payment overrides.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.
- **dotenv**: Loads environment variables from a `.env` file.

#### Key Logic
- **Day Detection**: Parses the user message to determine the number of days to look ahead.
- **Database Query**: Retrieves bills due in the next N days, considering payment overrides.
- **Result Formatting**: Converts query results into a list of dictionaries.
- **Summary Building**: Constructs a summary string detailing the bills due and their amounts.

#### Integration Points
- **SkillBase**: Integrates with the `SkillBase` class to handle skill execution and response generation.
- **Database**: Connects to the PostgreSQL database to retrieve bill information.
- **Message Parsing**: Processes user messages to determine the number of days to look ahead.
- **Response Generation**: Generates a `SkillResponse` object containing the summary of bills due.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a database connection using environment variables.
- **Dependencies**: `psycopg2`, `os`, `dotenv`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### `QueryBillsDueSkill`
- **Purpose**: Implements the logic for querying upcoming bills due in the next N days.
- **Methods**:
  - `execute`: Main method that processes the request, detects lookahead days, queries bills, formats results, and builds a summary.
  - `_detect_days`: Parses the message to determine the number of days to look ahead.
  - `_query_bills`: Queries the database for bills due in the next N days.
  - `_format_results`: Formats the query results into a list of dictionaries.
  - `_build_summary`: Builds a summary string from the formatted results.

#### `_detect_days`
- **Purpose**: Parses the user message to determine the number of days to look ahead.
- **Logic**: Checks for keywords like 'week', 'month', 'today', 'tomorrow', and extracts numerical values.

#### `_query_bills`
- **Purpose**: Queries the database for bills due in the next N days.
- **Logic**: Uses a `LEFT JOIN` to check for payment overrides and handles month wraparound.

#### `_format_results`
- **Purpose**: Converts query results into a list of dictionaries.
- **Logic**: Iterates over the query results and formats each bill into a dictionary.

#### `_build_summary`
- **Purpose**: Constructs a summary string detailing the bills due and their amounts.
- **Logic**: Separates paid and unpaid bills and constructs a summary string accordingly.

This file is a crucial part of the Mythos system, enabling users to query upcoming bills due in the next N days and receive a formatted summary of the results.
