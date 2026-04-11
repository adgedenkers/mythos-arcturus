# astrology/charts/fitz/arabic_parts.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 74

---

### File: astrology/charts/fitz/arabic_parts.json

#### Purpose
This JSON file contains data for various Arabic parts (also known as Arabian parts) in an astrological chart for a specific individual named Fitz. Each part includes its longitude, sign, degree and minute, full description, house, and the formula used to calculate its position.

#### Architecture
The file is structured as a JSON object where each key represents an Arabic part (e.g., "Part of Fortune", "Part of Spirit"). Each key maps to another JSON object containing details such as longitude, sign, degree and minute, full description, house, and formula.

#### Patterns
No design patterns are applicable since this is a data file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is intended to be read by other parts of the Mythos system, particularly those responsible for generating or interpreting astrological charts. It does not expose any functions or methods.

#### Database
This file does not directly interact with any database. However, the data it contains could be used to populate or update records in a database.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic here is the representation of the Arabic parts in an astrological chart. Each part's position is calculated using specific formulas involving the Ascendant (ASC), Sun, Moon, Venus, Mars, Saturn, and other astrological points.

#### Integration Points
This file integrates with the astrology subsystem of the Mythos system. Specifically, it is likely used by modules responsible for generating or interpreting astrological charts. The data in this file could be loaded into memory and used to populate an astrological chart or to perform further astrological calculations.

### Detailed Breakdown of Each Arabic Part

1. **Part of Fortune**
   - **Longitude**: 265.94224
   - **Sign**: Sagittarius
   - **DegMin**: 25°56'
   - **Full**: 25°56' Sagittarius
   - **House**: 1
   - **Formula**: ASC + Moon - Sun (day)

2. **Part of Spirit**
   - **Longitude**: 256.208072
   - **Sign**: Sagittarius
   - **DegMin**: 16°12'
   - **Full**: 16°12' Sagittarius
   - **House**: 12
   - **Formula**: ASC + Sun - Moon (day)

3. **Part of Eros**
   - **Longitude**: 214.959568
   - **Sign**: Scorpio
   - **DegMin**: 04°57'
   - **Full**: 04°57' Scorpio
   - **House**: 10
   - **Formula**: ASC + Venus - Part of Spirit

4. **Part of Marriage**
   - **Longitude**: 132.057828
   - **Sign**: Leo
   - **DegMin**: 12°03'
   - **Full**: 12°03' Leo
   - **House**: 8
   - **Formula**: ASC + DSC - Venus

5. **Part of Death**
   - **Longitude**: 208.145526
   - **Sign**: Libra
   - **DegMin**: 28°08'
   - **Full**: 28°08' Libra
   - **House**: 10
   - **Formula**: ASC + 8th cusp - Moon

6. **Part of Commerce**
   - **Longitude**: 251.710536
   - **Sign**: Sagittarius
   - **DegMin**: 11°42'
   - **Full**: 11°42' Sagittarius
   - **House**: 12
   - **Formula**: ASC + Mercury - Sun

7. **Part of Courage**
   - **Longitude**: 201.039241
   - **Sign**: Libra
   - **DegMin**: 21°02'
   - **Full**: 21°02' Libra
   - **House**: 10
   - **Formula**: ASC + Mars - Part of Fortune

8. **Part of Fatality**
   - **Longitude**: 280.09819
   - **Sign**: Capricorn
   - **DegMin**: 10°05'
   - **Full**: 10°05' Capricorn
   - **House**: 1
   - **Formula**: ASC + Saturn - Sun

9. **Part of Passion**
   - **Longitude**: 300.973617
   - **Sign**: Aquarius
   - **DegMin**: 00°58'
   - **Full**: 00°58' Aquarius
   - **House**: 2
   - **Formula**: ASC + Mars - Sun

### Integration with Mythos System
This JSON file is likely used by the astrology subsystem to generate detailed astrological charts for the individual named Fitz. The data can be loaded into the system to provide a comprehensive view of the individual's astrological profile, which can then be used for various purposes such as horoscope generation, astrological analysis, and interpretation.
