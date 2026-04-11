# eval/results/query_bills_due/20260305_091233/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 175

---

### Documentation for `query_bills_due/20260305_091233/pass05_attempt01.py`

#### Purpose
This file contains the implementation of the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due within a specified number of days from the current date. It retrieves bill information from the PostgreSQL database, checks for payment overrides, and formats the results into a summary.

#### Architecture
The file is structured around the `QueryBillsDueSkill` class, which inherits from `SkillBase`. The class contains several methods for different stages of the bill query process:
- `_detect_days`: Detects the number of days to look ahead from the user message.
- `_query_bills`: Queries the PostgreSQL database for bills due within the specified days.
- `_format_results`: Formats the query results into a more readable structure.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions for database connection and execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a consistent database connection.
- **Factory Method**: The `execute` method acts as a factory method to produce a `SkillResponse` object.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that processes the request and returns a `SkillResponse` object.
- **Private Methods**:
  - `_detect_days`: Detects the number of days to look ahead.
  - `_query_bills`: Queries the PostgreSQL database for bills.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Tables/Labels**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores payment overrides for specific bills.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
1. **Detect Days**:
   - The `_detect_days` method parses the user message to determine the number of days to look ahead. It checks for keywords like "week", "month", "today", and "tomorrow" and uses regular expressions to find numeric values.

2. **Query Bills**:
   - The `_query_bills` method constructs a SQL query to retrieve bills due within the specified days. It handles month wraparound by querying both the current and next month if necessary.

3. **Format Results**:
   - The `_format_results` method formats the query results into a list of dictionaries, each containing bill details.

4. **Build Summary**:
   - The `_build_summary` method constructs a summary string that includes the total number of bills, the total amount due, and details of each bill.

#### Integration Points
- **Mythos System**:
  - The `QueryBillsDueSkill` class integrates with the Mythos system by inheriting from `SkillBase` and using `SkillRequest` and `SkillResponse` objects.
  - It interacts with the PostgreSQL database to retrieve and process bill information.
  - It is triggered by specific keywords like "bill", "bills", "due", etc., as defined in the `triggers` attribute.

This file is a crucial component of the Mythos system, providing a robust mechanism for querying and summarizing upcoming bills due within a specified timeframe.
