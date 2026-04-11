# eval/results/query_bills_due/20260305_091233/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 164

---

### Documentation for `eval/results/query_bills_due/20260305_091233/pass04_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryBillsDueSkill`) that queries upcoming bills due in the next N days from a PostgreSQL database. It detects the number of days to look ahead from the input message, queries the bills, formats the results, and builds a summary.

#### Architecture
The file is structured around a single class `QueryBillsDueSkill` which inherits from `SkillBase`. The class contains several methods:
- `execute`: The main entry point for the skill, which orchestrates the bill query process.
- `_detect_days`: Parses the input message to determine the number of days to look ahead.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the raw query results into a structured list.
- `_build_summary`: Builds a summary string from the formatted results.

There are also several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential direct use.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function could be adapted to return a singleton connection if needed, but it currently returns a new connection each time.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `re`: For regular expression matching.
- `psycopg2`: For PostgreSQL database interaction.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Public Methods**:
  - `execute`: The main method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_detect_days`: Parses the input message to determine the number of days to look ahead.
  - `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
  - `_format_results`: Formats the raw query results into a structured list.
  - `_build_summary`: Builds a summary string from the formatted results.

#### Database
- **Tables/Labels**:
  - `recurring_bills`: Stores information about recurring bills.
  - `bill_overrides`: Stores overrides for specific bills, such as payment status.
  - `datetime`: Used for date calculations.
  - `psycopg2`: PostgreSQL connection and cursor factory.
  - `dotenv`: Used for loading environment variables.
  - `engine`: Base class for skills.
  - `message`: Used for parsing input messages.
  - `dom`: Day of the month used in queries.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Database host.
  - `DB_NAME`: Database name.
  - `DB_USER`: Database user.
  - `DB_PASSWORD`: Database password.
  - `DB_PORT`: Database port.

#### Key Logic
- **_detect_days**: Parses the input message to determine the number of days to look ahead, defaulting to 7 days if no specific number is found.
- **_query_bills**: Queries the PostgreSQL database for bills due in the next N days, handling month wraparound if necessary.
- **_format_results**: Converts the raw query results into a structured list of dictionaries.
- **_build_summary**: Builds a summary string from the formatted results, including the total number of bills and the total amount due.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.
- **Environment Variables**: Loads environment variables using `dotenv`, integrating with the Mythos configuration system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to interact with the Mythos skill execution framework.
