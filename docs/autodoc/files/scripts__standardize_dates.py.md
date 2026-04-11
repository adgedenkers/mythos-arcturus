# scripts/standardize_dates.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 432

---

### Documentation for `scripts/standardize_dates.py`

#### Purpose
This script standardizes date formats in the `GenPerson` nodes of a Neo4j database. It converts various non-standard date formats into the standard `MM-DD-YYYY` format, with `00` used for unknown month or day values.

#### Architecture
The script consists of three main functions:
1. `month_lookup(s)`: Converts month abbreviations or full names to their two-digit numeric representation.
2. `parse_date(raw)`: Parses a raw date string into the standard `MM-DD-YYYY` format or returns `None` if the date is already standard or unparseable.
3. `main()`: The entry point of the script, which connects to the Neo4j database, fetches non-standard dates, and updates them using the `parse_date` function.

#### Patterns
- **No specific design patterns**: The script is a straightforward procedural script with no complex design patterns.

#### Dependencies
- **Imports**: `re`, `os`, `neo4j.GraphDatabase`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration File**: `.env` for Neo4J password if not set in environment variables.

#### Interfaces
- **Exposed Functions**: `month_lookup`, `parse_date`, `main`
- **External Interfaces**: Connects to Neo4j database to fetch and update date fields.

#### Database
- **Neo4j Labels**: `GenPerson`
- **Neo4j Nodes**: `GenPerson` nodes are queried and updated.
- **Neo4j Properties**: `birth_date`, `death_date` properties of `GenPerson` nodes.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration File**: `.env` for Neo4J password if not set in environment variables.

#### Key Logic
- **Date Parsing**: The `parse_date` function uses a series of regular expressions to match and convert various date formats into the standard `MM-DD-YYYY` format.
- **Month Lookup**: The `month_lookup` function maps month names and abbreviations to their numeric representations.
- **Database Updates**: The `main` function fetches non-standard dates from the `GenPerson` nodes, converts them using `parse_date`, and updates the nodes accordingly.

#### Integration Points
- **Neo4j Integration**: The script connects to the Neo4j database to fetch and update date fields in `GenPerson` nodes.
- **Environment Configuration**: The script reads configuration from environment variables and a `.env` file for database connection details.

### Detailed Analysis

#### Functions

1. **`month_lookup(s)`**
   - **Purpose**: Converts a month string (e.g., "Jan", "January") to its two-digit numeric representation (e.g., "01").
   - **Parameters**: `s` (string) - the month string to look up.
   - **Returns**: The two-digit numeric representation of the month or `None` if the month is not found.

2. **`parse_date(raw)`**
   - **Purpose**: Parses a raw date string into the standard `MM-DD-YYYY` format.
   - **Parameters**: `raw` (string) - the raw date string to parse.
   - **Returns**: The parsed date in `MM-DD-YYYY` format or `None` if the date is already standard or unparseable.
   - **Logic**: Uses a series of regular expressions to match and convert various date formats. It handles various edge cases and formats, such as European date formats, month-day-year, year-month-day, and more.

3. **`main()`**
   - **Purpose**: The entry point of the script that connects to the Neo4j database, fetches non-standard dates, and updates them.
   - **Parameters**: None.
   - **Returns**: None.
   - **Logic**: Connects to the Neo4j database using the `GraphDatabase.driver` method. It fetches non-standard birth and death dates from `GenPerson` nodes, parses them using `parse_date`, and updates the nodes with the standardized dates.

#### Database Operations
- **Fetch Non-Standard Dates**: The script fetches non-standard dates from `GenPerson` nodes using Cypher queries.
- **Update Dates**: The script updates the `birth_date` and `death_date` properties of `GenPerson` nodes with the standardized dates.

#### Configuration and Environment Variables
- **Neo4j Connection**: The script reads the Neo4j connection details from environment variables (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`). If the password is not set in the environment variables, it reads it from a `.env` file.

#### Integration with Other Components
- **Neo4j**: The script directly interacts with the Neo4j database to fetch and update date fields in `GenPerson` nodes.
- **Environment Configuration**: The script reads configuration from environment variables and a `.env` file for database connection details.

This script plays a crucial role in ensuring that all date fields in the `GenPerson` nodes are standardized, which is essential for consistent data processing and querying within the Mythos system.
