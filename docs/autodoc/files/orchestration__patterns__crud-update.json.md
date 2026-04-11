# orchestration/patterns/crud-update.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 384

---

### File: orchestration/patterns/crud-update.json

#### Purpose
This JSON file defines the "CRUD Updates Pattern" for the Mythos system, which outlines a structured approach to handle changes across PostgreSQL, Neo4j, and flat files. It includes triggers, context gathering commands, and stages for reconnaissance and planning.

#### Architecture
The file is structured into several sections:
- **Pattern Metadata**: Contains basic information like `pattern_id`, `name`, `version`, and `description`.
- **Trigger**: Defines keywords and intent types that trigger this pattern, along with preconditions.
- **Data Layer Detection**: Rules for determining which data layers are affected by the request.
- **Context Gathering**: Commands and files to gather necessary context for analysis.
- **Stages**: Detailed stages for reconnaissance and planning, each with specific execution parameters.

#### Patterns
- **Trigger Patterns**: Uses keywords and intent types to match user requests.
- **Context Gathering**: Uses commands to gather data from different layers.
- **Stages**: Uses a structured approach with dependencies and execution modes.

#### Dependencies
- **PostgreSQL**: Commands to interact with PostgreSQL.
- **Neo4j**: Commands to interact with Neo4j.
- **Flat Files**: Commands to interact with flat files.
- **System Commands**: Uses `find`, `cat`, `grep`, `ls`, `systemctl`, etc.

#### Interfaces
- **Input Contract**: Specifies the input data required for each stage.
- **Output Contract**: Specifies the expected output format and required fields for each stage.

#### Database
- **PostgreSQL**: Interacts with tables, columns, and indexes.
- **Neo4j**: Interacts with node labels, relationship types, and node counts.
- **Flat Files**: Interacts with configuration files, markdown documents, and JSON files.

#### Configuration
- **Environment Variables**: Uses `.env` file for Neo4j password.
- **Files**: Uses `/opt/mythos/docs/TODO.md` and `/opt/mythos/docs/ARCHITECTURE.md`.

#### Key Logic
- **Reconnaissance Stage**: Analyzes the current state of the system across all three data layers and produces a gap analysis.
- **Plan Stage**: Produces a concrete plan based on the reconnaissance analysis, ensuring cross-layer consistency.

#### Integration Points
- **PostgreSQL**: Uses `psql` commands to gather schema and row counts.
- **Neo4j**: Uses `cypher-shell` commands to gather labels, relationship types, and node counts.
- **Flat Files**: Uses `find` and `cat` to gather file contents.
- **Code**: Uses `grep` and `find` to gather code files and bot handlers.
- **Services**: Uses `systemctl` to gather service statuses.
- **Environment**: Uses `cat` to gather environment configurations.

### Detailed Analysis

#### Pattern Metadata
- **pattern_id**: `crud-update`
- **name**: `CRUD Updates Pattern`
- **version**: `2.0.0`
- **description**: Describes the pattern's purpose and scope.

#### Trigger
- **Keywords**: List of keywords that trigger the pattern.
- **Intent Types**: List of intent types that match user requests.
- **Preconditions**: Conditions that must be met for the pattern to be triggered.

#### Data Layer Detection
- **Rules**: Defines indicators for each data layer (PostgreSQL, Neo4j, Flat Files) to determine which layers are affected by the request.

#### Context Gathering
- **Commands**: List of commands to gather context from different layers.
  - **PostgreSQL**: Commands to gather schema, row counts, and indexes.
  - **Neo4j**: Commands to gather labels, relationship types, node counts, and schema visualization.
  - **Flat Files**: Commands to gather file inventory and contents.
  - **Code**: Commands to gather code files and bot handlers.
  - **Services**: Commands to gather service statuses.
  - **Environment**: Commands to gather environment configurations.

#### Stages
- **Reconnaissance Stage**:
  - **Name**: `Multi-Layer Reconnaissance`
  - **Description**: Analyzes the current state across all three data layers and produces a gap analysis.
  - **Execution**: Uses an LLM (Language Model) to generate a JSON analysis.
  - **Input Contract**: Specifies the input data required.
  - **Output Contract**: Specifies the expected output format and required fields.

- **Plan Stage**:
  - **Name**: `Multi-Layer Change Plan`
  - **Description**: Produces a concrete plan based on the reconnaissance analysis.
  - **Depends On**: Depends on the `recon` stage.
  - **Execution**: Details on how the plan is generated.

### Conclusion
This JSON file serves as a comprehensive blueprint for handling CRUD updates across multiple data layers in the Mythos system. It includes detailed context gathering, reconnaissance, and planning stages to ensure consistency and accuracy in system changes.
