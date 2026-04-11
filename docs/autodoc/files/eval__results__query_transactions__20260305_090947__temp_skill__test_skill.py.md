# eval/results/query_transactions/20260305_090947/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 210

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file implements a `QueryTransactionsSkill` class that handles user queries to search for transaction records in a PostgreSQL database. It extracts search terms, detects account filters, queries the database, formats results, and builds a summary.

#### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. It includes methods for executing the skill, extracting search terms, detecting account filters, querying the database, formatting results, and building a summary. The class also includes a top-level function `_get_conn` for database connection and an asynchronous `execute` method.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is created.
- **Factory Method**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute`, `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary`.
- **Exposed Interfaces**: The `execute` method is the main entry point for executing the skill and returning a `SkillResponse`.

#### Database
- **Tables**: `transactions`, `accounts`.
- **Operations**: The `_query` method performs SELECT operations on `transactions` and `accounts` tables to retrieve transaction data based on search terms and account filters.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Key Logic
- **Search Term Extraction**: `_extract_search_terms` removes predefined triggers and normalizes the message to extract meaningful search terms.
- **Account Detection**: `_detect_account` identifies account abbreviations in the message to filter transactions by account.
- **Database Query**: `_query` constructs and executes a SQL query to retrieve transaction data based on search terms and account filters.
- **Result Formatting**: `_format_results` formats the retrieved transaction data into a structured list.
- **Summary Building**: `_build_summary` generates a summary of the query results, including the total amount and top 3 transactions.

#### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch transaction data.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, which is used to communicate results back to the Mythos system.

### Detailed Breakdown

#### Class: `QueryTransactionsSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Asynchronous method to execute the skill, extract search terms, detect account, query the database, format results, and build a summary.
  - `_extract_search_terms`: Extracts meaningful search terms from the message by removing predefined triggers.
  - `_detect_account`: Detects account abbreviations in the message to filter transactions by account.
  - `_query`: Constructs and executes a SQL query to retrieve transaction data based on search terms and account filters.
  - `_format_results`: Formats the retrieved transaction data into a structured list.
  - `_build_summary`: Generates a summary of the query results, including the total amount and top 3 transactions.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

### Example Usage
```python
# Example usage of QueryTransactionsSkill
skill = QueryTransactionsSkill()
request = SkillRequest(message="Find recent purchases from USAA")
response = skill.execute(request)
print(response.message)
```

This example demonstrates how the `QueryTransactionsSkill` class can be instantiated and used to process a user query, returning a structured response with transaction details and a summary.
