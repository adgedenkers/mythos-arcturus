# astrology/chart_pipeline.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 451

---

### File: astrology/chart_pipeline.py

#### Purpose
This file contains functions to source birth times from astrotheme.com and generate natal charts for individuals in the Mythos system. It integrates with the database to update birth times and store generated charts.

#### Architecture
The file is organized into several top-level functions:
- `search_astrotheme`: Searches astrotheme.com for birth times.
- `_fetch_page`: Fetches a web page and returns its HTML content.
- `_name_variations`: Generates URL slug variations for name lookup.
- `_parse_astrotheme`: Parses HTML content to extract birth data.
- `_convert_to_24h`: Converts 12-hour time format to 24-hour format.
- `update_birth_time`: Updates a person's birth time in the database.
- `generate_chart_for_person`: Generates a natal chart for a person.
- `source_birth_time_and_chart`: Full pipeline to source birth time and generate chart.

#### Patterns
- **Factory Method**: `_name_variations` generates different URL slugs for name lookup.
- **Singleton**: Not explicitly used, but the logging module (`log`) is a singleton.

#### Dependencies
- `json`, `logging`, `os`, `re`, `sys`, `urllib.parse`, `urllib.request`, `datetime`, `pathlib`, `typing`, `psycopg2`, `psycopg2.extras`

#### Interfaces
- Exposes functions to search for birth times, update birth times in the database, and generate natal charts.
- Used by other parts of the system, particularly `person_researcher.run_deep_research()`.

#### Database
- **Tables**: `people`
- **Operations**: 
  - `UPDATE people`: Updates birth time, city, and country.
  - `SELECT * FROM people`: Fetches person details for chart generation.

#### Configuration
- **Environment Variables**: Not used directly, but `db_config` is passed to functions for database connection details.
- **Constants**: `ASTRO_DIR`, `CHARTS_DIR`, `ASTROTHEME_URL`, `REQUEST_TIMEOUT`

#### Key Logic
- **Birth Time Sourcing**: 
  - Fetches HTML content from astrotheme.com using `_fetch_page`.
  - Parses HTML to extract birth time and location using `_parse_astrotheme`.
  - Converts 12-hour time to 24-hour format using `_convert_to_24h`.
- **Database Updates**: 
  - Updates `people` table with birth time, city, and country using `update_birth_time`.
- **Chart Generation**: 
  - Fetches person details from `people` table.
  - Geocodes birth location.
  - Writes metadata to `chart_metadata.json`.
  - Generates SVG chart using `generate_chart_wheel`.

#### Integration Points
- **Astrotheme Integration**: Fetches and parses birth data from astrotheme.com.
- **Database Integration**: Updates `people` table with birth data.
- **Chart Generation Pipeline**: Uses `astro_chart_handler` to generate charts.
- **Person Researcher**: Called by `person_researcher.run_deep_research()` to source birth times and generate charts.

### Detailed Documentation

#### `search_astrotheme`
- **Purpose**: Searches astrotheme.com for a person's birth time and location.
- **Logic**: 
  - Builds URL with name variations.
  - Fetches HTML content.
  - Parses HTML to extract birth data.
- **Returns**: Dictionary with birth time, city, country, Rodden rating, and source.

#### `_fetch_page`
- **Purpose**: Fetches a web page and returns its HTML content.
- **Logic**: Uses `urllib.request` to fetch the page.
- **Returns**: HTML content or `None` if fetch fails.

#### `_name_variations`
- **Purpose**: Generates URL slug variations for name lookup.
- **Logic**: Creates variations with full name, initials, and handling multi-part last names.
- **Returns**: List of URL slugs.

#### `_parse_astrotheme`
- **Purpose**: Extracts birth data from an astrotheme page.
- **Logic**: 
  - Uses regex to find birth time and location.
  - Converts 12-hour time to 24-hour format.
- **Returns**: Dictionary with birth time, city, country, and Rodden rating.

#### `_convert_to_24h`
- **Purpose**: Converts 12-hour time format to 24-hour format.
- **Logic**: Uses regex to parse time and convert to 24-hour format.
- **Returns**: 24-hour time string.

#### `update_birth_time`
- **Purpose**: Updates a person's birth time in the `people` table.
- **Logic**: 
  - Connects to PostgreSQL database.
  - Updates `time_of_birth`, `birth_city`, and `birth_country` fields.
- **Returns**: Boolean indicating if update was successful.

#### `generate_chart_for_person`
- **Purpose**: Generates a natal chart for a person.
- **Logic**: 
  - Fetches person details from `people` table.
  - Geocodes birth location.
  - Writes metadata to `chart_metadata.json`.
  - Generates SVG chart using `generate_chart_wheel`.
- **Returns**: Path to chart directory or `None` if insufficient data.

#### `source_birth_time_and_chart`
- **Purpose**: Full pipeline to source birth time and generate chart.
- **Logic**: 
  - Checks if person has birth time.
  - If not, searches astrotheme.com.
  - Updates birth time in database.
  - Generates chart.
- **Returns**: Path to chart directory or `None` if insufficient data.

### Summary
This file integrates web scraping, database updates, and chart generation to provide a comprehensive pipeline for sourcing and processing birth data for individuals in the Mythos system. It leverages external services and internal pipelines to ensure accurate and complete astrological data.
