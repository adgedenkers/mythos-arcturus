# astrology/astro_position.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 516

---

### File: astrology/astro_position.py

#### Purpose
This file contains functions for calculating astrological positions and generating birth charts using the Swiss Ephemeris library. It supports geolocation for exact birth chart coordinates and provides various output formats.

#### Architecture
The file consists of several top-level functions and constants. The main functions include:
- `resolve_location`: Resolves city and state to latitude, longitude, timezone, and display name.
- `datetime_to_jd`: Converts a datetime object to Julian Day.
- `lon_to_sign_pos`: Converts a longitude to a position within a zodiac sign.
- `get_position`: Calculates the position of a specific planet at a given Julian Day.
- `compute_all_positions`: Computes positions for multiple planets at a given date and time.
- `compute_noon_chart`: Computes a noon UTC chart for a given date.
- `get_houses`: Calculates house cusps and angles.
- `assign_houses`: Tags each planet with its house number.
- `to_chart_objects_json`: Converts results to a JSON format.
- `print_table`: Prints results in a table format.
- `print_csv`: Prints results in CSV format.
- `parse_dt`: Parses a date string.
- `resolve_planets`: Resolves planet keys.
- `main`: Main function for command-line interface.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the `compute_all_positions` function can be seen as a factory for generating multiple planet positions.
- **Singleton Pattern**: Not used.
- **Observer Pattern**: Not used.

#### Dependencies
- `argparse`: For command-line argument parsing.
- `json`: For JSON serialization.
- `sys`: For system-specific parameters and functions.
- `os`: For operating system interfaces.
- `swisseph`: For astrological calculations using the Swiss Ephemeris.
- `geopy`: For geolocation services.
- `timezonefinder`: For timezone determination based on coordinates.

#### Interfaces
- Exposes functions for resolving locations, computing positions, and generating charts.
- Provides main function for command-line interface.

#### Database
- References PostgreSQL tables `datetime`, `zoneinfo`, `geopy`, and `timezonefinder`.

#### Configuration
- Uses environment variables for setting the ephemeris path (`SWISSEPH_PATH`).

#### Key Logic
- **Geolocation**: Uses `geopy` and `timezonefinder` to resolve city and state to latitude, longitude, and timezone.
- **Julian Day Calculation**: Converts datetime to Julian Day for astrological calculations.
- **Zodiac Position Calculation**: Converts longitude to zodiac sign and position.
- **Planet Position Calculation**: Uses Swiss Ephemeris to calculate planet positions.
- **House Calculation**: Calculates house cusps and angles using Swiss Ephemeris.
- **Output Formatting**: Converts results to JSON and prints in table and CSV formats.

#### Integration Points
- Integrates with PostgreSQL for geolocation and timezone data.
- Uses Swiss Ephemeris for astrological calculations.
- Provides command-line interface for generating astrological charts.

### Detailed Function Descriptions

1. **resolve_location**
   - **Purpose**: Resolves city and state to latitude, longitude, timezone, and display name.
   - **Logic**: Uses `geopy` and `timezonefinder` to geocode the city and state, then determines the timezone.

2. **datetime_to_jd**
   - **Purpose**: Converts a datetime object to Julian Day.
   - **Logic**: Ensures the datetime is in UTC and converts it to Julian Day using `swisseph.julday`.

3. **lon_to_sign_pos**
   - **Purpose**: Converts a longitude to a position within a zodiac sign.
   - **Logic**: Calculates the sign index, degree, minute, and second from the longitude.

4. **get_position**
   - **Purpose**: Calculates the position of a specific planet at a given Julian Day.
   - **Logic**: Uses Swiss Ephemeris to calculate the planet's position and converts it to a zodiac position.

5. **compute_all_positions**
   - **Purpose**: Computes positions for multiple planets at a given date and time.
   - **Logic**: Iterates over the specified planets and calls `get_position` for each.

6. **compute_noon_chart**
   - **Purpose**: Computes a noon UTC chart for a given date.
   - **Logic**: Calls `compute_all_positions` with noon UTC time.

7. **get_houses**
   - **Purpose**: Calculates house cusps and angles.
   - **Logic**: Uses Swiss Ephemeris to calculate house cusps and angles and converts them to zodiac positions.

8. **assign_houses**
   - **Purpose**: Tags each planet with its house number.
   - **Logic**: Determines the house number based on the planet's longitude and house cusps.

9. **to_chart_objects_json**
   - **Purpose**: Converts results to a JSON format.
   - **Logic**: Constructs a JSON object from the planet results.

10. **print_table**
    - **Purpose**: Prints results in a table format.
    - **Logic**: Formats and prints the results in a tabular format.

11. **print_csv**
    - **Purpose**: Prints results in CSV format.
    - **Logic**: Formats and prints the results in CSV format.

12. **parse_dt**
    - **Purpose**: Parses a date string.
    - **Logic**: Converts a date string to a datetime object.

13. **resolve_planets**
    - **Purpose**: Resolves planet keys.
    - **Logic**: Maps planet aliases to their canonical keys.

14. **main**
    - **Purpose**: Main function for command-line interface.
    - **Logic**: Parses command-line arguments and calls the appropriate functions to generate and print astrological charts.
