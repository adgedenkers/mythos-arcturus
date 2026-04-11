# eval/results/query_natal_chart/20260305_103408/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 129

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass06_attempt04.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries and formats natal chart data from a PostgreSQL database. It handles requests for specific individuals' natal charts and provides a formatted summary and detailed placements.

#### Architecture
The file is structured around a single class `QueryNatalChartSkill` that inherits from `SkillBase`. The class contains methods for resolving names, querying chart data, querying placements, formatting the data, and building a summary. Additionally, there are top-level functions for getting a database connection and resolving names.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create and return a database connection.
- **Singleton**: The `_get_conn` function ensures that a connection is created only once and reused.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**:
  - `execute`: Processes a skill request and returns a formatted response.
- **Private Methods**:
  - `_resolve_name`: Resolves a name to a standardized format.
  - `_query_chart`: Queries the natal chart data from the database.
  - `_query_placements`: Queries the placements data from the database.
  - `_format`: Formats the chart data and placements into a readable string.
  - `_build_summary`: Builds a summary string from the chart data and placements.

#### Database
- **Tables**:
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements data for each chart.

#### Configuration
- **Environment Variables**: The file uses environment variables for database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`).

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names using a predefined mapping.
- **Database Queries**:
  - `_query_chart`: Retrieves chart data based on the name.
  - `_query_placements`: Retrieves placements data based on the chart ID.
- **Data Formatting**:
  - `_format`: Combines chart data and placements into a formatted string.
  - `_build_summary`: Builds a concise summary of major planet placements.

#### Integration Points
- **SkillBase Interface**: The `QueryNatalChartSkill` class implements the `SkillBase` interface, integrating with the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **Environment Configuration**: Loads environment variables using `dotenv` for database connection details.

### Detailed Breakdown

#### Class `QueryNatalChartSkill`
- **Attributes**:
  - `name`: The name of the skill.
  - `triggers`: List of trigger phrases that can invoke the skill.
  - `cache_ttl`: Time-to-live for caching responses.
  - `NAME_MAP`: Mapping of input names to standardized names.
- **Methods**:
  - `execute`: Processes a request, resolves the name, queries the chart and placements, formats the data, and builds a summary.
  - `_resolve_name`: Resolves input names to standardized names.
  - `_query_chart`: Queries the `astro_natal_charts` table for chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table for placements data.
  - `_format`: Formats the chart data and placements into a readable string.
  - `_build_summary`: Builds a concise summary of major planet placements.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables.
- **execute**: Processes a request and returns a response, similar to the class method but operates at the module level.

This file is integral to the Mythos system for providing detailed and formatted natal chart information based on user requests.
