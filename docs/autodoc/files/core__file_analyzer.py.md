# core/file_analyzer.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 398

---

### File: core/file_analyzer.py

#### Purpose
The `FileAnalyzer` class is responsible for analyzing files using a Large Language Model (LLM) and cataloging them into a PostgreSQL database. It handles file metadata extraction, content analysis, and database operations for storing and retrieving file information.

#### Architecture
The `FileAnalyzer` class contains several methods to handle file analysis and database operations. The class is designed to:
- Connect to and manage a PostgreSQL database connection.
- Compute file hashes, detect MIME types, and determine if a file is readable.
- Read file content and analyze it using an LLM.
- Catalog files in the database and update their records based on analysis results.
- Provide methods to search and retrieve files based on various criteria.

#### Patterns
- **Singleton Pattern**: The class manages a single database connection throughout its lifecycle, ensuring that the connection is reused and closed properly.
- **Factory Method**: The `analyze_with_llm` method acts as a factory method to generate analysis results based on the file content and LLM response.

#### Dependencies
The file imports the following modules:
- `hashlib` for computing file hashes.
- `json` for handling JSON data.
- `logging` for logging messages.
- `mimetypes` for detecting MIME types.
- `os` for interacting with the file system.
- `time` for measuring time intervals.
- `psycopg2` for PostgreSQL database operations.
- `requests` for making HTTP requests to the LLM service.

#### Interfaces
The `FileAnalyzer` class exposes the following methods:
- `__init__`: Initializes the class and connects to the database.
- `_connect_db`: Establishes a connection to the PostgreSQL database.
- `_ensure_db`: Ensures the database connection is active.
- `close`: Closes the database connection.
- `compute_hash`: Computes the SHA-256 hash of a file.
- `detect_mime`: Detects the MIME type of a file.
- `is_readable`: Determines if a file is readable.
- `read_content`: Reads the content of a file up to a specified limit.
- `analyze_with_llm`: Analyzes file content using an LLM.
- `catalog_file`: Catalogs a file, including metadata and analysis.
- `update_handler_result`: Updates the catalog record after a handler processes the file.
- `_find_by_hash`: Finds a file in the catalog by its hash.
- `_insert_catalog`: Inserts a new file record into the catalog.
- `_update_analysis`: Updates the analysis results for a file in the catalog.
- `_update_error`: Updates the error information for a file in the catalog.
- `search_files`: Searches for files based on a query.
- `recent_files`: Retrieves the most recently cataloged files.
- `files_by_tag`: Retrieves files by tag.

#### Database
The class interacts with the following PostgreSQL tables:
- `file_catalog`: Stores file metadata and analysis results.
- `failed`: Stores information about files that failed to be analyzed.

#### Configuration
The class uses the following environment variables:
- `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection parameters.
- `OLLAMA_URL`: URL for the LLM service.

#### Key Logic
- **Metadata Extraction**: Computes file hash, detects MIME type, and determines if the file is readable.
- **Content Analysis**: Sends file content to an LLM for analysis and processes the JSON response to extract summary, keywords, and tags.
- **Database Operations**: Inserts new file records into the `file_catalog` table, updates analysis results, and handles errors.

#### Integration Points
- **File System**: Reads files from the file system and determines their properties.
- **LLM Service**: Sends file content to an LLM for analysis via HTTP requests.
- **Database**: Stores and retrieves file metadata and analysis results from PostgreSQL.

### Detailed Method Descriptions

1. **`__init__`**: Initializes the `FileAnalyzer` instance and connects to the PostgreSQL database.
2. **`_connect_db`**: Establishes a connection to the PostgreSQL database using environment variables.
3. **`_ensure_db`**: Ensures the database connection is active and reconnects if necessary.
4. **`close`**: Closes the database connection.
5. **`compute_hash`**: Computes the SHA-256 hash of a file.
6. **`detect_mime`**: Detects the MIME type of a file.
7. **`is_readable`**: Determines if a file is readable based on its extension and size.
8. **`read_content`**: Reads the content of a file up to a specified limit.
9. **`analyze_with_llm`**: Analyzes file content using an LLM and processes the JSON response.
10. **`catalog_file`**: Catalogs a file, including metadata and analysis, and updates the database.
11. **`update_handler_result`**: Updates the catalog record after a handler processes the file.
12. **`_find_by_hash`**: Finds a file in the catalog by its hash.
13. **`_insert_catalog`**: Inserts a new file record into the `file_catalog` table.
14. **`_update_analysis`**: Updates the analysis results for a file in the `file_catalog` table.
15. **`_update_error`**: Updates the error information for a file in the `file_catalog` table.
16. **`search_files`**: Searches for files based on a query.
17. **`recent_files`**: Retrieves the most recently cataloged files.
18. **`files_by_tag`**: Retrieves files by tag.

This documentation provides a comprehensive overview of the `FileAnalyzer` class and its methods, detailing its purpose, architecture, dependencies, and integration points within the Mythos system.
