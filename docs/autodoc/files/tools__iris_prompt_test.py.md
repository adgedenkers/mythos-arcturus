# tools/iris_prompt_test.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 287

---

### File: tools/iris_prompt_test.py

#### Purpose
This file is a test harness for evaluating combinations of system prompts and models using the Ollama API. It tests how different prompts and models respond to a specific user message and memory context, saving the results to a text file and copying them to the clipboard.

#### Architecture
The file consists of several top-level functions and constants:
- `get_pulled_models()`: Fetches the list of available models from the Ollama API.
- `header(text)`: Adds a header to the output lines.
- `subheader(text)`: Adds a subheader to the output lines.

The main logic is structured around testing different combinations of system prompts and models, running tests, and summarizing the results.

#### Patterns
- **Singleton**: The Ollama client is instantiated once and reused throughout the script.
- **Factory**: The `get_pulled_models()` function acts as a factory method to fetch and return the list of available models.

#### Dependencies
- `os`: Used for environment variable access and file path handling.
- `time`: Used for timing the API calls.
- `json`: Not used in the provided code but might be used for JSON handling.
- `datetime`: Used for timestamping the test results.
- `ollama.Client`: Used to interact with the Ollama API.

#### Interfaces
- **Functions**: `get_pulled_models()`, `header()`, `subheader()`
- **Constants**: `OLLAMA_HOST`, `ALL_MODELS`, `MEMORY_CONTEXT`, `USER_MESSAGE`, `PROMPTS`

#### Database
The file references several PostgreSQL tables (`datetime`, `ollama`, `earth`, `reality`, `what`, `your`, `being`, `the`), but these references are not used in the provided code. They might be placeholders or part of a larger context not shown here.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST` is read from the environment to configure the Ollama API host.

#### Key Logic
1. **Fetching Models**: `get_pulled_models()` fetches the list of available models from the Ollama API.
2. **Testing Combinations**: The script iterates over predefined system prompts and models, sending a user message and memory context to the Ollama API, and records the response.
3. **Response Analysis**: The script checks the response for specific patterns (bullets, corporate phrases, closing questions) and records the time taken, word count, and other details.
4. **Output Formatting**: Results are formatted into a summary table and saved to a text file.

#### Integration Points
- **Ollama API**: The script interacts with the Ollama API to fetch models and send chat requests.
- **File System**: Results are saved to a text file (`~/iris_test_results.txt`).
- **Clipboard**: The results file is copied to the clipboard for easy sharing.

### Detailed Breakdown

#### `get_pulled_models()`
- **Purpose**: Fetches the list of available models from the Ollama API.
- **Logic**: Uses the `client.list()` method to get the list of models and processes the response to extract model names.

#### `header(text)` and `subheader(text)`
- **Purpose**: Adds formatted headers and subheaders to the output lines.
- **Logic**: Appends formatted strings to the `output_lines` list.

#### Main Logic
- **Initialization**: Sets up the Ollama client with the host from the environment variable.
- **Model and Prompt Setup**: Defines the list of models to test and the system prompts.
- **Test Execution**: Iterates over each prompt and model combination, sends the user message and memory context to the Ollama API, and records the response.
- **Response Analysis**: Checks the response for specific patterns and records the time taken, word count, and other details.
- **Summary and Output**: Formats the results into a summary table and saves them to a text file, which is then copied to the clipboard.

This file serves as a comprehensive test harness for evaluating the behavior of different system prompts and models in the Mythos system, ensuring that the responses meet the desired criteria.
