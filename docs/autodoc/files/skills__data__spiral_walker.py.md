# skills/data/spiral_walker.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 129

---

### File: skills/data/spiral_walker.py

#### Purpose
This file implements the `spiral_walker` skill for the Mythos system, which provides two modes of activation: a morning brief and on-demand responses to queries about the nine-day cycle and transit pressure.

#### Architecture
The file contains three top-level functions:
1. `get_skill_info`: Returns metadata about the skill.
2. `should_activate`: Determines if the skill should activate based on the message content and context.
3. `execute`: Executes the skill logic and returns the appropriate response.

The functions are designed to be modular and self-contained, with clear separation of concerns.

#### Patterns
- **Factory Method**: The `execute` function conditionally builds and returns different types of responses based on whether the morning brief has been delivered.
- **Singleton**: The `logging` module is used as a singleton for logging purposes.

#### Dependencies
- **Imports**: `logging`, `sys`, `datetime.date`, `pathlib.Path`
- **Dynamic Imports**: `astrology.spiral` for specific astrology-related functions.

#### Interfaces
- **`get_skill_info`**: Exposes metadata about the skill.
- **`should_activate`**: Determines the activation score based on the message and context.
- **`execute`**: Executes the skill logic and returns a `SkillResponse`-compatible dictionary.

#### Database
- **PostgreSQL Tables**: `datetime`, `pathlib`, `astrology`, `prompt`
- **Neo4j Labels**: None

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
1. **Activation Logic**:
   - `should_activate` checks if the morning brief has been delivered using `has_brief_been_delivered` from the `astrology.spiral` module.
   - If the morning brief has not been delivered, it returns a high activation score (0.95).
   - Otherwise, it checks for activation keywords in the message and returns a moderate score (0.85) if any keyword matches.

2. **Execution Logic**:
   - `execute` checks if the morning brief has been delivered.
   - If not, it builds the brief context using `build_brief_context` and returns it.
   - If the brief has been delivered, it retrieves the spiral status using `get_spiral_status` and returns it.

#### Integration Points
- **Iris SkillEngine**: The skill is auto-discovered by Iris SkillEngine and integrates with the skill execution framework.
- **Astrology Module**: The skill relies on the `astrology` module for specific astrology-related functionalities like checking if the brief has been delivered, building the brief context, and getting the spiral status.
- **Database**: The skill interacts with PostgreSQL tables for data retrieval and storage, particularly for `datetime`, `pathlib`, `astrology`, and `prompt` tables.

This file is a critical component of the Mythos system, providing dynamic and context-aware responses based on the user's message and the current state of the nine-day cycle.
