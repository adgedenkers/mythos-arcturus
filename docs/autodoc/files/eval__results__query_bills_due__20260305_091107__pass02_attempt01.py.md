# eval/results/query_bills_due/20260305_091107/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 163

---

### Documentation for `eval/results/query_bills_due/20260305_091107/pass02_attempt01.py`

#### Purpose
This Python script defines a skill (`QueryBillsDueSkill`) that queries upcoming bills due within a specified number of days and formats the results into a summary. The skill is part of the Mythos system and is designed to be executed asynchronously.

#### Architecture
The file contains a single class `QueryBillsDueSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main entry point for the skill, which orchestrates the query and formatting process.
- `_detect_days`: Detects the number of days ahead from the user message.
- `_query_bills`: Queries the PostgreSQL database for bills due within the specified number of days.
- `_format_results`: Formats the query results into a structured list.
- `_build_summary`: Builds a summary string from the formatted results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: An asynchronous function that handles the skill execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a consistent way to get a database connection.
- **Observer Pattern**: The `execute` method acts as an observer, reacting to the user request and updating the state based on the query results.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database interactions.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: 
  - `_detect_days`: Detects the number of days from the message.
  - `_query_bills`: Queries the database for bills due in the next N days.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Tables/Labels**:
  - `recurring_bills`: Table storing recurring bill information.
  - `bill_overrides`: Table storing overrides for specific bill payments.
- **Queries**:
  - The `_query_bills` method queries the `recurring_bills` table and performs a LEFT JOIN with `bill_overrides` to check payment status.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Database connection details.
- **Configuration Files**:
  - `.env`: Environment variables are loaded using `dotenv.load_dotenv()`.

#### Key Logic
- **_detect_days**: Parses the user message to determine the number of days ahead to query bills.
- **_query_bills**: Queries the PostgreSQL database for bills due within the next N days, considering overrides.
- **_format_results**: Converts the raw query results into a structured list.
- **_build_summary**: Constructs a summary string from the formatted results, indicating the number of bills and their total amount.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch bill information.
- **FastAPI**: The `execute` method is designed to be called asynchronously, likely integrated with a FastAPI endpoint for handling user requests.

This file is a critical component of the Mythos system, providing a robust mechanism for querying and summarizing upcoming bills due within a specified timeframe.
