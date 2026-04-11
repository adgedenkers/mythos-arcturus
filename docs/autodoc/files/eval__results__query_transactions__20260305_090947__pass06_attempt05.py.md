# eval/results/query_transactions/20260305_090947/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 220

---

### File: eval/results/query_transactions/20260305_090947/pass06_attempt05.py

#### Purpose
This file implements the `QueryTransactionsSkill` class, which is responsible for querying transaction data from a PostgreSQL database based on user input and returning formatted results and summaries.

#### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the transaction query process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_account`: Detects account abbreviations from the user message.
- `_query`: Executes the database query to fetch transactions.
- `_format_results`: Formats the raw query results into a more readable format.
- `_build_summary`: Builds a summary of the query results.
- `execute`: The main method that orchestrates the entire process from extracting search terms to building the summary.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object to the PostgreSQL database.
- **Factory**: The `SkillResponse` object is created and returned by the `execute` method, acting as a factory for the response.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `transactions`, `accounts`.
- **Operations**: The `_query` method performs SELECT operations on the `transactions` and `accounts` tables to fetch transaction data based on search terms and account IDs.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `QueryTransactionsSkill` class.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_terms` method removes common triggers and normalizes the user message to extract meaningful search terms.
- **Account Detection**: The `_detect_account` method checks for account abbreviations in the user message to filter transactions by account.
- **Database Query**: The `_query` method constructs a dynamic SQL query based on the search terms and account ID, fetching transaction data from the `transactions` table.
- **Result Formatting and Summary**: The `_format_results` and `_build_summary` methods format the query results and generate a summary, respectively.

#### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, integrating with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method interacts with the `SkillRequest` and `SkillResponse` objects, allowing seamless integration with other parts of the Mythos system.
- **PostgreSQL Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, enabling the `_query` method to fetch transaction data.

This file is a critical component of the Mythos system, enabling users to query transaction data based on various filters and receive formatted results and summaries.
