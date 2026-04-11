# skills/data/query_natal_chart.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 120

---

### File: `skills/data/query_natal_chart.py`

#### Purpose
This file contains the `QueryNatalChartSkill` class, which is responsible for querying and formatting natal chart data from a PostgreSQL database based on user input. It handles resolving user names, querying chart data, and formatting the results into a readable summary.

#### Architecture
- **Class**: `QueryNatalChartSkill` inherits from `SkillBase` and implements the `execute` method to process user requests.
- **Methods**: 
  - `_resolve_name`: Resolves user-provided names to standardized names.
  - `_query_chart`: Queries the `astro_natal_charts` table to get chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table to get placements for a given chart.
  - `_format`: Formats the chart data and placements into a readable string.
  - `_build_summary`: Builds a summary of major planet placements.
- **Top-level Functions**: 
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Top-level function to handle the skill execution.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database connection and query execution.
  - `dotenv`: For loading environment variables from `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Exposed to handle incoming requests and return responses.
- **Exposed Data**: 
  - `name`, `triggers`, `cache_ttl`: Properties of the `QueryNatalChartSkill` class.

#### Database
- **Tables**: 
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements of celestial objects in a chart.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured for database connection.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps user-provided names to standardized names using a predefined mapping.
- **Chart Querying**: The `_query_chart` method fetches chart data based on the resolved name.
- **Placements Querying**: The `_query_placements` method fetches placements for a given chart ID.
- **Formatting**: The `_format` method constructs a formatted string of chart data and placements.
- **Summary Building**: The `_build_summary` method creates a summary of major planet placements.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill execution framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for request and response handling.
- **Database**: Connects to PostgreSQL to fetch natal chart and placement data.
- **Logging**: Uses `logging` for error handling and logging.

### Detailed Explanation

1. **Class `QueryNatalChartSkill`**:
   - **Inheritance**: Inherits from `SkillBase`.
   - **Attributes**: 
     - `name`: Name of the skill.
     - `triggers`: List of phrases that trigger this skill.
     - `cache_ttl`: Time-to-live for caching results.
     - `NAME_MAP`: Mapping of user-provided names to standardized names.
   - **Methods**:
     - `execute`: Main method to handle the skill execution. It resolves the name, queries the chart and placements, formats the data, and builds a summary.
     - `_resolve_name`: Resolves user-provided names to standardized names.
     - `_query_chart`: Queries the `astro_natal_charts` table to get chart data.
     - `_query_placements`: Queries the `astro_chart_objects` table to get placements for a given chart.
     - `_format`: Formats the chart data and placements into a readable string.
     - `_build_summary`: Builds a summary of major planet placements.

2. **Top-level Functions**:
   - `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables.
   - `execute`: Top-level function to handle the skill execution, similar to the class method but for standalone use.

3. **Database Interaction**:
   - Uses `psycopg2` to connect to the PostgreSQL database and execute queries.
   - Fetches data from `astro_natal_charts` and `astro_chart_objects` tables.

4. **Error Handling**:
   - Uses `logging` to log errors and exceptions during execution.

5. **Configuration**:
   - Loads environment variables using `dotenv` for database connection details.

This file is a critical component of the Mythos system, handling the retrieval and formatting of natal chart data for user requests.
