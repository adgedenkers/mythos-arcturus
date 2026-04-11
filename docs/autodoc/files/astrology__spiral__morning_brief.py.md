# astrology/spiral/morning_brief.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 198

---

### Documentation for `astrology/spiral/morning_brief.py`

#### Purpose
This file is responsible for assembling and delivering the daily morning brief for a specific user (Ka'tuar'el) in the Mythos system. The brief includes the user's current spiral position and transit pressure, and it is delivered once per day.

#### Architecture
The file consists of several functions that handle different aspects of the morning brief process:
- `_get_conn`: Establishes a PostgreSQL database connection.
- `has_brief_been_delivered`: Checks if the brief has already been delivered for a given person and date.
- `mark_brief_delivered`: Marks the brief as delivered for a given person and date.
- `build_brief_context`: Builds the morning brief context block and ensures it is delivered only once per day.
- `_format_spiral_section`: Formats the spiral position for the brief context.
- `_assemble_brief`: Combines the spiral and transit sections into a single context block for Iris's prompt.
- `get_spiral_status`: Provides a formatted spiral status string for on-demand use.

#### Patterns
- **Singleton Pattern**: `_get_conn` function ensures a single database connection is established.
- **Factory Method**: `_format_spiral_section` and `_assemble_brief` can be seen as factory methods that create formatted strings based on input data.

#### Dependencies
- `logging`: For logging errors and warnings.
- `os`: To access environment variables for database connection.
- `datetime`: To handle date and time operations.
- `typing`: For type annotations.
- `psycopg2`: For PostgreSQL database operations.
- `psycopg2.extras`: For additional PostgreSQL utilities.
- `spiral_engine`, `transit_pressure`, `transit_interpreter`: Modules that provide spiral position, transit pressure, and transit interpretation functionalities.

#### Interfaces
- `has_brief_been_delivered(person_id: str, brief_date: Optional[date] = None) -> bool`: Checks if the brief has been delivered.
- `mark_brief_delivered(person_id: str, brief_date: Optional[date] = None)`: Marks the brief as delivered.
- `build_brief_context(person_id: str = ADGE_PERSON_ID, chart_id: int = ADGE_CHART_ID, force: bool = False) -> Optional[str]`: Builds the morning brief context block.
- `get_spiral_status(person_id: str = ADGE_PERSON_ID, chart_id: int = ADGE_CHART_ID) -> str`: Returns a formatted spiral status string for on-demand use.

#### Database
- `spiral_morning_brief_log`: Table used to log whether the brief has been delivered for a given person and date.
- `her`, `datetime`, `typing`, `Iris`, `a`: These are placeholders or mislabeled references and do not seem to be directly used in the provided code.

#### Configuration
- `POSTGRES_USER`, `POSTGRES_HOST`: Environment variables used to establish the PostgreSQL database connection.
- `ADGE_PERSON_ID`, `ADGE_CHART_ID`: Constants representing the person ID and chart ID for Ka'tuar'el.

#### Key Logic
- **Delivery Tracking**: Functions `has_brief_been_delivered` and `mark_brief_delivered` ensure that the brief is delivered only once per day.
- **Brief Assembly**: `build_brief_context` assembles the brief by fetching the spiral position and transit pressure, formatting them, and combining them into a single context block.
- **Formatting**: `_format_spiral_section` and `_assemble_brief` handle the formatting of the spiral position and the final brief, respectively.

#### Integration Points
- **Spiral Engine**: Integrates with `spiral_engine` to get the spiral position.
- **Transit Pressure**: Integrates with `transit_pressure` and `transit_interpreter` to get and format transit pressure.
- **Iris**: The assembled brief is intended to be injected into Iris's prompt context, where it is woven into her opening response.

This file is a critical component of the Mythos system, ensuring that the user receives a personalized and timely morning brief that reflects their current astrological context.
