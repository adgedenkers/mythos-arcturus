# eval/challenges/query_transactions/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 35

---

### Documentation for `eval/challenges/query_transactions/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a Python skill named `QueryTransactionsSkill`. The skill is designed to query transaction data from a PostgreSQL database based on various search criteria such as description, merchant, amount, date range, or account.

#### Architecture
The file contains a structured plan for building the `QueryTransactionsSkill` class, which is part of a larger skill-based system. The plan includes multiple passes, each with specific instructions for implementing different methods and functionalities. The class structure and method signatures are defined in the `scaffold` section.

#### Patterns
- **Factory Method**: The `_get_conn` method acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` method can be considered a singleton pattern as it returns the same database connection object.
- **Observer**: The skill observes user input and triggers specific actions based on keywords.

#### Dependencies
- **Imports**: The skill relies on `os`, `logging`, `psycopg2`, `RealDictCursor`, and `dotenv` for database connection and configuration.
- **Environment Variables**: The skill uses `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT` to configure the database connection.

#### Interfaces
- **Public Methods**: The class exposes the `execute` method, which processes user requests and returns a `SkillResponse` object.
- **Private Methods**: The class has private methods `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, and `_build_summary` to handle specific tasks.

#### Database
- **Tables**: The skill interacts with the `transactions` and `accounts` tables.
  - `transactions`: Columns include `id`, `account_id`, `transaction_date`, `description`, `merchant_name`, `amount`, `category_primary`, `category_secondary`, and `is_pending`.
  - `accounts`: Columns include `id`, `abbreviation`, `account_name`, and `account_type`.

#### Configuration
- **Environment Variables**: The skill uses environment variables to configure the PostgreSQL database connection.
- **Configuration File**: The skill uses `dotenv` to load environment variables from a `.env` file.

#### Key Logic
- **Search Logic**: The skill extracts search terms from user input and queries the `transactions` table using `ILIKE` for partial matches on `description` and `merchant_name`.
- **Account Detection**: The skill detects account abbreviations in the user input to filter transactions by account.
- **Result Formatting**: The skill formats query results into a list of dictionaries and builds a summary of the total amount spent.

#### Integration Points
- **Engine Base**: The skill inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` from the `engine.base` module.
- **Database Connection**: The skill integrates with the PostgreSQL database using the `_get_conn` method.
- **Skill Execution**: The skill is triggered by specific keywords and phrases, and it returns results in a structured format that can be used by other parts of the Mythos system.

### Detailed Breakdown of Build Plan Passes

1. **Pass 1**: Write the file skeleton, including the class definition with all attributes and methods with `pass`.
2. **Pass 2**: Implement `_extract_search_terms` and `_detect_account` methods to process user input.
3. **Pass 3**: Implement `_query` method to build and execute the SQL query.
4. **Pass 4**: Implement `_format_results` and `_build_summary` methods to format the query results and build a summary.
5. **Pass 5**: Implement the `execute` method to orchestrate the entire process and return a `SkillResponse`.
6. **Pass 6**: Review and ensure production readiness, including proper connection handling and ASCII-only comments.

### Test Cases
- **Test Case 1**: Search for transactions with the term "stewart".
- **Test Case 2**: Search for transactions related to "youtube".
- **Test Case 3**: Show recent transactions.

These test cases ensure that the skill functions correctly under various user input scenarios.
