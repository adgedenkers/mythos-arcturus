# eval/results/query_natal_chart/20260305_103408/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 129

---

### File: `eval/results/query_natal_chart/20260305_103408/pass06_attempt03.py`

#### Purpose
This file implements a skill for querying and formatting natal chart data from a PostgreSQL database. It processes user requests to retrieve and present astrological chart information for specific individuals.

#### Architecture
The file contains a single class `QueryNatalChartSkill` that inherits from `SkillBase`. This class has several methods to handle the execution of the skill, including resolving names, querying the database for chart and placement data, formatting the results, and building a summary.

Additionally, there are several top-level functions that support the class methods, such as `_get_conn` for database connection management.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it manages a single database connection.
- **Factory**: The class methods can be seen as a factory pattern, where each method is responsible for a specific part of the process (querying, formatting, summarizing).

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Database**: PostgreSQL tables `astro_natal_charts` and `astro_chart_objects`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute` (part of `SkillBase` interface)
- **Private Methods**: `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

#### Database
- **Tables**: `astro_natal_charts`, `astro_chart_objects`
- **Queries**:
  - `SELECT chart_id, name, birth_date, birth_time, birth_place, house_system, zodiac_type FROM astro_natal_charts WHERE name = %s`
  - `SELECT object_name, sign, deg_min, full_position, is_retrograde, house FROM astro_chart_objects WHERE chart_id = %s ORDER BY CASE object_name WHEN 'Sun' THEN 1 WHEN 'Moon' THEN 2 WHEN 'Mercury' THEN 3 WHEN 'Venus' THEN 4 WHEN 'Mars' THEN 5 WHEN 'Jupiter' THEN 6 WHEN 'Saturn' THEN 7 ELSE 8 END`

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`
- **Dotenv**: Configuration loaded using `dotenv.load_dotenv()`

#### Key Logic
1. **Name Resolution**: `_resolve_name` maps input names to standardized names.
2. **Chart Query**: `_query_chart` retrieves chart data from `astro_natal_charts`.
3. **Placement Query**: `_query_placements` retrieves placement data from `astro_chart_objects`.
4. **Formatting**: `_format` combines chart and placement data into a formatted string.
5. **Summary Building**: `_build_summary` creates a summary string highlighting major planet placements.

#### Integration Points
- **SkillBase Interface**: The `execute` method integrates with the broader Mythos system by handling `SkillRequest` and returning `SkillResponse`.
- **Database Connection**: Uses `_get_conn` to manage PostgreSQL connections.
- **Environment Configuration**: Relies on environment variables for database connection details.

### Detailed Explanation

#### Class: `QueryNatalChartSkill`
- **Attributes**:
  - `name`: 'query_natal_chart'
  - `triggers`: List of trigger phrases for the skill
  - `cache_ttl`: Cache time-to-live (3600 seconds)
  - `NAME_MAP`: Mapping of input names to standardized names

- **Methods**:
  - `execute`: Main method that processes the request, resolves the name, queries the chart and placements, formats the data, and builds a summary.
  - `_resolve_name`: Resolves input names to standardized names using `NAME_MAP`.
  - `_query_chart`: Queries the `astro_natal_charts` table for chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table for placement data.
  - `_format`: Combines chart and placement data into a formatted string.
  - `_build_summary`: Builds a summary string highlighting major planet placements.

#### Top-level Functions
- **_get_conn**: Manages the PostgreSQL database connection.
- **execute**: A top-level function that mirrors the `execute` method in the class, possibly for testing or standalone use.

### Example Usage
```python
skill = QueryNatalChartSkill()
request = SkillRequest(message="natal chart for adge")
response = skill.execute(request)
print(response.data)
```

This example demonstrates how the `QueryNatalChartSkill` class can be instantiated and used to process a request for a natal chart, returning a formatted response.
