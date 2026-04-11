# astrology/tools/seraphe_lunar.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 63

---

### File: `astrology/tools/seraphe_lunar.py`

#### Purpose
This Bash script serves as a command-line interface (CLI) wrapper for the Seraphe lunar calendar generator. It provides various options to generate lunar calendars, list generated calendars, and check the status of the calendar generation worker service.

#### Architecture
The script is structured as a series of conditional checks and command executions. It handles special flags (`--list`, `--status`, `--help`) and passes all other arguments to a Python script (`seraphe_lunar_generator.py`) for further processing.

#### Patterns
- **Command Pattern**: The script acts as a command dispatcher, handling different commands and options.
- **Facade Pattern**: It provides a simplified interface to the underlying Python generator and system services.

#### Dependencies
- **System Commands**: `ls`, `systemctl`, `tail`
- **Python Script**: `/opt/mythos/astrology/seraphe_lunar_generator.py`
- **Virtual Environment Python**: `/opt/mythos/.venv/bin/python3`

#### Interfaces
- **CLI Interface**: Exposes a CLI with options for generating lunar calendars, listing generated calendars, and checking the status of the worker service.
- **Command Line Arguments**: Accepts arguments like `--year`, `--month`, `--skip-ollama`, `--out`, `--list`, `--status`.

#### Database
- **No Direct Database Interaction**: The script does not directly interact with any database. However, the underlying Python script (`seraphe_lunar_generator.py`) may interact with databases for generating lunar calendars.

#### Configuration
- **Environment Variables**: None directly used in the script.
- **Paths and Files**: 
  - `GENERATOR`: Path to the Python generator script.
  - `VENV_PYTHON`: Path to the Python interpreter in the virtual environment.
  - `OUTPUT_DIR`: Directory where generated calendars are stored.

#### Key Logic
- **Handling Special Flags**:
  - `--list`: Lists all generated lunar calendars in the `OUTPUT_DIR`.
  - `--status`: Shows the status of the `mythos-worker-lunar` service and recent logs.
  - `--help`: Displays usage information and examples.
- **Passing Arguments**: Passes all other arguments to the Python generator script for calendar generation.

#### Integration Points
- **Python Generator Script**: The script invokes `/opt/mythos/astrology/seraphe_lunar_generator.py` to generate lunar calendars.
- **System Services**: Interacts with the `mythos-worker-lunar` service to check its status.
- **File System**: Reads from and writes to the `OUTPUT_DIR` for listing and generating calendars.

### Summary
The `seraphe_lunar.py` script serves as a CLI wrapper for generating lunar calendars using the Seraphe system. It handles various command-line options, including listing generated calendars, checking the status of the worker service, and providing help information. The script passes relevant arguments to a Python generator script for actual calendar generation and interacts with system services and file paths for additional functionality.
