## astrology
The astrology component generates celestial charts, calculates planetary positions and aspects, and produces astrological reports for user events (e.g., natal charts, transits). It processes astronomical data to deliver structured outputs for Mythos' user-facing astrology features.

**Key files and structure**  
Core logic resides in Python modules: `calculator.py` (position/aspect calculations), `astro_position.py` (celestial data handling), `astro_report.py` (output generation), and `astrochart_cli_engine.py` (main CLI workflow). Configuration data is stored in `aspects.json` (aspect definitions) and `arabic_parts.json` (special calculation points). Database schema is defined in `schema.sql` and `astro_schema.sql`, with event queries in `astro_events.sql`. Documentation is provided via `astro_events_README.md` and `astro_position_README.md`.

**Data flow**  
1. Input: User birth/event data (via CLI or API)  
2. `astro_loader.py` fetches ephemeris data from database (using `astro_events.sql`)  
3. `calculator.py` and `astro_position.py` compute positions/aspects (using `aspects.json` and `arabic_parts.json`)  
4. `astro_report.py` formats results into output (text/HTML)  
5. Output: Generated chart reports or event data for Mythos UI

**Dependencies and integration points**  
- **Dependencies**: PostgreSQL (via `schema.sql`), Python 3.8+ (math/geometry libraries)  
- **Integration points**:  
  - Mythos core: Exposed via CLI (`astrochart_cli_engine.py`) and API endpoints  
  - Data layer: Pulls ephemeris data from `astro_events.sql`  
  - User interface: Feeds chart data to Mythos frontend via report outputs

**Known issues**  
- Technical debt: `astrochart_cli_engine_WORKING.py` (duplicate/obsolete file) indicates unstable CLI engine maintenance.  
- Complexity: 105 files/23k lines suggest over-engineering; `astro_schema.sql` and `schema.sql` require synchronization.  
- Data gaps: `arabic_parts.json` lacks documentation for new calculation methods.
