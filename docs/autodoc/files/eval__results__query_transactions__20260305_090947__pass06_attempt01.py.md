# eval/results/query_transactions/20260305_090947/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 218

---

### Documentation for `pass06_attempt01.py`

#### Purpose
This file implements the `QueryTransactionsSkill` class, which is responsible for querying transaction data from a PostgreSQL database based on user-provided search terms and account filters. It processes user requests, extracts relevant information, queries the database, formats the results, and builds a summary.

#### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class contains several methods for different stages of processing a request:
- `execute`: Main method to handle the request, extract search terms, detect account, query the database, format results, and build a summary.
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_detect_account`: Detects account IDs based on abbreviations in the user message.
- `_query`: Executes the database query based on search terms and account filters.
- `_format_results`: Formats the raw query results into a more user-friendly structure.
- `_build_summary`: Builds a summary of the query results.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the creation and processing of search terms, account detection, query execution, result formatting, and summary building.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database connection and querying.
- `string`: For string manipulation.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**:
  - `_extract_search_terms`: Extracts and cleans search terms from a message.
  - `_detect_account`: Detects account IDs based on abbreviations in a message.
  - `_query`: Executes a database query based on search terms and account filters.
  - `_format_results`: Formats raw query results.
  - `_build_summary`: Builds a summary of the query results.

#### Database
- **Tables**:
  - `transactions`: Table containing transaction data.
  - `accounts`: Table containing account data.
- **Queries**:
  - The `_query` method constructs and executes a query on the `transactions` table, joining with the `accounts` table to retrieve account information.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host for the PostgreSQL database.
  - `DB_NAME`: Database name.
  - `DB_USER`: Database user.
  - `DB_PASSWORD`: Database password.
  - `DB_PORT`: Database port.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_terms` method removes common triggers and cleans the message to extract meaningful search terms.
- **Account Detection**: The `_detect_account` method checks for account abbreviations in the message and returns the corresponding account ID.
- **Database Query**: The `_query` method constructs a SQL query based on the search terms and account filters, retrieves transaction data, and returns the results.
- **Result Formatting**: The `_format_results` method formats the raw query results into a structured format.
- **Summary Building**: The `_build_summary` method builds a summary of the query results, including a count of transactions and a total amount.

#### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos system's request/response model.
- **Database Connection**: The `_get_conn` function provides a database connection, integrating with the PostgreSQL database.
- **Environment Variables**: The file uses environment variables for database configuration, integrating with the system's configuration management.

This file is a critical component of the Mythos system, enabling users to query transaction data based on various filters and receive formatted results and summaries.
