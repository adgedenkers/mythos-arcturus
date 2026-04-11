# eval/results/query_natal_chart/20260305_103408/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 129

---

### Documentation for `test_skill.py`

#### Purpose
This file defines the `QueryNatalChartSkill` class, which is responsible for querying and formatting natal chart data from a PostgreSQL database. It handles resolving names, querying chart data and placements, and formatting the results into a summary and detailed placements list.

#### Architecture
- **Class**: `QueryNatalChartSkill` inherits from `SkillBase` and implements methods for resolving names, querying chart data, and formatting the results.
- **Methods**:
  - `execute`: Main method to process a request and return a response.
  - `_resolve_name`: Resolves input names to standardized names.
  - `_query_chart`: Queries the `astro_natal_charts` table for chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table for placements data.
  - `_format`: Formats the chart and placements data into a readable string.
  - `_build_summary`: Builds a summary string from the chart and placements data.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that is not used within the class but might be for testing or other purposes.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a single connection is created and reused, though it is not strictly enforced as a singleton.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes a `SkillRequest` and returns a `SkillResponse`.
- **Exposed Functions**:
  - `_get_conn`: Establishes a database connection.
- **Exposed Class Attributes**:
  - `name`: Name of the skill.
  - `triggers`: List of trigger phrases for the skill.
  - `cache_ttl`: Time-to-live for caching results.

#### Database
- **Tables**:
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements data for each chart.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Database connection details.
- **Configuration Files**:
  - `.env`: Loads environment variables using `dotenv`.

#### Key Logic
- **Name Resolution**: Converts input names to standardized names using a predefined map.
- **Chart Query**: Retrieves chart data based on the resolved name.
- **Placements Query**: Retrieves placements data based on the chart ID.
- **Data Formatting**: Formats the chart and placements data into a readable summary and detailed list.
- **Error Handling**: Logs errors and raises exceptions for unhandled cases.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Database**: Integrates with PostgreSQL to fetch and process natal chart data.
- **Logging**: Uses `logging` for error reporting and debugging.

### Summary
The `QueryNatalChartSkill` class in `test_skill.py` is designed to query and format natal chart data from a PostgreSQL database. It handles name resolution, chart and placements queries, and data formatting, integrating with the Mythos skill system and PostgreSQL database. The class is well-structured with clear separation of concerns and robust error handling.
