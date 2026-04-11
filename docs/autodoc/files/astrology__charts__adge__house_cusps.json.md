# astrology/charts/adge/house_cusps.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 74

---

### File: astrology/charts/adge/house_cusps.json

#### Purpose
This JSON file contains the cusp positions and corresponding zodiac signs for each of the 12 houses in an astrological chart. The data is used to determine the boundaries between houses and the signs that occupy them.

#### Architecture
The file is structured as a JSON object where each key represents a house number (1 through 12). Each house entry is a nested JSON object containing the following fields:
- `Cusp`: The degree position of the house cusp.
- `Sign`: The zodiac sign that the cusp falls within.
- `DegMin`: The degree and minute position of the cusp.
- `Full`: A full description combining the degree and minute with the zodiac sign.

#### Patterns
This file does not employ any design patterns as it is a simple data structure.

#### Dependencies
This file is a data file and does not import or rely on any external dependencies. It is used as a data source by other parts of the system.

#### Interfaces
This file is used as a data source by other components of the Mythos system, particularly those responsible for generating astrological charts. It does not expose any functions or classes.

#### Database
This file does not interact directly with any database tables or Neo4j labels. It is a static data file used for reference.

#### Configuration
This file does not use any configuration files or environment variables. It is a standalone data file.

#### Key Logic
The key logic associated with this file involves interpreting the cusp positions and zodiac signs to determine the boundaries and contents of each house in an astrological chart. The data is used to map the positions of celestial bodies to specific houses and signs.

#### Integration Points
This file integrates with the astrological chart generation subsystem of Mythos. Specifically, it is likely used by functions or classes that generate or interpret astrological charts, such as:

- `astrology/charts/generate_chart.py`: A Python script that uses this data to create a complete astrological chart.
- `astrology/analysis/house_analysis.py`: A script that analyzes the influence of planets in specific houses based on the cusp positions.

### Example Usage
Here is an example of how this JSON data might be used in a Python script:

```python
import json

# Load the house cusp data
with open('astrology/charts/adge/house_cusps.json', 'r') as file:
    house_cusps = json.load(file)

# Example: Get the cusp position and sign for the 1st house
first_house = house_cusps['1']
cusp_position = first_house['Cusp']
sign = first_house['Sign']
deg_min = first_house['DegMin']
full_description = first_house['Full']

print(f"1st House Cusp: {cusp_position}, Sign: {sign}, DegMin: {deg_min}, Full: {full_description}")
```

This script loads the JSON data and extracts the cusp position, sign, degree and minute, and full description for the 1st house. Similar logic can be applied to other houses as needed.
