# tools/prompt_lab/lib/runner.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 104

---

### File: tools/prompt_lab/lib/runner.py

#### Purpose
This file contains utility functions to interact with the Ollama AI model server, including listing available models and running prompts against a specified model.

#### Architecture
The file consists of three main functions:
1. `get_client`: Returns an instance of the Ollama client.
2. `list_models`: Retrieves and returns the names of all available Ollama models.
3. `run_prompt`: Sends a prompt to the Ollama model and captures the full response, including timing and token counts.

#### Patterns
- **Singleton Pattern**: The `get_client` function ensures that the Ollama client is instantiated only once and reused, mimicking a singleton pattern.

#### Dependencies
- `os`: For environment variable access.
- `time`: For timing the execution.
- `json`: For JSON operations (though not used directly in the provided code).
- `logging`: For logging errors and information.
- `datetime`: For timestamp generation.
- `typing`: For type hints.
- `ollama`: For interacting with the Ollama client.

#### Interfaces
- `get_client`: Returns an instance of the Ollama client.
- `list_models`: Returns a list of model names.
- `run_prompt`: Takes system prompt, user message, model name, temperature, number of predictions, and conversation history, and returns a dictionary with the response and metadata.

#### Database
- The file references the following PostgreSQL tables:
  - `datetime`: Used for timestamp generation.
  - `typing`: Used for type hints.
  - `ollama`: Not directly used in the provided code but implied in the context of the Ollama client.

#### Configuration
- Uses the environment variable `OLLAMA_HOST` to configure the Ollama server host.

#### Key Logic
- **`get_client`**: Instantiates and returns an Ollama client.
- **`list_models`**: Fetches and returns the names of all available Ollama models.
- **`run_prompt`**: 
  - Constructs a list of messages including system prompts and user messages.
  - Sends the constructed messages to the Ollama model.
  - Captures and returns the response along with metadata such as timing, token counts, and system/user prompts.

#### Integration Points
- **Ollama Client**: The file integrates with the Ollama client to send prompts and retrieve responses.
- **Logging**: Uses Python's logging module to log errors and information.
- **Environment Variables**: Retrieves the Ollama host from the environment variable `OLLAMA_HOST`.

### Detailed Documentation

#### `get_client`
- **Purpose**: Returns an instance of the Ollama client.
- **Implementation**: Uses the `OLLAMA_HOST` environment variable to configure the client.

#### `list_models`
- **Purpose**: Retrieves and returns the names of all available Ollama models.
- **Implementation**: 
  - Uses the `get_client` function to get an Ollama client instance.
  - Calls the `list` method on the client to get the list of models.
  - Extracts and returns the names of the models.

#### `run_prompt`
- **Purpose**: Sends a prompt to the Ollama model and captures the full response.
- **Implementation**: 
  - Constructs a list of messages including system prompts and user messages.
  - Sends the constructed messages to the Ollama model using the `chat` method.
  - Captures the response and metadata such as timing, token counts, and system/user prompts.
  - Returns a dictionary containing the response and metadata.

### Example Usage
```python
from tools.prompt_lab.lib.runner import run_prompt, list_models

# List available models
models = list_models()
print(models)

# Run a prompt
response = run_prompt(
    system_prompt="You are a helpful assistant.",
    user_message="What is the capital of France?",
    model="qwen2.5:32b",
    temperature=0.7,
    num_predict=4096
)
print(response)
```

### Conclusion
This file provides essential functionality for interacting with the Ollama AI model server, enabling the listing of available models and the execution of prompts with detailed response capture. It integrates seamlessly with the Ollama client and logging mechanisms, ensuring robust and reliable operation within the Mythos system.
