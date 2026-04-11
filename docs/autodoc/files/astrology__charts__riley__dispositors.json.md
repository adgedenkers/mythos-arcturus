# astrology/charts/riley/dispositors.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 40

---

### File: `astrology/charts/riley/dispositors.json`

#### Purpose
This JSON file contains the dispositor relationships and other astrological configurations for a specific chart named "Riley". It includes details such as dispositor chains, final dispositors, mutual receptions, circular loops, and classical mutual receptions.

#### Architecture
The file is structured as a JSON object with several key-value pairs:
- **Chain**: A dictionary mapping each planet to its dispositor.
- **Final Dispositors**: A list of planets that are their own final dispositors.
- **Mutual Receptions**: A list of pairs of planets that mutually receive each other.
- **Circular Loops**: A list of pairs of planets that form circular loops.
- **Classical Mutual Receptions**: A list of objects detailing classical mutual receptions, including the planets involved, the type, and a description.
- **Modern Mutual Receptions**: An empty list indicating no modern mutual receptions.

#### Patterns
No specific design patterns are used since this is a static JSON file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is intended to be read by other parts of the system, such as astrology chart analysis modules. It does not expose any functions or classes.

#### Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file that could be used to populate or query a database.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic in this file is the representation of dispositor relationships and other astrological configurations:
- **Dispositor Chain**: Defines the dispositor for each planet.
- **Final Dispositors**: Identifies planets that are their own final dispositors.
- **Mutual Receptions**: Identifies pairs of planets that mutually receive each other.
- **Circular Loops**: Identifies pairs of planets that form circular loops.
- **Classical Mutual Receptions**: Provides details on classical mutual receptions.

#### Integration Points
This file is likely used by other components of the Mythos system, such as:
- Astrology chart analysis modules that interpret the dispositor relationships.
- Database population scripts that use this data to populate astrology-related tables or Neo4j nodes and relationships.
- User interfaces that display the dispositor information to users.

### Summary
This JSON file serves as a configuration file for the Riley astrology chart, detailing dispositor relationships, mutual receptions, and other astrological configurations. It is used by other components of the Mythos system for analysis and display purposes.
