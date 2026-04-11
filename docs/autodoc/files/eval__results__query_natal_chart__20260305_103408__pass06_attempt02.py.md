# eval/results/query_natal_chart/20260305_103408/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 129

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass06_attempt02.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries a PostgreSQL database to retrieve and format natal chart data for specified individuals. The skill is part of the Mythos system and is designed to handle requests for astrology chart information.

#### Architecture
The file is structured around a single class `QueryNatalChartSkill` which inherits from `SkillBase`. The class contains several methods that handle different aspects of the query and response process:
- `_resolve_name`: Resolves the input name to a standardized name.
- `_query_chart`: Queries the PostgreSQL database for the natal chart data.
- `_query_placements`: Queries the PostgreSQL database for the placements of celestial bodies in the chart.
- `_format`: Formats the chart data and placements into a readable string.
- `_build_summary`: Builds a summary of the chart data.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: Executes the skill logic and returns a response.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a form of singleton pattern as it ensures a single database connection is established and reused.
- **Factory Pattern**: The `execute` method acts as a factory method to produce a `SkillResponse` object based on the input request.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Exposed Methods**: `execute`
- **Exposed Classes**: `QueryNatalChartSkill`
- **Exposed Functions**: `_get_conn`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`

#### Database
- **Tables**: `astro_natal_charts`, `astro_chart_objects`
- **Queries**:
  - `SELECT chart_id, name, birth_date, birth_time, birth_place, house_system, zodiac_type FROM astro_natal_charts WHERE name = %s`
  - `SELECT object_name, sign, deg_min, full_position, is_retrograde, house FROM astro_chart_objects WHERE chart_id = %s ORDER BY CASE object_name WHEN 'Sun' THEN 1 WHEN 'Moon' THEN 2 WHEN 'Mercury' THEN 3 WHEN 'Venus' THEN 4 WHEN 'Mars' THEN 5 WHEN 'Jupiter' THEN 6 WHEN 'Saturn' THEN 7 ELSE 8 END`

#### Configuration
- **Environment Variables**: Used to configure the database connection.
- **Dotenv**: Loads environment variables from a `.env` file.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names using a predefined mapping.
- **Database Query**: The `_query_chart` and `_query_placements` methods query the PostgreSQL database to retrieve chart and placement data.
- **Data Formatting**: The `_format` and `_build_summary` methods format the retrieved data into a human-readable summary and detailed placements.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, which is a critical integration point for data retrieval.

This file is a crucial component of the Mythos system, providing a structured and efficient way to query and present natal chart data.
