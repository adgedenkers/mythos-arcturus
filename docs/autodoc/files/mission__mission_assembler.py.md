# mission/mission_assembler.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 116

---

### File: mission/mission_assembler.py

#### Purpose
The `mission_assembler.py` script assembles a mission configuration from modular parts (metadata, context, phase ordering, and prompt templates) into a single runnable YAML file. It also provides options to validate, dry-run, or execute the assembled mission.

#### Architecture
The script consists of several functions:
- `assemble_mission(mission_dir: str) -> dict`: Reads mission configuration and prompt files from a specified directory and assembles them into a single mission configuration.
- `write_assembled(config: dict, output_path: str)`: Writes the assembled mission configuration to a specified output path.
- `main()`: Parses command-line arguments and orchestrates the mission assembly process, including optional validation, dry-run, or execution.
- `str_representer(dumper, data)`: Custom YAML representer for handling multi-line strings.

#### Patterns
- **Command Line Interface (CLI)**: The script uses `argparse` to handle command-line arguments.
- **Custom Representer**: A custom YAML representer (`str_representer`) is used to handle multi-line strings.

#### Dependencies
- `argparse`: For parsing command-line arguments.
- `json`: For JSON handling (though not used in this script).
- `os`: For directory operations.
- `subprocess`: For running external commands.
- `sys`: For system-specific parameters and functions.
- `yaml`: For YAML parsing and writing.
- `pathlib`: For path operations.

#### Interfaces
- **Functions**:
  - `assemble_mission(mission_dir: str) -> dict`: Assembles mission configuration from a directory.
  - `write_assembled(config: dict, output_path: str)`: Writes assembled mission configuration to a file.
  - `main()`: Main function to parse arguments and orchestrate mission assembly.
  - `str_representer(dumper, data)`: Custom YAML representer for multi-line strings.

#### Database
- The script does not directly interact with any databases. The provided DB references appear to be a misinterpretation of the `pathlib` import.

#### Configuration
- The script uses command-line arguments for configuration:
  - `mission_dir`: Path to the mission directory.
  - `--output`: Output path for the assembled mission YAML.
  - `--run`: Assemble and immediately run the mission.
  - `--dry-run`: Assemble and dry-run the mission.
  - `--validate`: Assemble and validate the mission.

#### Key Logic
- **Mission Assembly**:
  - Reads `mission.yaml` from the mission directory.
  - Loads prompt templates from the `prompts/` subdirectory and injects them into the mission configuration.
  - Removes `prompt_file` and `retry_prompt_file` keys from the configuration.
- **Writing Assembled YAML**:
  - Uses a custom YAML representer to handle multi-line strings.
  - Writes the assembled mission configuration to the specified output path.
- **Execution Options**:
  - Validates, dry-runs, or runs the assembled mission using the `mythos-mission` command.

#### Integration Points
- **Mission Directory Structure**:
  - The script integrates with the mission directory structure, which includes `mission.yaml` and `prompts/` subdirectory.
- **External Commands**:
  - Uses `subprocess.run` to execute `mythos-mission` commands for validation, dry-run, and execution.
- **File System**:
  - Reads files from the mission directory and writes the assembled mission to the specified output path.

### Summary
The `mission_assembler.py` script is a command-line tool that assembles a mission configuration from modular parts into a single runnable YAML file. It provides options to validate, dry-run, or execute the assembled mission. The script handles mission configuration and prompt files, and uses a custom YAML representer for multi-line strings. It integrates with the mission directory structure and external `mythos-mission` commands for further processing.
