# eval/results/query_bills_due/20260305_091233/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 175

---

### Documentation for `eval/results/query_bills_due/20260305_091233/pass06_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryBillsDueSkill`) that queries upcoming bills due in the next N days from the Mythos database. It processes user messages to determine the lookahead period, retrieves relevant bill information, checks for payment overrides, and formats the results into a summary.

#### Architecture
The file defines a class `QueryBillsDueSkill` that inherits from `SkillBase`. The class contains methods for executing the skill, detecting the number of days to look ahead, querying bills, formatting results, and building a summary. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Factory Pattern**: The `_get_conn` function acts as a factory method to create and return a database connection.
- **Singleton Pattern**: The database connection is created and managed within the `_get_conn` function, ensuring a single connection is used throughout the execution.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `datetime`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_detect_days`, `_query_bills`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

#### Database
- **Tables**: `recurring_bills`, `bill_overrides`
- **Queries**: 
  - Retrieves bills due in the next N days from `recurring_bills`.
  - Left joins `bill_overrides` to check for payment status.

#### Configuration
- **Environment Variables**: Configured via `.env` file using `dotenv` for database connection details.

#### Key Logic
1. **Detect Lookahead Days**: `_detect_days` method parses the user message to determine the number of days to look ahead. It handles keywords like 'week', 'month', 'today', and 'tomorrow' and extracts numerical values.
2. **Query Bills**: `_query_bills` method constructs and executes a SQL query to retrieve bills due within the specified period. It handles month wraparound by splitting the query into two parts if the end day exceeds the current month's days.
3. **Format Results**: `_format_results` method formats the raw query results into a structured list.
4. **Build Summary**: `_build_summary` method generates a summary string that includes the total number of bills, total amount due, and details of each bill.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to manage database connections, ensuring consistent access to the PostgreSQL database.
- **Environment Variables**: Configures database connection details via environment variables, allowing for easy deployment and configuration changes.

### Summary
This file implements a skill that queries upcoming bills due in the next N days from the Mythos database. It processes user messages to determine the lookahead period, retrieves relevant bill information, checks for payment overrides, and formats the results into a summary. The skill integrates with the Mythos framework via `SkillBase` and manages database connections through a factory method.
