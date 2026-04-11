# astrology/gen_chart.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 68

---

### File: astrology/gen_chart.py

#### Purpose
This file contains functions to generate and render astrological natal charts using the `kerykeion` library. It supports both JSON input and direct birth data input to create the chart and save it in SVG format.

#### Architecture
The file consists of three main functions:
1. `make_subject`: Creates an astrological subject using birth data.
2. `from_json`: Loads birth data from a JSON file and creates a subject.
3. `render`: Renders the astrological chart based on the subject and saves it as an SVG file.

The file also includes a command-line interface (CLI) for running the chart generation process.

#### Patterns
- **Factory Pattern**: Used in `make_subject` to create an astrological subject using `AstrologicalSubjectFactory`.
- **Command Line Interface**: The `argparse` module is used to handle command-line arguments.

#### Dependencies
- `argparse`: For parsing command-line arguments.
- `json`: For reading JSON files.
- `sys`: For system-specific parameters and functions.
- `pathlib`: For path manipulations.
- `kerykeion`: For astrological calculations and chart generation.

#### Interfaces
- **Functions**:
  - `make_subject(name, year, month, day, hour, minute, lat, lon, tz, city=None, nation=None)`: Creates an astrological subject.
  - `from_json(path)`: Loads birth data from a JSON file and creates a subject.
  - `render(subject, output, theme, wheel_only, grid_only, with_angles)`: Renders the astrological chart and saves it as an SVG file.

#### Database
- **PostgreSQL Tables**:
  - `pathlib`: Not a PostgreSQL table, but a module for path manipulations.
  - `kerykeion`: Not a PostgreSQL table, but a library for astrological calculations.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
1. **Subject Creation**:
   - `make_subject` uses `AstrologicalSubjectFactory` to create an astrological subject from birth data.
   - `from_json` reads birth data from a JSON file and uses `make_subject` to create the subject.

2. **Chart Rendering**:
   - `render` uses `ChartDataFactory` to create chart data and `ChartDrawer` to render the chart.
   - The chart can be rendered with or without angles, and the output can be a full chart, a wheel-only chart, or a grid-only chart.

#### Integration Points
- **Kerykeion Library**: The file heavily relies on the `kerykeion` library for astrological calculations and chart generation.
- **Command Line Interface**: The file integrates with the command line to accept user input for generating charts.

### Detailed Analysis

#### `make_subject`
- **Purpose**: Creates an astrological subject using birth data.
- **Parameters**:
  - `name`: Name of the subject.
  - `year`, `month`, `day`, `hour`, `minute`: Birth date and time.
  - `lat`, `lon`: Geographic coordinates (latitude and longitude).
  - `tz`: Time zone.
  - `city`, `nation`: Optional parameters for location.
- **Logic**: Uses `AstrologicalSubjectFactory` to create the subject.

#### `from_json`
- **Purpose**: Loads birth data from a JSON file and creates a subject.
- **Parameters**:
  - `path`: Path to the JSON file.
- **Logic**: Reads the JSON file, extracts birth data, and calls `make_subject` to create the subject.

#### `render`
- **Purpose**: Renders the astrological chart and saves it as an SVG file.
- **Parameters**:
  - `subject`: Astrological subject.
  - `output`: Path to save the SVG file.
  - `theme`: Theme for the chart.
  - `wheel_only`, `grid_only`, `with_angles`: Flags to control the chart rendering options.
- **Logic**: Uses `ChartDataFactory` to create chart data and `ChartDrawer` to render the chart. The chart can be saved as a full chart, a wheel-only chart, or a grid-only chart.

#### Command Line Interface
- **Purpose**: Provides a command-line interface for generating astrological charts.
- **Parameters**:
  - `--json`: Path to a JSON file containing birth data.
  - `--name`, `--year`, `--month`, `--day`, `--hour`, `--minute`, `--lat`, `--lon`, `--tz`, `--city`, `--nation`: Birth data parameters.
  - `--output`: Path to save the SVG file.
  - `--theme`: Theme for the chart.
  - `--wheel-only`, `--grid-only`, `--with-angles`: Flags to control the chart rendering options.
- **Logic**: Parses command-line arguments, creates a subject using either JSON input or direct birth data, and calls `render` to generate and save the chart.
