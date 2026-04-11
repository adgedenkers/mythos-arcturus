# eval/results/search_documents/20260305_062927/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### File: eval/results/search_documents/20260305_062927/temp_skill/test_skill.py

#### Purpose
This file contains the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type and returning formatted results.

#### Architecture
The file is structured around the `SearchDocumentsSkill` class, which inherits from `SkillBase`. The class contains several methods for extracting search terms, detecting document types, searching the document registry, formatting results, and building summaries. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Factory Method**: The `_get_conn` function can be considered a factory method for creating database connections.
- **Singleton**: The `_get_conn` function could be adapted to use a singleton pattern to ensure only one connection is created per request.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the skill and returns a response.
- **Private Methods**:
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the message.
  - `_detect_doc_type(message: str) -> str`: Detects the document type from the message.
  - `_search_docs(search_terms: str, doc_type: str = None, limit: int = 15) -> list`: Searches the document registry.
  - `_format_results(rows: list) -> list`: Formats the search results.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a summary of the search results.
- **Top-level Functions**:
  - `_get_conn()`: Returns a PostgreSQL database connection.

#### Database
- **Tables**:
  - `document_registry`: Used to store and retrieve document information.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured via `.env` file.

#### Key Logic
1. **Extracting Search Terms**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Detecting Document Type**: The `_detect_doc_type` method identifies the document type based on keywords in the message.
3. **Searching Documents**: The `_search_docs` method constructs a SQL query based on the search terms and document type, then executes the query against the `document_registry` table.
4. **Formatting Results**: The `_format_results` method formats the raw query results into a more readable structure.
5. **Building Summary**: The `_build_summary` method creates a summary of the search results, including a count and details of the top matches.

#### Integration Points
- **SkillBase**: The `SearchDocumentsSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, allowing seamless integration with other parts of the Mythos system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, ensuring that the skill can interact with the `document_registry` table.
