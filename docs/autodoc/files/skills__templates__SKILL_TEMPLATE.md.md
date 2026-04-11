# skills/templates/SKILL_TEMPLATE.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 77

---

### Analysis of `skills/templates/SKILL_TEMPLATE.md`

#### Purpose
This markdown file serves as a template for defining new skills in the Mythos system. It outlines the structure and required metadata for a skill, including its name, version, category, risk tier, description, dependencies, inputs, outputs, and detailed process steps.

#### Architecture
The file is structured into several sections:
1. **Metadata**: YAML front matter containing metadata such as `name`, `version`, `category`, `risk_tier`, `description`, `requires`, `inputs`, and `outputs`.
2. **Purpose**: A brief description of the skill's purpose.
3. **Pre-Flight Checks**: Steps to verify prerequisites before execution.
4. **Process**: Detailed steps of the skill's execution, including decision points.
5. **Output Format**: Description of the expected output format.
6. **Error Handling**: Common errors and their resolutions.
7. **Examples**: Example scenarios with inputs, process notes, and outputs.

#### Patterns
- **Template Pattern**: The file is a template that other skill definitions will follow.
- **Configuration Pattern**: The YAML front matter acts as a configuration section for the skill.

#### Dependencies
- **Services**: Listed under `requires.services` (e.g., PostgreSQL, Neo4j, Ollama, FastAPI).
- **Tools**: Listed under `requires.tools` (e.g., Python3, psql, cypher-shell, curl).
- **Files**: Listed under `requires.files` (e.g., `/opt/mythos/docs/ARCHITECTURE.md`).
- **Environment Variables**: Listed under `requires.env_vars` (e.g., `NEO4J_PASSWORD`, `TELEGRAM_BOT_TOKEN`).

#### Interfaces
- **Metadata Interface**: Exposes metadata fields for skill configuration.
- **Process Interface**: Defines the steps and logic for the skill execution.
- **Input/Output Interface**: Specifies required inputs and expected outputs.

#### Database
- **Tables/Labels**: Not directly specified in the template, but may be referenced in the `requires` section or within the process steps.

#### Configuration
- **YAML Front Matter**: Configuration fields such as `name`, `version`, `category`, `risk_tier`, `description`, `requires`, `inputs`, and `outputs`.

#### Key Logic
- **Pre-Flight Checks**: Ensures that all prerequisites are met before the skill execution.
- **Process Steps**: Detailed steps for the skill execution, including decision points and validation.
- **Error Handling**: Defines common errors and their resolutions.

#### Integration Points
- **Skill Manager**: The skill manager component of Mythos will use this template to define and execute skills.
- **Dependency Manager**: Ensures that all required services, tools, files, and environment variables are available.
- **Output Manager**: Handles the output files and formats as specified in the `outputs` section.

### Detailed Breakdown

#### Metadata
- **name**: The name of the skill.
- **version**: The version of the skill.
- **category**: The category of the skill (e.g., analytical, builder).
- **risk_tier**: The risk tier of the skill (e.g., T1-autonomous, T2-patch, T3-propose).
- **description**: A one-paragraph description of the skill, including trigger phrases and contexts.
- **requires**: Dependencies required for the skill, including services, tools, files, and environment variables.
- **inputs**: Required and optional inputs for the skill.
- **outputs**: Files produced, formats, and destinations.

#### Purpose
- Brief description of the skill's purpose and the problem it solves.

#### Pre-Flight Checks
- Steps to verify prerequisites before execution, listed as imperative commands.

#### Process
- Detailed steps of the skill's execution, including decision points and validation.

#### Output Format
- Description of the expected output format, including templates or examples.

#### Error Handling
- Common failure modes and their resolutions, presented in a table format.

#### Examples
- Example scenarios with inputs, process notes, and outputs.

This template ensures consistency and completeness in skill definitions within the Mythos system, making it easier to manage and integrate new skills.
