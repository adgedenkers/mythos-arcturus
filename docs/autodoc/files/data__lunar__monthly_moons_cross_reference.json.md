# data/lunar/monthly_moons_cross_reference.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 240

---

### File: `data/lunar/monthly_moons_cross_reference.json`

#### Purpose
This JSON file serves as a comprehensive cross-reference for named monthly moons across various cultural and spiritual traditions, including special moon types. It provides a detailed mapping of moon names for each Gregorian month across 10 different naming systems.

#### Architecture
The file is structured as a JSON object with the following key components:
- **meta**: Contains metadata about the file, including title, version, date, author, and counts of systems, moons, and special types.
- **naming_systems**: An array of objects, each representing a cultural/spiritual naming system with details like key, name, tradition, region, calendar type, and number of months.
- **cross_reference_by_gregorian_month**: A nested dictionary mapping each Gregorian month to moon names from different cultural systems.

#### Patterns
No design patterns are applicable as this is a static data file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is intended to be read by other parts of the Mythos system, particularly those dealing with lunar calendars and cultural moon naming systems. It does not expose any functions or methods but provides data that can be accessed and utilized programmatically.

#### Database
This file does not interact directly with any database. However, it could be used to populate or reference data in a database table or Neo4j labels related to lunar calendars and cultural moon names.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic involves organizing and presenting moon names across different cultural systems for each Gregorian month. This allows for easy lookup and comparison of moon names across various traditions.

#### Integration Points
This file integrates with other subsystems in the Mythos system that require lunar calendar data, such as:
- **Lunar Calendar Subsystem**: Uses this data to generate lunar calendars for different cultural traditions.
- **Cultural Astronomy Subsystem**: References this data to provide cultural context for moon names and their significance.
- **Database Population Scripts**: May use this data to populate database tables or Neo4j nodes and relationships related to lunar calendars and cultural moon names.

### Example Usage
This file can be read and processed by a Python script to generate lunar calendars or to provide cultural moon names based on the current Gregorian month. For example:

```python
import json

with open('data/lunar/monthly_moons_cross_reference.json', 'r') as file:
    data = json.load(file)

# Accessing moon names for January
january_moons = data['cross_reference_by_gregorian_month']['1_january']
print(january_moons)
```

This would output:
```json
{
  "algonquin": "Wolf Moon",
  "ojibwe": "Spirit Moon (Minado Giizis)",
  "lakota": "Moon of Frost in the Tipi (Wiótheȟika Wí)",
  "celtic": "Quiet Moon",
  "neo_pagan": "Wolf Moon",
  "hindu": "Pushya Purnima",
  "chinese": "12th Month / Sacrificial Month (腊月 Làyuè)",
  "maori": "Kohitātea (fruits ripen)",
  "sri_lankan": "Duruthu Poya",
  "anglo_saxon": "Moon After Yule"
}
```

This data can then be used to display or process moon names in various cultural contexts within the Mythos system.
