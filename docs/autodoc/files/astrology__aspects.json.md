# astrology/aspects.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 90

---

### File: astrology/aspects.json

#### Purpose
This JSON file contains a comprehensive list of astrological aspects, each defined by its angle, orb, and a descriptive interpretation. This data is likely used by the Mythos system to interpret astrological charts and provide insights based on the relationships between celestial bodies.

#### Architecture
The file is structured as a JSON object where each key represents an astrological aspect. Each aspect is further defined by a nested object containing three properties: `Angle`, `Orb`, and `Description`.

#### Patterns
There are no design patterns used in this JSON file as it is a simple data structure.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is likely read by other parts of the Mythos system, such as a service or module that interprets astrological data. The data is exposed through the JSON structure, which can be parsed and accessed programmatically.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data it contains might be used to populate or reference entries in a database.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic revolves around the definition and interpretation of astrological aspects. Each aspect is defined by its angle and orb, which are used to determine the influence and significance of the aspect in an astrological chart.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly with modules or services that interpret astrological data. For example, a service that calculates and interprets planetary positions might use this file to determine the significance of the aspects formed between planets.

### Detailed Breakdown

1. **Conjunction**: 
   - **Angle**: 0 degrees
   - **Orb**: 8.0 degrees
   - **Description**: Merges energies; very powerful; can be harmonious or conflicting depending on planets involved.

2. **Opposition**: 
   - **Angle**: 180 degrees
   - **Orb**: 7.0 degrees
   - **Description**: Polarization; reflection and projection; potential for balance or conflict.

3. **Trine**: 
   - **Angle**: 120 degrees
   - **Orb**: 7.0 degrees
   - **Description**: Harmonious and easy energy exchange; talents and natural flows.

4. **Square**: 
   - **Angle**: 90 degrees
   - **Orb**: 6.0 degrees
   - **Description**: Dynamic tension; challenges that drive growth and confrontation.

5. **Sextile**: 
   - **Angle**: 60 degrees
   - **Orb**: 6.5 degrees
   - **Description**: Easy flow of energy; opportunities that require initiative.

6. **Quincunx**: 
   - **Angle**: 150 degrees
   - **Orb**: 3.0 degrees
   - **Description**: Adjustment aspect; incongruent energies that must compromise or shift.

7. **Semi-sextile**: 
   - **Angle**: 30 degrees
   - **Orb**: 3.0 degrees
   - **Description**: Mildly positive; represents potential growth through minor adjustments.

8. **Semi-square**: 
   - **Angle**: 45 degrees
   - **Orb**: 3.0 degrees
   - **Description**: Minor tension; encourages action through subtle challenge. (Also called Octile.)

9. **Sesquiquadrate**: 
   - **Angle**: 135 degrees
   - **Orb**: 3.5 degrees
   - **Description**: Minor challenging aspect; irritations that require discipline.

10. **Quintile**: 
    - **Angle**: 72 degrees
    - **Orb**: 2.5 degrees
    - **Description**: Creative/talent-driven link; refined skill or artistry.

11. **Biquintile**: 
    - **Angle**: 144 degrees
    - **Orb**: 2.0 degrees
    - **Description**: Harmonic creative flow; specialized talents or genius-level expression.

12. **Decile**: 
    - **Angle**: 36 degrees
    - **Orb**: 1.5 degrees
    - **Description**: Semi-quintile; subtle creativity, finesse and technique.

13. **Tridecile**: 
    - **Angle**: 108 degrees
    - **Orb**: 1.5 degrees
    - **Description**: Quintile family; inventive, elegant problem solving.

14. **Quindecile**: 
    - **Angle**: 165 degrees
    - **Orb**: 1.5 degrees
    - **Description**: Intense focus/compulsion; persistent drive toward integration.

15. **Septile**: 
    - **Angle**: 51.428571 degrees
    - **Orb**: 1.2 degrees
    - **Description**: Subtle, numinous link; inspiration/obsession, 'fated' vibe.

16. **Biseptile**: 
    - **Angle**: 102.857143 degrees
    - **Orb**: 1.2 degrees
    - **Description**: Septile family; unusual timing/synchrony, creative compulsion.

17. **Triseptile**: 
    - **Angle**: 154.285714 degrees
    - **Orb**: 1.2 degrees
    - **Description**: Septile family; inner calling, synchronistic pressure to adjust.

### Summary
This JSON file serves as a foundational data source for astrological interpretations within the Mythos system. It provides a structured and detailed list of astrological aspects, which can be used by various components of the system to generate meaningful insights based on astrological data.
