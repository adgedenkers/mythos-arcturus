# astrology/scripts/aggregate_chart_json.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 74

---

### File: `astrology/scripts/aggregate_chart_json.py`

#### Purpose
This script aggregates and processes JSON data from astrology charts, extracting planet positions, house cusps, and aspects, and then writes the aggregated data to a new JSON file.

#### Architecture
The script consists of four top-level functions:
1. `extract_planets(data)`: Extracts planet positions from the input data.
2. `extract_houses(data)`: Extracts house cusps from the input data.
3. `build_chart(chart_dir)`: Builds the final astrology chart by aggregating data from multiple JSON files within a directory.
4. `main()`: The entry point of the script, iterating over directories and calling `build_chart()` for each.

#### Patterns
- **No explicit design patterns**: The script is straightforward and does not employ any specific design patterns like factory, singleton, or observer.

#### Dependencies
- `json`: For parsing and writing JSON data.
- `pathlib`: For handling file paths.

#### Interfaces
- **Functions**:
  - `extract_planets(data)`: Exposes a function to extract planet positions.
  - `extract_houses(data)`: Exposes a function to extract house cusps.
  - `build_chart(chart_dir)`: Exposes a function to build the final astrology chart.
  - `main()`: The main entry point of the script.

#### Database
- **References**: The script uses `pathlib` to handle file paths, but there are no direct database references (e.g., PostgreSQL or Neo4j) in the provided code.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Config Files**: No configuration files are used.

#### Key Logic
1. **`extract_planets(data)`**: 
   - Checks if the input `data` is a dictionary.
   - Iterates through the dictionary to extract planet names and their longitudes, storing them in a new dictionary `planets`.

2. **`extract_houses(data)`**: 
   - Checks if the input `data` is a dictionary.
   - Iterates through house numbers (1 to 12) to extract house cusps, storing them in a list `houses`.

3. **`build_chart(chart_dir)`**: 
   - Constructs paths to JSON files containing chart objects, house cusps, and aspects.
   - Reads and parses these JSON files.
   - Calls `extract_planets()` and `extract_houses()` to aggregate the data.
   - Constructs the final output dictionary `out` and writes it to a new JSON file named `react_chart.json`.

4. **`main()`**: 
   - Iterates over all directories in the base directory (`/opt/mythos/astrology/charts`).
   - Calls `build_chart()` for each directory.

#### Integration Points
- The script integrates with the filesystem by reading and writing JSON files within the `/opt/mythos/astrology/charts` directory. It does not directly integrate with other subsystems of the Mythos platform, but it could be part of a larger pipeline that processes and aggregates astrology data.

### Summary
This script is designed to process and aggregate astrology chart data from multiple JSON files within a directory, extracting relevant information and writing it to a new JSON file. It handles file paths using `pathlib` and JSON parsing using the `json` module. The script is self-contained and does not rely on external configurations or environment variables.
