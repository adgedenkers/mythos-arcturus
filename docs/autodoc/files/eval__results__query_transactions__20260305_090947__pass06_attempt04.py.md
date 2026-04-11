# eval/results/query_transactions/20260305_090947/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 220

---

### Purpose
The `pass06_attempt04.py` file implements the `QueryTransactionsSkill` class, which is responsible for querying transaction data from a PostgreSQL database based on user input. It processes user messages to extract search terms and account identifiers, queries the database, formats the results, and builds a summary.

### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. It also includes several helper functions for extracting search terms, detecting accounts, querying the database, formatting results, and building summaries. The class and functions are designed to handle the entire process of transaction querying and result presentation.

### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is created and reused.
- **Factory**: The `_query` method acts as a factory for generating SQL queries based on the input parameters.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### Interfaces
- **Public Methods**: `execute` (async)
- **Helper Methods**: `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary`

### Database
- **Tables**: `transactions`, `accounts`
- **Operations**: Reads from `transactions` and `accounts` tables to fetch transaction details and account information.

### Configuration
- **Environment Variables**: Configured using `dotenv` for database connection details.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`

### Key Logic
1. **Message Processing**: Extracts search terms and account identifiers from the user message.
2. **Database Querying**: Constructs and executes SQL queries to fetch transaction data based on search terms and account filters.
3. **Result Formatting**: Formats the fetched data into a structured format.
4. **Summary Building**: Generates a summary of the results, including a total amount and top transactions.

### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request handling and response generation.
- **Database Connection**: Uses `_get_conn` to manage database connections, ensuring seamless integration with PostgreSQL.

### Detailed Breakdown

#### Class: `QueryTransactionsSkill`
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Metadata for the skill.
- **Methods**:
  - `execute`: Main method that processes the user request, extracts search terms, detects accounts, queries the database, formats results, and builds a summary.
  - `_extract_search_terms`: Cleans and processes the user message to extract meaningful search terms.
  - `_detect_account`: Identifies account abbreviations from the user message.
  - `_query`: Constructs and executes the SQL query to fetch transaction data.
  - `_format_results`: Formats the raw database results into a more readable structure.
  - `_build_summary`: Generates a summary of the query results.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: (redundant with class method, likely a typo or placeholder)

#### Database Operations
- **Tables**: `transactions`, `accounts`
- **Operations**: 
  - **Join**: Joins `transactions` and `accounts` tables to fetch transaction details along with account information.
  - **Filtering**: Filters transactions based on search terms and account IDs.
  - **Ordering**: Orders results by transaction date in descending order.

#### Configuration and Environment
- **Database Connection**: Uses environment variables for database configuration.
- **Logging**: Uses `logging` for error handling and logging.

This file is a crucial component of the Mythos system, enabling users to query transaction data based on various filters and receive formatted results and summaries.
