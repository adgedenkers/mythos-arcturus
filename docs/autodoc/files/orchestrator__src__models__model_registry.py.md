# orchestrator/src/models/model_registry.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 327

---

### Documentation for `orchestrator/src/models/model_registry.py`

#### Purpose
The `ModelRegistry` class provides a database-backed registry for managing Large Language Model (LLM) models, including their capabilities and metadata. It supports CRUD operations for models and their capabilities.

#### Architecture
The `ModelRegistry` class contains methods for registering, retrieving, listing, updating, and deleting models and their capabilities. The class is designed to interact with a PostgreSQL database to store and retrieve model information.

#### Patterns
- **Factory Method**: The `normalize_model_id` method acts as a factory method to generate a safe `model_id` from a given model name.
- **Singleton**: The `ModelRegistry` class can be used as a singleton to ensure a single instance manages the model registry.

#### Dependencies
- **Imports**: The file imports `logging`, `sys`, `os`, and uses `db` from a `database` module and `generate_id`, `safe_json_dumps`, `safe_json_loads` from a `utils` module.
- **Database**: The class interacts with PostgreSQL tables `orch_models` and `orch_model_capabilities`.

#### Interfaces
- **Public Methods**:
  - `normalize_model_id`: Converts a model name to a safe `model_id`.
  - `register_model`: Registers a new model in the database.
  - `get_model`: Retrieves a model by its `model_id`.
  - `get_model_by_name`: Retrieves a model by its name.
  - `list_models`: Lists all models with optional filtering by provider and installation status.
  - `mark_installed`: Marks a model as installed or uninstalled.
  - `update_last_used`: Updates the last used timestamp for a model.
  - `delete_model`: Deletes a model from the registry.
  - `add_capability`: Adds a capability for a model.
  - `get_capabilities`: Retrieves all capabilities for a model.
  - `get_best_model_for_task`: Retrieves the best model for a specific task type.
  - `get_model_stats`: Retrieves statistics about the models in the registry.

#### Database
- **Tables**:
  - `orch_models`: Stores model information such as `model_id`, `name`, `provider`, `size_params`, `context_window`, `installed`, `installed_at`, `metadata`, `created_at`, and `last_used`.
  - `orch_model_capabilities`: Stores model capabilities such as `capability_id`, `model_id`, `task_type`, `quality_score`, `speed_tier`, `notes`, and `created_at`.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Config Files**: No explicit configuration files are used.

#### Key Logic
- **Register Model**: Inserts a new model into the `orch_models` table or updates an existing one.
- **Get Model**: Retrieves a model from the `orch_models` table by `model_id`.
- **List Models**: Queries the `orch_models` table with optional filters for provider and installation status.
- **Mark Installed**: Updates the `installed` and `installed_at` fields in the `orch_models` table.
- **Add Capability**: Inserts a new capability into the `orch_model_capabilities` table.
- **Get Best Model for Task**: Joins `orch_models` and `orch_model_capabilities` tables to find the model with the highest quality score for a given task type.

#### Integration Points
- **Database**: The class interacts with the PostgreSQL database through the `db` module for CRUD operations.
- **Utils**: The class uses utility functions from the `utils` module for generating IDs and handling JSON data.
- **Logging**: The class logs important operations using the `logging` module.

### Example Usage
```python
from orchestrator.src.models.model_registry import ModelRegistry

# Initialize the registry
registry = ModelRegistry()

# Register a new model
model_id = await registry.register_model("llama3.1:70b", provider="ollama", size_params="70B", context_window=128000)

# Get a model by ID
model = await registry.get_model(model_id)

# List all models
models = await registry.list_models(provider="ollama", installed_only=True)

# Mark a model as installed
await registry.mark_installed(model_id)

# Add a capability to a model
capability_id = await registry.add_capability(model_id, "math", quality_score=0.9, speed_tier="fast")

# Get the best model for a task
best_model = await registry.get_best_model_for_task("math", installed_only=True)
```

This documentation provides a comprehensive overview of the `ModelRegistry` class and its methods, detailing its purpose, architecture, dependencies, interfaces, database interactions, and key logic.
