# astrology/charts/test_person/dispositors.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 21

---

### File: astrology/charts/test_person/dispositors.json

#### Purpose
This JSON file contains the dispositive relationships and other astrological configurations for a test person's chart, specifically detailing the chain of dispositors and final dispositors.

#### Architecture
The file is structured as a JSON object with several key-value pairs:
- `Chain`: A dictionary mapping each planet to its dispositor.
- `Final Dispositors`: A list of planets that are their own dispositors.
- `Mutual Receptions`: A list of mutual reception pairs (empty in this case).
- `Circular Loops`: A list of circular dispositor loops (empty in this case).
- `Classical Mutual Receptions`: A list of classical mutual reception pairs (empty in this case).
- `Modern Mutual Receptions`: A list of modern mutual reception pairs (empty in this case).

#### Patterns
This file does not follow any specific design patterns as it is a simple data structure.

#### Dependencies
This file does not have any direct dependencies. It is a static data file used by other parts of the system.

#### Interfaces
This file is used as a data source by other components of the Mythos system, particularly those responsible for astrological chart analysis and interpretation.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it may be used to populate or query such structures in the context of the Mythos system.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic represented in this file is the dispositional relationships between planets. The `Chain` key shows which planet disposes another, and the `Final Dispositors` key identifies planets that are their own dispositors, indicating the end of a dispositional chain.

#### Integration Points
This file integrates with the astrological chart analysis subsystem of Mythos. It is likely used by functions or classes that interpret astrological charts, such as:
- `AstrologyChartAnalyzer` class in `astrology/charts/analyzer.py`
- `DispositorCalculator` class in `astrology/dispositors/calculator.py`

These components may read from this file to understand the dispositional relationships and use this information to generate interpretations or further astrological analyses.

### Summary
This JSON file serves as a static data source for dispositional relationships in an astrological chart. It is used by the Mythos system to analyze and interpret astrological charts, particularly focusing on the dispositional chains and final dispositors. The file is integrated into the astrological chart analysis subsystem, providing essential data for the interpretation of planetary influences.
