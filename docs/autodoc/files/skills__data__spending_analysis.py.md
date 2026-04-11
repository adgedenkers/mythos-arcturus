# skills/data/spending_analysis.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 116

---

### File: `skills/data/spending_analysis.py`

#### Purpose
This file defines the `SpendingAnalysisSkill` class, which provides spending analysis by category and month-over-month comparison. It connects to a PostgreSQL database to fetch transaction data and constructs a summary of spending trends.

#### Architecture
- **Class**: `SpendingAnalysisSkill` inherits from `SkillBase` and implements methods to execute the skill, fetch category totals, get monthly comparisons, and build a summary.
- **Functions**: `_get_conn` is a utility function to establish a database connection. The `execute` method is an asynchronous function that orchestrates the execution of the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of connection to the database.
- **Factory**: The `execute` method acts as a factory to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**: `_get_category_totals`, `_get_monthly_comparison`, and `_build_summary` are internal methods used to fetch data and construct the summary.

#### Database
- **Tables**: The `transactions` table is queried to fetch spending data.
- **Queries**: 
  - Fetches category totals and transaction counts for the last `days` days.
  - Compares spending totals for the current and previous months.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.
- **Logging**: Uses the `logging` module to log errors.

#### Key Logic
- **Category Totals**: Fetches the total spending and transaction count for each category over a specified number of days.
- **Monthly Comparison**: Compares the total spending of the current month with the previous month and calculates the percentage change.
- **Summary Construction**: Builds a human-readable summary of the spending analysis, including category-wise spending and month-over-month comparison.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **Database**: Connects to the PostgreSQL database to fetch transaction data.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output of the skill execution.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `os`, `psycopg2`, `dotenv`.

#### `SpendingAnalysisSkill`
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Asynchronous method that orchestrates the execution of the skill by calling `_get_category_totals`, `_get_monthly_comparison`, and `_build_summary`.
  - `_get_category_totals`: Fetches category-wise spending totals for the last `days` days.
  - `_get_monthly_comparison`: Fetches and compares spending totals for the current and previous months.
  - `_build_summary`: Constructs a human-readable summary of the spending analysis.

#### `_get_category_totals`
- **Purpose**: Fetches category-wise spending totals and transaction counts for the last `days` days.
- **Database Queries**: 
  - Fetches category totals and transaction counts.
  - Fetches the grand total spending for the specified period.

#### `_get_monthly_comparison`
- **Purpose**: Fetches and compares spending totals for the current and previous months.
- **Database Queries**: 
  - Fetches the total spending for the current month.
  - Fetches the total spending for the previous month.
  - Calculates the percentage change between the two months.

#### `_build_summary`
- **Purpose**: Constructs a human-readable summary of the spending analysis.
- **Logic**: 
  - Lists the top categories with their spending amounts.
  - Compares the current month's spending with the previous month's spending and calculates the percentage change.

This file is a critical component of the Mythos system, providing detailed spending analysis and integration with the PostgreSQL database for data retrieval.
