# eval/results/query_natal_chart/20260305_103408/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Purpose
The `pass05_attempt01.py` file contains the implementation of a skill (`QueryNatalChartSkill`) that queries and formats natal chart data from a PostgreSQL database. It processes user requests to retrieve and summarize astrological chart information for specific individuals.

### Architecture
The file is structured around a single class `QueryNatalChartSkill` that inherits from `SkillBase`. The class contains several methods for resolving names, querying the database, formatting results, and building summaries. Additionally, there are top-level functions for establishing database connections and resolving names.

### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create and return a PostgreSQL connection.
- **Singleton**: The `_get_conn` function ensures that a connection is created and closed properly, mimicking a singleton pattern for database connections within the scope of the methods.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

### Database
- **Tables**: `astro_natal_charts`, `astro_chart_objects`
- **Queries**:
  - `astro_natal_charts`: Fetches chart data based on name.
  - `astro_chart_objects`: Fetches placements based on chart ID.

### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`) are loaded from environment variables using `dotenv`.

### Key Logic
- **Name Resolution**: `_resolve_name` maps user input names to standardized names.
- **Database Querying**: `_query_chart` and `_query_placements` fetch chart data and placements from the database.
- **Result Formatting**: `_format` and `_build_summary` construct the final response text, including a summary and detailed placements.

### Integration Points
- **SkillBase**: The class inherits from `SkillBase`, indicating it integrates with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request/response model.
- **Database**: The skill interacts with PostgreSQL tables `astro_natal_charts` and `astro_chart_objects` to retrieve and format astrological data.

### Detailed Breakdown

#### Class: `QueryNatalChartSkill`
- **Inheritance**: `SkillBase`
- **Attributes**:
  - `name`: Skill name (`'query_natal_chart'`).
  - `triggers`: List of trigger phrases.
  - `cache_ttl`: Cache time-to-live in seconds.
  - `NAME_MAP`: Mapping of names to standardized names.

- **Methods**:
  - `execute`: Main method to process the request, resolve name, query chart and placements, format results, and build summary.
  - `_resolve_name`: Resolves user input names to standardized names.
  - `_query_chart`: Queries the `astro_natal_charts` table to fetch chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table to fetch placements for a given chart ID.
  - `_format`: Formats the chart data and placements into a readable string.
  - `_build_summary`: Builds a summary string of major planets in the chart.

#### Top-level Functions
- `_get_conn`: Establishes a PostgreSQL database connection.
- `execute`: A top-level function that mirrors the class method `execute` for external calls.

### Example Usage
```python
skill = QueryNatalChartSkill()
request = SkillRequest(message="natal chart for adge")
response = skill.execute(request)
print(response.data)
```

This would fetch and format the natal chart data for "Adge" and return it in a structured response.
