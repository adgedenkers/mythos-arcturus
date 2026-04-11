# eval/results/query_natal_chart/20260305_103408/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 130

---

### File: `eval/results/query_natal_chart/20260305_103408/pass06_attempt01.py`

#### Purpose
This file contains a Python class `QueryNatalChartSkill` that handles the retrieval and formatting of natal chart data from a PostgreSQL database. It processes user requests for astrology-related information and returns formatted responses.

#### Architecture
- **Class**: `QueryNatalChartSkill` extends `SkillBase` and includes methods for resolving names, querying the database, formatting data, and building summaries.
- **Functions**: Several top-level functions are defined for database connection and data processing.
- **Data Flow**: The class processes a user request, resolves the name, queries the database for chart and placement data, formats the data, and builds a summary before returning a response.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connection management.
- **Factory**: The `SkillBase` class likely follows a factory pattern to instantiate different skill classes.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `RealDictCursor` from `psycopg2.extras`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the main method exposed to other parts of the system, taking a `SkillRequest` and returning a `SkillResponse`.
- **Private Methods**: `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary` are used internally to process the request.

#### Database
- **Tables**: `astro_natal_charts`, `astro_chart_objects`.
- **Queries**: 
  - `_query_chart`: Queries `astro_natal_charts` for chart data.
  - `_query_placements`: Queries `astro_chart_objects` for placements data.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **Name Resolution**: `_resolve_name` maps user input names to standardized names.
- **Database Queries**: `_query_chart` and `_query_placements` fetch chart and placement data from PostgreSQL.
- **Data Formatting**: `_format` and `_build_summary` format the chart and placement data into a readable summary.

#### Integration Points
- **SkillBase**: The class extends `SkillBase`, indicating it integrates with a broader skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to interface with the skill execution pipeline.
- **Database Connection**: Uses `_get_conn` to manage database connections, likely shared across multiple skills.

### Detailed Documentation

#### Classes
- **QueryNatalChartSkill**
  - **Inheritance**: `SkillBase`
  - **Attributes**:
    - `name`: 'query_natal_chart'
    - `triggers`: List of trigger phrases for the skill.
    - `cache_ttl`: Time-to-live for caching results.
    - `NAME_MAP`: Mapping of names to standardized names.
  - **Methods**:
    - `execute`: Main method to process a request and return a response.
    - `_resolve_name`: Resolves input names to standardized names.
    - `_query_chart`: Queries the database for natal chart data.
    - `_query_placements`: Queries the database for chart placements.
    - `_format`: Formats the chart and placement data.
    - `_build_summary`: Builds a summary of the chart data.

#### Top-Level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables.
- **execute**: Placeholder for the main execution logic, likely overridden by `QueryNatalChartSkill.execute`.
- **_resolve_name**: Placeholder for resolving names, likely overridden by `QueryNatalChartSkill._resolve_name`.
- **_query_chart**: Placeholder for querying chart data, likely overridden by `QueryNatalChartSkill._query_chart`.
- **_query_placements**: Placeholder for querying placement data, likely overridden by `QueryNatalChartSkill._query_placements`.
- **_format**: Placeholder for formatting data, likely overridden by `QueryNatalChartSkill._format`.
- **_build_summary**: Placeholder for building a summary, likely overridden by `QueryNatalChartSkill._build_summary`.

#### Database References
- **Tables**: `astro_natal_charts`, `astro_chart_objects`.
- **Queries**:
  - `_query_chart`: Fetches chart data based on the name.
  - `_query_placements`: Fetches placements data based on the chart ID.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are used to configure the database connection.

#### Key Logic
- **Name Resolution**: `_resolve_name` maps user input names to standardized names.
- **Database Queries**: `_query_chart` and `_query_placements` fetch chart and placement data from PostgreSQL.
- **Data Formatting**: `_format` and `_build_summary` format the chart and placement data into a readable summary.

#### Integration Points
- **SkillBase**: The class extends `SkillBase`, indicating it integrates with a broader skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to interface with the skill execution pipeline.
- **Database Connection**: Uses `_get_conn` to manage database connections, likely shared across multiple skills.
