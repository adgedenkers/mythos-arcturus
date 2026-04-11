# astrology/charts/fitz/dispositors.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 49

---

### File: astrology/charts/fitz/dispositors.json

#### Purpose
This JSON file contains detailed astrological dispositions and relationships for a specific chart, including dispositive chains, mutual receptions, and circular loops.

#### Architecture
The file is structured as a JSON object with several key-value pairs, each representing different aspects of astrological relationships:
- `Chain`: A dictionary mapping each planet to its dispositor.
- `Final Dispositors`: A list of planets that are their own dispositors.
- `Mutual Receptions`: A list of pairs of planets that mutually receive each other.
- `Circular Loops`: A list of pairs of planets that form circular loops.
- `Classical Mutual Receptions`: A list of objects detailing classical mutual receptions with descriptions.
- `Modern Mutual Receptions`: A list of objects detailing modern mutual receptions with descriptions.

#### Patterns
This file does not contain any design patterns as it is a static data file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is not an executable or a class; it is a data file that can be read and parsed by other parts of the system. It does not expose any interfaces.

#### Database
This file does not interact with any database tables or Neo4j labels directly. However, it could be used to populate or update such tables or labels in a database.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic is embedded in the data structure itself, representing the relationships and dispositions in an astrological chart:
- **Dispositive Chain**: Each planet is mapped to its dispositor.
- **Final Dispositors**: Planets that are their own dispositors.
- **Mutual Receptions**: Pairs of planets that mutually receive each other.
- **Circular Loops**: Pairs of planets that form circular loops.
- **Classical and Modern Mutual Receptions**: Detailed descriptions of mutual receptions with specific types and descriptions.

#### Integration Points
This file can be integrated into the Mythos system in the following ways:
- **Astrology Module**: The data can be read and processed by the astrology module to generate astrological charts and interpretations.
- **Database Population**: The data can be used to populate or update database tables or Neo4j labels related to astrological charts.
- **User Interface**: The data can be used to display detailed astrological information in the user interface.

### Example Usage
This file could be read by a Python script or a FastAPI endpoint to process and display the astrological data:
```python
import json

with open('astrology/charts/fitz/dispositors.json', 'r') as file:
    data = json.load(file)

# Example: Print the dispositive chain
print(data['Chain'])

# Example: Print the final dispositors
print(data['Final Dispositors'])

# Example: Print the classical mutual receptions
for reception in data['Classical Mutual Receptions']:
    print(reception['Description'])
```

This JSON file serves as a critical data source for generating and interpreting astrological charts within the Mythos system.
