# eval/results/query_natal_chart/20260305_103408/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 106

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass03_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries a PostgreSQL database to retrieve and format natal chart data for a given name. The skill resolves the name, queries the chart data, retrieves placements, formats the data, and builds a summary.

#### Architecture
The file consists of a single class `QueryNatalChartSkill` that inherits from `SkillBase`. It includes several methods for resolving names, querying the database, formatting data, and building summaries. Additionally, there are top-level functions for database connection and execution.

- **Class**: `QueryNatalChartSkill`
  - **Methods**: `execute`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (part of the `SkillBase` interface)
- **Private Methods**: `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`

#### Database
- **Tables**: `astro_natal_charts`, `astro_chart_objects`
- **Queries**:
  - `SELECT chart_id, name, birth_date, birth_time, birth_place, house_system, zodiac_type FROM astro_natal_charts WHERE name = %s`
  - `SELECT object_name, sign, deg_min, full_position, is_retrograde, house FROM astro_chart_objects WHERE chart_id = %s ORDER BY CASE object_name WHEN 'Sun' THEN 1 WHEN 'Moon' THEN 2 WHEN 'Mercury' THEN 3 WHEN 'Venus' THEN 4 WHEN 'Mars' THEN 5 WHEN 'Jupiter' THEN 6 WHEN 'Saturn' THEN 7 ELSE 8 END`

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are loaded from `.env` using `dotenv`.

#### Key Logic
- **Name Resolution**: `_resolve_name` maps input names to standardized names using `NAME_MAP`.
- **Database Querying**: `_query_chart` and `_query_placements` fetch natal chart and placement data from the database.
- **Data Formatting**: `_format` and `_build_summary` construct the final response text from the queried data.

#### Integration Points
- **SkillBase Interface**: The `execute` method integrates with the broader Mythos system by implementing the `SkillBase` interface, which handles skill execution and response generation.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to ensure consistent database connections.
- **Environment Configuration**: The `load_dotenv` function integrates with the environment configuration to load database credentials.

### Summary
This file implements a skill that queries a PostgreSQL database to retrieve and format natal chart data for a given name. It includes methods for resolving names, querying the database, formatting data, and building summaries. The skill integrates with the Mythos system through the `SkillBase` interface and uses environment variables for database configuration.
