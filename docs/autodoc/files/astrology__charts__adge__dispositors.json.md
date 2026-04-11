# astrology/charts/adge/dispositors.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 26

---

### File: astrology/charts/adge/dispositors.json

#### Purpose
This JSON file contains configuration data for planetary dispositors and related astrological relationships in the Mythos system. It defines chains of planetary influence, circular loops, and mutual receptions.

#### Architecture
The JSON file is structured with several key-value pairs:
- `Chain`: A dictionary mapping each planet to its dispositor.
- `Final Dispositors`: An empty list for final dispositors.
- `Mutual Receptions`: An empty list for mutual receptions.
- `Circular Loops`: A list containing lists of planets that form circular loops.
- `Classical Mutual Receptions`: An empty list for classical mutual receptions.
- `Modern Mutual Receptions`: An empty list for modern mutual receptions.

#### Patterns
This file does not implement any design patterns as it is a configuration file. However, it serves as a data source for other components that might use patterns like factory or singleton to manage and access this data.

#### Dependencies
This file is a configuration file and does not import or rely on any external modules directly. It is likely read by other Python scripts or classes within the Mythos system.

#### Interfaces
This file is read by other parts of the system, particularly by classes or functions that need to understand planetary dispositors and their relationships. It does not expose any methods or functions but serves as a data source.

#### Database
This JSON file does not directly interact with any database tables or Neo4j labels. However, the data it contains might be used to populate or query such tables or labels in the Mythos system.

#### Configuration
This file itself is a configuration file. It might be referenced by environment variables or configuration settings that specify the path to this JSON file.

#### Key Logic
The key logic related to this file involves interpreting the planetary dispositors and their relationships. For example:
- **Dispositor Chain**: The `Chain` dictionary defines the direct dispositor for each planet.
- **Circular Loops**: The `Circular Loops` list identifies groups of planets that form circular relationships.

#### Integration Points
This file is likely integrated into the Mythos system through:
- **Astrology Module**: Classes or functions in the astrology module that read and interpret this JSON file.
- **Chart Generation**: Functions that generate astrological charts might use this data to determine planetary influences.
- **Database Population**: Scripts or functions that populate database tables or Neo4j nodes and relationships with planetary data.

### Example Usage
```python
import json

# Load the dispositors data from the JSON file
with open('astrology/charts/adge/dispositors.json', 'r') as file:
    dispositors_data = json.load(file)

# Accessing the chain of dispositors
dispositor_chain = dispositors_data['Chain']
print(dispositor_chain['Sun'])  # Output: Jupiter

# Accessing circular loops
circular_loops = dispositors_data['Circular Loops']
print(circular_loops)  # Output: [['Jupiter', 'Moon', 'Mars', 'Sun']]
```

This JSON file serves as a foundational data source for astrological computations and chart generation within the Mythos system.
