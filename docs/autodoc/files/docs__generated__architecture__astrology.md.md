# docs/generated/architecture/astrology.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 24

---

### Documentation for `docs/generated/architecture/astrology.md`

#### Purpose
The astrology component of the Mythos system generates celestial charts, calculates planetary positions and aspects, and produces astrological reports for user events such as natal charts and transits. It processes astronomical data to deliver structured outputs for Mythos' user-facing astrology features.

#### Architecture
The core logic of the astrology component is divided into several Python modules:
- `calculator.py`: Handles position and aspect calculations.
- `astro_position.py`: Manages celestial data.
- `astro_report.py`: Generates output reports.
- `astrochart_cli_engine.py`: Manages the main CLI workflow.

Configuration data is stored in JSON files:
- `aspects.json`: Contains aspect definitions.
- `arabic_parts.json`: Contains special calculation points.

Database schema and queries are defined in:
- `schema.sql`: General schema.
- `astro_schema.sql`: Astrology-specific schema.
- `astro_events.sql`: Queries for event data.

#### Patterns
- **Factory Pattern**: Likely used in `astrochart_cli_engine.py` for creating different types of chart reports.
- **Singleton Pattern**: Potentially used in `calculator.py` to ensure a single instance of the calculation engine.

#### Dependencies
- **Python 3.8+**: Required for the math and geometry libraries.
- **PostgreSQL**: Used for storing ephemeris data and event queries.

#### Interfaces
- **CLI**: Exposed via `astrochart_cli_engine.py`.
- **API**: Endpoints for integrating with the Mythos core system.
- **Database**: Pulls ephemeris data from `astro_events.sql`.
- **User Interface**: Feeds chart data to the Mythos frontend via report outputs.

#### Database
- **Tables**: Defined in `schema.sql` and `astro_schema.sql`.
- **Queries**: Event queries are defined in `astro_events.sql`.

#### Configuration
- **Configuration Files**: `aspects.json` and `arabic_parts.json`.
- **Environment Variables**: Not explicitly mentioned in the file.

#### Key Logic
- **Data Flow**:
  1. **Input**: User birth/event data (via CLI or API).
  2. **Fetching Data**: `astro_loader.py` fetches ephemeris data from the database using `astro_events.sql`.
  3. **Calculations**: `calculator.py` and `astro_position.py` compute positions and aspects using `aspects.json` and `arabic_parts.json`.
  4. **Output Generation**: `astro_report.py` formats the results into text or HTML output.
  5. **Output**: Generated chart reports or event data for the Mythos UI.

#### Integration Points
- **Mythos Core**: Exposed via CLI (`astrochart_cli_engine.py`) and API endpoints.
- **Data Layer**: Pulls ephemeris data from `astro_events.sql`.
- **User Interface**: Feeds chart data to the Mythos frontend via report outputs.

#### Known Issues
- **Technical Debt**: `astrochart_cli_engine_WORKING.py` indicates unstable CLI engine maintenance.
- **Complexity**: The system is over-engineered with 105 files and 23k lines, requiring synchronization between `astro_schema.sql` and `schema.sql`.
- **Data Gaps**: `arabic_parts.json` lacks documentation for new calculation methods.

This documentation provides a comprehensive overview of the astrology component within the Mythos system, detailing its purpose, architecture, dependencies, interfaces, and key logic.
