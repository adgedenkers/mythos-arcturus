# astrology/astro_loader.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 389

---

### File: `astrology/astro_loader.py`

#### Purpose
The `astro_loader.py` script is designed to parse consolidated astrology chart JSON files and load the data into a PostgreSQL database. It handles both concatenated JSON files with specific delimiters and single natal report JSON files.

#### Architecture
The file is structured into three main sections:
1. **Parsing Functions**: `parse_consolidated` and `unpack_natal_report` handle parsing the input files.
2. **Insert Functions**: A series of functions (`upsert_chart`, `insert_objects`, `insert_points`, etc.) are responsible for inserting parsed data into the PostgreSQL database.
3. **Main Function**: The `main` function orchestrates the parsing and insertion process.

#### Patterns
- **Single Responsibility Principle**: Each function has a single, well-defined responsibility.
- **Idempotence**: The script ensures that re-running for the same chart replaces old data.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `re`
- **PostgreSQL Adapter**: `psycopg2`, `psycopg2.extras.Json`

#### Interfaces
- **Public Functions**:
  - `parse_consolidated(filepath: str) -> dict[str, any]`: Parses a file with specific delimiters into a dictionary.
  - `unpack_natal_report(report: dict) -> dict[str, any]`: Unpacks a natal report JSON into individual section dictionaries.
  - `upsert_chart(cur, meta: dict) -> int`: Inserts or replaces a chart record and returns the chart ID.
  - `insert_objects(cur, chart_id: int, objects: dict)`: Inserts planetary positions.
  - `insert_points(cur, chart_id: int, points: dict)`: Inserts chart points.
  - `insert_house_cusps(cur, chart_id: int, cusps: dict)`: Inserts house cusps.
  - `insert_aspects(cur, chart_id: int, aspects: list)`: Inserts aspects.
  - `insert_arabic_parts(cur, chart_id: int, parts: dict)`: Inserts Arabic parts.
  - `insert_dignities(cur, chart_id: int, dignities: dict)`: Inserts dignities.
  - `insert_retrogrades(cur, chart_id: int, retros: list)`: Inserts retrogrades.
  - `insert_fixed_stars(cur, chart_id: int, stars: list)`: Inserts fixed stars.
  - `insert_patterns(cur, chart_id: int, patterns: list)`: Inserts geometric patterns.
  - `insert_geometry_audit(cur, chart_id: int, audit: dict)`: Inserts geometry audit.
  - `insert_balance(cur, chart_id: int, bal: dict)`: Inserts balance.
  - `insert_sect(cur, chart_id: int, sect: dict)`: Inserts sect.
  - `insert_chart_ruler(cur, chart_id: int, ruler: dict)`: Inserts chart ruler.
  - `insert_dispositors(cur, chart_id: int, disp: dict)`: Inserts dispositor information.
  - `main()`: Main function to orchestrate the parsing and insertion process.

#### Database
The script interacts with multiple PostgreSQL tables:
- `astro_natal_charts`
- `astro_chart_objects`
- `astro_chart_points`
- `astro_natal_house_cusps`
- `astro_natal_aspects`
- `astro_arabic_parts`
- `astro_dignities`
- `astro_retrogrades`
- `astro_fixed_star_conjunctions`
- `astro_geometric_patterns`
- `astro_geometry_audit`
- `astro_balance`
- `astro_sect`
- `astro_chart_ruler`
- `astro_dispositors`

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
1. **Parsing**: The `parse_consolidated` function reads and parses the input file, handling both consolidated and single JSON formats.
2. **Data Insertion**: The `upsert_chart` function ensures idempotence by deleting existing records with the same identity before inserting new ones.
3. **Data Integrity**: Each insert function ensures that data is correctly formatted and inserted into the appropriate tables.

#### Integration Points
- **PostgreSQL**: The script connects to a PostgreSQL database to insert parsed data.
- **File System**: The script reads input files from the file system.
- **Command Line**: The script is invoked from the command line, taking a file path as an argument.

### Summary
`astro_loader.py` is a critical component of the Mythos system, responsible for parsing and loading astrology chart data into a PostgreSQL database. It ensures data integrity and idempotence, making it a robust and reliable part of the system.
