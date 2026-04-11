# iris/core/src/config.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 125

---

### File: `iris/core/src/config.py`

#### 1. Purpose
This file contains the `Config` class, which is responsible for loading configuration settings from environment variables and providing methods to access specific configuration details, such as the PostgreSQL connection string.

#### 2. Architecture
The file is structured around the `Config` class, which uses the `dataclass` decorator from the `dataclasses` module. The class contains a variety of configuration attributes related to database connections, Telegram settings, Docker configurations, paths, loop timing, and thresholds. The `from_environment` class method is used to initialize the `Config` instance by loading values from environment variables. The `get_postgres_dsn` method generates the PostgreSQL connection string based on the configuration attributes.

#### 3. Patterns
- **Data Class**: The `Config` class uses the `dataclass` decorator to automatically generate special methods like `__init__`, `__repr__`, and `__eq__`.
- **Factory Method**: The `from_environment` class method acts as a factory method to create instances of `Config` by loading values from environment variables.

#### 4. Dependencies
- **Imports**: The file imports `os` for accessing environment variables and `dataclasses` and `typing` for defining the `Config` class and optional types.

#### 5. Interfaces
- **Public Methods**:
  - `from_environment(cls)`: A class method that loads configuration from environment variables and returns an instance of `Config`.
  - `get_postgres_dsn(self)`: A method that returns the PostgreSQL connection string based on the configuration attributes.

#### 6. Database
- **References**: The file references PostgreSQL configuration attributes (`postgres_host`, `postgres_port`, `postgres_db`, `postgres_user`, `postgres_password`) but does not directly interact with database tables or Neo4j labels.

#### 7. Configuration
- **Environment Variables**: The `Config` class relies on a variety of environment variables to initialize its attributes. These include settings for PostgreSQL, Neo4j, Redis, Ollama, Telegram, Docker, paths, loop timing, and thresholds.

#### 8. Key Logic
- **Loading Configuration**: The `from_environment` method loads configuration values from environment variables, handling default values and multiple naming conventions for certain variables (e.g., `TELEGRAM_USER_ID` and `TELEGRAM_ID_KA`).
- **Generating Connection String**: The `get_postgres_dsn` method constructs the PostgreSQL connection string based on the configuration attributes, handling both Unix socket and TCP connection scenarios.

#### 9. Integration Points
- **Environment Variables**: The `Config` class integrates with the environment variables set in the system, which are used to configure various subsystems of the Mythos system.
- **Subsystems**: The configuration values are used by other subsystems such as PostgreSQL, Neo4j, Redis, Ollama, Telegram, and Docker. The paths and timing configurations are used by the core IRIS systems for managing paths and loop intervals.

### Summary
The `config.py` file provides a centralized configuration management system for the Mythos platform. It loads configuration settings from environment variables and provides methods to access specific configuration details, such as the PostgreSQL connection string. This file is crucial for initializing the various subsystems of the Mythos platform with the correct configuration settings.
