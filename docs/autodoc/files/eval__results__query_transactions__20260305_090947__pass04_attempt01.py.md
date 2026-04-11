# eval/results/query_transactions/20260305_090947/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 188

---

### File: `eval/results/query_transactions/20260305_090947/pass04_attempt01.py`

#### Purpose
This file contains the implementation of the `QueryTransactionsSkill` class, which is responsible for querying transaction data from a PostgreSQL database based on user-provided search terms and account filters. It processes user requests, extracts relevant information, queries the database, formats the results, and builds a summary.

#### Architecture
The file consists of a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class contains several methods for handling different stages of the query process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_account`: Detects account abbreviations from the user message.
- `_query`: Executes the database query to fetch transaction data.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the query results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, which orchestrates the query process.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function could be considered a singleton as it ensures a single connection is established per invocation.
- **Factory Method Pattern**: The `execute` method acts as a factory method, coordinating the creation and processing of the query results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Private Methods**: `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary`

#### Database
- **Tables**: `transactions`, `accounts`
- **Operations**: Reads from `transactions` and `accounts` tables using `psycopg2` for database connections and queries.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
1. **Extract Search Terms**: Removes predefined triggers and normalizes the user message to extract meaningful search terms.
2. **Detect Account**: Identifies account abbreviations from the user message.
3. **Query Execution**: Constructs and executes a SQL query to fetch transactions based on the extracted search terms and account filters.
4. **Result Formatting**: Converts raw query results into a structured format.
5. **Summary Building**: Generates a summary of the query results, including a total amount and top 3 transactions.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **Database Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **Environment Configuration**: Loads database configuration from environment variables using `dotenv`.

### Detailed Method Descriptions

- **`_get_conn`**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **`execute`**: Main entry point for the skill. It processes the user request, extracts search terms and account filters, queries the database, formats the results, and builds a summary.
- **`_extract_search_terms`**: Processes the user message to extract meaningful search terms by removing predefined triggers and normalizing the text.
- **`_detect_account`**: Identifies account abbreviations from the user message and returns the corresponding account ID.
- **`_query`**: Constructs and executes a SQL query to fetch transaction data based on the provided search terms and account filters.
- **`_format_results`**: Converts the raw query results into a structured format suitable for presentation.
- **`_build_summary`**: Generates a summary of the query results, including a total amount and top 3 transactions.

This file is a critical component of the Mythos system, enabling users to query transaction data in a flexible and user-friendly manner.
