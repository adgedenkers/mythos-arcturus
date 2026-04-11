# orchestrator/src/config.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 191

---

### File: orchestrator/src/config.py

#### Purpose
This file manages the configuration settings for the Mythos Orchestrator, loading them from environment variables and a `.env` file using Pydantic for type-safe handling. It provides methods to get paths to various directories and files, and checks the environment type (production or development).

#### Architecture
The file contains a single class `Settings` that inherits from `BaseSettings` from Pydantic. This class encapsulates all application settings, including database URLs, paths, and environment-specific configurations. The class also includes methods to generate paths to data, test suite, results, and log files, and to ensure that required directories exist. Additionally, there is a `Config` inner class for Pydantic configuration settings. The file also includes a top-level function `get_settings` for dependency injection in FastAPI.

#### Patterns
- **Singleton Pattern**: The `Settings` class is used as a singleton through a global instance `settings`.
- **Dependency Injection**: The `get_settings` function is used for dependency injection in FastAPI routes.

#### Dependencies
- `os`: For interacting with the operating system.
- `pydantic_settings.BaseSettings`: For loading and validating settings from environment variables.
- `typing.Optional`: For optional type annotations.
- `pathlib.Path`: For handling file paths.

#### Interfaces
- **Global Settings Instance**: The `settings` instance of `Settings` is globally available for importing in other modules.
- **Dependency Injection**: The `get_settings` function is used to inject the `Settings` instance into FastAPI routes.
- **Path Methods**: Methods like `get_data_path`, `get_test_suite_path`, `get_results_path`, and `get_log_path` provide paths to various files and directories.

#### Database
- **PostgreSQL Tables**: The file references the `config` and `pydantic_settings` tables, but these are likely placeholders or examples, as the actual database interactions are not present in the file.

#### Configuration
- **Environment Variables**: Settings are loaded from environment variables and a `.env` file located at `/opt/mythos/orchestrator/.env`.
- **Pydantic Configuration**: The `Config` class within `Settings` specifies the `.env` file location and encoding.

#### Key Logic
- **Path Generation**: Methods like `get_data_path`, `get_test_suite_path`, `get_results_path`, and `get_log_path` generate full paths to files based on provided names.
- **Directory Creation**: The `ensure_directories` method ensures that all required directories exist by creating them if necessary.
- **Environment Checks**: Properties `is_production` and `is_development` check the current environment type based on the `ENVIRONMENT` setting.

#### Integration Points
- **FastAPI Dependency Injection**: The `get_settings` function is used to inject the `Settings` instance into FastAPI routes, allowing access to configuration settings within route handlers.
- **Global Settings Access**: The `settings` instance is globally accessible, allowing other parts of the system to access configuration settings.

### Example Usage
```python
from fastapi import Depends
from config import get_settings, Settings

@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {"version": settings.VERSION}
```

This file serves as a central configuration manager for the Mythos Orchestrator, providing a robust and type-safe way to handle application settings and paths.
