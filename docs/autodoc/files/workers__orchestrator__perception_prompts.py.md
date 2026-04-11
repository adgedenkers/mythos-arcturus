# workers/orchestrator/perception_prompts.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 22

---

### Documentation for `workers/orchestrator/perception_prompts.py`

#### Purpose
This file is responsible for loading the system prompt for the perception subsystem. Currently, it extracts the prompt from a test suite file, but it is intended to eventually load from a YAML configuration file.

#### Architecture
The file contains a single top-level function `_load_from_test_suite` which reads a specific file and extracts a string between triple quotes. The extracted string is then assigned to the global variable `PERCEPTION_SYSTEM_PROMPT`.

#### Patterns
- **Singleton Pattern**: The `PERCEPTION_SYSTEM_PROMPT` variable acts as a singleton, holding the system prompt throughout the execution of the application.

#### Dependencies
- **Imports**: `os` (for file path operations)
- **External Files**: `/opt/mythos/workers/tests/perception_test_suite.py` (for reading the system prompt)

#### Interfaces
- **Exposed Variables**: `PERCEPTION_SYSTEM_PROMPT` (the system prompt string)

#### Database
- **References**: 
  - `perception_template` (PostgreSQL table)
  - `the` (PostgreSQL table)
  - `template` (PostgreSQL table)
  - `test` (PostgreSQL table)

  Note: Although these tables are referenced in the DB references, the current implementation does not interact with these tables. The references might be placeholders for future implementation.

#### Configuration
- **Environment Variables**: None
- **Config Files**: None (currently using hard-coded path)

#### Key Logic
- **Function `_load_from_test_suite`**:
  - Reads the content of `/opt/mythos/workers/tests/perception_test_suite.py`.
  - Extracts the string between `SYSTEM_PROMPT = """` and the next `"""`.
  - Returns the extracted string or a default value if the extraction fails.

#### Integration Points
- **Perception Subsystem**: The `PERCEPTION_SYSTEM_PROMPT` is used by the perception subsystem to initialize its processing logic.
- **Orchestrator**: The orchestrator module will use `PERCEPTION_SYSTEM_PROMPT` to configure the perception subsystem.

### Detailed Analysis

#### `_load_from_test_suite` Function
- **Purpose**: Temporarily extract the system prompt from the test suite file.
- **Implementation**:
  - Checks if the file `/opt/mythos/workers/tests/perception_test_suite.py` exists.
  - Reads the file content.
  - Finds the substring `SYSTEM_PROMPT = """` and extracts the content between the triple quotes.
  - Returns the extracted string or a default value if the extraction fails.

#### Global Variable `PERCEPTION_SYSTEM_PROMPT`
- **Purpose**: Holds the system prompt used by the perception subsystem.
- **Initialization**: Set by calling `_load_from_test_suite`.

### Future Considerations
- **YAML Loader**: The file mentions a TODO to build a YAML loader to extract the system prompt from YAML files. This will likely involve adding a YAML parsing library and modifying the `_load_from_test_suite` function to read from YAML files instead of the test suite.
- **Database Integration**: The current implementation does not interact with the PostgreSQL tables listed in the DB references. Future work might involve integrating these tables to store and retrieve system prompts dynamically.

This file serves as a temporary solution until a more robust system prompt loading mechanism is implemented, likely involving YAML files and possibly database integration.
