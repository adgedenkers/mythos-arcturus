# docs/generated/architecture/mission_system.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 24

---

### Documentation for `mission_system`

#### Purpose
The `mission_system` is an LLM-powered component of Mythos designed to analyze missions through YAML-defined multi-phase pipelines. It gathers context from various sources such as files, Postgres databases, Neo4j graphs, and shell commands, renders prompt templates, interacts with the Ollama API for processing, parses the output, and writes results back to files or other storage mediums. This system is particularly adept at conducting "system archaeology" missions that identify dead code, architectural stress points, and hidden patterns within complex software systems.

#### Architecture
The `mission_system` is modular and relies on YAML configuration files to define mission pipelines. Each phase in the pipeline can include steps such as context gathering from different sources (files, databases), rendering prompts, API calls, and output handling. The system is designed to be flexible and extensible, allowing for the addition of new phases and steps as needed.

#### Patterns
- **Modular Design**: The system is designed to be modular, with each phase and step defined in YAML configurations.
- **Pipeline Pattern**: The mission execution follows a pipeline pattern, where each phase is processed sequentially.

#### Dependencies
- **External APIs**: The system relies on the Ollama API for LLM processing.
- **Data Sources**: Integrates with Postgres, Neo4j, file systems, and shell commands to gather context.
- **CLI Tools**: Utilizes custom CLI tools such as `mythos-mission`, `mythos-mission-assemble`, and `graph-bridge` for mission execution and data handling.

#### Interfaces
The `mission_system` exposes interfaces through its CLI tools (`mythos-mission`, `mythos-mission-assemble`, `graph-bridge`) for mission execution and data handling. These tools allow users to define, execute, and manage missions.

#### Database
- **Postgres**: Used for storing mission-related data and context.
- **Neo4j**: Used for storing and querying graph data related to missions.

#### Configuration
- **YAML Configuration Files**: Define mission pipelines and phases.
- **Environment Variables**: Used for configuration settings such as API keys and database connection strings.

#### Key Logic
- **Context Gathering**: Collects information from various sources including files, Postgres databases, Neo4j graphs, and shell commands.
- **Prompt Rendering**: Uses collected data to render prompt templates for LLM processing.
- **LLM Interaction**: Sends prompts to the Ollama API for processing and receives outputs.
- **Output Parsing & Storage**: Parses the output from the LLM and writes results back to files or other storage mediums as specified in the mission configuration.

#### Integration Points
- **Postgres**: For storing mission-related data and context.
- **Neo4j**: For storing and querying graph data related to missions.
- **Ollama API**: For LLM processing.
- **File Systems**: For storing mission outputs and context.
- **Shell Commands**: For executing commands to gather context.
- **CLI Tools**: `mythos-mission`, `mythos-mission-assemble`, `graph-bridge` for mission execution and data handling.

### Known Issues or Technical Debt
- **Lack of Specific Key Files**: The current implementation lacks specific key files and detailed documentation, which may complicate future maintenance and expansion.
- **Error Handling**: There is a need to enhance error handling mechanisms in the context gathering phase from various sources to ensure robustness.
- **Manual Configuration Updates**: Integration with new data sources requires manual configuration updates, indicating potential for automation improvements.
