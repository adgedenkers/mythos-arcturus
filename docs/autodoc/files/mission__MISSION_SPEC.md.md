# mission/MISSION_SPEC.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 112

---

### Purpose
The `MISSION_SPEC.md` file serves as the specification document for the mission files in the Mythos system. It outlines the structure and components of a mission file, detailing how missions are defined, executed, and validated by the system.

### Architecture
The document is structured into several sections, each detailing different aspects of mission files:
1. **Overview**: Describes the purpose and components of a mission file.
2. **Context Sources**: Lists the various sources of context data that can be used in a mission.
3. **Phase Types**: Defines the types of phases that can be included in a mission.
4. **Output Formats**: Specifies the formats in which mission outputs can be returned.
5. **Validation Types**: Details the types of validations that can be performed.
6. **Template Variables**: Explains how to use template variables in mission prompts.
7. **CLI Usage**: Provides command-line examples for executing and validating missions.
8. **Graph Bridge CLI**: Lists commands for interacting with the Neo4j graph database.

### Patterns
The document does not implement any design patterns as it is a specification document rather than executable code.

### Dependencies
The document does not import or rely on any external dependencies. It is a standalone markdown file that serves as a reference for mission file structure and usage.

### Interfaces
The document does not expose any interfaces. It is a specification document that defines the structure and usage of mission files for the Mythos system.

### Database
The document mentions interactions with the PostgreSQL database (`mythos`) and the Neo4j graph database, but it does not specify any particular tables or labels. It only outlines how context can be gathered from these databases through SQL and Cypher queries.

### Configuration
The document does not mention any specific configuration files or environment variables. However, it implies that the mission files themselves are configuration documents that define the tasks and context for the system.

### Key Logic
The key logic described in the document revolves around the structure and execution of mission files:
- **Mission Execution**: Sequential execution of phases, with context injection into Ollama prompts.
- **Validation**: Conditional checks to ensure mission success criteria are met.
- **Context Gathering**: Retrieval of context from various sources (files, directories, databases, shell commands).

### Integration Points
The document integrates with several subsystems of the Mythos system:
- **Claude**: The architect component that generates mission files.
- **Iris/Ollama**: The executor components that run the mission files.
- **PostgreSQL**: For context gathering via SQL queries.
- **Neo4j**: For context gathering via Cypher queries.
- **Shell Commands**: For context gathering via system commands.
- **Graph Bridge CLI**: For interacting with the Neo4j graph database.

### Summary
The `MISSION_SPEC.md` document provides a comprehensive specification for mission files in the Mythos system, detailing their structure, execution flow, and integration with various subsystems. It serves as a critical reference for both the generation and execution of mission files within the Mythos infrastructure.
