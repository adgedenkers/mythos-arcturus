# astrology/tools/seraphe-moon-calcs/seraphe_lunar_transits.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 661

---

### File: `astrology/tools/seraphe-moon-calcs/seraphe_lunar_transits.py`

#### Purpose
This file contains functions to calculate and report lunar transits for a specific individual named Seraphe. It uses the Swiss Ephemeris library to compute the Moon's position and its aspects with natal points for a given month and year.

#### Architecture
The file consists of several top-level functions that handle different aspects of lunar transit calculations and reporting. These functions are:
- `lon_to_sign`: Converts a longitude to a zodiac sign.
- `fmt_degree`: Formats a longitude as a degree and sign.
- `ang_dist`: Calculates the angular distance between two longitudes.
- `get_moon_lon`: Retrieves the Moon's longitude at a given Julian Day.
- `get_moon_speed`: Retrieves the Moon's speed in degrees per day.
- `jd_to_datetime`: Converts a Julian Day to a local datetime.
- `datetime_to_jd`: Converts a local datetime to a Julian Day.
- `days_in_month`: Calculates the number of days in a given month.
- `compute_natal_points`: Computes all natal points for Seraphe.
- `get_point_weight`: Retrieves the weight of a natal point.
- `get_point_category`: Retrieves the category of a natal point.
- `signed_aspect_error`: Computes the signed error for aspect detection.
- `scan_month`: Scans a month for Moon aspects to natal points.
- `find_special_windows`: Identifies critical monthly windows.
- `format_text_report`: Generates a full text report.
- `build_json_output`: Builds structured JSON output.
- `main`: Entry point for the script.

#### Patterns
- **Singleton**: The Swiss Ephemeris library is initialized once and reused.
- **Helper Functions**: Functions like `lon_to_sign`, `fmt_degree`, and `ang_dist` are used as helpers for other functions.

#### Dependencies
- `sys`, `os`, `json`, `math`, `argparse`: Standard Python libraries.
- `datetime`, `timedelta`, `timezone`: From the `datetime` module.
- `swisseph`: Swiss Ephemeris library for astronomical calculations.

#### Interfaces
- **Functions**: Exposes several functions for calculating lunar transits, aspects, and generating reports.
- **Main Entry Point**: The `main` function serves as the entry point for the script.

#### Database
- **PostgreSQL Tables**: References to `datetime`, `the`, `Swiss`, `the`, and `UTC` tables in PostgreSQL are mentioned, but no direct database operations are performed in this file.

#### Configuration
- **Birth Data**: Birth data for Seraphe is hardcoded in the `BIRTH` dictionary.
- **Aspect Definitions**: Aspect definitions are hardcoded in the `ASPECTS` dictionary.
- **Signs and Elements**: Zodiac signs and their elements are defined in `SIGNS`, `SIGN_GLYPHS`, `ELEMENT_MAP`, and `ELEMENT_QUALITY`.

#### Key Logic
1. **Natal Points Calculation**: The `compute_natal_points` function calculates all natal points for Seraphe using the Swiss Ephemeris library.
2. **Aspect Detection**: The `signed_aspect_error` function computes the signed error for aspect detection, which helps in determining when the Moon is in aspect with a natal point.
3. **Transit Scanning**: The `scan_month` function scans a month for Moon aspects to natal points using a 2-hour step and binary search for precise timing.
4. **Report Generation**: The `format_text_report` and `build_json_output` functions generate text and JSON reports, respectively.

#### Integration Points
- **Swiss Ephemeris**: The Swiss Ephemeris library is used for all astronomical calculations.
- **Command Line Interface**: The script can be run from the command line to generate reports for a specific month and year.
- **Output Formats**: The script supports both text and JSON output formats.

### Detailed Analysis

#### Functions

1. **`lon_to_sign(lon)`**
   - Converts a given longitude to a zodiac sign and returns the sign and the degree within the sign.

2. **`fmt_degree(lon)`**
   - Formats a given longitude as a degree and sign (e.g., "14°44' Pisces").

3. **`ang_dist(a, b)`**
   - Calculates the angular distance between two longitudes.

4. **`get_moon_lon(jd)`**
   - Retrieves the Moon's longitude at a given Julian Day using the Swiss Ephemeris library.

5. **`get_moon_speed(jd)`**
   - Retrieves the Moon's speed in degrees per day at a given Julian Day.

6. **`jd_to_datetime(jd, tz_offset)`**
   - Converts a Julian Day to a local datetime considering a timezone offset.

7. **`datetime_to_jd(year, month, day, hour, minute, tz_offset)`**
   - Converts a local datetime to a Julian Day.

8. **`days_in_month(year, month)`**
   - Calculates the number of days in a given month.

9. **`compute_natal_points()`**
   - Calculates all natal points for Seraphe using the Swiss Ephemeris library.

10. **`get_point_weight(name)`**
    - Retrieves the weight of a given natal point.

11. **`get_point_category(name)`**
    - Retrieves the category of a given natal point.

12. **`signed_aspect_error(moon_lon, natal_lon, target_angle)`**
    - Computes the signed error for aspect detection, which helps in determining when the Moon is in aspect with a natal point.

13. **`scan_month(year, month, natal_points, tz_offset, step_hours)`**
    - Scans a month for Moon aspects to natal points using a 2-hour step and binary search for precise timing.

14. **`find_special_windows(events, natal_points)`**
    - Identifies critical monthly windows based on the events and natal points.

15. **`format_text_report(year, month, events, natal_points, windows)`**
    - Generates a full text report for the given year, month, events, natal points, and windows.

16. **`build_json_output(year, month, events, natal_points, windows)`**
    - Builds structured JSON output for the given year, month, events, natal points, and windows.

17. **`main()`**
    - Entry point for the script, which processes command-line arguments and generates the report.

### Example Usage
```bash
python3 seraphe_lunar_transits.py 03/2026
python3 seraphe_lunar_transits.py 03/2026 --json
python3 seraphe_lunar_transits.py 03/2026 --json --output transits_march2026.json
```

This script can be used to generate detailed reports on lunar transits for Seraphe for a specific month and year, supporting both text and JSON output formats.
