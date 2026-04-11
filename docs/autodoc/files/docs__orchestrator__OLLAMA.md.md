# docs/orchestrator/OLLAMA.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 353

---

### Documentation for `docs/orchestrator/OLLAMA.md`

#### Purpose
This markdown file serves as a comprehensive guide for integrating and managing Ollama models within the Mythos system. It details the components, methods, and configurations required for model discovery, registration, and management.

#### Architecture
The file is structured into several sections:
- **Overview**: Provides a high-level description of the integration.
- **Quick Start**: Offers basic commands and Python usage examples.
- **OllamaClient**: Describes the asynchronous API wrapper for Ollama.
- **ModelRegistry**: Details the database-backed model registry.
- **ModelManager**: Explains the high-level operations for managing models.
- **Database Schema**: Outlines the database tables used for storing model information.
- **Configuration**: Lists the environment variables used for configuration.
- **Examples**: Provides code snippets for common operations.
- **Troubleshooting**: Offers guidance for resolving common issues.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the `ModelManager` and `OllamaClient` can be seen as factory-like constructs that provide instances for managing models and interacting with Ollama.
- **Singleton Pattern**: The `ModelManager` and `OllamaClient` can be considered singleton-like in their usage, as they are typically instantiated once and reused.

#### Dependencies
- **Environment Variables**: `.env` file for configuration settings.
- **Python Modules**: `asyncio`, `models` (which includes `ModelManager`, `OllamaClient`, and `ModelRegistry`).

#### Interfaces
- **OllamaClient**: Exposes methods like `list_models`, `show_model`, `generate`, `pull_model`, and `delete_model`.
- **ModelRegistry**: Provides methods such as `register_model`, `get_model`, `list_models`, `add_capability`, and `get_best_model_for_task`.
- **ModelManager**: Offers high-level methods including `sync_models`, `get_available_models`, `get_model_info`, `ensure_model`, `select_model_for_task`, and `generate`.

#### Database
- **Tables**: `orch_models` and `orch_model_capabilities`.
- **Labels**: Not applicable as the system uses PostgreSQL.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_TIMEOUT`, `OLLAMA_MAX_RETRIES`, `DEFAULT_MODEL`.

#### Key Logic
- **Model Synchronization**: The `sync_models` method in `ModelManager` synchronizes models from Ollama to the database.
- **Model Management**: Methods like `register_model`, `get_model`, and `list_models` in `ModelRegistry` manage the lifecycle of models.
- **Task Selection**: The `select_model_for_task` method in `ModelManager` selects the best model for a given task based on capabilities.

#### Integration Points
- **Ollama API**: The `OllamaClient` interacts with Ollama to list, pull, delete, and generate completions.
- **Database**: The `ModelRegistry` interacts with the PostgreSQL database to store and retrieve model information.
- **Orchestrator**: The `ModelManager` integrates with the orchestrator to manage models and provide high-level operations.

### Summary
This markdown file provides detailed documentation for integrating and managing Ollama models within the Mythos system. It covers the architecture, key components, and integration points, along with examples and troubleshooting tips. The system leverages PostgreSQL for storing model information and uses asynchronous Python for interacting with the Ollama API.
