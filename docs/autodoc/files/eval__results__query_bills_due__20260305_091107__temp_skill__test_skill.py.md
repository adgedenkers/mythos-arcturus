# eval/results/query_bills_due/20260305_091107/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 199

---

### File: `eval/results/query_bills_due/20260305_091107/temp_skill/test_skill.py`

#### Purpose
This file contains the implementation of the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due in the next N days from a PostgreSQL database and formatting the results for a user-friendly summary.

#### Architecture
The file is structured around the `QueryBillsDueSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the bill query process:
- `_get_conn`: A top-level function to establish a PostgreSQL database connection.
- `execute`: The main method that orchestrates the bill query process.
- `_detect_days`: Determines the number of days ahead based on the user message.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the query results into a list of dictionaries.
- `_build_summary`: Builds a summary of the results for user consumption.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create and return a database connection.
- **Singleton**: The `_get_conn` function ensures a single connection is created and reused, mimicking a singleton pattern for database connections.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `datetime`, `timedelta`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), which takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_detect_days`, `_query_bills`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `recurring_bills`, `bill_overrides`.
- **Queries**: The `_query_bills` method performs a query on `recurring_bills` and `bill_overrides` to fetch bills due in the next N days.

#### Configuration
- **Environment Variables**: The `_get_conn` function uses environment variables to configure the PostgreSQL database connection.
- **Dotenv**: `load_dotenv()` is used to load environment variables from a `.env` file.

#### Key Logic
1. **Detect Lookahead Days**: `_detect_days` method parses the user message to determine the number of days ahead to query bills.
2. **Query Bills**: `_query_bills` method queries the PostgreSQL database for bills due in the next N days, handling month wraparound if necessary.
3. **Format Results**: `_format_results` method formats the query results into a list of dictionaries.
4. **Build Summary**: `_build_summary` method constructs a summary of the results, ensuring ASCII encoding for compatibility.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, indicating integration with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request/response pipeline.
- **Database Connection**: The `_get_conn` function provides a reusable database connection, ensuring consistent database access across the system.

### Summary
This file implements the `QueryBillsDueSkill` class, which queries upcoming bills due in the next N days from a PostgreSQL database and formats the results for user consumption. The class is designed to integrate seamlessly with the Mythos system's skill framework and database access mechanisms.
