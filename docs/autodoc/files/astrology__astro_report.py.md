# astrology/astro_report.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 270

---

### Documentation for `astro_report.py`

#### Purpose
The `astro_report.py` script generates a CSV report comparing astrological charts for a predefined set of individuals. It retrieves data from a PostgreSQL database and formats it into a structured CSV file.

#### Architecture
The script is organized into several top-level functions and constants:
- **Constants**: `CONN_PARAMS`, `PERSON_ORDER`, `SIGN_ABBR`, `OBJECT_ORDER`, `POINT_ORDER`, `HOUSE_ORDER`, `PART_ORDER`.
- **Functions**: 
  - `lon_to_parts(lon)`: Converts ecliptic longitude to degrees, minutes, and sign abbreviation.
  - `parse_degmin(degmin_str)`: Parses a degree-minute string into degrees and minutes.
  - `main()`: Main function that orchestrates the data retrieval and CSV generation.
  - `blank_row()`: Appends a blank row to the CSV rows.
  - `add_row(cls, obj, data_by_name)`: Adds a row to the CSV with the specified class, object, and data.

#### Patterns
- **No specific design patterns**: The script is a straightforward procedural script without any complex design patterns.

#### Dependencies
- **Imports**: `sys`, `csv`, `psycopg2`, `os`.
- **Database**: PostgreSQL tables `astro_natal_charts`, `astro_chart_objects`, `astro_chart_points`, `astro_natal_house_cusps`, `astro_arabic_parts`.

#### Interfaces
- **Exposed Functions**: None. The script is designed to be run as a standalone script.
- **Main Entry Point**: `main()` function.

#### Database
- **Tables Accessed**:
  - `astro_natal_charts`: Retrieves chart IDs and names.
  - `astro_chart_objects`: Retrieves object data (planets).
  - `astro_chart_points`: Retrieves point data (angles).
  - `astro_natal_house_cusps`: Retrieves house cusp data.
  - `astro_arabic_parts`: Retrieves Arabic part data.

#### Configuration
- **Environment Variables**: None.
- **Configuration Constants**: `CONN_PARAMS` for database connection parameters.

#### Key Logic
1. **Data Retrieval**:
   - Connects to the PostgreSQL database using `psycopg2`.
   - Retrieves and maps chart data for predefined individuals.
   - Fetches and processes data for planets, angles, house cusps, and Arabic parts.

2. **Data Processing**:
   - Converts ecliptic longitudes to degrees, minutes, and signs.
   - Parses degree-minute strings into degrees and minutes.
   - Organizes data into a structured format suitable for CSV.

3. **CSV Generation**:
   - Constructs the CSV header and rows.
   - Writes the CSV file to the specified path or a default location.

#### Integration Points
- **Database Integration**: Connects to the PostgreSQL database to retrieve astrological chart data.
- **File System Integration**: Writes the generated CSV report to the file system.

### Detailed Breakdown

#### Constants
- `CONN_PARAMS`: Database connection parameters.
- `PERSON_ORDER`: List of individuals for whom charts are to be compared.
- `SIGN_ABBR`: Dictionary mapping astrological signs to their abbreviations.
- `OBJECT_ORDER`, `POINT_ORDER`, `HOUSE_ORDER`, `PART_ORDER`: Lists defining the order of planets, angles, houses, and Arabic parts.

#### Functions
- **`lon_to_parts(lon)`**: Converts an ecliptic longitude to degrees, minutes, and sign abbreviation.
- **`parse_degmin(degmin_str)`**: Parses a degree-minute string into degrees and minutes.
- **`main()`**: Main function that:
  - Connects to the database.
  - Retrieves and maps chart data.
  - Fetches and processes data for planets, angles, house cusps, and Arabic parts.
  - Constructs the CSV header and rows.
  - Writes the CSV file to the specified path.
- **`blank_row()`**: Appends a blank row to the CSV rows.
- **`add_row(cls, obj, data_by_name)`**: Adds a row to the CSV with the specified class, object, and data.

#### Data Flow
1. **Database Connection**: Establishes a connection to the PostgreSQL database.
2. **Data Retrieval**: Fetches chart data, object data, point data, house cusp data, and Arabic part data.
3. **Data Processing**: Converts longitudes and parses degree-minute strings.
4. **CSV Construction**: Builds the CSV header and rows.
5. **CSV Writing**: Writes the constructed CSV to the file system.

This script is a critical component of the Mythos system, providing a structured way to compare astrological charts for a predefined set of individuals.
