# astrology/charts/adriaan_harold_denkers/chart_metadata.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 37

---

### File: astrology/charts/adriaan_harold_denkers/chart_metadata.json

#### Purpose
This JSON file contains metadata for an astrological chart for the individual Adriaan Harold Denkers, including birth details, house system, zodiac type, ephemeris information, and the celestial objects included in the chart.

#### Architecture
The file is structured as a JSON object with nested objects and arrays. It contains key-value pairs for various metadata fields related to the astrological chart.

#### Patterns
No design patterns are applicable as this is a data file, not a code file.

#### Dependencies
This file does not import or rely on any external modules or libraries. However, it is used by the Astrology subsystem of the Mythos system.

#### Interfaces
This file is consumed by the Astrology subsystem to generate and interpret astrological charts. It does not expose any interfaces directly.

#### Database
This file does not interact directly with any database tables or Neo4j labels. However, the data it contains might be used to populate or query a database in the Astrology subsystem.

#### Configuration
This file itself is a form of configuration for the Astrology subsystem. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic involves storing and providing the necessary metadata required to generate an astrological chart. This includes birth details, house system, zodiac type, ephemeris information, and the list of celestial objects to be included in the chart.

#### Integration Points
This file integrates with the Astrology subsystem of the Mythos system. The Astrology subsystem uses this metadata to generate and interpret astrological charts for Adriaan Harold Denkers. The data in this file is likely used to initialize the chart generation process, which might involve querying ephemeris data and applying specific astrological calculations.

### Detailed Breakdown of Fields

1. **Name**: The name of the individual for whom the chart is generated.
2. **Birth**: A nested object containing:
   - **Date**: The birth date in ISO 8601 format.
   - **Time**: The birth time in 24-hour format.
   - **Place**: The birth place.
   - **Latitude**: The latitude of the birth place.
   - **Longitude**: The longitude of the birth place.
   - **Timezone**: The timezone of the birth place.
3. **House System**: The type of house system used in the chart (e.g., Placidus).
4. **Zodiac Type**: The type of zodiac used (e.g., Tropical).
5. **Ephemeris**: The type of ephemeris used for celestial positions (e.g., Swiss Ephemeris).
6. **Ephemeris Path**: The file path to the ephemeris data.
7. **Included Objects**: An array of celestial objects included in the chart.
8. **Engine Version**: The version of the astrological engine used to generate the chart.

This metadata file is crucial for ensuring that the Astrology subsystem can accurately generate and interpret the astrological chart for Adriaan Harold Denkers based on the specified parameters and data.
