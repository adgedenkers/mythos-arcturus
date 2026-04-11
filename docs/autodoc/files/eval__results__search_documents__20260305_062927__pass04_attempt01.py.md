# eval/results/search_documents/20260305_062927/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### File: eval/results/search_documents/20260305_062927/pass04_attempt01.py

#### Purpose
This file contains the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type. It processes user input to extract search terms, detect document types, perform database queries, and format the results.

#### Architecture
The file is structured around a single class, `SearchDocumentsSkill`, which inherits from `SkillBase`. The class contains several methods that handle different aspects of the search process:

- `_extract_search_terms`: Extracts search terms from the user message by removing trigger phrases.
- `_detect_doc_type`: Detects the document type based on keywords in the user message.
- `_search_docs`: Queries the PostgreSQL database to find documents matching the search terms and type.
- `_format_results`: Formats the raw query results into a more readable structure.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions `_get_conn` and `execute` that handle database connection and asynchronous execution, respectively.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a consistent connection configuration by using environment variables.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Private Methods**: `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, `_build_summary`

#### Database
- **Tables**: `document_registry` (PostgreSQL)
- **Operations**: Reads from `document_registry` to retrieve documents based on search terms and type.

#### Configuration
- **Environment Variables**: Configured via `.env` file located at `/opt/mythos/.env`
- **Database Connection**: Uses environment variables to configure the PostgreSQL connection.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes predefined trigger phrases from the user message to isolate the actual search terms.
2. **Detect Document Type**: The `_detect_doc_type` method identifies the document type based on keywords in the user message.
3. **Search Documents**: The `_search_docs` method constructs and executes a PostgreSQL query to find documents matching the search terms and type.
4. **Format Results**: The `_format_results` method transforms the raw query results into a structured format.
5. **Build Summary**: The `_build_summary` method generates a summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill execution framework.
- **Database**: Connects to the PostgreSQL database to query the `document_registry` table.
- **Environment Configuration**: Uses environment variables for database connection details, loaded via `dotenv`.

### Summary
This file implements the `SearchDocumentsSkill` class, which provides functionality to search the document registry by title or type. It processes user input to extract search terms and document types, queries the PostgreSQL database, and formats the results for presentation. The class integrates with the Mythos system's skill execution framework and uses environment variables for configuration.
