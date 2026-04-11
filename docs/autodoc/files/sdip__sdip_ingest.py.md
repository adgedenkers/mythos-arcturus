# sdip/sdip_ingest.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 388

---

### File: `sdip/sdip_ingest.py`

#### Purpose
This file contains the main ingestion pipeline for the SDIP system, which processes files from a curated vault, chunks them, and populates the PostgreSQL database with the necessary records.

#### Architecture
The file consists of several top-level functions that handle different aspects of the ingestion process:
- `get_connection`: Establishes a PostgreSQL connection.
- `sha256_file`: Computes the SHA-256 hash of a file.
- `should_skip`: Determines if a file should be skipped based on various criteria.
- `ensure_source`: Ensures a source record exists and returns its ID.
- `upsert_document`: Inserts or updates a document record and returns its ID and chunking status.
- `insert_chunks`: Inserts chunk records for a document.
- `collect_files`: Collects all processable files from the vault.
- `ingest_vault`: Main ingestion pipeline that orchestrates the collection, processing, and database population.
- `show_stats`: Displays current database statistics.
- `main`: Entry point for the script.

#### Patterns
- **Factory Method**: The `get_connection` function acts as a factory method for creating a PostgreSQL connection.
- **Singleton**: The `get_connection` function could be considered a singleton if it ensures a single connection instance.
- **Observer**: The `ingest_vault` function observes the vault for changes and updates the database accordingly.

#### Dependencies
- `sys`, `os`, `json`, `hashlib`, `argparse`: Standard Python libraries for system operations, file handling, JSON processing, hashing, and argument parsing.
- `psycopg2`: PostgreSQL database adapter for Python.
- `config`: Custom module for configuration settings.
- `sdip_chunker`: Custom module for chunking files.

#### Interfaces
- `get_connection()`: Returns a PostgreSQL connection.
- `sha256_file(filepath: Path) -> str`: Computes the SHA-256 hash of a file.
- `should_skip(filepath: Path, vault_path: Path) -> bool`: Determines if a file should be skipped.
- `ensure_source(conn, name: str, path: str, source_type: str) -> int`: Ensures a source record exists and returns its ID.
- `upsert_document(conn, source_id: int, relative_path: str, filepath: Path) -> tuple[int, bool]`: Inserts or updates a document record and returns its ID and chunking status.
- `insert_chunks(conn, document_id: int, chunks: list) -> int`: Inserts chunk records for a document.
- `collect_files(vault_path: Path) -> list[Path]`: Collects all processable files from the vault.
- `ingest_vault(vault_path: Path, incremental: bool = False, dry_run: bool = False)`: Main ingestion pipeline.
- `show_stats()`: Displays current database statistics.

#### Database
- **Tables/Labels**:
  - `sdip_sources`: Stores source records.
  - `sdip_documents`: Stores document records.
  - `sdip_chunks`: Stores chunk records.

#### Configuration
- `VAULT_PATH`, `SUPPORTED_FORMATS`, `BINARY_FORMATS`, `SKIP_PATTERNS`, `SKIP_DIRS`, `DEFAULT_SOURCE_NAME`, `DEFAULT_SOURCE_TYPE`: Configuration settings from the `config` module.
- `get_db_connection()`: Function to get the database connection from the `config` module.

#### Key Logic
- **SHA-256 Hashing**: Computes the SHA-256 hash of a file to determine if it has changed.
- **File Skipping**: Determines if a file should be skipped based on its name, directory, or extension.
- **Source and Document Management**: Ensures source and document records exist and updates them as necessary.
- **Chunking**: Chunks files and inserts chunk records into the database.
- **Database Transactions**: Manages database transactions, committing in batches and rolling back on errors.

#### Integration Points
- **Configuration Module**: Uses `config` for configuration settings and database connection.
- **Chunking Module**: Uses `sdip_chunker` for chunking files.
- **Database**: Interacts with PostgreSQL to manage source, document, and chunk records.

### Detailed Analysis

#### `get_connection()`
- **Purpose**: Establishes a PostgreSQL connection.
- **Logic**: Uses `get_db_connection()` from the `config` module to get the connection.

#### `sha256_file(filepath: Path) -> str`
- **Purpose**: Computes the SHA-256 hash of a file.
- **Logic**: Reads the file in chunks and updates the hash.

#### `should_skip(filepath: Path, vault_path: Path) -> bool`
- **Purpose**: Determines if a file should be skipped.
- **Logic**: Checks the file name, directory, and extension against predefined patterns and supported formats.

#### `ensure_source(conn, name: str, path: str, source_type: str) -> int`
- **Purpose**: Ensures a source record exists and returns its ID.
- **Logic**: Queries the `sdip_sources` table to check if the source exists. If not, inserts a new record.

#### `upsert_document(conn, source_id: int, relative_path: str, filepath: Path) -> tuple[int, bool]`
- **Purpose**: Inserts or updates a document record and returns its ID and chunking status.
- **Logic**: Computes the SHA-256 hash of the file and checks if the document record exists. If it does, updates the record if the file has changed. Otherwise, inserts a new record.

#### `insert_chunks(conn, document_id: int, chunks: list) -> int`
- **Purpose**: Inserts chunk records for a document.
- **Logic**: Inserts each chunk record into the `sdip_chunks` table.

#### `collect_files(vault_path: Path) -> list[Path]`
- **Purpose**: Collects all processable files from the vault.
- **Logic**: Walks the vault directory and collects files that should not be skipped.

#### `ingest_vault(vault_path: Path, incremental: bool = False, dry_run: bool = False)`
- **Purpose**: Main ingestion pipeline that orchestrates the collection, processing, and database population.
- **Logic**: Collects files, ensures the source exists, and processes each file to insert or update document and chunk records. Manages database transactions and handles errors.

#### `show_stats()`
- **Purpose**: Displays current database statistics.
- **Logic**: Queries the `sdip_sources`, `sdip_documents`, and `sdip_chunks` tables to gather statistics and prints them.

#### `main()`
- **Purpose**: Entry point for the script.
- **Logic**: Parses command-line arguments and calls the appropriate functions (`ingest_vault` or `show_stats`).

This file is a critical component of the SDIP system, handling the ingestion of files from the vault and ensuring that the PostgreSQL database is up-to-date with the latest file content and metadata.
