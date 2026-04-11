# eval/results/search_documents/20260305_062927/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 153

---

### Documentation for `eval/results/search_documents/20260305_062927/pass02_attempt01.py`

#### Purpose
This file contains the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type. It processes user requests to extract search terms, detect document types, perform database queries, and format the results.

#### Architecture
The file consists of a single class `SearchDocumentsSkill` that inherits from `SkillBase`. It contains several methods for processing user requests and interacting with the PostgreSQL database. The class is designed to handle asynchronous execution through the `execute` method.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it ensures a consistent way to get a database connection.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `engine.base`
- **Database**: PostgreSQL (`document_registry` table)

#### Interfaces
- **Public Methods**:
  - `async execute(request: SkillRequest) -> SkillResponse`: Main entry point for executing the skill.
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the user message.
  - `_detect_doc_type(message: str) -> str`: Detects the document type from the user message.
  - `_search_docs(search_terms: str, doc_type: str = None, limit: int = 15) -> list`: Searches the document registry based on the search terms and document type.
  - `_format_results(rows: list) -> list`: Formats the search results into a list of dictionaries.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a summary of the search results.

#### Database
- **Tables**: `document_registry` (PostgreSQL)
- **Operations**: 
  - **Read**: Queries the `document_registry` table based on search terms and document type.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **_extract_search_terms**: Removes trigger phrases and cleans the message to extract meaningful search terms.
- **_detect_doc_type**: Identifies the document type based on keywords in the message.
- **_search_docs**: Queries the `document_registry` table to find documents matching the search terms and document type.
- **_format_results**: Converts raw database rows into a more readable format.
- **_build_summary**: Generates a summary of the search results for display.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **PostgreSQL**: Uses `psycopg2` to interact with the PostgreSQL database.
- **dotenv**: Loads environment variables from `.env` for database connection details.

### Detailed Analysis

#### Class `SearchDocumentsSkill`
- **Attributes**:
  - `name`: 'search_documents'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Search the document registry by title or type'
  - `triggers`: List of trigger phrases for the skill
  - `cache_ttl`: 600 (cache time-to-live in seconds)

- **Methods**:
  - `execute`: Asynchronous method to handle the skill execution.
  - `_extract_search_terms`: Processes the user message to extract meaningful search terms.
  - `_detect_doc_type`: Detects the document type from the user message.
  - `_search_docs`: Queries the `document_registry` table to find documents based on search terms and document type.
  - `_format_results`: Formats the raw database results into a more readable format.
  - `_build_summary`: Generates a summary of the search results for display.

#### Top-level Functions
- **_get_conn**: Returns a PostgreSQL database connection using environment variables for configuration.
- **execute**: Placeholder for the asynchronous execution method (currently not implemented).
- **_extract_search_terms**: Processes the user message to extract meaningful search terms.
- **_detect_doc_type**: Detects the document type from the user message.
- **_search_docs**: Queries the `document_registry` table to find documents based on search terms and document type.
- **_format_results**: Formats the raw database results into a more readable format.
- **_build_summary**: Generates a summary of the search results for display.

### Summary
This file implements the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type. It processes user requests, interacts with a PostgreSQL database, and formats the results for display. The class is designed to be integrated into the Mythos skill system and uses environment variables for configuration.
