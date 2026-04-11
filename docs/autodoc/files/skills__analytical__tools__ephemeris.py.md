# skills/analytical/tools/ephemeris.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 647

---

### Documentation for `skills/analytical/tools/ephemeris.py`

#### Purpose
This file provides a comprehensive set of functions for astrological calculations, including natal charts, transits, and synastry, using the Swiss Ephemeris library. It supports Western Tropical, Hellenistic, and Vedic astrological frameworks.

#### Architecture
The file is organized into several sections:
1. **Constants and Dictionaries**: Contains predefined constants and mappings for planets, signs, dignities, nakshatras, and aspects.
2. **Helper Functions**: Functions that perform specific calculations, such as converting longitudes to signs, determining nakshatras, and calculating aspects.
3. **Core Calculation Functions**: Functions that perform the main astrological calculations, such as calculating planet positions, house cusps, and aspects.

#### Patterns
- **Singleton Pattern**: Not explicitly used, but the Swiss Ephemeris library (`swisseph`) is used as a singleton-like resource.
- **Factory Pattern**: Not explicitly used, but the `calculate_planets` function acts as a factory for generating planet data.

#### Dependencies
- **Imports**: `swisseph`, `json`, `sys`, `argparse`, `datetime`, `timezone`, `math`
- **External Libraries**: Swiss Ephemeris (`swisseph`)

#### Interfaces
- **Public Functions**: 
  - `calculate_natal`: Full natal chart calculation.
  - `calculate_transits`: Calculate transits against a natal chart.
  - `calculate_synastry`: Calculate synastry between two natal charts.
  - Other helper functions like `lon_to_sign`, `format_position`, `get_nakshatra`, etc.

#### Database
- **PostgreSQL Tables**: `ephemeris`, `datetime`, `math`, `Moon`, `UTC`, `calculate_natal`, `transiting`, `natal`
- **References**: The file references these tables for storing and retrieving astrological data.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Planet Position Calculation**: Uses `swisseph` to calculate positions for all planets at a given Julian Day.
- **Aspect Calculation**: Determines aspects between planets based on their longitudes.
- **Nakshatra Calculation**: Determines the Vedic nakshatra for a given sidereal longitude.
- **Dasha Calculation**: Computes Vimshottari Dasha periods based on the Moon's position in the sidereal zodiac.

#### Integration Points
- **Mythos Subsystems**: 
  - **Database Integration**: Stores and retrieves astrological data from PostgreSQL tables.
  - **API Integration**: Exposes functions to calculate natal charts, transits, and synastry, which can be integrated into the Mythos API.
  - **External Libraries**: Integrates with the Swiss Ephemeris library for precise astrological calculations.

### Detailed Function Descriptions

1. **lon_to_sign(longitude)**
   - **Purpose**: Converts ecliptic longitude to the corresponding zodiac sign and degree.
   - **Logic**: Uses integer division and modulo operations to determine the sign and degree within the sign.

2. **format_position(longitude)**
   - **Purpose**: Formats the longitude as a string in the format "15° 23' Aries".
   - **Logic**: Converts the longitude to a sign and degree using `lon_to_sign` and formats the result.

3. **get_nakshatra(sidereal_longitude)**
   - **Purpose**: Determines the Vedic nakshatra for a given sidereal longitude.
   - **Logic**: Uses integer division and modulo operations to determine the nakshatra and pada.

4. **get_dignity(planet_name, sign)**
   - **Purpose**: Determines the essential dignity status of a planet in a given sign.
   - **Logic**: Checks predefined mappings for domicile, exaltation, detriment, and fall.

5. **is_retrograde(speed)**
   - **Purpose**: Checks if a celestial body is retrograde based on its speed.
   - **Logic**: Returns `True` if the speed is negative.

6. **calculate_aspect(lon1, lon2)**
   - **Purpose**: Calculates the aspect between two longitudes.
   - **Logic**: Determines the smallest angular difference and checks against predefined aspect definitions.

7. **determine_sect(sun_longitude, asc_longitude)**
   - **Purpose**: Determines if a chart is diurnal or nocturnal based on the Sun's position relative to the ascendant.
   - **Logic**: Uses a simplified approach to determine the chart's sect.

8. **get_sect_status(planet_name, sect)**
   - **Purpose**: Determines the sect status of a planet based on the chart's sect.
   - **Logic**: Checks predefined lists of diurnal and nocturnal planets.

9. **compute_vimshottari_dasha(moon_sidereal_lon, birth_jd)**
   - **Purpose**: Computes the Vimshottari Dasha periods based on the Moon's position in the sidereal zodiac.
   - **Logic**: Uses the Moon's nakshatra position to determine the starting lord and calculates subsequent dasha periods.

10. **calculate_planets(jd, flags=0)**
    - **Purpose**: Calculates the positions of all planets at a given Julian Day.
    - **Logic**: Uses `swisseph` to calculate positions and formats the results, including additional astrological data like dignities and rulerships.

11. **calculate_houses(jd, lat, lon, system)**
    - **Purpose**: Calculates house cusps for a given Julian Day, latitude, longitude, and house system.
    - **Logic**: Uses `swisseph` to calculate house cusps and formats the results.

12. **assign_houses(planets, houses)**
    - **Purpose**: Assigns planets to houses based on house cusps.
    - **Logic**: Determines which house each planet falls into based on its longitude and the house cusps.

13. **calculate_aspects(planets)**
    - **Purpose**: Calculates all aspects between planets.
    - **Logic**: Uses `calculate_aspect` to determine aspects between each pair of planets.

14. **calculate_vedic_layer(jd, planets)**
    - **Purpose**: Calculates Vedic/sidereal positions and dashas.
    - **Logic**: Uses `swisseph` to calculate sidereal positions and computes Vimshottari Dasha periods.

15. **calculate_natal(year, month, day, hour, minute, lat, lon, tz_offset, name)**
    - **Purpose**: Calculates a full natal chart across all three astrological frameworks.
    - **Logic**: Combines calculations for Western Tropical, Hellenistic, and Vedic frameworks.

16. **calculate_transits(natal_data, transit_year, transit_month, transit_day, transit_hour, transit_minute, tz_offset)**
    - **Purpose**: Calculates current transits against a natal chart.
    - **Logic**: Uses `calculate_planets` to calculate transit positions and compares them to the natal chart.

17. **calculate_synastry(chart_a, chart_b)**
    - **Purpose**: Calculates synastry between two natal charts.
    - **Logic**: Compares the positions of planets in two charts to determine aspects and interactions.

This file is a crucial component of the Mythos system, providing robust astrological calculations that can be integrated into various parts of the platform.
