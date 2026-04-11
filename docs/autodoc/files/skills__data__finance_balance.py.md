# skills/data/finance_balance.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 166

---

### Documentation for `skills/data/finance_balance.py`

#### Purpose
The `finance_balance.py` file implements a skill (`FinanceBalanceSkill`) that retrieves current account balances and upcoming bills from a PostgreSQL database. This skill is part of the Mythos system and is designed to provide financial data to users through a skill interface.

#### Architecture
The file contains a single class `FinanceBalanceSkill` that inherits from `SkillBase`. The class has a single method `execute` which is asynchronous and handles the retrieval of financial data. The file also includes a top-level function `_get_conn` for establishing a database connection.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a form of singleton pattern as it provides a single connection object.
- **Factory Method Pattern**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object based on the retrieved data.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `sys`, `datetime`, `typing`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async method that takes a `SkillRequest` and returns a `SkillResponse`).
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Database
- **Tables**: `accounts`, `recurring_bills`, `bill_overrides`.
- **Queries**:
  - Retrieves active accounts with their balances.
  - Retrieves upcoming bills due in the next 5 days.

#### Configuration
- **Environment Variables**: Configured using `dotenv` from `/opt/mythos/.env`.
- **Logging**: Uses `logging` module with a logger named `__name__`.

#### Key Logic
- **Account Balances Retrieval**: Fetches active accounts from the `accounts` table and organizes them by account type.
- **Upcoming Bills Retrieval**: Fetches upcoming bills from the `recurring_bills` and `bill_overrides` tables for the next 5 days.
- **Summary Construction**: Builds a summary string and structured data for the response.
- **Error Handling**: Catches exceptions and logs errors, returning a `SkillResponse` with an error message if an exception occurs.

#### Integration Points
- **Skill Interface**: Integrates with the Mythos skill system by inheriting from `SkillBase` and implementing the `execute` method.
- **Database Access**: Connects to the PostgreSQL database using `psycopg2` to fetch financial data.
- **Environment Configuration**: Uses environment variables loaded via `dotenv` for database connection details.

### Detailed Breakdown

#### Classes
- **FinanceBalanceSkill**
  - **Inheritance**: `SkillBase`
  - **Attributes**:
    - `name`: "finance_balance"
    - `version`: "1.0"
    - `category`: "data"
    - `description`: "Current account balances and upcoming bills"
    - `triggers`: List of trigger keywords
    - `cache_ttl`: 300 seconds (5 minutes)
  - **Methods**:
    - `execute`: Asynchronous method that retrieves account balances and upcoming bills, constructs a summary, and returns a `SkillResponse`.

#### Top-level Functions
- **_get_conn**
  - Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**
  - Asynchronous function that takes a `SkillRequest` and returns a `SkillResponse` with financial data.

#### Database Operations
- **Account Balances Query**:
  - Retrieves active accounts with their balances from the `accounts` table.
- **Upcoming Bills Query**:
  - Retrieves upcoming bills due in the next 5 days from the `recurring_bills` and `bill_overrides` tables.

#### Summary Construction
- **Parts**:
  - Checking accounts balance summary.
  - Credit card balances summary.
  - Upcoming bills summary.
- **Data Structure**:
  - Organizes account and bill data into a structured dictionary for the response.

#### Error Handling
- **Exception Handling**:
  - Logs errors and returns a `SkillResponse` with an error message if an exception occurs during execution.

This documentation provides a comprehensive overview of the `finance_balance.py` file, detailing its purpose, architecture, dependencies, and key logic within the Mythos system.
