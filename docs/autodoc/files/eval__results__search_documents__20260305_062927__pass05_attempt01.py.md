# eval/results/search_documents/20260305_062927/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### File: `eval/results/search_documents/20260305_062927/pass05_attempt01.py`

#### Purpose
This file contains the `SearchDocumentsSkill` class, which is responsible for searching the document registry by title or type and returning formatted results. It interacts with a PostgreSQL database to retrieve document information and processes user queries to extract search terms and document types.

#### Architecture
The file is structured around the `SearchDocumentsSkill` class, which inherits from `SkillBase`. The class contains several methods for executing the search, extracting search terms, detecting document types, searching the database, formatting results, and building summaries. Additionally, there are top-level functions for getting the database connection and handling the execution of the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection to the database.
- **Factory**: The `_search_docs` method can be seen as a factory method that returns a list of documents based on the provided search terms and document type.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `engine.base`
- **External Libraries**: `psycopg2` for PostgreSQL database interaction, `dotenv` for loading environment variables.

#### Interfaces
- **Public Methods**: `execute` (asynchronous)
- **Private Methods**: `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, `_build_summary`

#### Database
- **Tables**: `document_registry` (PostgreSQL)
- **Operations**: 
  - `SELECT COUNT(*)` to get the total number of documents.
  - `SELECT id, title, doc_type, file_path, created_at, updated_at` to retrieve specific documents based on search terms and document type.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Configuration File**: `.env` located at `/opt/mythos/.env`

#### Key Logic
1. **_extract_search_terms**: Removes predefined trigger phrases from the user message and cleans up the remaining text to form search terms.
2. **_detect_doc_type**: Identifies the document type based on keywords in the user message.
3. **_search_docs**: Constructs and executes a SQL query to search the `document_registry` table based on the provided search terms and document type.
4. **_format_results**: Formats the raw database results into a more readable dictionary format.
5. **_build_summary**: Generates a summary of the search results, including the number of matches and details of the first few matches.

#### Integration Points
- **SkillBase**: The `SearchDocumentsSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response system.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, ensuring seamless integration with the Mythos database infrastructure.

### Summary
This file implements the `SearchDocumentsSkill` class, which provides functionality to search and retrieve documents from a PostgreSQL database based on user queries. It integrates with the Mythos skill framework, uses environment variables for configuration, and follows a modular design with clear separation of concerns among its methods.
