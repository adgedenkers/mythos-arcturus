# astrology/charts/fitz/sect.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 9

---

### File: astrology/charts/fitz/sect.json

#### Purpose
This JSON file contains configuration data for the sect classification in astrology, specifically for the Fitz system. It defines which celestial bodies are considered sect benefics, malefics, and lights, both for the day and night, based on traditional astrological principles.

#### Architecture
The file is a simple JSON object with key-value pairs, where each key represents a specific astrological sect classification and the value represents the corresponding celestial body.

#### Patterns
No design patterns are applicable as this is a static configuration file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is used to configure the sect classification within the astrology subsystem. It is likely read by a Python script or module that processes astrological charts.

#### Database
This file does not interact with any database tables or Neo4j labels directly. However, the data it contains might be used to populate or query a database related to astrological charts.

#### Configuration
This file itself serves as a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic here is the classification of celestial bodies into sect categories (benefics, malefics, and lights) for day and night. This classification is fundamental to interpreting astrological charts within the Fitz system.

#### Integration Points
This file integrates with the astrology subsystem, particularly with modules or scripts that process and interpret astrological charts. It likely provides the necessary sect classifications to these modules for accurate astrological analysis.

### Detailed Explanation

- **Sect**: Indicates whether the chart is for a day or night. In this case, it is "Day".
- **Sect Light**: The primary celestial body that defines the sect. For a day chart, it is the "Sun".
- **Sect Benefic**: Celestial body that is considered beneficial within the sect. For a day chart, it is "Jupiter".
- **Sect Malefic**: Celestial body that is considered malevolent within the sect. For a day chart, it is "Saturn".
- **Contra Light**: The primary celestial body that defines the opposite sect. For a day chart, it is the "Moon".
- **Contra Benefic**: Celestial body that is considered beneficial in the opposite sect. For a day chart, it is "Venus".
- **Contra Malefic**: Celestial body that is considered malevolent in the opposite sect. For a day chart, it is "Mars".

This configuration is critical for the astrological analysis performed by the Fitz system within the Mythos platform. The data from this file is likely used to determine the influence and interpretation of celestial bodies in astrological charts based on the time of day.
