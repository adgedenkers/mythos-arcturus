# eval/results/query_bills_due/20260305_091233/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 175

---

### File: `eval/results/query_bills_due/20260305_091233/temp_skill/test_skill.py`

#### Purpose
This file contains the implementation of a skill named `QueryBillsDueSkill` which queries upcoming bills due in the next N days from the Mythos database and provides a formatted summary of the results.

#### Architecture
The file is structured around a class `QueryBillsDueSkill` which inherits from `SkillBase`. The class contains several methods to handle different parts of the bill query process:
- `execute`: The main entry point for the skill, which orchestrates the bill query process.
- `_detect_days`: Detects the number of days ahead from the user's message.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the query results into a more readable structure.
- `_build_summary`: Builds a summary of the bill results.

Additionally, there are top-level functions `_get_conn` and `execute` which are used for database connection and asynchronous execution respectively.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_detect_days`: Detects the number of days ahead from the user's message.
  - `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the bill results.

#### Database
- **Tables/Labels**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores overrides for specific bills, such as payment status.
  - `datetime`: Used for date and time operations.
  - `message`: Used for storing or querying message data.
  - `dom`: Used for day-of-month operations.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Hostname of the PostgreSQL database.
  - `DB_NAME`: Name of the database.
  - `DB_USER`: Username for the database.
  - `DB_PASSWORD`: Password for the database.
  - `DB_PORT`: Port number for the database.

#### Key Logic
1. **Detecting Days**:
   - The `_detect_days` method parses the user's message to determine the number of days ahead to query for bills. It handles keywords like 'week', 'month', 'today', and 'tomorrow', and also looks for explicit numbers.

2. **Querying Bills**:
   - The `_query_bills` method queries the PostgreSQL database for bills due in the next N days. It uses a `LEFT JOIN` to check for overrides in the `bill_overrides` table to determine if a bill has already been paid.

3. **Formatting Results**:
   - The `_format_results` method formats the query results into a list of dictionaries, each containing bill details.

4. **Building Summary**:
   - The `_build_summary` method constructs a summary string that includes the number of bills due, the total amount due, and details of each bill.

#### Integration Points
- **SkillBase Integration**:
  - The `QueryBillsDueSkill` class inherits from `SkillBase`, which provides a framework for executing skills.
- **Database Integration**:
  - The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_query_bills` method.
- **Environment Variables**:
  - The `load_dotenv` function loads environment variables from a `.env` file, which are used to configure the database connection.
