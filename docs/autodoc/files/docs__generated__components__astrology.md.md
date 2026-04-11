# docs/generated/components/astrology.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 50

---

### Documentation for `docs/generated/components/astrology.md`

#### Purpose
The `astrology.md` file serves as a comprehensive reference for the Astrology component of the Mythos system, detailing its functionality, key files, data stores, integration points, and configuration.

#### Architecture
The Astrology component is structured around several key Python files and JSON configuration files:
- **`astrochart_cli_engine.py`**: The core engine that orchestrates chart calculation, aspect analysis, and report generation.
- **`astro_position.py`**: Handles celestial position calculations such as longitude, house cusps, and retrograde status.
- **`calculator.py`**: Implements mathematical algorithms for planetary positions and aspects.
- **`astro_report.py`**: Generates final JSON reports from precomputed chart data.
- **`geometry_audit.py`**: Validates geometric patterns (e.g., grand trines, T-squares) in chart data.
- **JSON Configuration Files**: `aspects.json`, `elements.json`, `houses.json`, `modalities.json`, `polarities.json`, and `arabic_parts.json`, `dignities.json`, `geometric_patterns.json` store configuration and precomputed data.

#### Patterns
- **Precomputation**: All chart data is stored as JSON and not calculated on-demand.
- **Per-User Isolation**: Each user profile has dedicated JSON files in `/charts/{user}/`.
- **Aspect Thresholds**: Defined in `aspects.json` (e.g., `0.5°` for conjunctions).
- **Geometry Validation**: `geometry_audit.py` checks patterns against `geometric_patterns.json`.
- **Report Structure**: All reports follow a consistent schema defined in `natal_report.json`.

#### Dependencies
- **PostgreSQL**: For storing user profiles and chart metadata.
- **JSON Files**: For storing precomputed chart data and configuration.
- **YAML Files**: For user profile configurations (`user_input/*.yaml`).

#### Interfaces
- **Telegram Bot**: Triggers chart generation via `/astro` command.
- **FastAPI Backend**: Exposes `/api/astro` endpoint for chart generation.
- **User Input**: YAML files (`user_input/*.yaml`) feed birth data into `astro_position.py`.
- **Data Pipeline**: `astro_loader.py` populates PostgreSQL from JSON chart data.

#### Database
- **PostgreSQL**:
  - `astrology_charts`: Stores user profiles and chart metadata.
  - `astrology_aspects`: Precomputed aspect relationships.
  - `astrology_positions`: Planetary positions (longitude, house, dignity).

#### Configuration
- **User Profiles**: Configured via `user_input/{user}.yaml` (birth time, location, timezone).
- **Chart Types**: Defined by directory structure (`adge/`, `becky/`, etc.) – each represents a test profile.
- **No environment variables** detected in component files (all config via YAML/JSON).

#### Key Logic
- **Chart Calculation**: `astro_position.py` calculates celestial positions.
- **Aspect Analysis**: `calculator.py` computes planetary aspects.
- **Report Generation**: `astro_report.py` generates structured JSON reports.
- **Geometry Validation**: `geometry_audit.py` validates geometric patterns.

#### Integration Points
- **Telegram Bot**: Requests chart generation via `/astro` command → triggers `astro_report.py`.
- **FastAPI Backend**: Exposes `/api/astro` endpoint → routes to `astro_report.py`.
- **User Input**: `user_input/*.yaml` feeds birth data into `astro_position.py`.
- **Data Pipeline**: `astro_loader.py` populates PostgreSQL from JSON chart data.

This documentation provides a detailed overview of the Astrology component within the Mythos system, covering its purpose, architecture, dependencies, interfaces, database usage, configuration, key logic, and integration points.
