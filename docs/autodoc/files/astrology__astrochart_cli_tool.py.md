# astrology/astrochart_cli_tool.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 359

---

### File: `astrology/astrochart_cli_tool.py`

#### Purpose
This file provides a command-line interface (CLI) tool to generate natal astrology charts from birth information. It can load input data either from a JSON/YAML file or from CLI flags, generate the chart data, perform a geometry audit, and save the output to JSON files.

#### Architecture
The file consists of three main functions:
1. **`load_input_data(file_path, args)`**: Loads input data either from a JSON/YAML file or from CLI flags, ensuring a consistent structure.
2. **`save_output(data, filename_prefix)`**: Saves the generated chart data into individual JSON files within a subfolder named after the `filename_prefix`.
3. **`main()`**: The entry point of the script, which parses CLI arguments, loads input data, generates the chart, performs a geometry audit, and saves the output.

#### Patterns
- **Command Line Interface (CLI)**: The script uses `argparse` to handle command-line arguments.
- **Data Loading and Saving**: The script follows a straightforward data loading and saving pattern, where input is loaded and output is saved in a structured manner.

#### Dependencies
- **Standard Libraries**: `argparse`, `json`, `yaml`, `os`, `collections`
- **Custom Module**: `astrochart_cli_engine` (imported as `chart_engine`)

#### Interfaces
- **`load_input_data(file_path, args)`**: Exposes a function to load input data from a file or CLI flags.
- **`save_output(data, filename_prefix)`**: Exposes a function to save chart data to JSON files.
- **`main()`**: The entry point function that orchestrates the entire process.

#### Database
The file references several PostgreSQL tables, but the exact usage within the file is not clear from the provided code. The tables mentioned are:
- `astrochart_cli_engine`
- `its`
- `birth`
- `collections`
- `a`
- `CLI`

#### Configuration
The script uses command-line arguments for configuration:
- `-f` or `--file`: Path to input JSON or YAML file.
- `-d` or `--date`: Birth date.
- `-t` or `--time`: Birth time.
- `-c` or `--city`: City of birth.
- `-s` or `--state`: State/region of birth.
- `--lat`: Latitude.
- `--lon`: Longitude.
- `--ephe`: Path to Swiss Ephemeris data files (currently unused).
- `--prefix`: Prefix (folder) for output files.

#### Key Logic
1. **Input Data Loading**: The `load_input_data` function ensures that input data is loaded in a consistent format, either from a file or CLI flags.
2. **Chart Generation**: The `chart_engine.generate_natal_chart` function generates the natal chart data based on the input birth information.
3. **Geometry Audit**: The `run_geometry_audit` function performs a geometry audit on the generated chart data to verify pattern detection.
4. **Output Saving**: The `save_output` function saves the chart data into individual JSON files within a specified folder.

#### Integration Points
- **`astrochart_cli_engine`**: The script heavily relies on the `astrochart_cli_engine` module for generating the natal chart and performing the geometry audit.
- **File System**: The script interacts with the file system to load input data from files and save output data to JSON files.

### Summary
The `astrology/astrochart_cli_tool.py` script provides a CLI tool for generating natal astrology charts. It handles input data loading, chart generation, geometry audit, and output saving, integrating with the `astrochart_cli_engine` module for core functionality. The script is designed to be flexible, allowing input data to be provided either via a file or CLI flags.
