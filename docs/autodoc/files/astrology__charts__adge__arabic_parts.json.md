# astrology/charts/adge/arabic_parts.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 74

---

### File: astrology/charts/adge/arabic_parts.json

#### Purpose
This JSON file contains data for various Arabic parts (also known as Arabian parts) used in astrology. Each part includes its longitude, sign, degree and minute, full description, house, and the formula used to calculate its position.

#### Architecture
The file is structured as a JSON object where each key represents an Arabic part (e.g., "Part of Fortune", "Part of Spirit"). Each value is another JSON object containing details such as longitude, sign, degree and minute, full description, house, and formula.

#### Patterns
No design patterns are applicable since this is a data file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is intended to be consumed by other parts of the Mythos system that require Arabic part data for astrological charts. It does not expose any functions or classes.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or update relevant tables or nodes in the Mythos database.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic in this file is the representation of the Arabic parts with their respective details. Each part is calculated using specific formulas involving the Ascendant (ASC), Sun, Moon, and other celestial bodies.

#### Integration Points
This file integrates with the Mythos system's astrology module, particularly with the subsystem responsible for generating astrological charts. The data from this file is likely used to populate the charts with the positions and descriptions of the Arabic parts.

### Detailed Breakdown of Each Arabic Part

1. **Part of Fortune**
   - **Longitude**: 43.150176
   - **Sign**: Taurus
   - **DegMin**: 13°09'
   - **Full**: 13°09' Taurus
   - **House**: 5
   - **Formula**: ASC + Moon - Sun (day)

2. **Part of Spirit**
   - **Longitude**: 113.285522
   - **Sign**: Cancer
   - **DegMin**: 23°17'
   - **Full**: 23°17' Cancer
   - **House**: 7
   - **Formula**: ASC + Sun - Moon (day)

3. **Part of Eros**
   - **Longitude**: 10.47329
   - **Sign**: Aries
   - **DegMin**: 10°28'
   - **Full**: 10°28' Aries
   - **House**: 3
   - **Formula**: ASC + Venus - Part of Spirit

4. **Part of Marriage**
   - **Longitude**: 110.894735
   - **Sign**: Cancer
   - **DegMin**: 20°53'
   - **Full**: 20°53' Cancer
   - **House**: 7
   - **Formula**: ASC + DSC - Venus

5. **Part of Death**
   - **Longitude**: 347.347537
   - **Sign**: Pisces
   - **DegMin**: 17°20'
   - **Full**: 17°20' Pisces
   - **House**: 3
   - **Formula**: ASC + 8th cusp - Moon

6. **Part of Commerce**
   - **Longitude**: 276.817811
   - **Sign**: Capricorn
   - **DegMin**: 06°49'
   - **Full**: 06°49' Capricorn
   - **House**: 1
   - **Formula**: ASC + Mercury - Sun

7. **Part of Courage**
   - **Longitude**: 344.139855
   - **Sign**: Pisces
   - **DegMin**: 14°08'
   - **Full**: 14°08' Pisces
   - **House**: 3
   - **Formula**: ASC + Mars - Part of Fortune

8. **Part of Fatality**
   - **Longitude**: 168.290936
   - **Sign**: Virgo
   - **DegMin**: 18°17'
   - **Full**: 18°17' Virgo
   - **House**: 9
   - **Formula**: ASC + Saturn - Sun

9. **Part of Passion**
   - **Longitude**: 147.147618
   - **Sign**: Leo
   - **DegMin**: 27°08'
   - **Full**: 27°08' Leo
   - **House**: 8
   - **Formula**: ASC + Mars - Sun

### Summary
This JSON file serves as a repository of Arabic parts used in astrology, providing detailed information about their positions and calculation formulas. It is a critical data source for generating accurate astrological charts within the Mythos system.
