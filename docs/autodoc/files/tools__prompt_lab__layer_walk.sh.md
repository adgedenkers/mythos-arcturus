# tools/prompt_lab/layer_walk.sh

**Language:** bash
**Stream:** SYS
**Module:** Tools
**Lines:** 137

---

### Documentation for `tools/prompt_lab/layer_walk.sh`

#### Purpose
This script, `layer_walk.sh`, is designed to incrementally add layers to a prompt and observe how the response changes across different profiles. It tests the same prompt(s) across various profiles from "naked" to "full_stack" and can optionally compare the results for two different models side by side.

#### Architecture
The script is structured as follows:
1. **Initialization**: Sets up default values and parses command-line arguments.
2. **Execution Loop**: Iterates over specified models and profiles, executing the `bench.py` script for each combination.
3. **Summary Generation**: Collects and summarizes the results in a tabular format.

#### Patterns
- **Command-Line Argument Parsing**: Uses a `while` loop to parse and set variables based on provided arguments.
- **Conditional Execution**: Uses conditional checks to handle optional arguments and default values.

#### Dependencies
- **Bash Environment**: Relies on the Bash shell for execution.
- **Python Script**: Calls `/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py` to execute benchmark tests.
- **JSON Parsing**: Uses Python to parse JSON files for summary generation.

#### Interfaces
- **Command-Line Arguments**:
  - `--test`: Specifies a specific test to run.
  - `--suite`: Specifies the test suite.
  - `--mode`: Specifies the mode.
  - `--personality`: Specifies the personality.
  - `--models`: Specifies the models to test (comma-separated).

#### Database
- **No Direct Database Interaction**: The script does not directly interact with any database. However, it relies on the `bench.py` script, which may interact with databases to retrieve or store test results.

#### Configuration
- **Environment Variables**: No environment variables are used directly in the script.
- **Configuration Files**: No configuration files are used directly in the script. The script relies on the `bench.py` script, which may use configuration files.

#### Key Logic
1. **Argument Parsing**: Sets up default values and parses command-line arguments to configure the test parameters.
2. **Execution Loop**: Iterates over specified models and profiles, executing the `bench.py` script for each combination and saving the results.
3. **Summary Generation**: Collects the results from the JSON files and generates a summary table showing the average scores, word counts, and times for each profile.

#### Integration Points
- **`bench.py`**: The script calls this Python script to execute the benchmark tests. The `bench.py` script is responsible for running the actual tests and saving the results to JSON files.
- **Results Directory**: The script saves the results in the `/opt/mythos/tools/prompt_lab/results` directory, which can be accessed by other scripts or tools for further analysis.

### Detailed Breakdown

#### Initialization
- Sets up the `BENCH` variable to point to the `bench.py` script.
- Defines the `PROFILES` array with different profile names.
- Sets default values for `TEST`, `SUITE`, `MODE`, `PERSONALITY`, and `MODELS`.

#### Argument Parsing
- Uses a `while` loop to parse command-line arguments and set corresponding variables.

#### Execution Loop
- Iterates over each model and profile, calling `bench.py` with the appropriate parameters.
- Saves the latest result file path in the `RUN_MAP` associative array.

#### Summary Generation
- Iterates over each model and profile to generate a summary table.
- Uses Python to parse the JSON result files and compute average scores, word counts, and times.

### Example Usage
```bash
./layer_walk.sh --test ego_inflation --suite sovereignty --mode sovereign
./layer_walk.sh --test soul_code_synthesis --suite sovereignty --mode sovereign --models "qwen2.5:32b iris-thinking-v2"
./layer_walk.sh --suite sovereignty --mode sovereign
```

This script provides a systematic way to evaluate how different layers of a prompt affect the responses from various models, making it a valuable tool for testing and refining prompt configurations in the Mythos system.
