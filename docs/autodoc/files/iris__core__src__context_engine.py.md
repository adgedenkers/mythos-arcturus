# iris/core/src/context_engine.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 843

---

### File: `iris/core/src/context_engine.py`

#### Purpose
This file contains the core logic for the `ContextEngine` in the Mythos system, which gathers diagnostic information from various registered providers. It ensures that all gathered data is sanitized to prevent the exposure of sensitive information.

#### Architecture
The file consists of three primary classes:
1. **AccessPolicy**: Manages file and path access restrictions.
2. **ContextProviders**: Registers and manages individual context providers.
3. **ContextEngine**: Orchestrates the gathering of context from multiple providers based on a specification.

The file also includes top-level functions for sanitizing text and dictionaries.

#### Patterns
- **Factory Pattern**: The `ContextProviders` class acts as a factory for different context providers.
- **Singleton Pattern**: The `AccessPolicy` class can be considered a singleton as it loads a policy configuration once and reuses it.

#### Dependencies
- `asyncio`, `json`, `logging`, `os`, `re`, `subprocess`, `psycopg2`, `psycopg2.extras`, `signal`, `urllib.parse`, `urllib.request`, `yaml`, `redis`

#### Interfaces
- **AccessPolicy**:
  - `__init__`: Initializes the policy with default or loaded values.
  - `check_file_path`: Checks if a file path is allowed.
  - `check_pg_query`: Checks if a PostgreSQL query is allowed.
- **ContextProviders**:
  - `__init__`: Initializes the context providers with database configuration, access policy, and default settings.
  - `list_providers`: Lists all available providers.
  - `has_provider`: Checks if a provider is registered.
  - `get`: Retrieves and runs a provider.
- **ContextEngine**:
  - `__init__`: Initializes the context engine with database configuration and access policy.
  - `gather`: Gathers context from multiple providers based on a specification.
  - `gather_single`: Gathers context from a single provider.
  - `list_providers`: Lists all available providers.

#### Database
- **PostgreSQL**: 
  - `_prov_pg_query`: Executes read-only queries.
  - `_prov_table_schema`: Retrieves table schema information.
- **Neo4j**: 
  - `_prov_neo4j_query`: Executes read-only Cypher queries.
- **Redis**: 
  - `_prov_redis_state`: Retrieves Redis state information.

#### Configuration
- **AccessPolicy**: Loads configuration from `/opt/mythos/config/context_access_policy.yaml`.
- **ContextEngine**: Uses `db_config` and `policy_path` for initialization.

#### Key Logic
- **Sanitization**: Ensures that all text and dictionary outputs are sanitized to remove sensitive information.
- **Provider Execution**: Each provider function (e.g., `_prov_journalctl`, `_prov_git_log`, `_prov_file_content`) gathers specific diagnostic data and ensures it adheres to the access policy.
- **Timeout Handling**: Providers are executed with a timeout to prevent indefinite waits.

#### Integration Points
- **TriggerEngine**: The `ContextEngine` is called by the `TriggerEngine` to gather context before routing to the decision gate.
- **CLI**: The `iris-context` CLI can use the `ContextEngine` for standalone context gathering.
- **Database Access**: Integrates with PostgreSQL, Neo4j, and Redis to gather data.
- **File Access**: Uses the `AccessPolicy` to ensure file access is within allowed paths.

### Detailed Analysis

#### AccessPolicy
- **Purpose**: Manages access restrictions for file paths and PostgreSQL queries.
- **Methods**:
  - `__init__`: Initializes with a policy path.
  - `_load`: Loads policy from a YAML file.
  - `_set_defaults`: Sets default policy values.
  - `check_file_path`: Checks if a file path is allowed.
  - `check_pg_query`: Checks if a PostgreSQL query is allowed.

#### ContextProviders
- **Purpose**: Manages a registry of context providers.
- **Methods**:
  - `__init__`: Initializes with database configuration, access policy, and default settings.
  - `list_providers`: Lists all available providers.
  - `has_provider`: Checks if a provider is registered.
  - `get`: Retrieves and runs a provider.
  - `_run_with_timeout`: Runs a function with a timeout.
  - `_run_cmd`: Runs a shell command.
  - `_prov_*`: Various provider functions for different types of data gathering.

#### ContextEngine
- **Purpose**: Orchestrates the gathering of context from multiple providers.
- **Methods**:
  - `__init__`: Initializes with database configuration and access policy.
  - `gather`: Gathers context from multiple providers based on a specification.
  - `gather_single`: Gathers context from a single provider.
  - `list_providers`: Lists all available providers.

### Top-Level Functions
- **sanitize_text**: Strips secrets from text output.
- **sanitize_dict**: Recursively sanitizes a dictionary, redacting sensitive values.

### Example Usage
```python
engine = ContextEngine(db_config, "/opt/mythos/config/context_access_policy.yaml")
context_spec = [
    {"provider": "service_status", "args": {"service": "mythos-api"}},
    {"provider": "journalctl", "args": {"unit": "mythos-bot", "lines": 20}},
]
context = engine.gather(context_spec)
```

This file is a critical component of the Mythos system, ensuring that the context gathered is both comprehensive and secure.
