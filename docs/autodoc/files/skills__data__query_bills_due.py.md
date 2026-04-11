# skills/data/query_bills_due.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 175

---

### File: skills/data/query_bills_due.py

#### Purpose
This file contains the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due within a specified number of days from the Mythos database. It processes user messages to determine the lookahead period, queries the database for bills due within that period, and formats the results into a summary.

#### Architecture
The file is structured around the `QueryBillsDueSkill` class, which inherits from `SkillBase`. The class contains several methods:
- `execute`: The main entry point for the skill, which orchestrates the entire process.
- `_detect_days`: Detects the number of days to look ahead from the user message.
- `_query_bills`: Queries the database for bills due within the specified number of days.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: A top-level function that serves as an entry point for the skill execution.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is used throughout the execution.
- **Factory**: The `_build_summary` and `_format_results` methods can be seen as factory methods that create formatted results and summaries from raw data.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database interactions.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that processes the user request and returns a `SkillResponse` object containing the results.
- **Private Methods**:
  - `_detect_days`: Detects the number of days to look ahead from the user message.
  - `_query_bills`: Queries the database for bills due within the specified number of days.
  - `_format_results`: Formats the raw query results.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Tables**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores overrides for specific bills, such as payment status.
- **Labels**: None (since this file only interacts with PostgreSQL tables).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host for the PostgreSQL database.
  - `DB_NAME`: Name of the database.
  - `DB_USER`: Username for the database.
  - `DB_PASSWORD`: Password for the database.
  - `DB_PORT`: Port for the database.

#### Key Logic
1. **Detecting Lookahead Days**:
   - The `_detect_days` method parses the user message to determine the number of days to look ahead. It supports keywords like "week", "month", "today", and "tomorrow", and can also detect numeric values.

2. **Querying Bills**:
   - The `_query_bills` method queries the `recurring_bills` table for bills due within the specified number of days. It also joins with the `bill_overrides` table to check if any bills are already paid.

3. **Formatting Results**:
   - The `_format_results` method converts the raw query results into a more structured format, including the expected amount, merchant name, and payment status.

4. **Building Summary**:
   - The `_build_summary` method creates a summary string that includes the total number of bills due, the total amount due, and details of each bill.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, which provides a framework for skill execution.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, which is used throughout the file.
- **SkillRequest/SkillResponse**: The `execute` method processes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos skill execution framework.
