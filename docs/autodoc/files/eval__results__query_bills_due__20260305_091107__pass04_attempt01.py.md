# eval/results/query_bills_due/20260305_091107/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 180

---

### Documentation for `eval/results/query_bills_due/20260305_091107/pass04_attempt01.py`

#### Purpose
This file contains the `QueryBillsDueSkill` class, which is designed to query upcoming bills due within a specified number of days from the current date. It processes user messages to determine the number of days to look ahead, queries the PostgreSQL database for relevant bills, and formats the results into a summary.

#### Architecture
The file is structured around the `QueryBillsDueSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the bill query process:
- `_detect_days`: Detects the number of days to look ahead based on the user message.
- `_query_bills`: Queries the PostgreSQL database for bills due within the detected number of days.
- `_format_results`: Formats the query results into a structured list.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: The main execution method that orchestrates the bill query process.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and reused.
- **Factory Method**: The `execute` method acts as a factory method, coordinating the creation and execution of the bill query process.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from `.env` files.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- `execute`: Exposes the main execution method that takes a `SkillRequest` and returns a `SkillResponse`.
- `_detect_days`, `_query_bills`, `_format_results`, `_build_summary`: Internal methods used by `execute` to process the bill query.

#### Database
- **PostgreSQL Tables**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores overrides for specific bills, such as payment status.

#### Configuration
- Environment variables:
  - `DB_HOST`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_PORT`

#### Key Logic
1. **Detect Lookahead Days**:
   - The `_detect_days` method parses the user message to determine the number of days to look ahead. It supports keywords like "week", "month", "today", and "tomorrow", and can also detect numeric values.

2. **Query Bills**:
   - The `_query_bills` method queries the PostgreSQL database for bills due within the specified number of days. It handles month wraparound by splitting the query into two parts if the lookahead period spans two months.

3. **Format Results**:
   - The `_format_results` method formats the query results into a structured list, including bill details and payment status.

4. **Build Summary**:
   - The `_build_summary` method constructs a summary string that includes the count of bills, total amount due, and details of each bill.

#### Integration Points
- **Mythos System**:
  - The `QueryBillsDueSkill` class integrates with the Mythos system through the `SkillBase` class, which likely handles the overall skill execution framework.
  - The `execute` method is the entry point for the skill, which is likely invoked by the Mythos system's skill execution engine.
  - The `SkillResponse` object returned by `execute` is used to communicate the results back to the Mythos system.

This file is a critical component of the Mythos system, providing a robust and flexible way to query and summarize upcoming bills based on user input.
