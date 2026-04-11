# neuro/perception/engine.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 360

---

### File: `neuro/perception/engine.py`

#### Purpose
The `PerceptionEngine` class in this file is responsible for running Layer 1 perception across all active grid nodes for a given message exchange. It processes user messages and assistant responses, extracts knowledge, and writes the results to a manifest and knowledge store.

#### Architecture
- **Class**: `PerceptionEngine`
  - **Methods**:
    - `__init__`: Initializes the `PerceptionEngine` with manifest, registry, and knowledge writers.
    - `process`: Main method to run perception on all nodes for a given exchange.
    - `_run_node_perception`: Runs perception for a single node.
    - `_parse_extractions`: Parses the raw text response from the LLM into extraction dictionaries.
    - `_validate_extractions`: Validates and cleans the extraction dictionaries.
    - `close`: Cleans up resources.

#### Patterns
- **Singleton**: The `PerceptionEngine` class can be considered a singleton pattern as it is instantiated once and reused.
- **Factory**: The `get_perception_prompt`, `get_all_active_nodes`, and `get_node_domain` functions act as factories to provide necessary data and configurations.

#### Dependencies
- **Imports**: `os`, `json`, `re`, `logging`, `hashlib`, `time`, `requests`, `sys`, `dotenv`, `grid_manifest`, `perception`.
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_MODEL`.

#### Interfaces
- **Public Methods**:
  - `process`: Exposes the main functionality to run perception on all nodes.
  - `close`: Allows for resource cleanup.

#### Database
- **PostgreSQL Tables**:
  - `the`, `typing`, `dotenv`, `grid_manifest`, `perception`, `extraction`, `response`.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_MODEL`.
- **Configuration Files**: `.env` file loaded using `dotenv`.

#### Key Logic
- **Processing Workflow**:
  1. **Initialization**: Initializes manifest, registry, and knowledge writers.
  2. **Node Perception**:
     - Fetches active nodes and their versions.
     - Determines if a node should be activated based on grid scores and activation threshold.
     - Runs perception for each node using the Ollama API.
     - Parses and validates extractions from the LLM response.
     - Writes manifest and knowledge entries.
  3. **Error Handling**: Logs errors and handles timeouts gracefully.

- **Perception Execution**:
  - Uses the Ollama API to generate responses.
  - Parses JSON responses and handles different formats (clean JSON, JSON-in-thinking-tags).
  - Validates and writes extractions to the knowledge store.

#### Integration Points
- **Grid Manifest**: Uses `ManifestWriter` and `VersionRegistry` to record perception activations and skips.
- **Knowledge Writer**: Uses `KnowledgeWriter` to write extractions to the knowledge store.
- **Ollama API**: Integrates with the Ollama API to generate perception prompts.
- **Logging**: Uses `logging` to log processing details and errors.

### Summary
The `PerceptionEngine` class in `neuro/perception/engine.py` is a critical component of the Mythos system, responsible for running Layer 1 perception across all grid nodes. It integrates with various subsystems, including the Ollama API, PostgreSQL databases, and logging, to process user messages, extract knowledge, and write results to the knowledge store.
