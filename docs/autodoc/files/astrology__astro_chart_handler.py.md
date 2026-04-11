# astrology/astro_chart_handler.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 876

---

### File: `astrology/astro_chart_handler.py`

#### Purpose
This file contains the logic for handling the `/chart` command in the Mythos system, which processes user input to generate and store natal charts. It includes parsing user input, geocoding locations, generating YAML files, running the chart engine, loading data into PostgreSQL, and formatting chart summaries.

#### Architecture
The file consists of several top-level functions that handle different stages of the chart generation pipeline:
1. **Parsing**: Functions like `parse_date`, `parse_time`, `parse_location`, and `parse_chart_request` handle parsing user input.
2. **Geocoding**: The `geocode_location` function converts city and region to latitude, longitude, and timezone.
3. **YAML Generation**: Functions like `generate_yaml` and `save_yaml` create and save YAML files.
4. **Engine Execution**: Functions like `run_chart_engine` and `run_db_loader` execute the chart generation engine and load the results into PostgreSQL.
5. **Summary Formatting**: Functions like `format_chart_summary` and `generate_chart_wheel` create summaries and images of the charts.
6. **Telegram Integration**: Functions like `handle_chart_command` and `handle_chart_callback` integrate with the Telegram bot.

#### Patterns
- **Singleton Pattern**: The `logger` object is a singleton used for logging throughout the file.
- **Factory Pattern**: The `parse_chart_request` function can be seen as a factory that creates a structured data dictionary from user input.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `re`, `json`, `yaml`, `logging`, `subprocess`, `datetime`, `pathlib`
- **External Libraries**: `geopy`, `timezonefinder`, `cairosvg`, `psycopg2`
- **Local Modules**: `astrochart_cli_tool.py`, `astro_loader.py`

#### Interfaces
- **Public Functions**: `handle_chart_command`, `handle_chart_callback`, `register_handlers`
- **Internal Functions**: `parse_date`, `parse_time`, `parse_location`, `parse_chart_request`, `geocode_location`, `generate_yaml`, `save_yaml`, `run_chart_engine`, `run_db_loader`, `format_chart_summary`, `generate_chart_wheel`, `get_chart_wheel_path`, `get_chart_list_data`, `format_chart_list`, `resolve_chart_dir`, `format_chart_lookup`, `run_full_pipeline`

#### Database
- **Tables**: `astro_natal_charts`, `chart_ruler`, `chart_objects`
- **Operations**: Insertion of chart data into `astro_natal_charts`, retrieval of chart data for summaries and lists.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
1. **Parsing**: Converts flexible date, time, and location inputs into standardized formats.
2. **Geocoding**: Uses `geopy` and `timezonefinder` to convert city and region into latitude, longitude, and timezone.
3. **YAML Generation**: Constructs a YAML file from parsed data and geocoded results.
4. **Engine Execution**: Runs the `astrochart_cli_tool.py` to generate chart data.
5. **Database Loading**: Uses `astro_loader.py` to load chart data into PostgreSQL.
6. **Summary Formatting**: Builds a concise summary of the chart for display in Telegram.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot to handle `/chart` commands and inline button callbacks.
- **Chart Engine**: Executes the `astrochart_cli_tool.py` to generate chart data.
- **Database Loader**: Uses `astro_loader.py` to load chart data into PostgreSQL.
- **File System**: Writes YAML files to `/opt/mythos/astrology/user_input/` and reads/writes chart data from `/opt/mythos/astrology/charts/`.

### Detailed Function Descriptions

1. **`parse_date(date_str)`**
   - **Purpose**: Converts flexible date input to `YYYY-MM-DD` format.
   - **Logic**: Uses regex to match and reformat the date string.

2. **`parse_time(time_str)`**
   - **Purpose**: Converts flexible time input to `HH:MM` (24-hour format).
   - **Logic**: Uses regex to match and reformat the time string.

