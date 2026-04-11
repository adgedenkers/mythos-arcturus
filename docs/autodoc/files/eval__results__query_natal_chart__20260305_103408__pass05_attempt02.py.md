# eval/results/query_natal_chart/20260305_103408/pass05_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### File: `eval/results/query_natal_chart/20260305_103408/pass05_attempt02.py`

#### Purpose
This file contains a class `QueryNatalChartSkill` that queries a PostgreSQL database to retrieve and format natal chart data for specified individuals. It handles requests for natal chart information and provides formatted responses.

#### Architecture
- **Class**: `QueryNatalChartSkill` inherits from `SkillBase` and implements methods to resolve names, query chart data, and format the results.
- **Methods**:
  - `execute`: Main method to process the request and return a formatted response.
  - `_resolve_name`: Resolves a given name to a standardized name.
  - `_query_chart`: Queries the PostgreSQL database for natal chart data.
  - `_query_placements`: Queries the PostgreSQL database for placements of celestial objects in the chart.
  - `_format`: Formats the chart data and placements into a readable string.
  - `_build_summary`: Builds a summary of the chart data and placements.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for external use.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connections, ensuring a single connection is established and closed properly.
- **Factory**: The class `QueryNatalChartSkill` can be seen as a factory for creating responses based on the input request.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Processes a request and returns a `SkillResponse` object.
- **Top-level Functions**:
  - `_get_conn`: Establishes a database connection.
  - `execute`: Processes a request and returns a `SkillResponse` object.

#### Database
- **Tables/Labels**:
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements of celestial objects within a chart.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Used to establish a connection to the PostgreSQL database.
- **Configuration Files**:
  - `.env`: Used to load environment variables.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names.
- **Database Queries**:
  - `_query_chart`: Retrieves natal chart data based on the name.
  - `_query_placements`: Retrieves placements of celestial objects based on the chart ID.
- **Data Formatting**:
  - `_format`: Combines chart data and placements into a formatted string.
  - `_build_summary`: Builds a summary of the chart data and placements.

#### Integration Points
- **SkillBase**: The class `QueryNatalChartSkill` inherits from `SkillBase`, integrating with the broader Mythos system for handling skills and requests.
- **Database**: The file integrates with the PostgreSQL database to fetch natal chart and placement data.
- **Logging**: Errors are logged using the `logging` module, which can be integrated with the broader logging system of Mythos.
- **Environment Variables**: The file uses environment variables to configure database connections, which can be managed centrally in the Mythos system.

This file is a crucial component of the Mythos system, providing a specific skill for querying and formatting natal chart data, and integrating with the broader infrastructure through database access and logging.
