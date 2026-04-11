# eval/results/query_natal_chart/20260305_103408/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 120

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/final.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries and formats natal chart data from a PostgreSQL database. It handles requests to retrieve and display astrological chart information for specific individuals.

#### Architecture
The file is structured around a single class `QueryNatalChartSkill` which inherits from `SkillBase`. The class contains several methods to handle different aspects of the query and formatting process:
- `_resolve_name`: Resolves the name of the individual from the request.
- `_query_chart`: Queries the natal chart data from the database.
- `_query_placements`: Queries the placements of celestial objects in the chart.
- `_format`: Formats the chart data and placements into a readable string.
- `_build_summary`: Builds a summary of the chart data.

Additionally, there are top-level functions for database connection and execution.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function can be considered a singleton pattern since it manages the creation of a single database connection.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database interactions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute`: The main method that processes the request and returns a `SkillResponse` object.
- **Private Methods**:
  - `_resolve_name`: Resolves the name from the request.
  - `_query_chart`: Queries the natal chart data.
  - `_query_placements`: Queries the placements of celestial objects.
  - `_format`: Formats the chart data and placements.
  - `_build_summary`: Builds a summary of the chart data.

#### Database
- **Tables and Labels**:
  - `astro_natal_charts`: Stores natal chart data.
  - `astro_chart_objects`: Stores placements of celestial objects in the chart.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured via `.env` file for database connection.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names using a predefined mapping.
- **Database Queries**:
  - `_query_chart`: Fetches natal chart data based on the name.
  - `_query_placements`: Fetches placements of celestial objects based on the chart ID.
- **Formatting**:
  - `_format`: Combines the chart data and placements into a formatted string.
  - `_build_summary`: Builds a concise summary of the chart data.

#### Integration Points
- **SkillBase Inheritance**: The `QueryNatalChartSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request-response mechanism.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, integrating with the Mythos database layer.

### Summary
This file implements a skill to query and format natal chart data from a PostgreSQL database. It integrates with the Mythos skill system, handles database interactions, and provides formatted responses for astrological chart requests.
