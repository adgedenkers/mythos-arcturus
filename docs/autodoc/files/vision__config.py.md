# vision/config.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 58

---

### File: vision/config.py

#### Purpose
This file manages the configuration for the vision analysis module within the Mythos system. It provides a mechanism to load and reload configuration settings from environment variables.

#### Architecture
- **Classes**: 
  - `VisionConfig`: A dataclass that holds configuration settings for vision analysis.
- **Functions**: 
  - `get_config()`: Retrieves or creates the configuration instance.
  - `reload_config()`: Forces a reload of the configuration from environment variables.
- **Data Flow**: 
  - Configuration settings are loaded from environment variables and stored in a `VisionConfig` instance.
  - The `get_config()` function returns the configuration instance, which is reused unless `reload_config()` is called to refresh it.

#### Patterns
- **Singleton Pattern**: The `get_config()` function ensures that only one instance of `VisionConfig` is created and reused, unless explicitly reloaded.

#### Dependencies
- **Imports**: 
  - `os`: Used to retrieve environment variables.
  - `dataclasses`: Used to define the `VisionConfig` dataclass.
  - `typing`: Used for type annotations.

#### Interfaces
- **Exposed Functions**: 
  - `get_config()`: Returns the current configuration.
  - `reload_config()`: Forces a reload of the configuration from environment variables.

#### Database
- **References**: 
  - The file does not directly interact with any database tables or Neo4j labels. However, it references environment variables that might be managed through a database (e.g., `environment`).

#### Configuration
- **Environment Variables**: 
  - `OLLAMA_HOST`: Host for the Ollama service.
  - `OLLAMA_VISION_MODEL`: Vision model to use.
  - `OLLAMA_TIMEOUT`: Timeout for Ollama requests.
  - `MYTHOS_INTAKE_PENDING`: Path for pending intake files.
  - `MYTHOS_INTAKE_PROCESSED`: Path for processed intake files.
  - `MYTHOS_INTAKE_FAILED`: Path for failed intake files.
  - `MYTHOS_ASSETS_PATH`: Path for image assets.
  - `DEFAULT_PICKUP_LOCATION`: Default pickup location.
  - `DEFAULT_PICKUP_CONTACT`: Default pickup contact.
  - `DEFAULT_PAYMENT_METHOD`: Default payment method.

#### Key Logic
- **Configuration Loading**: The `get_config()` function loads configuration settings from environment variables and stores them in a `VisionConfig` instance. If the configuration has not been loaded before, it initializes the instance with default values.
- **Reloading Configuration**: The `reload_config()` function sets the global `_config` to `None`, effectively forcing the `get_config()` function to reload the configuration from environment variables.

#### Integration Points
- **Vision Module**: This configuration file is used by the vision module to access necessary settings for vision analysis tasks.
- **Environment Management**: The configuration is loaded from environment variables, which can be managed through the system's environment or a configuration management tool.

### Summary
The `vision/config.py` file is responsible for managing the configuration settings for the vision analysis module. It uses a singleton pattern to ensure that configuration settings are loaded only once and reused unless explicitly reloaded. The configuration is loaded from environment variables, providing flexibility in managing settings across different environments.
