# eval/results/query_natal_chart/20260305_103408/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 106

---

### Purpose
The `20260305_103408/pass02_attempt01.py` file contains the `QueryNatalChartSkill` class, which is responsible for querying and formatting natal chart data from a PostgreSQL database based on user input. It resolves names, queries chart data, and formats the response.

### Architecture
The file consists of a single class `QueryNatalChartSkill` inheriting from `SkillBase`. It contains several methods for resolving names, querying the database, formatting the response, and building summaries. Additionally, there are top-level functions for database connection and name resolution.

### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and closed properly.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the creation and formatting of the response.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`

### Interfaces
- **Public Methods**: 
  - `execute`: Processes the request and returns a formatted response.
- **Private Methods**: 
  - `_resolve_name`: Resolves the input name to a standardized name.
  - `_query_chart`: Queries the natal chart data from the database.
  - `_query_placements`: Queries the placements data from the database.
  - `_format`: Formats the chart and placements data into a readable string.
  - `_build_summary`: Builds a summary of the chart data.

### Database
- **Tables**: 
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements data.

### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT` are used to connect to the PostgreSQL database.
- **Configuration File**: `.env` file is loaded using `dotenv` to set environment variables.

### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names using a predefined map.
- **Database Querying**: 
  - `_query_chart` queries the `astro_natal_charts` table for chart data.
  - `_query_placements` queries the `astro_chart_objects` table for placements data.
- **Response Formatting**: 
  - `_format` combines the chart and placements data into a formatted string.
  - `_build_summary` creates a summary of the chart data.

### Integration Points
- **SkillBase Class**: The `QueryNatalChartSkill` class inherits from `SkillBase`, integrating with the broader Mythos system for skill execution.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, facilitating integration with the Mythos request-response framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, enabling integration with the database subsystem of Mythos.

### Summary
This file implements a skill for querying and formatting natal chart data from a PostgreSQL database. It resolves input names, queries the necessary data, and formats the response for the user. The class integrates with the Mythos system through inheritance and the use of request-response objects, and it connects to the database using environment variables and a singleton connection pattern.
