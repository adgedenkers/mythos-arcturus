# skills/analytical/western_tropical_natal_chart.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 147

---

### File: skills/analytical/western_tropical_natal_chart.md

#### Purpose
This markdown file describes the process and requirements for generating a Western Tropical natal chart using the Mythos system. It outlines the steps from input validation to chart interpretation and rectification, ensuring all planetary positions are computed using the Swiss Ephemeris engine.

#### Architecture
The file is structured as a markdown document with sections detailing the purpose, critical steps, pre-flight checks, process, and validation. It does not contain any code but provides detailed instructions and guidelines for the implementation of the natal chart generation process.

#### Patterns
No design patterns are used as this is a documentation file and not a code file.

#### Dependencies
- **Services**: None
- **Tools**: `python3`, `pyswisseph`
- **Files**: `/opt/mythos/skills/analytical/tools/ephemeris.py`
- **Environment Variables**: None

#### Interfaces
This file serves as a guide for the implementation of the natal chart generation process. It does not expose any direct interfaces but provides instructions for other parts of the system to follow.

#### Database
No direct database interactions are described in this file. However, the process involves using the ephemeris engine, which might interact with a database to store or retrieve ephemeris data.

#### Configuration
- **Config Files**: None
- **Environment Variables**: None

#### Key Logic
The key logic involves:
1. **Input Validation**: Ensuring all required birth data (date, time, location) is provided.
2. **Ephemeris Engine Execution**: Running the ephemeris engine to compute planetary positions, houses, aspects, and dignities.
3. **Chart Interpretation**: Interpreting the chart based on the computed data, focusing on core identity, emotional nature, interface with the world, and other key features.
4. **Rectification**: Adjusting the birth time if uncertain, using life events to align transits with major life events.
5. **Output Formatting**: Generating a structured report in Markdown and JSON formats.

#### Integration Points
This file integrates with:
- **Ephemeris Engine**: `/opt/mythos/skills/analytical/tools/ephemeris.py` for computing planetary positions and aspects.
- **Mythos System**: The overall Mythos system for handling user requests and generating outputs.
- **Output Storage**: The output files are stored in `/mnt/user-data/outputs/` or sent to the conversation interface.

### Detailed Steps

1. **Pre-Flight Checks**:
   - Verify birth data (date, time, location).
   - Run the ephemeris engine to get real planetary positions.
   - Gather life events for rectification if needed.
   - Confirm house system preference (default Placidus).

2. **Process**:
   - **Step 1: Calculate Positions**: Use the ephemeris engine to compute tropical positions, houses, aspects, and dignities.
   - **Step 2: Identify Key Features**: Identify chart ruler, stellia, aspect patterns, planets on angles, and mutual receptions.
   - **Step 3: Read Aspects**: Prioritize aspects based on orb, luminaries, and geometric patterns.
   - **Step 4: Interpret**: Interpret the chart based on core identity, emotional nature, interface with the world, and other key features.
   - **Step 5: Rectification**: Adjust birth time using life events if uncertain.
   - **Step 6: Format Output**: Generate a structured report in Markdown and JSON formats.

### Validation
- Ensure all positions and aspects are derived from the ephemeris engine output.
- Validate house cusps for the given location and time.
- Ensure interpretation references actual chart positions, not generic descriptions.
- No fabricated degrees should be used.

This markdown file serves as a comprehensive guide for generating and interpreting Western Tropical natal charts within the Mythos system, ensuring accuracy and consistency through the use of the ephemeris engine.
