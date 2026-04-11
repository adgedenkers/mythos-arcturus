# skills/analytical/soul_stratigraphy.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 294

---

### Documentation for `skills/analytical/soul_stratigraphy.md`

#### Purpose
This markdown file documents the process and requirements for performing a Soul Stratigraphy, a comprehensive astrological analysis combining Western Tropical, Hellenistic, and Vedic (Jyotish) systems. It outlines the steps, dependencies, and outputs required for generating a detailed report.

#### Architecture
The document is structured into several sections:
- **Purpose**: Describes the high-level goal and context of Soul Stratigraphy.
- **CRITICAL: Use the Ephemeris Engine**: Emphasizes the importance of using real planetary positions.
- **Pre-Flight Checks**: Lists necessary verifications before starting the analysis.
- **Process**: Detailed steps for calculating and analyzing the charts.
- **Validation**: Ensures the accuracy and integrity of the analysis.
- **Error Handling**: Provides guidance on common issues and their resolutions.

#### Patterns
- **Dependency Injection**: The document specifies dependencies like `pyswisseph` and `ephemeris.py`.
- **Configuration Management**: Describes how to handle and validate input data.

#### Dependencies
- **Services**: None.
- **Tools**: `python3`, `pyswisseph`.
- **Files**: `/opt/mythos/skills/analytical/tools/ephemeris.py`.
- **Environment Variables**: None.

#### Interfaces
- **Inputs**: Required inputs include full birth name, birth date, birth time, and birth location. Optional inputs include spiritual lineage, focus areas, and rectification notes.
- **Outputs**: Two files are generated:
  - `soul_stratigraphy_{name}.md`: Full report in Markdown format.
  - `soul_stratigraphy_{name}.json`: Structured data for Neo4j import.

#### Database
- **Tables/Labels**: The JSON output is intended for Neo4j import, but specific labels or tables are not detailed in the document.

#### Configuration
- **Config Files**: None.
- **Environment Variables**: None.

#### Key Logic
- **Ephemeris Calculation**: Uses the `ephemeris.py` script to compute planetary positions for Western Tropical, Hellenistic, and Vedic systems.
- **Chart Analysis**: Analyzes the charts for psychological patterns, karmic structures, and spiritual mechanics.
- **Synthesis**: Combines insights from all three systems to identify convergences, tensions, and soul trajectory.

#### Integration Points
- **Ephemeris Engine**: Integrates with the `ephemeris.py` script to compute planetary positions.
- **Neo4j Import**: The JSON output is designed to be imported into Neo4j for further analysis or storage.

### Detailed Steps and Logic

#### Step 1: Calculate Charts Using the Engine
- **Command**: Uses the `ephemeris.py` script to calculate natal charts.
- **Output**: JSON structure containing all three layers of calculated data.

#### Step 2: Layer 1 Analysis — Western Tropical
- **Core Identity**: Analyzes Sun-Moon-Ascendant.
- **Sect and Dignities**: Evaluates planetary positions and their essential dignities.
- **Aspect Patterns**: Identifies dominant aspect patterns and element/modality balance.

#### Step 3: Layer 2 Analysis — Vedic
- **Sidereal Positions**: Analyzes sidereal positions and Nakshatra placements.
- **Dasha Periods**: Evaluates Vimshottari Dasha timeline.
- **Atmakaraka**: Identifies the planet with the highest degree in any sign.

#### Step 4: Layer 3 Analysis — Hellenistic
- **Sect and Dignities**: Evaluates planetary conditions and bonification/maltreatment.
- **Planetary Joys**: Identifies planetary joys based on Whole Sign houses.
- **Profection Year**: Calculates the profection year and its ruler.

#### Step 5: Synthesis Layer (Layer 4)
- **Convergences and Tensions**: Identifies areas where all systems agree or disagree.
- **Temporal Alignment**: Evaluates periods of maximal activation.
- **Soul Trajectory**: Synthesizes the narrative arc of the soul.

#### Step 6: Format Output
- **Markdown Report**: Generates a detailed report in Markdown format.
- **JSON Data**: Augments the engine output with interpretation data.

#### Validation
- Ensures all positions come from the ephemeris engine output.
- Validates sidereal positions, dasha periods, and profection year.

#### Error Handling
- Provides resolutions for common issues like unknown birth time, ambiguous location, and missing dependencies.

This document serves as a comprehensive guide for performing a Soul Stratigraphy, ensuring accuracy and thoroughness in the astrological analysis.
