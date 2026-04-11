# eval/results/spending_analysis/20260305_110130/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 189

---

### File: eval/results/spending_analysis/20260305_110130/pass06_attempt01.py

#### Purpose
This file implements a spending analysis skill for the Mythos system, which analyzes spending patterns and provides a summary of spending across different categories and over time.

#### Architecture
The file contains a single class `SpendingAnalysisSkill` that inherits from `SkillBase`. This class is responsible for executing the spending analysis logic. The class has the following methods:
- `execute`: The main method that orchestrates the spending analysis process.
- `_get_category_totals`: Fetches category-wise spending totals.
- `_get_monthly_comparison`: Compares spending between the current and previous months.
- `_build_summary`: Constructs a summary of the spending analysis.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that wraps the class method for execution.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection is established.
- **Factory**: The `execute` method constructs the response object using the `SkillResponse` class.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**: 
  - `execute`: Accepts a `SkillRequest` object and returns a `SkillResponse` object.
- **Internal Methods**:
  - `_get_category_totals`: Fetches category totals.
  - `_get_monthly_comparison`: Fetches monthly spending comparisons.
  - `_build_summary`: Builds the summary of the analysis.

#### Database
- **Tables**:
  - `accounts`: Used to fetch account IDs.
  - `transactions`: Used to fetch transaction data for spending analysis.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configured in the `.env` file for database connection.

#### Key Logic
1. **Database Connection**: Establishes a connection to the PostgreSQL database using environment variables.
2. **Account IDs**: Fetches account IDs from the request or defaults to all accounts.
3. **Date Range**: Retrieves the start and end dates from the request.
4. **Category Totals**: Fetches spending totals for each category over the specified date range.
5. **Monthly Comparison**: Compares spending between the current and previous months.
6. **Summary Construction**: Builds a summary of the spending analysis, including category-wise totals and monthly comparisons.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill execution framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Database**: Connects to PostgreSQL to fetch transaction and account data.
- **Logging**: Uses Python's `logging` module to log errors.

### Detailed Analysis

#### Class: `SpendingAnalysisSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: Name of the skill.
  - `triggers`: List of phrases that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results.
- **Methods**:
  - `execute`: Main method that orchestrates the spending analysis.
  - `_get_category_totals`: Fetches category-wise spending totals.
  - `_get_monthly_comparison`: Fetches monthly spending comparisons.
  - `_build_summary`: Constructs a summary of the spending analysis.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database.
- **execute**: Wraps the class method for execution.

#### Key Logic Breakdown
1. **Database Connection**:
   ```python
   def _get_conn():
       conn = psycopg2.connect(
           host=os.getenv('POSTGRES_HOST', 'localhost'),
           database=os.getenv('DB_NAME', 'mythos'),
           user=os.getenv('DB_USER', 'mythos_user'),
           password=os.getenv('DB_PASSWORD', 'mythos_password'),
           port=os.getenv('DB_PORT', '5432'),
           cursor_factory=RealDictCursor
       )
       return conn
   ```

2. **Category Totals**:
   ```python
   def _get_category_totals(self, conn, account_ids, start_date, end_date):
       try:
           with conn.cursor() as cursor:
               query = """
               SELECT category_primary, SUM(amount) as total, COUNT(*) as count 
               FROM transactions 
               WHERE transaction_date >= CURRENT_DATE - %s 
               AND amount < 0 
               GROUP BY category_primary 
               ORDER BY total ASC
               """
               cursor.execute(query, (30,))
               categories = cursor.fetchall()
               
               grand_total_query = """
               SELECT SUM(amount) as grand_total 
               FROM transactions 
               WHERE transaction_date >= CURRENT_DATE - %s 
               AND amount < 0
               """
               cursor.execute(grand_total_query, (30,))
               grand_total_result = cursor.fetchone()
               grand_total = grand_total_result['grand_total'] if grand_total_result else 0
               
               return {
                   'categories': categories,
                   'grand_total': grand_total
               }
       finally:
           pass
   ```

3. **Monthly Comparison**:
   ```python
   def _get_monthly_comparison(self, conn, account_ids, start_date, end_date):
       try:
           with conn.cursor() as cursor:
               this_month_query = """
               SELECT SUM(amount) as total 
               FROM transactions 
               WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE) 
               AND amount < 0
               """
               cursor.execute(this_month_query)
               this_month_result = cursor.fetchone()
               this_month = this_month_result['total'] if this_month_result else 0
               
               last_month_query = """
               SELECT SUM(amount) as total 
               FROM transactions 
               WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE - interval '1 month') 
               AND amount < 0
               """
               cursor.execute(last_month_query)
               last_month_result = cursor.fetchone()
               last_month = last_month_result['total'] if last_month_result else 0
               
               if last_month != 0:
                   change_pct = ((this_month - last_month) / abs(last_month)) * 100
               else:
                   change_pct = 0
               
               return {
                   'this_month': this_month,
                   'last_month': last_month,
                   'change_pct': change_pct
               }
       finally:
           pass
   ```

4. **Summary Construction**:
   ```python
   def _build_summary(self, category_totals, monthly_comparison):
       grand_total = abs(category_totals['grand_total'])
       total_formatted = f"${grand_total:,.2f}"
       
       num_categories = len(category_totals['categories'])
       
       summary = f"Spending last 30 days: {total_formatted} across {num_categories} categories.\n"
       
       top_categories = category_totals['categories'][:5]
       summary += "Top 5 categories:\n"
       for cat in top_categories:
           category_name = cat['category_primary']
           amount = abs(cat['total'])
           count = cat['count']
           amount_formatted = f"${amount:,.2f}"
           summary += f"  {category_name}: {amount_formatted} ({count} transactions)\n"
       
       this_month = abs(monthly_comparison['this_month'])
       last_month = abs(monthly_comparison['last_month'])
       change_pct = monthly_comparison['change_pct']
       
       this_month_formatted = f"${this_month:,.2f}"
       last_month_formatted = f"${last_month:,.2f}"
       
       if change_pct > 0:
           direction = "UP"
       elif change_pct < 0:
           direction = "DOWN"
       else:
           direction = "SAME"
           
       change_pct_abs = abs(change_pct)
       summary += f"This month: {this_month_formatted} vs last month: {last_month_formatted} ({direction} {change_pct_abs:.1f}%)\n"
       
       if not summary.strip():
           summary = "No spending data available."
       
       return summary
   ```

This file is a critical component of the Mythos system, providing detailed spending analysis and summaries based on transaction data stored in PostgreSQL.
