# eval/results/search_ideas/20260305_062733/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 221

---

### Documentation for `final.py`

#### Purpose
The `final.py` file implements the `SearchIdeasSkill` class, which is responsible for searching the idea inbox based on keywords, domain, or status. It processes user requests to extract search terms and filters, performs the search, formats the results, and builds a summary.

#### Architecture
- **Class**: `SearchIdeasSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Methods**:
  - `execute`: Main method that orchestrates the search process.
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_detect_filters`: Detects filters (disposition and domain) from the user message.
  - `_search_ideas`: Executes the database query to search for ideas.
  - `_format_results`: Formats the raw database results.
  - `_build_summary`: Builds a summary of the search results.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential external use.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of connection to the database.
- **Factory**: The `execute` method acts as a factory method by orchestrating the creation and processing of search terms, filters, and results.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Exposed Methods**: `execute` method of `SearchIdeasSkill` class.
- **Exposed Functions**: `_get_conn`, `execute`.

#### Database
- **Tables**: `idea_inbox`.
- **Operations**:
  - **Read**: Queries the `idea_inbox` table to retrieve ideas based on search terms and filters.
  - **Count**: Retrieves the count of pending ideas.

#### Configuration
- **Environment Variables**: Database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`) are loaded from `.env` file using `dotenv`.

#### Key Logic
- **Search Terms Extraction**: Removes trigger phrases and strips punctuation to extract meaningful search terms.
- **Filter Detection**: Identifies disposition and domain filters from the user message.
- **Database Query**: Constructs a dynamic SQL query to search the `idea_inbox` table based on search terms and filters.
- **Result Formatting**: Formats the raw database results into a more readable form.
- **Summary Building**: Constructs a summary based on the search results and terms.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **Request Handling**: Processes `SkillRequest` and returns `SkillResponse`.

### Detailed Breakdown

#### Class: `SearchIdeasSkill`
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Handles the entire search process.
  - `_extract_search_terms`: Extracts meaningful search terms from the user message.
  - `_detect_filters`: Detects disposition and domain filters.
  - `_search_ideas`: Executes the database query to search for ideas.
  - `_format_results`: Formats the raw database results.
  - `_build_summary`: Builds a summary of the search results.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for potential external use.

#### Database Operations
- **Query Construction**: Dynamically constructs SQL queries based on search terms and filters.
- **Result Fetching**: Fetches and processes results from the `idea_inbox` table.

#### Configuration
- **Environment Variables**: Database connection details are loaded from the `.env` file.

#### Key Logic
- **Search Terms Extraction**: Removes trigger phrases and strips punctuation.
- **Filter Detection**: Identifies disposition and domain filters.
- **Database Query**: Constructs a dynamic SQL query to search the `idea_inbox` table.
- **Result Formatting**: Formats the raw database results into a more readable form.
- **Summary Building**: Constructs a summary based on the search results and terms.

This documentation provides a comprehensive overview of the `final.py` file, detailing its purpose, architecture, dependencies, interfaces, database operations, configuration, key logic, and integration points within the Mythos system.
