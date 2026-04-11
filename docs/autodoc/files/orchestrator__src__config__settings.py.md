# orchestrator/src/config/settings.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 277

---

### File: orchestrator/src/config/settings.py

#### Purpose
This file manages the configuration settings for the Mythos Orchestrator, providing methods to load and resolve configurations from various sources including environment variables, registry files, and test overrides.

#### Architecture
- **Classes**:
  - `Settings`: Inherits from `BaseSettings` to manage and validate all orchestrator settings. It includes methods to get paths, ensure directories, and load Neo4j passwords.
  - `Config`: A nested class within `Settings` that configures the behavior of `BaseSettings`.
- **Top-level Functions**:
  - `_load_registry`: Loads the registry YAML file with file-change caching.
  - `get_registry`: Retrieves the current prompt registry.
  - `get_registry_version`: Retrieves the version string of the registry.
  - `get_model_config`: Retrieves the model configuration for a given pipeline role from the registry.
  - `resolve_config`: Resolves the full configuration for a pipeline role, considering overrides, settings, registry, and defaults.
  - `load_test_config`: Loads a test configuration override file.
  - `snapshot_config`: Captures the full resolved configuration state for reproducibility.
  - `get_path`: Gets the full path within a subdirectory.
  - `ensure_directories`: Ensures all required directories are created.
  - `get_neo4j_password`: Loads the Neo4j password from environment variables or files.

#### Patterns
- **Singleton Pattern**: The `Settings` class is instantiated as a global singleton `settings`, ensuring consistent configuration across the application.
- **Factory Method Pattern**: The `resolve_config` function acts as a factory method to create and return a resolved configuration dictionary based on the role and optional overrides.

#### Dependencies
- **Imports**:
  - `yaml`: For parsing YAML files.
  - `json`: For JSON operations.
  - `os`: For file and directory operations.
  - `logging`: For logging.
  - `pydantic_settings.BaseSettings`: For configuration management.
  - `typing`: For type hints.
  - `pathlib.Path`: For path operations.

#### Interfaces
- **Exposed Functions**:
  - `get_registry`: Returns the current prompt registry.
  - `get_registry_version`: Returns the version string of the registry.
  - `get_model_config`: Returns the model configuration for a given pipeline role.
  - `resolve_config`: Resolves the full configuration for a pipeline role.
  - `load_test_config`: Loads a test configuration override file.
  - `snapshot_config`: Captures the full resolved configuration state.
- **Global Instance**:
  - `settings`: A global instance of the `Settings` class.

#### Database
- **References**:
  - PostgreSQL tables: `src`, `pydantic_settings`, `typing`, `pathlib`, `registry`, `env`.
  - Neo4j: Configuration for Neo4j user and password.

#### Configuration
- **Environment Variables and Files**:
  - `.env` file: Loaded by `Settings.Config` for environment-specific configurations.
  - `NEO4J_PASSWORD`: Loaded from environment variables or `.env` files.
  - `DATABASE_URL`: PostgreSQL database URL.
  - `REDIS_URL`: Redis URL.
  - `OLLAMA_HOST`, `OLLAMA_API_URL`: Ollama API URLs.
  - `PIPELINE_MODE`: Determines the pipeline mode (production, test, dry-run).
  - `PERCEPTION_MODEL`, `IRIS_MODEL`, `STRATEGY_MODEL`: Model overrides for different roles.

#### Key Logic
- **Configuration Resolution**:
  - `resolve_config`: Prioritizes overrides, settings, registry, and defaults to resolve the full configuration for a pipeline role.
- **Registry Management**:
  - `_load_registry`: Caches the registry YAML file to avoid reloading on every access.
  - `get_registry`: Provides access to the current prompt registry.
- **Directory Management**:
  - `ensure_directories`: Ensures all required directories are created.

#### Integration Points
- **Mythos Subsystems**:
  - **Pipeline Configuration**: Integrates with the pipeline subsystem to provide role-specific configurations.
  - **Database**: Provides configuration for PostgreSQL and Neo4j connections.
  - **Logging**: Configures logging settings.
  - **Test Overrides**: Loads and applies test configuration overrides for bench runs.
  - **Ollama API**: Configures Ollama API URLs and timeouts.
  - **Redis**: Configures Redis connection settings.

This file serves as the central configuration manager for the Mythos Orchestrator, ensuring that all subsystems have access to the correct and consistent settings.
