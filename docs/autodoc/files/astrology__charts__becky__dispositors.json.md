# astrology/charts/becky/dispositors.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 41

---

### File: astrology/charts/becky/dispositors.json

#### Purpose
This JSON file contains detailed dispositor information for a specific astrological chart named "Becky". It includes chains of planetary dispositors, final dispositor planets, mutual receptions, circular loops, and classical mutual receptions.

#### Architecture
The file is structured as a JSON object with several key-value pairs:
- **Chain**: A dictionary mapping each planet to its final dispositor.
- **Final Dispositors**: A list of planets that are their own dispositor or the end of a dispositor chain.
- **Mutual Receptions**: A list of pairs of planets that are in each other's signs.
- **Circular Loops**: A list of pairs of planets that form a circular loop in their dispositor chain.
- **Classical Mutual Receptions**: A list of objects detailing classical mutual receptions, including the planets involved, the type of reception, and a description.
- **Modern Mutual Receptions**: A list (currently empty) for modern mutual receptions.

#### Patterns
No specific design patterns are applicable since this is a data file and not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is intended to be read by other parts of the Mythos system, particularly the astrology subsystem, to provide dispositor information for the "Becky" chart.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a static data file.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic represented in this file involves the dispositor relationships between planets:
- **Dispositor Chain**: Each planet is mapped to its final dispositor.
- **Final Dispositors**: Identifies planets that are their own dispositor or the end of a dispositor chain.
- **Mutual Receptions**: Identifies pairs of planets that are in each other's signs.
- **Circular Loops**: Identifies pairs of planets that form a circular loop in their dispositor chain.
- **Classical Mutual Receptions**: Provides detailed information about classical mutual receptions.

#### Integration Points
This file is likely integrated into the Mythos astrology subsystem for:
- **Dispositor Analysis**: To analyze dispositor chains and final dispositors.
- **Mutual Receptions Analysis**: To identify and analyze mutual receptions and circular loops.
- **Astrological Chart Interpretation**: To provide dispositor information for the "Becky" chart, which can be used in broader astrological interpretations.

### Summary
This JSON file serves as a static data source for dispositor information in the "Becky" astrological chart. It is structured to provide detailed dispositor chains, final dispositors, mutual receptions, and classical mutual receptions, which can be used by the Mythos astrology subsystem for further analysis and interpretation.
