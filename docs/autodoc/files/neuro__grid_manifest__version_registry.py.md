# neuro/grid_manifest/version_registry.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 224

---

### File: `neuro/grid_manifest/version_registry.py`

#### Purpose
This file manages the versioning and status of node-layer combinations within the Arcturian Grid, providing methods to query, update, and summarize version information stored in a PostgreSQL database.

#### Architecture
The file contains a single class, `VersionRegistry`, which encapsulates all the logic related to managing node-layer versions. The class uses a cache to store version information in memory for faster access and relies on PostgreSQL for persistent storage. The class methods handle various operations such as fetching current versions, checking if a node-layer is active, bumping versions, and finding stale exchanges.

#### Patterns
- **Singleton Pattern**: The `VersionRegistry` class can be considered a singleton as it is designed to manage a centralized registry of node-layer versions.
- **Cache Pattern**: The class uses an in-memory cache (`self._cache`) to store version information, which is loaded from the database on demand.

#### Dependencies
- **Imports**: `os`, `hashlib`, `logging`, `psycopg2`, `dotenv`
- **Database**: PostgreSQL (`grid_version_registry`, `grid_processing_manifest` tables)

#### Interfaces
- **Public Methods**:
  - `get_version(node: str, layer: int) -> str`: Retrieves the current version of a node-layer.
  - `is_active(node: str, layer: int) -> bool`: Checks if a node-layer is active.
  - `get_prompt_hash(node: str, layer: int) -> Optional[str]`: Retrieves the stored prompt hash for a node-layer.
  - `get_all_active(layer: int = None) -> List[Dict]`: Retrieves all active node-layer entries, optionally filtered by layer.
  - `bump_version(node: str, layer: int, new_version: str, prompt_text: str = None, change_description: str = '') -> bool`: Bumps the version of a node-layer and records the change in the changelog.
  - `find_stale_exchanges(node: str, layer: int, old_version: str = None, limit: int = 100) -> List[Dict]`: Finds exchanges processed under an older version of a node-layer.
  - `get_status_summary() -> Dict[str, Any]`: Retrieves a summary of the version registry for diagnostics.
  - `compute_prompt_hash(prompt_text: str) -> str`: Computes a short hash for a prompt string.

#### Database
- **Tables**:
  - `grid_version_registry`: Stores version information for node-layer combinations.
  - `grid_processing_manifest`: Stores processing details for exchanges.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for connecting to the PostgreSQL database.
- **Configuration File**: `.env` file located at `/opt/mythos/.env`.

#### Key Logic
- **Version Management**:
  - `get_version`: Fetches the current version from the cache or database.
  - `is_active`: Checks if a node-layer is active using cached information.
  - `bump_version`: Updates the version in the database and busts the cache to ensure the new version is fetched on the next lookup.
- **Stale Exchange Detection**:
  - `find_stale_exchanges`: Queries the database to find exchanges processed under an older version.
- **Cache Management**:
  - `_load_cache`: Loads all versions from the database into memory for faster access.
  - `_cache_loaded`: Tracks whether the cache has been loaded to avoid redundant database queries.

#### Integration Points
- **PostgreSQL**: The class interacts with the PostgreSQL database to fetch and update version information.
- **Logging**: Uses the `logging` module to log important events and errors.
- **Environment Configuration**: Relies on environment variables and a `.env` file for configuration, ensuring the system is self-contained and configurable.

This file is crucial for maintaining the integrity and consistency of node-layer versions within the Mythos system, ensuring that processing is done with the correct version of prompts and that stale exchanges are identified and reprocessed as needed.
