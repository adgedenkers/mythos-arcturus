# tools/prompt_lab/tweak.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 227

---

### File: tools/prompt_lab/tweak.py

#### Purpose
This file provides a command-line tool for managing and adjusting personality slider settings in both production and preset configurations. It allows users to show, set, create, reset, and list personality presets.

#### Architecture
The file is structured around several top-level functions that handle specific commands:
- `load_yaml`: Loads YAML data from a file.
- `save_yaml`: Saves YAML data to a file.
- `render_bar`: Renders a bar chart for visualizing slider values.
- `show_sliders`: Displays the current slider settings with a bar chart.
- `cmd_show`: Handles the `show` command to display slider settings.
- `cmd_set`: Handles the `set` command to modify slider settings.
- `cmd_create`: Handles the `create` command to create new presets.
- `cmd_reset`: Handles the `reset` command to reset production settings to defaults.
- `cmd_list`: Handles the `list` command to list available presets.
- `main`: The main entry point that parses command-line arguments and dispatches to the appropriate command handler.

#### Patterns
- **Command Pattern**: The `main` function dispatches to different command handlers (`cmd_show`, `cmd_set`, etc.) based on the command-line arguments.
- **Factory Method**: The `argparse.ArgumentParser` is used to create subparsers for different commands.

#### Dependencies
- `argparse`: For parsing command-line arguments.
- `sys`: For system-specific parameters and functions.
- `copy`: For deep copying data structures.
- `yaml`: For reading and writing YAML files.
- `pathlib`: For handling file paths.

#### Interfaces
- The file exposes a command-line interface with the following commands:
  - `show`: Display current slider settings.
  - `set`: Modify slider settings.
  - `create`: Create a new preset.
  - `reset`: Reset production settings to defaults.
  - `list`: List available presets.

#### Database
- **PostgreSQL**: References to `default` and `pathlib` are noted, but these are likely placeholders or misinterpretations. The file primarily deals with file I/O and does not interact with a database directly.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: The file reads and writes to YAML files located in `/opt/mythos/prompts/personality.yaml` and `tools/prompt_lab/personalities/`.

#### Key Logic
- **Slider Management**: The file manages personality sliders, ensuring values are within the range of 0 to 100.
- **Data Persistence**: Uses YAML files to store and retrieve slider settings.
- **Command Handling**: Each command (`show`, `set`, `create`, `reset`, `list`) has a dedicated function that performs the required action.

#### Integration Points
- **File System**: The tool interacts with the file system to read and write YAML files.
- **Command Line**: The tool is invoked from the command line and integrates with the Mythos system by modifying configuration files used by other parts of the system.

### Detailed Analysis

#### `load_yaml(path)`
- **Purpose**: Loads YAML data from a file.
- **Logic**: Checks if the file exists, reads it, and returns the parsed YAML data.

#### `save_yaml(path, data)`
- **Purpose**: Saves YAML data to a file.
- **Logic**: Writes the provided data to the specified file in YAML format.

#### `render_bar(value, width=20)`
- **Purpose**: Renders a bar chart for visualizing slider values.
- **Logic**: Calculates the filled portion of the bar based on the value and width, and returns a string representation of the bar.

#### `show_sliders(sliders, title="")`
- **Purpose**: Displays the current slider settings with a bar chart.
- **Logic**: Iterates over valid sliders, renders the bar chart for each, and prints the result.

#### `cmd_show(args)`
- **Purpose**: Handles the `show` command to display slider settings.
- **Logic**: Depending on the target, either shows the production settings or a specific preset.

#### `cmd_set(args)`
- **Purpose**: Handles the `set` command to modify slider settings.
- **Logic**: Parses the slider-value pairs, validates the values, and updates the corresponding YAML file.

#### `cmd_create(args)`
- **Purpose**: Handles the `create` command to create a new preset.
- **Logic**: Copies a base preset, applies any specified slider changes, and saves the new preset.

#### `cmd_reset(args)`
- **Purpose**: Handles the `reset` command to reset production settings to defaults.
- **Logic**: Resets the production settings to predefined default values and saves them.

#### `cmd_list(args)`
- **Purpose**: Handles the `list` command to list available presets.
- **Logic**: Iterates over the preset files and prints their names and descriptions.

#### `main()`
- **Purpose**: The main entry point that parses command-line arguments and dispatches to the appropriate command handler.
- **Logic**: Uses `argparse` to parse the command-line arguments and calls the corresponding command function based on the command specified.
