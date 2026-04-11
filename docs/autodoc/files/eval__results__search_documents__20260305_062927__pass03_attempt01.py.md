# eval/results/search_documents/20260305_062927/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 152

---

### Documentation for `pass03_attempt01.py`

#### Purpose
This file contains the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type. It processes user requests to extract search terms, detect document types, and query the PostgreSQL database to retrieve relevant documents.

#### Architecture
The file is structured around the `SearchDocumentsSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the document search process:
- `_extract_search_terms`: Extracts relevant search terms from the user message.
- `_detect_doc_type`: Detects the document type based on keywords in the user message.
- `_search_docs`: Queries the PostgreSQL database to retrieve documents based on search terms and document type.
- `_format_results`: Formats the query results into a more readable structure.
- `_build_summary`: Builds a summary of the search results.

Additionally, the file contains a top-level function `_get_conn` to establish a connection to the PostgreSQL database.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The database connection is managed in a way that ensures a single connection is used for the duration of the query, which can be considered a form of singleton pattern for the connection scope.

#### Dependencies
- **Imports**: The file imports `os`, `logging`, `re`, `psycopg2`, and `dotenv`.
- **Database**: It relies on PostgreSQL for database operations, specifically using the `document_registry` table.

#### Interfaces
- **Public Methods**: The `execute` method is the primary interface for executing the skill, which is called with a `SkillRequest` object and returns a `SkillResponse` object.
- **Internal Methods**: `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, and `_build_summary` are internal methods used to process the search logic.

#### Database
- **Tables**: The file interacts with the `document_registry` table in PostgreSQL to retrieve document information.
- **Queries**: It constructs and executes SQL queries to filter documents based on search terms and document type.

#### Configuration
- **Environment Variables**: The file uses environment variables loaded from `.env` to configure the PostgreSQL connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Key Logic
- **Search Term Extraction**: The `_extract_search_terms` method removes predefined trigger phrases and cleans the message to extract meaningful search terms.
- **Document Type Detection**: The `_detect_doc_type` method identifies the document type based on keywords in the message.
- **Database Query**: The `_search_docs` method constructs and executes a SQL query to retrieve documents from the `document_registry` table based on the search terms and document type.
- **Result Formatting and Summary**: The `_format_results` and `_build_summary` methods format the query results and build a summary of the search results, respectively.

#### Integration Points
- **SkillBase**: The `SearchDocumentsSkill` class inherits from `SkillBase`, indicating that it integrates with the broader Mythos skill framework.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response cycle.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_search_docs` method to execute queries.

### Summary
The `pass03_attempt01.py` file implements the `SearchDocumentsSkill` class, which handles document search requests by extracting search terms, detecting document types, querying the PostgreSQL database, and formatting the results. It integrates with the Mythos skill framework and relies on PostgreSQL for data storage and retrieval.
