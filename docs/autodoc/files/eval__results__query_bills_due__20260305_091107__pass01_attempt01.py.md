# eval/results/query_bills_due/20260305_091107/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 69

---

### File: eval/results/query_bills_due/20260305_091107/pass01_attempt01.py

#### Purpose
This file contains the implementation of a skill (`QueryBillsDueSkill`) that queries upcoming bills due within a specified number of days from the current date. It processes user requests to determine the number of days to look ahead and retrieves relevant bill information from a PostgreSQL database.

#### Architecture
The file contains a single class `QueryBillsDueSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the bill query process:
- `execute`: The main method that orchestrates the bill query process.
- `_detect_days`: Detects the number of days to look ahead from the user message.
- `_query_bills`: Queries the database for bills due within the specified number of days.
- `_format_results`: Formats the query results into a usable structure.
- `_build_summary`: Builds a summary of the results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential external use.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a single database connection is created and reused.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`
- **External Modules**: `engine.base` for `SkillBase`, `SkillRequest`, `SkillResponse`

#### Interfaces
- **Public Methods**: `execute` (both class method and top-level function)
- **Private Methods**: `_detect_days`, `_query_bills`, `_format_results`, `_build_summary`

#### Database
- **Tables/Labels**: `datetime`, `message`, `bill_overrides`
- **Operations**: Reads from `bill_overrides` and `message` tables to retrieve and process bill information.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.

#### Key Logic
1. **Detect Days**: The `_detect_days` method parses the user message to determine the number of days to look ahead for bills due.
2. **Query Bills**: The `_query_bills` method queries the PostgreSQL database for bills due within the specified number of days, using a `LEFT JOIN` with `bill_overrides` to check for any paid statuses.
3. **Format Results**: The `_format_results` method formats the raw query results into a structured list.
4. **Build Summary**: The `_build_summary` method generates a summary string that includes the number of bills due, the total amount, and individual bill details.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, integrating with the broader Mythos system's skill framework.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch bill information.
- **Environment Configuration**: Uses environment variables loaded via `dotenv` for database connection details.

### Detailed Documentation

#### Class: `QueryBillsDueSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'query_bills_due'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Show upcoming bills due in the next N days'
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (300 seconds).

- **Methods**:
  - `execute`: Asynchronous method that orchestrates the bill query process.
  - `_detect_days`: Parses the user message to determine the number of days to look ahead.
  - `_query_bills`: Queries the database for bills due within the specified number of days.
  - `_format_results`: Formats the query results into a structured list.
  - `_build_summary`: Builds a summary string of the bill results.

#### Top-Level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- `execute`: A top-level function that mirrors the class method for potential external use.

#### Database Operations
- **Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **Tables**: Queries `bill_overrides` and `message` tables.
- **Cursor Factory**: Uses `RealDictCursor` to return query results as dictionaries.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are loaded using `dotenv` for database connection details.

This file is a critical component of the Mythos system, providing a robust mechanism for querying and summarizing upcoming bills due within a specified timeframe.
