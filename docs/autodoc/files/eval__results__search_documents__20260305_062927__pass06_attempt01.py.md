# eval/results/search_documents/20260305_062927/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### Documentation for `pass06_attempt01.py`

#### Purpose
This file defines the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type and returning formatted results. It handles the extraction of search terms, detection of document types, and querying the PostgreSQL database to retrieve relevant documents.

#### Architecture
The file contains a single class `SearchDocumentsSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the search process:
- `_extract_search_terms`: Extracts search terms from the input message.
- `_detect_doc_type`: Detects the document type from the input message.
- `_search_docs`: Queries the PostgreSQL database to retrieve documents based on search terms and document type.
- `_format_results`: Formats the retrieved documents into a list of dictionaries.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main method that orchestrates the search process and returns a `SkillResponse`.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection to the database is used throughout the execution.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` are loaded from the `.env` file.

#### Interfaces
- **Public Methods**: `execute` is the main public method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, `_build_summary` are private methods used internally by the class.

#### Database
- **Tables**: The `document_registry` table is queried to retrieve documents based on search terms and document type.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `SearchDocumentsSkill` class.

#### Key Logic
- **Search Terms Extraction**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract meaningful search terms.
- **Document Type Detection**: The `_detect_doc_type` method checks for keywords in the message to determine the document type.
- **Database Query**: The `_search_docs` method constructs a SQL query based on the search terms and document type, and retrieves documents from the `document_registry` table.
- **Result Formatting**: The `_format_results` method formats the retrieved documents into a list of dictionaries.
- **Summary Building**: The `_build_summary` method creates a summary of the search results.

#### Integration Points
- **SkillBase Class**: The `SearchDocumentsSkill` class inherits from `SkillBase`, which likely provides a framework for handling skill requests and responses.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos system's request-response mechanism.
- **PostgreSQL Database**: The `_get_conn` function and `_search_docs` method interact with the PostgreSQL database to retrieve documents from the `document_registry` table.

This file is a critical component of the Mythos system, enabling users to search for documents by title or type and providing formatted results and summaries.
