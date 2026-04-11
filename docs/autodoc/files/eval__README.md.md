# eval/README.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 229

---

### Purpose
The `eval/README.md` file provides comprehensive documentation for the Chunk Factory, a subsystem within the Mythos system that evaluates local Ollama models' ability to generate valid Mythos skills (radioactive chunks) based on structured specifications. It includes instructions, directory structure, and details on how to create and run new challenges.

### Architecture
The file is structured as a README document, detailing the purpose, usage, and inner workings of the Chunk Factory. It includes:
- **Quick Start**: Basic command-line usage.
- **How It Works**: Detailed flowchart and description of the evaluation loop.
- **Validation Checks**: Criteria for validating generated code.
- **Directory Structure**: Layout of the `eval` directory.
- **Creating a New Challenge**: Steps to define and run a new challenge.
- **Recommended Models**: List of suitable Ollama models.
- **Interpreting Results**: Guidance on understanding the evaluation outcomes.
- **Integration with Iris**: Information on deploying validated skills.

### Patterns
The file does not contain code but describes the system's architecture and flow, which follows a recursive evaluation pattern and uses a composite score to determine the success of generated skills.

### Dependencies
The file does not directly import or rely on any code dependencies but references:
- `ollama_builder.py`: The recursive evaluation harness.
- `chunk-eval.sh`: The CLI wrapper script.
- `SKILL.md`: Instructions for skill generation.
- `challenge_schema.json`: JSON schema for challenge specifications.
- `challenge_spec.json`: Specific challenge specifications.
- `gold/`: Directory containing gold standard files.

### Interfaces
The file exposes a CLI interface through `chunk-eval.sh` for running evaluations, listing challenges, and comparing results.

### Database
The file mentions the use of PostgreSQL for database connections within the generated skills but does not detail specific tables or queries.

### Configuration
The file references environment variables and configuration files implicitly through the `chunk-eval.sh` script and the `challenge_spec.json` schema.

### Key Logic
The key logic described involves:
- **Evaluation Loop**: Iteratively generating and validating code until a valid skill is produced or iterations are exhausted.
- **Validation Checks**: Ensuring the generated code meets structural and behavioral criteria.
- **Gold Standard Comparison**: Comparing the generated code against a gold standard for similarity and structural accuracy.

### Integration Points
The Chunk Factory integrates with:
- **Ollama Models**: Local language models for generating code.
- **Skill Engine**: Deploying validated skills to `/opt/mythos/skills/data/` for use by the Mythos system.
- **CLI**: `chunk-eval.sh` for user interaction and script execution.

### Summary
The `eval/README.md` file serves as a comprehensive guide for setting up, running, and interpreting the results of the Chunk Factory subsystem within the Mythos system. It details the evaluation process, validation criteria, and integration with other components, providing a clear roadmap for users and developers.
