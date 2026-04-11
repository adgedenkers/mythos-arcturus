# eval/results/query_bills_due/20260305_091107/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 180

---

### Documentation for `eval/results/query_bills_due/20260305_091107/pass03_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryBillsDueSkill`) that queries upcoming bills due in the next N days and formats the results into a summary. The skill is part of the Mythos system and interacts with a PostgreSQL database to retrieve and process bill data.

#### Architecture
The file is structured around a single class `QueryBillsDueSkill` that inherits from `SkillBase`. The class contains several methods to handle the execution of the skill, including:
- `_detect_days`: Detects the number of days ahead from the message.
- `_query_bills`: Queries bills due in the next N days from the database.
- `_format_results`: Formats the query results into a structured list.
- `_build_summary`: Builds a summary of the formatted results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: The main execution method for the skill, which orchestrates the other methods.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and reused.
- **Factory Method**: The `execute` method acts as a factory method, coordinating the execution of other methods to produce a `SkillResponse`.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary public method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_detect_days`, `_query_bills`, `_format_results`, `_build_summary` are private methods used internally by the `execute` method.

#### Database
- **Tables**: `recurring_bills`, `bill_overrides`.
- **Queries**: The `_query_bills` method performs a query on `recurring_bills` and `bill_overrides` to retrieve bills due in the next N days.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `QueryBillsDueSkill` class.

#### Key Logic
- **_detect_days**: Detects the number of days ahead from the message using regular expressions and keyword matching.
- **_query_bills**: Queries the database for bills due in the next N days, handling month wraparound.
- **_format_results**: Formats the query results into a structured list.
- **_build_summary**: Builds a summary of the formatted results, including the total amount and details of each bill.

#### Integration Points
- **SkillBase**: The `QueryBillsDueSkill` class inherits from `SkillBase`, integrating with the Mythos skill framework.
- **Database Connection**: The `_get_conn` function is used to establish a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request/response model.

### Summary
This file implements a skill in the Mythos system that queries upcoming bills due in the next N days, formats the results, and builds a summary. It integrates with the Mythos skill framework and the PostgreSQL database to retrieve and process bill data. The skill is designed to be reusable and extensible, with clear separation of concerns between different methods and a well-defined interface for execution.
