# eval/results/spending_analysis/20260305_110130/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 185

---

### File: eval/results/spending_analysis/20260305_110130/final.py

#### Purpose
This file contains the implementation of a spending analysis skill for the Mythos system. It provides functionality to analyze spending patterns, categorize expenses, and compare monthly spending trends.

#### Architecture
The file is structured around a single class `SpendingAnalysisSkill` which inherits from `SkillBase`. The class contains methods for executing the skill, fetching category totals, getting monthly comparisons, and building a summary. Additionally, there are top-level functions for establishing a database connection and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a consistent connection to the PostgreSQL database.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the execution of various sub-methods to produce a final response.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `psycopg2`, `dotenv`, `engine.base`
- **Database**: PostgreSQL (`transactions`, `accounts` tables)
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Private Methods**: `_get_category_totals`, `_get_monthly_comparison`, `_build_summary`

#### Database
- **Tables**: `transactions`, `accounts`
- **Operations**:
  - `transactions`: Queries for category totals and monthly spending trends.
  - `accounts`: Fetches account IDs if not provided in the request.

#### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`)
- **Dotenv**: Loads environment variables using `dotenv.load_dotenv()`

#### Key Logic
- **Category Totals**: Aggregates spending by category over a specified period.
- **Monthly Comparison**: Compares spending between the current and previous month.
- **Summary Building**: Constructs a human-readable summary of spending trends and category breakdowns.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **SkillRequest/SkillResponse**: Utilizes `SkillRequest` and `SkillResponse` classes for request handling and response generation.
- **Database Connection**: Uses `psycopg2` to connect to and query the PostgreSQL database.

### Detailed Documentation

#### Classes
- **SpendingAnalysisSkill**
  - **Inherits**: `SkillBase`
  - **Attributes**:
    - `name`: 'spending_analysis'
    - `triggers`: List of trigger phrases for the skill
    - `cache_ttl`: Time to live for caching results (600 seconds)
  - **Methods**:
    - `execute`: Main execution method that orchestrates the analysis and returns a `SkillResponse`.
    - `_get_category_totals`: Fetches category totals from the `transactions` table.
    - `_get_monthly_comparison`: Compares monthly spending trends.
    - `_build_summary`: Constructs a summary of the spending analysis.

#### Top-Level Functions
- **_get_conn**
  - Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**
  - Asynchronous function that handles the execution of the spending analysis skill.
- **_get_category_totals**
  - Fetches category totals from the `transactions` table.
- **_get_monthly_comparison**
  - Compares spending between the current and previous month.
- **_build_summary**
  - Constructs a human-readable summary of the spending analysis.

#### Key Methods
- **execute**
  - **Parameters**: `request` (SkillRequest)
  - **Returns**: `SkillResponse`
  - **Logic**:
    1. Establishes a database connection.
    2. Retrieves account IDs from the request or defaults to all accounts.
    3. Fetches category totals and monthly comparisons.
    4. Builds a summary of the analysis.
    5. Returns a `SkillResponse` with the analysis data and summary.
- **_get_category_totals**
  - **Parameters**: `conn`, `account_ids`, `start_date`, `end_date`
  - **Returns**: Dictionary containing category totals and grand total.
  - **Logic**:
    1. Queries the `transactions` table for category totals.
    2. Calculates the grand total.
    3. Returns the results.
- **_get_monthly_comparison**
  - **Parameters**: `conn`, `account_ids`, `start_date`, `end_date`
  - **Returns**: Dictionary containing this month's total, last month's total, and change percentage.
  - **Logic**:
    1. Queries the `transactions` table for this month's and last month's totals.
    2. Calculates the change percentage.
    3. Returns the results.
- **_build_summary**
  - **Parameters**: `category_totals`, `monthly_comparison`
  - **Returns**: String summary of the spending analysis.
  - **Logic**:
    1. Formats the grand total and category totals.
    2. Constructs a summary string with spending trends and category breakdowns.
    3. Returns the summary.

This file is a critical component of the Mythos system, providing detailed spending analysis and integration with the skill execution framework.
