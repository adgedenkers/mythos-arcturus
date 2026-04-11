# orchestrator/src/models/model_manager.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 305

---

### Documentation for `orchestrator/src/models/model_manager.py`

#### Purpose
The `ModelManager` class in `model_manager.py` is responsible for high-level operations that coordinate between the Ollama client and the model registry. It handles model discovery, synchronization, and management, providing methods to sync models, retrieve model information, ensure model availability, select models for specific tasks, and generate text using models.

#### Architecture
The `ModelManager` class is designed with the following methods:
- `__init__`: Initializes the `ModelManager` instance.
- `sync_models`: Synchronizes installed Ollama models with the registry.
- `get_available_models`: Retrieves a list of available models.
- `get_model_info`: Fetches detailed information about a specific model.
- `ensure_model`: Ensures a model is available, optionally pulling it if needed.
- `select_model_for_task`: Selects the best model for a given task type.
- `generate`: Generates text using a specified model.
- `get_stats`: Retrieves statistics about the model manager.

#### Patterns
- **Singleton**: The `ModelManager` class is not explicitly designed as a singleton, but it could be used as one to manage the state of model synchronization and availability.
- **Factory**: The `OllamaClient` is used as a factory to interact with the Ollama service.
- **Observer**: The `ModelManager` observes the state of models in the registry and updates it based on the Ollama service.

#### Dependencies
- `logging`: For logging messages.
- `sys`: For modifying the system path.
- `os`: For path manipulations.
- `models.ollama_client`: For interacting with the Ollama service.
- `models.model_registry`: For managing the model registry.

#### Interfaces
- `__init__`: Initializes the `ModelManager`.
- `sync_models`: Synchronizes models.
- `get_available_models`: Retrieves available models.
- `get_model_info`: Retrieves detailed model information.
- `ensure_model`: Ensures model availability.
- `select_model_for_task`: Selects a model for a task.
- `generate`: Generates text using a model.
- `get_stats`: Retrieves statistics.

#### Database
The `ModelManager` interacts with the following PostgreSQL tables:
- `models`: For storing model information.
- `Ollama`: For storing Ollama-specific details.
- `families`: For storing model families.
- `registry`: For storing model registry information.
- `last`: For storing the last used timestamp.

#### Configuration
No specific configuration files are used, but environment variables or configuration settings could be used to customize the behavior of the `ModelManager`.

#### Key Logic
- **Sync Models**: The `sync_models` method discovers models from Ollama, registers them in the database, and updates their installation status.
- **Model Information**: The `get_model_info` method combines registry data with live Ollama data to provide detailed model information.
- **Model Availability**: The `ensure_model` method ensures a model is available by pulling it if necessary.
- **Task Model Selection**: The `select_model_for_task` method selects the best model for a given task type.
- **Text Generation**: The `generate` method generates text using a specified model and updates the last used timestamp in the registry.

#### Integration Points
- **Ollama Client**: The `ModelManager` interacts with the `OllamaClient` to discover, pull, and generate text using models.
- **Model Registry**: The `ModelManager` interacts with the `ModelRegistry` to manage model information, including registration, retrieval, and updating.

### Summary
The `ModelManager` class in `model_manager.py` serves as a high-level orchestrator for managing models in the Mythos system. It integrates with the Ollama service and the model registry to provide comprehensive model management functionalities, including synchronization, retrieval, and generation.
