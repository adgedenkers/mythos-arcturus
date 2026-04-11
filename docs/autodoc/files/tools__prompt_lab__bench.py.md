# tools/prompt_lab/bench.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 340

---

### File: tools/prompt_lab/bench.py

#### Purpose
This file provides a command-line interface for testing and comparing prompt configurations against standardized messages using the Mythos system. It supports running tests, comparing profiles, and listing available resources.

#### Architecture
The file is structured around several top-level functions:
- `cmd_run`: Runs a test (single message, single test, or full suite).
- `cmd_compare`: Runs the same test(s) across two profiles and shows the difference.
- `cmd_list`: Lists available resources such as models, profiles, personalities, and test suites.
- `main`: The entry point that parses command-line arguments and dispatches to the appropriate function.

#### Patterns
- **Command Pattern**: The `cmd_run`, `cmd_compare`, and `cmd_list` functions act as commands that perform specific actions based on the input arguments.
- **Factory Pattern**: The `load_profile`, `load_personality_preset`, and `load_test_messages` functions act as factories to load different configurations and test messages.

#### Dependencies
- **Standard Libraries**: `argparse`, `sys`, `os`, `json`, `pathlib`, `datetime`
- **Custom Modules**: `assembler`, `runner`, `scorer`, `store`

#### Interfaces
- **Command-line Interface**: The `main` function parses command-line arguments and calls the appropriate command function (`cmd_run`, `cmd_compare`, `cmd_list`).
- **Functions**: `cmd_run`, `cmd_compare`, `cmd_list` are exposed to handle different command-line operations.

#### Database
- **PostgreSQL Tables**: `suite`, `pathlib`, `datetime`, `assembler`, `runner`, `scorer`, `store`, `a`
  - These tables are referenced but not directly interacted with in the provided code snippet. The interactions are likely through the imported modules (`assembler`, `runner`, `scorer`, `store`).

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: YAML files in `profiles`, `personalities`, and `messages` directories are loaded for configurations and test messages.

#### Key Logic
- **Test Execution**:
  - Loads a profile and optional personality preset.
  - Assembles a system prompt based on the profile and personality.
  - Runs tests with the assembled prompt and user messages.
  - Scores and formats the responses.
  - Optionally saves the results to a file.
- **Comparison**:
  - Loads two profiles and runs the same tests for both.
  - Displays the differences in responses and scores.
- **Listing**:
  - Lists available models, profiles, personalities, test suites, and saved runs.

#### Integration Points
- **assembler**: Loads profiles and personality presets, assembles system prompts.
- **runner**: Runs prompts with specified models and user messages.
- **scorer**: Scores the responses and formats the scorecard.
- **store**: Saves and lists run results.

### Detailed Breakdown

#### `cmd_run`
- **Purpose**: Runs a test (single message, single test, or full suite).
- **Logic**:
  - Loads the specified profile and optional personality preset.
  - Determines the test messages based on command-line arguments.
  - Assembles the system prompt.
  - Runs the tests and scores the responses.
  - Optionally saves the results to a file.

#### `cmd_compare`
- **Purpose**: Runs the same test(s) across two profiles and shows the difference.
- **Logic**:
  - Loads two profiles and optional personality preset.
  - Determines the test messages based on command-line arguments.
  - Runs the tests for both profiles and displays the differences in responses and scores.

#### `cmd_list`
- **Purpose**: Lists available resources.
- **Logic**:
  - Lists available models, profiles, personalities, test suites, and saved runs.
  - Reads YAML files for descriptions and prints them in a formatted manner.

#### `main`
- **Purpose**: Entry point that parses command-line arguments and dispatches to the appropriate function.
- **Logic**:
  - Uses `argparse` to parse command-line arguments.
  - Calls `cmd_run`, `cmd_compare`, or `cmd_list` based on the arguments.

### Example Usage
```sh
bench.py -m "hey what's up"  # Quick test with default profile
bench.py --profile naked -m "hey what's up"  # Test with naked model
bench.py --profile identity_only --test greeting  # Run a specific test
bench.py --profile full_stack --suite calibration  # Run a full suite
bench.py --profile full_stack --personality tars_75 --suite calibration  # Run with personality preset
bench.py --profile full_stack --dry-run  # Show prompt without sending
bench.py --profile full_stack --model qwen2:72b --suite calibration  # Specify model
bench.py --compare naked identity_only --test greeting  # Compare two profiles
bench.py --list-models  # List available models
bench.py --list-profiles  # List available profiles
bench.py --list-personalities  # List available personalities
bench.py --list-suites  # List available test suites
bench.py --results  # Show saved runs
bench.py --diff run_a.json run_b.json  # Compare two runs
```
