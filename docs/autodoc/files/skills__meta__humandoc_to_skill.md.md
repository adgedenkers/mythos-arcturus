# skills/meta/humandoc_to_skill.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 198

---

### Purpose
The `humandoc_to_skill.md` file serves as a detailed guide for converting human-readable documents, process descriptions, or informal instructions into structured Mythos skill files. This document outlines the steps and considerations required to transform these inputs into executable skills that Iris, the Mythos system, can reliably process.

### Architecture
The file is structured as a markdown document with sections for:
- **Pre-Flight Checks**: Initial verification steps before starting the conversion.
- **Process**: A step-by-step guide detailing the extraction of core process elements, resolving ambiguities, converting to imperative instructions, structuring the skill file, determining trigger conditions, validating the skill, and generating outputs.
- **Output Format**: Describes the format of the generated skill file and registry entry.
- **Error Handling**: Lists potential errors and their resolutions.
- **Examples**: Provides a concrete example of the conversion process.

### Patterns
The document follows a **template pattern** by using the `SKILL_TEMPLATE.md` as a reference for structuring the skill file. It also uses a **step-by-step guide pattern** to ensure a systematic approach to the conversion process.

### Dependencies
- **Files**: 
  - `/opt/mythos/skills/templates/SKILL_TEMPLATE.md`
  - `/opt/mythos/skills/REGISTRY.yaml`
- **Environment Variables**: None
- **Services/Tools**: None

### Interfaces
The document exposes a detailed process for converting human-readable documents into Mythos skill files. It does not expose any direct interfaces but serves as a guide for human operators to create new skills.

### Database
- **Neo4j Labels/Tables**: None
- **Files**: 
  - `/opt/mythos/skills/{category}/{skill_name}.md` (generated skill file)
  - `/opt/mythos/skills/REGISTRY.yaml` (updated with new skill entry)

### Configuration
- **Config Files**: None
- **Environment Variables**: None

### Key Logic
The key logic involves:
1. **Extracting Core Process**: Identifying the goal, inputs, steps, decisions, outputs, and validation criteria from the source document.
2. **Resolving Ambiguity**: Ensuring all steps are clear and unambiguous.
3. **Converting to Imperative Instructions**: Transforming narrative descriptions into precise, executable commands.
4. **Structuring the Skill File**: Using the `SKILL_TEMPLATE.md` to format the skill file.
5. **Determining Trigger Conditions**: Writing conditions for the skill to be invoked.
6. **Validating the Skill**: Ensuring the skill is complete and unambiguous.
7. **Generating Outputs**: Producing the skill file and updating the registry.

### Integration Points
This document integrates with:
- **Skill Registry**: The generated skill file is added to the registry (`REGISTRY.yaml`).
- **Skill Execution**: The structured skill file can be executed by Iris, the Mythos system.
- **Human Operators**: Human operators use this document to create new skills based on human-readable inputs.

### Summary
The `humandoc_to_skill.md` document provides a comprehensive guide for converting human-readable documents into structured Mythos skill files. It outlines a step-by-step process for extracting and structuring the necessary information, ensuring the resulting skill is executable and reliable within the Mythos system.
