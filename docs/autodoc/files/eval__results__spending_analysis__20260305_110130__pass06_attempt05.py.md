# eval/results/spending_analysis/20260305_110130/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 205

---

### File: eval/results/spending_analysis/20260305_110130/pass06_attempt05.py

#### Purpose
This file contains the implementation of the `SpendingAnalysisSkill` class, which is responsible for analyzing spending patterns and generating a summary based on transaction data from PostgreSQL. It provides functionality to retrieve category totals and monthly spending comparisons.

#### Architecture
- **Classes**: 
  - `SpendingAnalysisSkill` inherits from `SkillBase` and includes methods for executing the skill, retrieving category totals, monthly comparisons, and building a summary.
- **Functions**: 
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Main entry point for the skill, orchestrates the retrieval of data and summary generation.
  - `_get_category_totals`: Retrieves category totals for specified accounts and date range.
  - `_get_monthly_comparison`: Retrieves monthly spending comparisons.
  - `_build_summary`: Constructs a summary based on the retrieved data.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection is established per request.
- **Factory**: The `execute` method acts as a factory method, orchestrating the creation and combination of data from different sources.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `datetime`: For date and time operations.
  - `engine.base`: For base classes `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Accepts a `SkillRequest` object and returns a `SkillResponse` object.
- **Internal Methods**: 
  - `_get_category_totals`: Retrieves category totals.
  - `_get_monthly_comparison`: Retrieves monthly spending comparisons.
  - `_build_summary`: Constructs a summary based on the retrieved data.

#### Database
- **Tables**: 
  - `accounts`: Used to retrieve account IDs.
  - `transactions`: Used to retrieve transaction data for category totals and monthly comparisons.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL connection.

#### Key Logic
- **Category Totals Calculation**: 
  - Retrieves category totals and grand total for the last 30 days.
- **Monthly Comparison Calculation**: 
  - Compares spending for the current month versus the previous month.
- **Summary Construction**: 
  - Constructs a summary including grand total, top 5 categories, and monthly spending comparison.

#### Integration Points
- **Mythos Subsystems**: 
  - **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
  - **Request/Response Handling**: Uses `SkillRequest` and `SkillResponse` to handle input and output.
  - **Database Integration**: Connects to PostgreSQL to retrieve transaction and account data.

### Detailed Documentation

#### Classes
- **SpendingAnalysisSkill**
  - **Inherits**: `SkillBase`
  - **Attributes**: 
    - `name`: Name of the skill (`'spending_analysis'`).
    - `triggers`: List of phrases that trigger this skill.
    - `cache_ttl`: Time-to-live for caching results (`600` seconds).
  - **Methods**: 
    - `execute`: Main execution method that retrieves account IDs, date range, category totals, monthly comparisons, and builds a summary.
    - `_get_category_totals`: Retrieves category totals and grand total for specified accounts and date range.
    - `_get_monthly_comparison`: Retrieves monthly spending comparisons.
    - `_build_summary`: Constructs a summary based on the retrieved data.

#### Functions
- **_get_conn**
  - **Purpose**: Establishes a connection to the PostgreSQL database.
  - **Returns**: A PostgreSQL connection object.
- **execute**
  - **Purpose**: Main entry point for the skill, orchestrates the retrieval of data and summary generation.
  - **Parameters**: `request` (SkillRequest object).
  - **Returns**: `SkillResponse` object containing the analysis results.
- **_get_category_totals**
  - **Purpose**: Retrieves category totals and grand total for specified accounts and date range.
  - **Parameters**: `conn` (database connection), `account_ids` (list of account IDs), `start_date` (start date), `end_date` (end date).
  - **Returns**: Dictionary containing category totals and grand total.
- **_get_monthly_comparison**
  - **Purpose**: Retrieves monthly spending comparisons.
  - **Parameters**: `conn` (database connection), `account_ids` (list of account IDs), `start_date` (start date), `end_date` (end date).
  - **Returns**: Dictionary containing this month's total, last month's total, and change percentage.
- **_build_summary**
  - **Purpose**: Constructs a summary based on the retrieved data.
  - **Parameters**: `category_totals` (dictionary of category totals), `monthly_comparison` (dictionary of monthly comparison data).
  - **Returns**: Summary string.

### Example Usage
```python
# Example request object
request = SkillRequest(account_ids=[1, 2], start_date='2023-01-01', end_date='2023-01-31')

# Instantiate the skill
skill = SpendingAnalysisSkill()

# Execute the skill
response = await skill.execute(request)

# Print the response
print(response.data)
print(response.summary)
```

This file is a critical component of the Mythos system, providing detailed spending analysis and summaries based on transaction data.
