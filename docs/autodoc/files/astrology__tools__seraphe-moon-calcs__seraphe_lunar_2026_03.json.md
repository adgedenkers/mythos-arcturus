# astrology/tools/seraphe-moon-calcs/seraphe_lunar_2026_03.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 4045

---

### File: astrology/tools/seraphe-moon-calcs/seraphe_lunar_2026_03.json

#### Purpose
This JSON file contains detailed astrological data for the subject "Seraphe (Rebecca Lydia Denkers)" for the month of March 2026, including natal points, special lunar windows, and significant astrological events.

#### Architecture
The file is structured as a JSON object with the following key sections:
- `meta`: Contains metadata about the subject, including birth details, month, year, timezone, and generation timestamp.
- `natal_points`: A dictionary of celestial bodies and their respective positions, signs, and categories.
- `special_windows`: An array of significant lunar windows with descriptions, start and end times, and severity levels.
- `events`: An array of astrological events with detailed information about each event, including time, celestial bodies involved, and intensity.

#### Patterns
- **Data Aggregation**: The file aggregates various data points related to astrological events and positions.
- **Structured Data**: The use of JSON provides a structured format for storing and accessing data.

#### Dependencies
- This file is a data file and does not have any direct dependencies. However, it is likely used by other parts of the Mythos system that process or analyze astrological data.

#### Interfaces
- The file is designed to be consumed by other components of the Mythos system, particularly those responsible for astrological analysis and event scheduling.

#### Database
- This file does not directly interact with any database. However, it may be used to populate or update tables in a database that stores astrological data.

#### Configuration
- The file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
- The key logic in this file is the representation of astrological data. It includes the calculation and representation of celestial body positions, aspects, and their significance over a specific period.

#### Integration Points
- This file is likely integrated with other subsystems of the Mythos system that process astrological data, such as:
  - **Astrological Analysis Engine**: Processes the data to generate insights or predictions.
  - **Event Scheduling System**: Uses the data to schedule significant astrological events.
  - **User Interface**: Displays the data to users in a readable format.

### Detailed Breakdown

#### Meta Section
- **subject**: Name of the subject.
- **birth**: Birth details including date, time, and location.
- **month**: Month of the data.
- **year**: Year of the data.
- **month_num**: Numeric representation of the month.
- **timezone**: Timezone of the subject's location.
- **total_events**: Total number of significant events in the month.
- **generated**: Timestamp of when the data was generated.

#### Natal Points Section
- Contains celestial bodies (Moon, Sun, Mercury, Venus, etc.) with their:
  - `longitude`: Position in degrees.
  - `formatted`: Position in degrees, minutes, and sign.
  - `sign`: Astrological sign.
  - `weight`: Weight assigned to the celestial body.
  - `category`: Category of the celestial body (e.g., LUNAR CORE, HEAVYWEIGHTS).

#### Special Windows Section
- Contains significant lunar windows with:
  - `name`: Name of the window.
  - `description`: Description of the window's significance.
  - `start`: Start time of the window.
  - `end`: End time of the window.
  - `severity`: Severity level of the window (CRITICAL, HIGH, SUPPORTIVE).

#### Events Section
- Contains detailed astrological events with:
  - `datetime_str`: Timestamp of the event.
  - `date_str`: Date of the event.
  - `time_str`: Time of the event.
  - `natal_point`: Celestial body involved.
  - `natal_lon`: Longitude of the natal point.
  - `natal_formatted`: Formatted position of the natal point.
  - `natal_category`: Category of the natal point.
  - `aspect`: Aspect (e.g., sextile, conjunction).
  - `aspect_symbol`: Symbol representing the aspect.
  - `orb`: Orb of the aspect.
  - `moon_lon`: Longitude of the Moon.
  - `moon_sign`: Sign of the Moon.
  - `moon_deg`: Degree of the Moon.
  - `moon_formatted`: Formatted position of the Moon.
  - `intensity`: Intensity of the event.
  - `point_weight`: Weight of the natal point.
  - `aspect_weight`: Weight of the aspect.
  - `jd`: Julian date of the event.

This JSON file serves as a comprehensive data source for astrological analysis within the Mythos system, providing detailed information about celestial positions and significant events for a specific subject and time period.