3. **`parse_location(loc_str)`**
   - **Purpose**: Parses location string into `(city, state/region)`.
   - **Logic**: Uses regex to match and split the location string.

4. **`_merge_comma_parts(raw_parts)`**
   - **Purpose**: Re-merges parts that were split by commas but belong together.
   - **Logic**: Iterates through parts and merges them based on specific patterns.

5. **`parse_chart_request(text)`**
   - **Purpose**: Parses a `/chart` command into a structured data dictionary.
   - **Logic**: Splits the input text, merges parts, and parses date, time, and location.

6. **`geocode_location(city, region, country="USA")`**
   - **Purpose**: Geocodes a city/region to latitude, longitude, and timezone.
   - **Logic**: Uses `geopy` and `timezonefinder` to get geocoding and timezone information.

7. **`generate_yaml(parsed, geo)`**
   - **Purpose**: Builds a YAML-ready dictionary from parsed input and geocoded results.
   - **Logic**: Constructs a dictionary with birth details and geocoded data.

8. **`save_yaml(data, output_dir=None)`**
   - **Purpose**: Writes YAML data to a file and returns the file path.
   - **Logic**: Writes the YAML data to a file in the specified directory.

9. **`run_chart_engine(yaml_path, output_prefix=None)`**
   - **Purpose**: Runs the astrochart CLI engine to generate chart data.
   - **Logic**: Executes the `astrochart_cli_tool.py` script with the YAML file as input.

10. **`run_db_loader(chart_dir)`**
    - **Purpose**: Loads chart data into PostgreSQL via `astro_loader.py`.
    - **Logic**: Executes the `astro_loader.py` script to load chart data into the database.

11. **`format_chart_summary(chart_dir)`**
    - **Purpose**: Builds a concise summary of the chart from the output JSONs.
    - **Logic**: Reads JSON files and constructs a summary text.

12. **`generate_chart_wheel(chart_dir)`**
    - **Purpose**: Generates a natal chart wheel PNG from chart metadata.
    - **Logic**: Uses `kerykeion` for SVG generation and `cairosvg` for PNG conversion.

13. **`get_chart_wheel_path(chart_dir)`**
    - **Purpose**: Returns the path to an existing wheel PNG or generates one.
    - **Logic**: Checks for an existing PNG, otherwise generates one.

14. **`get_chart_list_data()`**
    - **Purpose**: Retrieves chart list data from the database.
    - **Logic**: Queries the database to get a list of charts.

15. **`format_chart_list()`**
    - **Purpose**: Formats the chart list as styled text.
    - **Logic**: Constructs a formatted text list of charts.

16. **`resolve_chart_dir(name)`**
    - **Purpose**: Finds the chart directory for a given name.
    - **Logic**: Searches for an exact match or a fuzzy match for the name.

17. **`format_chart_lookup(name)`**
    - **Purpose**: Looks up a stored chart by name and returns a text summary.
    - **Logic**: Retrieves and formats the chart summary for the given name.

18. **`run_full_pipeline(text)`**
    - **Purpose**: Executes the full pipeline from parsing to summary generation.
    - **Logic**: Calls the necessary functions to parse input, geocode, generate YAML, run the engine, load into the database, and generate a summary.

19. **`handle_chart_command(update, context)`**
    - **Purpose**: Handles the `/chart` command in the Telegram bot.
    - **Logic**: Processes the command and generates a chart or summary.

20. **`handle_chart_callback(update, context)`**
    - **Purpose**: Handles inline button clicks from the `/chart` list.
    - **Logic**: Processes button clicks and generates the appropriate response.

21. **`register_handlers(app)`**
    - **Purpose**: Registers the `/chart` command and callback handlers with the Telegram bot.
    - **Logic**: Registers the handlers with the bot application.

This file is a crucial part of the Mythos system, handling the end-to-end process of generating and managing natal charts, integrating with both the Telegram bot and the PostgreSQL database.
