# astrology/tools/seraphe-moon-calcs/ephemeris.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 422

---

### File: astrology/tools/seraphe-moon-calcs/ephemeris.py

#### Purpose
This file contains a collection of functions for calculating various astrological elements such as planetary positions, aspects, houses, and fixed stars. It serves as a core component for generating detailed natal and transit charts.

#### Architecture
The file consists of several top-level functions that perform specific astrological calculations. Each function is designed to handle a particular aspect of the astrological computations, such as determining planetary positions, calculating aspects, and assigning planets to houses. The functions rely on constants and dictionaries defined at the top of the file for reference data like planet IDs, signs, and aspects.

#### Patterns
- **Singleton**: The `swisseph` library is used as a singleton for planetary calculations.
- **Factory**: Functions like `calc_planets` and `calc_fixed_stars` can be seen as factory methods that produce detailed planetary and fixed star data based on input parameters.

#### Dependencies
- **Imports**: `swisseph`, `json`, `sys`, `copy`, `math`, `argparse`
- **External Libraries**: `swisseph` for planetary calculations.

#### Interfaces
- **Public Functions**: 
  - `lon_to_sign`, `fmt_pos`, `fmt_full`, `get_decan`, `get_dignity`, `ang_dist`, `calc_aspect`, `det_sect`, `sect_status`, `precess`, `calc_planets`, `calc_fixed_stars`, `find_star_conj`, `calc_houses`, `assign_houses`, `detect_intercepted`, `calc_aspects`, `detect_patterns`, `calculate_natal`, `calculate_transits`, `calculate_synastry`.

#### Database
- **No direct database interactions**: This file does not interact directly with any database. However, it could be integrated into a larger system that stores or retrieves astrological data from a database.

#### Configuration
- **Environment Variables**: None.
- **Configuration Files**: None.

#### Key Logic
- **Planetary Calculations**: Functions like `calc_planets` and `calc_fixed_stars` use the `swisseph` library to calculate planetary and fixed star positions.
- **Aspect Calculation**: `calc_aspect` determines the aspects between two planets based on their longitudes and predefined aspect definitions.
- **House Calculation**: `calc_houses` computes the cusps and angles of the houses using the Placidus system.
- **House Assignment**: `assign_houses` assigns planets to houses based on their longitudes and the calculated cusps.

#### Integration Points
- **Mythos Subsystems**: This file can be integrated into the Mythos system to provide astrological data for various applications, such as generating natal charts, transit charts, and synastry charts.
- **Data Flow**: The functions in this file can be called by higher-level components to retrieve and process astrological data. For example, `calculate_natal` can be used to generate a full natal chart, which can then be stored or displayed in the Mythos system.

### Detailed Function Descriptions

1. **lon_to_sign**
   - **Purpose**: Converts a given longitude to a zodiac sign and degree within the sign.
   - **Parameters**: `lon` (float)
   - **Returns**: Tuple containing the sign and degree within the sign.

2. **fmt_pos**
   - **Purpose**: Formats a longitude into a string representation of the degree and sign.
   - **Parameters**: `lon` (float)
   - **Returns**: Formatted string.

3. **fmt_full**
   - **Purpose**: Provides a full formatted string representation of the degree and sign.
   - **Parameters**: `lon` (float)
   - **Returns**: Formatted string.

4. **get_decan**
   - **Purpose**: Determines the decan and its ruler for a given sign and degree.
   - **Parameters**: `sign` (str), `deg` (float)
   - **Returns**: Dictionary containing the decan and its ruler.

5. **get_dignity**
   - **Purpose**: Determines the dignity (domicile, exaltation, detriment, fall) of a planet in a given sign.
   - **Parameters**: `planet` (str), `sign` (str)
   - **Returns**: String indicating the dignity.

6. **ang_dist**
   - **Purpose**: Calculates the angular distance between two longitudes.
   - **Parameters**: `a` (float), `b` (float)
   - **Returns**: Angular distance.

7. **calc_aspect**
   - **Purpose**: Determines the aspect between two planets based on their longitudes.
   - **Parameters**: `l1` (float), `l2` (float), `s1` (str), `s2` (str)
   - **Returns**: Dictionary containing aspect details.

8. **det_sect**
   - **Purpose**: Determines whether the chart is diurnal or nocturnal based on the Sun's position.
   - **Parameters**: `sun_lon` (float), `asc_lon` (float), `mc_lon` (float)
   - **Returns**: String indicating the sect.

9. **sect_status**
   - **Purpose**: Determines the sect status of a planet.
   - **Parameters**: `planet` (str), `sect` (str)
   - **Returns**: String indicating the sect status.

10. **precess**
    - **Purpose**: Precesses a J2000 longitude to a given year.
    - **Parameters**: `lon_j2000` (float), `year` (int)
    - **Returns**: Precessed longitude.

11. **calc_planets**
    - **Purpose**: Calculates the positions and details of all planets for a given Julian date.
    - **Parameters**: `jd` (float), `flags` (int)
    - **Returns**: Dictionary containing detailed planetary data.

12. **calc_fixed_stars**
    - **Purpose**: Calculates the positions of fixed stars for a given Julian date and year.
    - **Parameters**: `jd` (float), `year` (int)
    - **Returns**: Dictionary containing detailed fixed star data.

13. **find_star_conj**
    - **Purpose**: Finds conjunctions between planets and fixed stars.
    - **Parameters**: `planets` (dict), `stars` (dict), `orb` (float)
    - **Returns**: List of conjunctions.

14. **calc_houses**
    - **Purpose**: Calculates the cusps and angles of the houses for a given Julian date, latitude, and longitude.
    - **Parameters**: `jd` (float), `lat` (float), `lon` (float), `system` (str)
    - **Returns**: Dictionary containing house data.

15. **assign_houses**
    - **Purpose**: Assigns planets to houses based on their longitudes and the calculated cusps.
    - **Parameters**: `planets` (dict), `houses` (dict)
    - **Returns**: Updated `planets` dictionary with house assignments.

16. **detect_intercepted**
    - **Purpose**: Detects intercepted houses.
    - **Parameters**: `houses` (dict)
    - **Returns**: List of intercepted houses.

17. **calc_aspects**
    - **Purpose**: Calculates aspects between planets.
    - **Parameters**: `planets` (dict), `include_minor` (bool)
    - **Returns**: List of aspects.

18. **detect_patterns**
    - **Purpose**: Detects astrological patterns based on aspects.
    - **Parameters**: `aspects` (list), `planets` (dict)
    - **Returns**: List of detected patterns.

19. **calculate_natal**
    - **Purpose**: Generates a full natal chart.
    - **Parameters**: `year` (int), `month` (int), `day` (int), `hour` (int), `minute` (int), `lat` (float), `lon` (float), `tz_offset` (float), `name` (str)
    - **Returns**: Dictionary containing the natal chart data.

20. **calculate_transits**
    - **Purpose**: Calculates transits for a given natal chart.
    - **Parameters**: `natal_data` (dict), `ty` (int), `tm` (int), `td` (int), `th` (int), `tmin` (int), `tz` (int)
    - **Returns**: Dictionary containing transit data.

21. **calculate_synastry**
    - **Purpose**: Calculates synastry between two charts.
    - **Parameters**: `chart_a` (dict), `chart_b` (dict)
    - **Returns**: Dictionary containing synastry data.

This file serves as a robust astrological engine that can be integrated into the Mythos system to provide comprehensive astrological data and insights.
