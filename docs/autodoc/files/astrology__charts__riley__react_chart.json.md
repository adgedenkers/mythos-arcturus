# astrology/charts/riley/react_chart.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 1014

---

### File: astrology/charts/riley/react_chart.json

#### Purpose
This JSON file contains the astrological chart data for a person named Riley, including natal positions of planets, house cusps, and aspects between celestial bodies.

#### Architecture
The file is structured as a JSON object with the following key components:
- `name`: The name of the individual whose chart this is.
- `natal`: A dictionary containing the zodiacal positions of the planets in degrees.
- `houses`: An array of house cusps in degrees.
- `aspects`: An array of objects, each representing an aspect between two celestial bodies, including the type of aspect, angle, exact difference, orb, tier, motion, and description.

#### Patterns
- **Data Structure**: The file uses a simple key-value structure for storing the chart data.

#### Dependencies
- This file does not import or rely on any external libraries or modules. It is a standalone data file.

#### Interfaces
- This file is intended to be read by other parts of the Mythos system, particularly those responsible for generating or analyzing astrological charts.

#### Database
- This file does not directly interact with any database tables or Neo4j labels. However, it could be used to populate a database table or Neo4j graph representing astrological charts.

#### Configuration
- This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
- The key logic in this file is the representation of the astrological chart data, including the positions of planets, house cusps, and aspects. Each aspect object contains detailed information about the relationship between two celestial bodies, including the type of aspect, the angle, the exact difference, the orb, the tier, the motion, and a description.

#### Integration Points
- This file integrates with other parts of the Mythos system that handle astrological chart generation and analysis. For example:
  - **Astrological Chart Generation**: The data in this file could be used to generate a visual representation of the chart.
  - **Aspect Analysis**: The aspects data could be used to analyze the interactions between celestial bodies and provide insights or interpretations.
  - **Database Population**: The data could be used to populate a database table or Neo4j graph representing astrological charts for further analysis or storage.

### Detailed Breakdown

#### `name`
- **Description**: The name of the individual whose chart this is.
- **Value**: `"riley"`

#### `natal`
- **Description**: A dictionary containing the zodiacal positions of the planets in degrees.
- **Example**: 
  ```json
  "natal": {
    "sun": 205.649974,
    "moon": 299.234382,
    "mercury": 191.830387,
    ...
  }
  ```

#### `houses`
- **Description**: An array of house cusps in degrees.
- **Example**: 
  ```json
  "houses": [
    313.990647,
    357.296674,
    33.071318,
    ...
  ]
  ```

#### `aspects`
- **Description**: An array of objects, each representing an aspect between two celestial bodies.
- **Example**: 
  ```json
  "aspects": [
    {
      "Object 1": "North Node",
      "Object 2": "South Node",
      "Aspect": "Opposition",
      "Angle": 180.0,
      "Exact Difference": 180.0,
      "Orb": 0.0,
      "Tier": "major",
      "Motion": "Exact (partile)",
      "Description": "Polarization; reflection and projection; potential for balance or conflict."
    },
    ...
  ]
  ```

### Summary
This JSON file serves as a data source for astrological chart information, providing detailed positions and aspects for a specific individual named Riley. It is designed to be consumed by other components of the Mythos system for further processing, such as chart generation, aspect analysis, and database population.
