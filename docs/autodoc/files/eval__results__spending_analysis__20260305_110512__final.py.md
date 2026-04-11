# eval/results/spending_analysis/20260305_110512/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 106

---

### Documentation for `eval/results/spending_analysis/20260305_110512/final.py`

#### Purpose
This file contains the `SpendingAnalysisSkill` class, which is responsible for analyzing spending data for a given account over a specified period. It retrieves category-wise spending totals and monthly spending comparisons, and builds a summary of the spending trends.

#### Architecture
- **Class**: `SpendingAnalysisSkill` extends `SkillBase` and contains methods for executing the skill, fetching database connections, getting category totals, monthly comparisons, and building summaries.
- **Methods**:
  - `execute`: Main method to execute the skill, fetching category totals and monthly comparisons, and building a summary.
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `_get_category_totals`: Retrieves category-wise spending totals for the last `days` days.
  - `_get_monthly_comparison`: Retrieves spending comparisons between the current month and the previous `months` months.
  - `_build_summary`: Constructs a summary of the spending data.

#### Patterns
- **Singleton**: The database connection is managed within `_get_conn` to ensure a single connection per method call.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the analysis results.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `psycopg2`, `dotenv`, `engine.base` (for `SkillBase`, `SkillRequest`, `SkillResponse`).

#### Interfaces
- **Exposed Methods**: `execute` is the primary method that other parts of the system can call to execute the spending analysis.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object containing the analysis results and a summary.

#### Database
- **Tables**: The `transactions` table in the PostgreSQL database is queried to retrieve spending data.
- **Queries**:
  - `_get_category_totals`: Queries `transactions` for category-wise spending totals.
  - `_get_monthly_comparison`: Queries `transactions` for monthly spending comparisons.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` are used to configure the PostgreSQL connection.
- **Dotenv**: The `dotenv` library is used to load environment variables from a `.env` file.

#### Key Logic
- **Category Totals**: Aggregates spending data by category for the last `days` days.
- **Monthly Comparison**: Compares spending between the current month and the previous `months` months.
- **Summary Construction**: Builds a summary string that includes category-wise spending and monthly trends.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` objects to communicate with the Mythos skill execution system.
- **Database**: Connects to the PostgreSQL database to fetch transaction data for analysis.

### Detailed Breakdown

#### Class: `SpendingAnalysisSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: Name of the skill (`'spending_analysis'`).
  - `triggers`: List of trigger phrases that can activate this skill.
  - `cache_ttl`: Time-to-live for caching results (600 seconds).

#### Methods:
- **`execute`**:
  - **Purpose**: Executes the spending analysis and returns a `SkillResponse`.
  - **Parameters**: `request` (SkillRequest object).
  - **Logic**: Fetches category totals and monthly comparisons, builds a summary, and returns a `SkillResponse` object.
  - **Error Handling**: Logs exceptions and returns a default `SkillResponse` on failure.

- **`_get_conn`**:
  - **Purpose**: Establishes a connection to the PostgreSQL database.
  - **Logic**: Loads environment variables, constructs a connection string, and returns a database connection.

- **`_get_category_totals`**:
  - **Purpose**: Retrieves category-wise spending totals for the last `days` days.
  - **Parameters**: `account_id`, `days`.
  - **Logic**: Executes SQL queries to fetch category totals and the grand total for the specified period.

- **`_get_monthly_comparison`**:
  - **Purpose**: Retrieves spending comparisons between the current month and the previous `months` months.
  - **Parameters**: `account_id`, `months`.
  - **Logic**: Executes SQL queries to fetch spending totals for the current and previous months, calculates the percentage change.

- **`_build_summary`**:
  - **Purpose**: Constructs a summary string based on category totals and monthly comparisons.
  - **Parameters**: `category_totals`, `monthly_comparison`.
  - **Logic**: Builds a summary string that includes category-wise spending and monthly trends.

### Example Usage
```python
from eval.results.spending_analysis.20260305_110512.final import SpendingAnalysisSkill

skill = SpendingAnalysisSkill()
request = SkillRequest(account_id=12345)
response = skill.execute(request)
print(response.summary)
```

This example demonstrates how to instantiate the `SpendingAnalysisSkill` and execute it with a sample `SkillRequest`, printing the summary of the spending analysis.
