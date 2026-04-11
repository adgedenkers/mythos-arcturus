# eval/results/query_bills_due/20260305_091233/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 65

---

### File: `eval/results/query_bills_due/20260305_091233/pass01_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryBillsDueSkill`) that queries upcoming bills due within a specified number of days from the current date. It interacts with a PostgreSQL database to retrieve bill information and checks for payment overrides.

#### Architecture
The file is structured around a single class `QueryBillsDueSkill` that inherits from `SkillBase`. This class contains several methods to handle different aspects of the bill query process:
- `_detect_days`: Detects the number of days ahead to look for bills from the input message.
- `_query_bills`: Queries the database for bills due within the specified number of days.
- `_format_results`: Formats the query results into a readable list.
- `_build_summary`: Builds a summary of the results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: The main entry point for the skill, which orchestrates the bill query process.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and orchestrates the execution of the bill query process.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `datetime`, `timedelta`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the main method exposed to other parts of the system.
- **Internal Methods**: `_detect_days`, `_query_bills`, `_format_results`, `_build_summary`.

#### Database
- **Tables/Labels**: `datetime`, `psycopg2`, `dotenv`, `engine`, `message`, `bill_overrides`.
- **Operations**: The file reads from the `bill_overrides` table to check for payment overrides and likely queries a `bills` table (not explicitly named but implied).

#### Configuration
- **Environment Variables**: The file uses environment variables to configure the database connection (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).
- **Dotenv**: Uses `dotenv` to load environment variables from a `.env` file.

#### Key Logic
1. **Detect Lookahead Days**: The `_detect_days` method parses the input message to determine the number of days ahead to look for bills. If no specific number is found, it defaults to 7 days.
2. **Query Bills**: The `_query_bills` method queries the database for bills due within the specified number of days. It likely performs a `LEFT JOIN` with the `bill_overrides` table to check if any bills have been paid.
3. **Format Results**: The `_format_results` method formats the query results into a readable list.
4. **Build Summary**: The `_build_summary` method creates a summary of the results, indicating the number of bills due, their total amount, and the specific details of each bill.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, indicating that it integrates with the Mythos skill system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_query_bills` method.
- **Logging**: The file uses the `logging` module to log any relevant information or errors during execution.

This file is a crucial component of the Mythos system, providing a way to query and summarize upcoming bills due within a specified timeframe, integrating with the database and skill system to provide a seamless user experience.
