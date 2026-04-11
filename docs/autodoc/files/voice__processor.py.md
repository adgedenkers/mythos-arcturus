# voice/processor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 41

---

### File: `voice/processor.py`

#### Purpose
This file contains functions to load a system prompt and process text by sending it to the Ollama API, returning the generated response.

#### Architecture
The file consists of two primary functions:
1. `load_system_prompt(config)`: Loads a system prompt from a YAML file or returns a default prompt.
2. `process_text(text, config, history)`: Processes the input text by sending it to the Ollama API along with any history and a system prompt, and returns the API's response.

#### Patterns
- **No explicit design patterns**: The file uses straightforward procedural code without any specific design patterns like factory, singleton, or observer.

#### Dependencies
- `os`: For file path operations.
- `logging`: For logging errors.
- `requests`: For making HTTP requests to the Ollama API.
- `yaml`: For loading YAML configuration files.

#### Interfaces
- `load_system_prompt(config)`: Exposes a function to load a system prompt from a configuration file.
- `process_text(text, config, history)`: Exposes a function to process text by sending it to the Ollama API and returning the response.

#### Database
- **No direct database interactions**: This file does not interact directly with PostgreSQL, Neo4j, or Redis.

#### Configuration
- Uses configuration parameters from a `config` dictionary:
  - `system_prompt_path`: Path to the system prompt YAML file.
  - `ollama_url`: URL of the Ollama API.
  - `model`: Model name to use with Ollama.
  - `temperature`: Temperature setting for the Ollama API.
  - `max_tokens`: Maximum number of tokens for the Ollama API response.
  - `timeout`: Timeout for the HTTP request to the Ollama API.

#### Key Logic
- **Loading System Prompt**: The `load_system_prompt` function reads a YAML file to load a system prompt. If the file does not exist or fails to load, it returns a default prompt.
- **Processing Text**: The `process_text` function constructs a request to the Ollama API, including the system prompt, user text, and history. It handles exceptions and returns appropriate responses for timeouts and other errors.

#### Integration Points
- **Ollama API**: The `process_text` function sends a POST request to the Ollama API to generate a response based on the input text and system prompt.
- **Configuration**: The functions rely on a `config` dictionary that is passed in, which contains various settings and paths.
- **History**: The `process_text` function can incorporate a history of previous interactions to provide context for the Ollama API.

### Detailed Function Descriptions

#### `load_system_prompt(config)`
- **Purpose**: Loads a system prompt from a specified YAML file or returns a default prompt.
- **Parameters**:
  - `config`: A dictionary containing configuration settings.
- **Logic**:
  - Reads the `system_prompt_path` from the `config` dictionary.
  - Checks if the file exists and loads it using `yaml.safe_load`.
  - Returns the system prompt from the YAML file or a default prompt if the file is not found or fails to load.

#### `process_text(text, config, history=None)`
- **Purpose**: Sends the input text to the Ollama API along with a system prompt and history, and returns the API's response.
- **Parameters**:
  - `text`: The input text to be processed.
  - `config`: A dictionary containing configuration settings.
  - `history`: (Optional) A list of previous interactions to provide context.
- **Logic**:
  - Constructs the URL for the Ollama API using the `ollama_url` from the `config` dictionary.
  - Loads the system prompt using the `load_system_prompt` function.
  - Constructs the list of messages to be sent to the Ollama API, including the system prompt and any history.
  - Sends a POST request to the Ollama API with the constructed messages and configuration settings.
  - Handles exceptions and returns appropriate responses for timeouts and other errors.
