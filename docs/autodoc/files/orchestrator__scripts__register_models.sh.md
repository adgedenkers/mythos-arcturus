# orchestrator/scripts/register_models.sh

**Language:** bash
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 42

---

### File: `orchestrator/scripts/register_models.sh`

#### Purpose
This script registers installed Ollama models in the Mythos database by activating a virtual environment and running a Python script to sync the models.

#### Architecture
The script consists of a bash script that sources a virtual environment and runs an embedded Python script. The Python script imports necessary modules and uses an `asyncio` loop to call methods from the `ModelManager` class to sync and list models.

#### Patterns
- **Embedded Script**: The Python script is embedded within the bash script using a here document (`<< 'EOPY'`).

#### Dependencies
- **Bash**: For executing the script.
- **Python**: For running the embedded Python script.
- **Virtual Environment**: Activated from `${MYTHOS_ROOT}/.venv/bin/activate`.
- **Python Modules**: `sys`, `os`, `asyncio`, and `ModelManager` from `models.model_manager`.

#### Interfaces
- **Bash Script**: Exposes no direct interfaces but relies on the environment and virtual environment setup.
- **Python Script**: Uses `ModelManager` class methods `sync_models` and `get_available_models`.

#### Database
- **Writes**: The `sync_models` method likely writes to a database table or Neo4j label to register and update models.
- **Reads**: The `get_available_models` method likely reads from the same table or label to list the models.

#### Configuration
- **Environment Variables**: Uses `MYTHOS_ROOT` to set the root directory of the Mythos system.
- **Virtual Environment**: Uses `${MYTHOS_ROOT}/.venv/bin/activate` to activate the virtual environment.

#### Key Logic
1. **Sync Models**: The `sync_models` method in `ModelManager` is called to register and update models in the database.
2. **List Models**: The `get_available_models` method in `ModelManager` is called to list the installed models.

#### Integration Points
- **ModelManager**: The script integrates with the `ModelManager` class from the `models.model_manager` module to interact with the Ollama models and the database.
- **Database**: The `ModelManager` class interacts with the database to register and update models.
- **Ollama Models**: The script assumes that Ollama models are installed and available for synchronization.

### Detailed Breakdown

1. **Bash Script**:
   - **Purpose**: To activate the virtual environment and run the embedded Python script.
   - **Steps**:
     1. Set `MYTHOS_ROOT` to `/opt/mythos`.
     2. Source the virtual environment from `${MYTHOS_ROOT}/.venv/bin/activate`.
     3. Change directory to `${MYTHOS_ROOT}/orchestrator`.
     4. Run the embedded Python script.

2. **Embedded Python Script**:
   - **Purpose**: To sync installed Ollama models with the database and list the available models.
   - **Steps**:
     1. Set the path to include the `orchestrator/src` directory.
     2. Import necessary modules (`asyncio` and `ModelManager`).
     3. Define an `async` function `main` that:
        - Creates an instance of `ModelManager`.
        - Calls `sync_models` to register and update models.
        - Prints the results of the sync operation.
        - Calls `get_available_models` to list the installed models.
        - Prints the list of installed models.
     4. Run the `main` function using `asyncio.run(main())`.

### Example Output
```
Syncing installed Ollama models...
✓ Registered: 3 new models
✓ Updated: 2 existing models
✓ Total: 5 models synced

Installed models:
  • model1 (100M parameters)
  • model2 (200M parameters)
  • model3 (300M parameters)
  • model4 (400M parameters)
  • model5 (500M parameters)
```

This script ensures that the Ollama models are properly registered and updated in the Mythos database, providing a clear and concise output of the sync operation and the list of installed models.
