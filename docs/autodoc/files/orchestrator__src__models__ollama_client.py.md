# orchestrator/src/models/ollama_client.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 329

---

### File: orchestrator/src/models/ollama_client.py

#### Purpose
This file defines an asynchronous client (`OllamaClient`) for interacting with the Ollama API, providing methods for model management and inference operations such as listing models, pulling models, generating text, and checking health.

#### Architecture
The file contains a single class `OllamaClient` with multiple methods for different operations. The class uses an asynchronous context manager (`__aenter__` and `__aexit__`) to manage the lifecycle of an `aiohttp.ClientSession`. The `_request` method handles HTTP requests with retry logic, and other methods like `list_models`, `generate`, and `pull_model` use this method to interact with the Ollama API.

#### Patterns
- **Singleton**: The `OllamaClient` can be used as a singleton within a context manager to ensure that the session is properly managed.
- **Factory**: The `_request` method acts as a factory for creating and managing HTTP requests.
- **Observer**: The `pull_model` and `_generate_stream` methods use an observer pattern to stream responses.

#### Dependencies
- **aiohttp**: For asynchronous HTTP requests.
- **asyncio**: For asynchronous operations.
- **logging**: For logging.
- **sys**: For modifying the system path.
- **re**: For regular expression operations.
- **json**: For JSON handling.
- **config**: For accessing settings from the configuration.

#### Interfaces
- **Initialization**: `__init__` initializes the client with base URL, timeout, and retry settings.
- **Context Management**: `__aenter__` and `__aexit__` for managing the session lifecycle.
- **Connection Management**: `connect` and `close` for session management.
- **Request Handling**: `_request` for making HTTP requests with retry logic.
- **Model Management**: `list_models`, `show_model`, `pull_model`, `delete_model` for managing models.
- **Generation**: `generate` and `_generate_stream` for text generation.
- **Embeddings**: `embeddings` for generating text embeddings.
- **Health Check**: `health_check` for checking the health of the Ollama service.
- **Utility**: `parse_model_name` for parsing model names.

#### Database
- **References**: The file references several PostgreSQL tables and settings, but does not directly interact with the database. It uses settings and configurations from the `config` module.

#### Configuration
- **Settings**: The client uses settings from the `config` module, such as `OLLAMA_HOST`, `OLLAMA_TIMEOUT`, and `DEFAULT_TEMPERATURE`.

#### Key Logic
- **HTTP Request Handling**: The `_request` method handles HTTP requests with retry logic, ensuring robust communication with the Ollama API.
- **Model Management**: Methods like `list_models`, `show_model`, `pull_model`, and `delete_model` manage models by making appropriate HTTP requests.
- **Text Generation**: The `generate` method handles text generation, supporting both streaming and non-streaming responses.
- **Embeddings**: The `embeddings` method generates embeddings for text using the Ollama API.
- **Health Check**: The `health_check` method verifies the health of the Ollama service by attempting to list models.

#### Integration Points
- **Orchestrator**: The `OllamaClient` integrates with the orchestrator subsystem to manage models and generate text.
- **Settings**: It uses settings from the `config` module to configure timeouts and other parameters.
- **Logging**: It logs important events and errors using the `logging` module.

### Summary
The `OllamaClient` class provides a comprehensive interface for interacting with the Ollama API, supporting model management, text generation, and health checks. It uses asynchronous operations for efficient handling of HTTP requests and ensures robust communication through retry logic. The client integrates with the orchestrator subsystem and uses settings from the configuration module to customize its behavior.
