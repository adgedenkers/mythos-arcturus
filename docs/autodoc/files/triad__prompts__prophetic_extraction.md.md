# triad/prompts/prophetic_extraction.md

**Language:** markdown
**Stream:** LOG
**Module:** Triad Identity System
**Lines:** 74

---

### Documentation for `triad/prompts/prophetic_extraction.md`

#### Purpose
This markdown file contains a detailed prompt for the Prophetic Extraction process within the Mythos system. The prompt guides the AI to sense and articulate the trajectory, attractor state, readiness signals, obstacles, invitations, seeds, and convergences from a given conversation or dataset.

#### Architecture
The file is structured as a markdown document that outlines various sections for the AI to consider:
1. **Trajectory / Vector**: Identifies the direction of movement.
2. **The Attractor**: Describes the future state the current pattern is moving towards.
3. **Readiness Signal**: Assesses what is nearly ready to manifest.
4. **Obstacle Sensed**: Identifies potential obstacles.
5. **Invitation**: Describes the next authentic step.
6. **Seed Present**: Identifies small elements that will grow later.
7. **Convergence**: Identifies threads converging with the current one.

The output is expected to be in a specific JSON format.

#### Patterns
This file does not directly implement design patterns but serves as a template or prompt for the AI to follow, which can be seen as a form of the Template Method pattern where the structure and steps are predefined.

#### Dependencies
This file does not directly import or rely on any external libraries or modules. It is a configuration file that guides the AI's behavior.

#### Interfaces
The file interfaces with the AI component of the Mythos system, specifically guiding the AI's analysis and output format. It does not expose any direct functions or classes but serves as a configuration for the AI's processing logic.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the AI's output based on this prompt might be stored in a database for further analysis or logging.

#### Configuration
The file itself acts as a configuration for the AI's analysis process. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic is embedded in the prompt's structure and the JSON output format. The AI must interpret the given conversation or dataset and map its findings to the predefined sections and output format.

#### Integration Points
This file integrates with the AI component of the Mythos system, particularly with the Ollama AI service. The AI processes the conversation or dataset using this prompt and produces the structured JSON output. The output might be further processed or stored in other components of the Mythos system, such as PostgreSQL or Neo4j.

### Summary
The `prophetic_extraction.md` file serves as a detailed prompt for the AI to analyze and interpret the trajectory, attractor state, readiness signals, obstacles, invitations, seeds, and convergences from a given conversation or dataset. It guides the AI to produce a structured JSON output, integrating with the Mythos system's AI component to provide insights and predictions based on the provided data.
