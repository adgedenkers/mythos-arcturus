# skills/data/search_documents.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 216

---

### Documentation for `skills/data/search_documents.py`

#### Purpose
The `search_documents.py` file implements the `SearchDocumentsSkill` class, which is responsible for searching both the document registry and file catalog in the Mythos system. It provides a comprehensive document discovery mechanism based on title, content, or type.

#### Architecture
The file contains a single class `SearchDocumentsSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the document search process:
- `_extract_search_terms`: Extracts search terms from the input message.
- `_detect_doc_type`: Detects the document type based on keywords in the input message.
- `_search_docs`: Performs the actual search in the document registry and file catalog.
- `_format_results`: Formats the search results into a consistent structure.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, which orchestrates the search process.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern for database connection management, ensuring a single connection is reused.
- **Factory Method**: The `_search_docs` method can be seen as a factory method that produces search results based on input parameters.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method exposed to other parts of the system, which takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `document_registry`, `file_catalog`.
- **Operations**: The file performs SELECT operations on these tables to retrieve document and file metadata.

#### Configuration
- **Environment Variables**: The file reads environment variables for database connection details from a `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method removes trigger phrases and non-alphanumeric characters from the input message, then filters out single-character words.
2. **Document Type Detection**: The `_detect_doc_type` method identifies the document type based on predefined keywords.
3. **Document Search**: The `_search_docs` method performs two searches:
   - In the `document_registry` table by title.
   - In the `file_catalog` table using full-text search, filename, and keywords.
4. **Result Formatting**: The `_format_results` method formats the search results into a consistent dictionary structure.
5. **Summary Building**: The `_build_summary` method constructs a summary of the search results, highlighting curated and catalog documents.

#### Integration Points
- **SkillBase Integration**: The `SearchDocumentsSkill` class inherits from `SkillBase`, integrating with the Mythos skill framework.
- **Database Integration**: The file connects to the PostgreSQL database to retrieve document and file metadata.
- **SkillRequest/SkillResponse**: The `execute` method handles incoming requests and returns responses using the `SkillRequest` and `SkillResponse` classes, integrating with the Mythos request/response system.

This documentation provides a comprehensive overview of the `search_documents.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
