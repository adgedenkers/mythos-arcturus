# eval/results/query_transactions/20260305_090947/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 208

---

### Purpose
The `final.py` file implements the `QueryTransactionsSkill` class, which is responsible for querying transaction data from a PostgreSQL database based on user-provided search terms and account filters. It processes user requests, extracts relevant information, queries the database, formats the results, and builds a summary.

### Architecture
The file contains a single class `QueryTransactionsSkill` inheriting from `SkillBase`. This class includes several methods for handling different stages of the transaction query process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_account`: Detects the account based on abbreviations in the user message.
- `_query`: Executes the database query to fetch transactions.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Constructs a summary of the query results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for executing the skill, which orchestrates the other methods.

### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern, as it ensures a single database connection is used throughout the execution.
- **Factory Method**: The `_query` method can be seen as a factory method that constructs and executes the query based on input parameters.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary` are used internally by the `execute` method.

### Database
- **Tables**: `transactions`, `accounts`.
- **Operations**: Reads from `transactions` and `accounts` tables to fetch transaction details and account information.

### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.
- **Configuration Files**: No explicit configuration files are used, but environment variables are loaded from a `.env` file.

### Key Logic
- **Search Term Extraction**: The `_extract_search_terms` method removes common triggers and normalizes the remaining words.
- **Account Detection**: The `_detect_account` method checks for account abbreviations in the user message.
- **Database Query**: The `_query` method constructs and executes a SQL query based on the search terms and account filter.
- **Result Formatting**: The `_format_results` method converts raw query results into a structured format.
- **Summary Building**: The `_build_summary` method creates a summary of the query results, including a total amount and top 3 transactions.

### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, integrating with the Mythos data storage layer.

This file is a critical component of the Mythos system, enabling users to query and retrieve transaction data based on various filters and search terms.
