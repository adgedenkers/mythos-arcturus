# tools/iris_calibrate.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 579

---

### Documentation for `tools/iris_calibrate.py`

#### Purpose
This Python script, `iris_calibrate.py`, is a tool for calibrating the system prompt of the Iris AI model across different layers of complexity. It tests the model's behavior at each layer, allowing for incremental review and tweaking.

#### Architecture
The script is organized into several functions that handle different aspects of the calibration process:
- **Data Handling**: Functions like `load_modelfile_prompt` and `build_prompt_for_layer` manage the extraction and construction of prompts.
- **Testing**: Functions like `run_single_test` and `print_result` handle the execution and reporting of tests.
- **User Interaction**: Functions like `interactive_mode`, `compare_layers`, and `run_all_layers` provide various modes of interaction for running tests.

#### Patterns
- **Singleton**: The `Client` from the `ollama` module is instantiated once and reused.
- **Factory**: The `build_prompt_for_layer` function acts as a factory for constructing prompts based on the layer number.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `time`, `copy`, `argparse`, `tempfile`, `subprocess`
- **External Libraries**: `datetime` from `datetime`, `Path` from `pathlib`, `Client` from `ollama`

#### Interfaces
- **Command-line Interface**: The `main` function parses command-line arguments to determine the mode of operation (interactive, specific layer, comparison, etc.).
- **Functions**: Exposes functions like `interactive_mode`, `compare_layers`, `run_all_layers` for different testing scenarios.

#### Database
- **PostgreSQL**: The script does not directly interact with PostgreSQL tables. The references to `the`, `datetime`, `pathlib`, `ollama`, `what`, `a`, and `print` are not actual database tables but rather parts of the code or standard library imports.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST` is read from the environment to configure the Ollama client.
- **Constants**: `RESULTS_DIR` is set to `/opt/mythos/orchestrator/benchmark/calibration` for storing results.

#### Key Logic
- **Prompt Construction**: The `build_prompt_for_layer` function accumulates prompts from the `LAYERS` dictionary up to the specified layer.
- **Testing**: The `run_single_test` function sends a constructed prompt and user message to the Ollama model and captures the response.
- **Quality Checks**: The script includes checks for bullet points, tables, and corporate language in the model's responses.

#### Integration Points
- **Ollama Client**: The script interacts with the Ollama model through the `Client` from the `ollama` library.
- **File System**: Results are saved to `/opt/mythos/orchestrator/benchmark/calibration`.
- **Command-line Arguments**: The script accepts various command-line arguments to control the testing process.

### Detailed Function Descriptions

1. **`load_modelfile_prompt`**
   - **Purpose**: Extracts the SYSTEM block from the deployed Modelfile.
   - **Logic**: Reads the Modelfile, finds the SYSTEM block, and returns its content.

2. **`build_prompt_for_layer`**
   - **Purpose**: Constructs the cumulative system prompt for a given layer.
   - **Logic**: Iterates through layers up to the specified layer and concatenates their prompts.

3. **`run_single_test`**
   - **Purpose**: Runs a single Ollama test with a given model, system prompt, and user message.
   - **Logic**: Sends the constructed prompt and message to the Ollama model and captures the response.

4. **`format_checks`**
   - **Purpose**: Formats quality checks as a compact status line.
   - **Logic**: Evaluates the response for specific patterns and formats the results.

5. **`print_result`**
   - **Purpose**: Prints a single test result.
   - **Logic**: Outputs the layer number, layer name, and result message.

6. **`save_results`**
   - **Purpose**: Saves test results to a JSON file.
   - **Logic**: Writes the results to a JSON file in the `RESULTS_DIR`.

7. **`interactive_mode`**
   - **Purpose**: Steps through layers one at a time, pausing for review.
   - **Logic**: Iterates through layers, runs tests, and waits for user input before proceeding.

8. **`compare_layers`**
   - **Purpose**: Runs specific layers side-by-side for comparison.
   - **Logic**: Runs tests for specified layers and prints results.

9. **`run_all_layers`**
   - **Purpose**: Runs all layers without pausing.
   - **Logic**: Iterates through all layers and runs tests.

10. **`list_messages`**
    - **Purpose**: Lists available test messages.
    - **Logic**: Outputs the keys and values of `DEFAULT_MESSAGES`.

11. **`main`**
    - **Purpose**: Entry point for the script, parses command-line arguments and calls appropriate functions.
    - **Logic**: Uses `argparse` to handle command-line arguments and delegates to other functions based on the arguments.

This documentation provides a comprehensive overview of the `iris_calibrate.py` script, detailing its purpose, architecture, dependencies, and key logic.
