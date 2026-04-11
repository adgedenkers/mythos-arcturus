# sdip/config.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 83

---

### File: `sdip/config.py`

#### Purpose
This file contains configuration settings and utility functions for the Sovereign Document Intelligence Platform (SDIP) subsystem within the Mythos system. It includes paths, database connection details, chunking parameters, supported file formats, and embedding settings.

#### Architecture
The file is structured with several sections:
- **Paths**: Defines important paths such as the root directory, vault path, and migrations directory.
- **Database**: Configures PostgreSQL database connection parameters.
- **Chunking**: Defines parameters for text chunking.
- **Supported Formats**: Lists supported file formats and special handling formats.
- **Embedding**: Defines embedding dimensions and model.
- **Source Defaults**: Provides default values for source names and types.

The main function is `get_db_connection`, which returns a PostgreSQL database connection.

#### Patterns
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern as it returns a single instance of a database connection.

#### Dependencies
- **Imports**: `os`, `pathlib`, `psycopg2`
- **Environment Variables**: `SDIP_VAULT_PATH`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Functions**: `get_db_connection()`
- **Constants**: Various constants for paths, chunking, supported formats, embedding, and source defaults.

#### Database
- **PostgreSQL**: The `get_db_connection` function connects to a PostgreSQL database using the `psycopg2` library.

#### Configuration
- **Environment Variables**: The file uses environment variables to configure paths and database connection details.
- **Constants**: The file defines several constants for paths, chunking parameters, supported formats, embedding settings, and source defaults.

#### Key Logic
- **Database Connection**: The `get_db_connection` function constructs and returns a PostgreSQL database connection using the `psycopg2.connect` method with parameters sourced from environment variables or default values.

#### Integration Points
- **Database Connection**: The `get_db_connection` function is likely used by other parts of the Mythos system to establish a connection to the PostgreSQL database.
- **Configuration**: The constants defined in this file are used throughout the SDIP subsystem for paths, chunking, supported formats, embedding, and source defaults.

### Detailed Breakdown

#### Paths
- `SDIP_ROOT`: Root directory for SDIP.
- `VAULT_PATH`: Path to the vault, defaulting to `~/curated-vault`.
- `MIGRATIONS_DIR`: Directory for database migrations.

#### Database
- `POSTGRES_HOST`: Host for PostgreSQL, defaulting to `/var/run/postgresql`.
- `POSTGRES_DB`: Database name, defaulting to `mythos`.
- `POSTGRES_USER`: User for PostgreSQL, defaulting to `postgres`.
- `POSTGRES_PASSWORD`: Password for PostgreSQL, defaulting to an empty string.
- `POSTGRES_PORT`: Port for PostgreSQL, defaulting to `5432`.

#### Chunking
- `MAX_CHUNK_WORDS`: Maximum number of words in a chunk.
- `MIN_CHUNK_WORDS`: Minimum number of words in a chunk.
- `SMALL_FILE_THRESHOLD`: Threshold for small files to be treated as a single chunk.

#### Supported Formats
- `SUPPORTED_FORMATS`: Set of supported file formats.
- `BINARY_FORMATS`: Set of binary formats that require special handling.
- `SKIP_PATTERNS`: Set of file patterns to skip.
- `SKIP_DIRS`: Set of directories to skip.

#### Embedding
- `EMBEDDING_DIM`: Dimension of the embedding vector.
- `EMBEDDING_MODEL`: Default embedding model.

#### Source Defaults
- `DEFAULT_SOURCE_NAME`: Default name for the source.
- `DEFAULT_SOURCE_TYPE`: Default type for the source.

This file serves as a central configuration hub for the SDIP subsystem, providing essential settings and utility functions for database connections and other operational parameters.
