# eval/results/query_transactions/20260305_090947/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 210

---

### File: eval/results/query_transactions/20260305_090947/pass05_attempt01.py

#### Purpose
This file implements a skill (`QueryTransactionsSkill`) for the Mythos system that allows users to query transaction data from a PostgreSQL database based on search terms and account filters. It processes user requests, extracts relevant search terms, queries the database, formats the results, and builds a summary.

#### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the query process:
- `execute`: The main method that handles the request, extracts search terms, detects account filters, queries the database, formats results, and builds a summary.
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_detect_account`: Detects account abbreviations in the user message.
- `_query`: Executes the database query based on search terms and account filters.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the query results.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function could be considered a singleton pattern if the connection is reused across multiple queries.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the public method that processes the request and returns a `SkillResponse` object.
- **Internal Methods**: `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary` are internal methods used by `execute`.

#### Database
- **Tables**: `transactions`, `accounts`.
- **Operations**: The `_query` method performs a SELECT operation on the `transactions` table, joining with the `accounts` table to retrieve account details.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method removes common triggers and normalizes the message to extract meaningful search terms.
2. **Account Detection**: The `_detect_account` method checks for account abbreviations in the message and returns the corresponding account ID.
3. **Database Query**: The `_query` method constructs and executes a SQL query based on the search terms and account ID, fetching transaction details.
4. **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form.
5. **Summary Building**: The `_build_summary` method generates a summary of the query results, including a top 3 list of transactions.

#### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos system's request/response model.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos system's data storage.

This file is a critical component of the Mythos system, enabling users to query transaction data efficiently and receive well-formatted results and summaries.
