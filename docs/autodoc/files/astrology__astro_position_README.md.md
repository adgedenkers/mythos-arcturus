# astrology/astro_position_README.md

**Language:** markdown
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 277

---

### File: `astro_position.py`

#### Purpose
The `astro_position.py` script calculates precise ecliptic positions for celestial bodies (planets, asteroids, points) using the Swiss Ephemeris. It supports geolocation for birth chart work, including full house cusp and angle calculations, and outputs the results in various formats (table, JSON, CSV).

#### Architecture
The script is designed as a command-line tool with a main function that parses command-line arguments and delegates to specific functions for position calculation and output formatting. It uses the `pyswisseph` library for ephemeris calculations and `pytz` for timezone handling. The script also supports geocoding using `geopy` and `timezonefinder` for location-based calculations.

#### Patterns
- **Command Line Interface (CLI)**: The script is structured as a CLI tool, parsing arguments and executing corresponding logic.
- **Dependency Injection**: The script relies on external libraries for ephemeris calculations, timezone handling, and geocoding.

#### Dependencies
- `pyswisseph`: Swiss Ephemeris Python bindings.
- `pytz`: Timezone handling.
- `geopy`: Geocoding for location-based calculations.
- `timezonefinder`: Timezone finder for geocoded locations.

#### Interfaces
The script exposes a command-line interface with various options for date, time, location, and output format. It supports JSON, CSV, and table output formats.

#### Database
The script does not directly interact with the database. However, the JSON output format is designed to be compatible with `astro_loader.py`, which inserts the data into PostgreSQL.

#### Configuration
The script relies on environment variables and configuration files for ephemeris paths and timezone data. It uses the `/opt/mythos/astrology/ephe/` directory for ephemeris files.

#### Key Logic
1. **Date and Time Parsing**: The script parses date and time strings, converting them to UTC for consistency.
2. **Geocoding**: If a city and state are provided, the script uses `geopy` to geocode the location and `timezonefinder` to determine the timezone.
3. **Ephemeris Calculation**: The script uses `pyswisseph` to calculate the positions of specified celestial bodies.
4. **Output Formatting**: The script formats the results into table, JSON, or CSV formats based on the `--output` argument.

#### Integration Points
- **`astro_loader.py`**: The JSON output from `astro_position.py` is designed to be compatible with `astro_loader.py`, which loads the data into PostgreSQL.
- **`astrochart_cli_engine.py`**: The script shares planet naming conventions and ephemeris file paths with `astrochart_cli_engine.py`.
- **`astrochart_cli_tool.py`**: The script is a standalone tool that can be used as part of the larger Mythos system for quick lookups and data extraction.

### Detailed Breakdown of Key Sections

#### Overview
- **Purpose**: Calculates ecliptic positions for celestial bodies using Swiss Ephemeris.
- **Features**: Supports geolocation for birth charts, full house cusp and angle calculation, and various output formats.

#### Quick Start
- **Examples**: Provides examples for calculating positions for current sky, specific dates, and full birth charts with location.

#### Arguments
- **Date and Time**: `--date`, `--now`, `--tz`.
- **Location**: `--city`, `--state`, `--lat`, `--lon`.
- **Planets**: `--planet`.
- **Chart Mode**: `--chart`.
- **House Systems**: `--houses`.
- **Output Formats**: `--output`.

#### Usage Examples
- **Planets Only**: Examples for calculating positions without location.
- **Full Birth Chart**: Examples for calculating full birth charts with location.

#### Bash Aliases
- **Aliases**: Provides shell functions for quick access to common operations.

#### Output Formats
- **Table**: Human-readable terminal display.
- **JSON**: Structured output compatible with `astro_loader.py`.
- **CSV**: One row per planet with header.

#### Supported Planets & Points
- **List**: Provides a list of supported celestial bodies with their CLI names and symbols.

#### Ephemeris Files
- **Files**: Lists ephemeris files and their coverage.

#### Dependencies
- **Libraries**: Lists required Python libraries and their installation instructions.

#### Mythos Integration
- **`astro_loader.py`**: JSON output is compatible with `astro_loader.py`.
- **`astrochart_cli_engine.py`**: Shares planet naming conventions and ephemeris file paths.

#### Related Files
- **Files**: Lists related files in the `astrology` directory.

### Conclusion
The `astro_position.py` script is a critical component of the Mythos system, providing precise astrological position calculations and supporting various output formats for integration with other subsystems.
