# mission/templates/audit_handler.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 107

---

### Purpose
The `audit_handler.yaml` file defines a mission for the Mythos system to audit a specific Telegram bot handler file (`finance_handler.py`). It collects information about the file's structure, dependencies, and database interactions, and generates a structured audit report.

### Architecture
The file is structured as a YAML document that defines a mission with the following components:
- **Mission Metadata**: Contains the mission name, version, and description.
- **Model Configuration**: Specifies the AI model (`qwen2.5:32b`) and temperature for generating the audit report.
- **Context**: Collects various pieces of information about the target handler file:
  - **Files**: The path to the target handler file.
  - **Graph Queries**: Cypher queries to retrieve functions defined in the file, files it imports, and files that import it.
  - **PostgreSQL Queries**: SQL query to find related database tables.
- **Phases**: Defines the steps to be executed, primarily the analysis phase.
- **Success**: Defines the actions to be taken upon successful completion of the mission.

### Patterns
- **Template Pattern**: The mission template is a reusable configuration for auditing handler files.
- **Command Pattern**: The mission is executed via a command (`mythos-mission run`).

### Dependencies
- **Neo4j**: For graph queries to retrieve information about the handler file.
- **PostgreSQL**: For SQL queries to find related database tables.
- **File System**: Access to the target handler file (`finance_handler.py`).

### Interfaces
- **Mission Execution**: The mission is executed via a command-line interface.
- **Output**: The audit report is generated as a JSON file at `/tmp/mythos-mission/audit_finance_handler.json`.

### Database
- **Neo4j Labels**: 
  - `IntegrityFile`: Represents files in the system.
  - `IntegrityFunction`: Represents functions defined in the files.
- **PostgreSQL Tables**: 
  - `information_schema.tables`: Used to retrieve table names related to finance, account, transaction, and bill.

### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: The mission configuration is defined within the YAML file itself.

### Key Logic
- **Graph Queries**:
  - Retrieve functions defined in the target handler file.
  - Retrieve files imported by the target handler file.
  - Retrieve files that import the target handler file.
- **SQL Query**:
  - Retrieve related database tables based on specific naming patterns.
- **AI Prompt**:
  - The AI model is prompted to generate a JSON audit report based on the collected information.

### Integration Points
- **Neo4j Integration**: The mission relies on Neo4j to retrieve graph data about the handler file.
- **PostgreSQL Integration**: The mission uses PostgreSQL to find related database tables.
- **File System Integration**: The mission accesses the target handler file from the file system.
- **AI Model Integration**: The mission uses the specified AI model (`qwen2.5:32b`) to generate the audit report.

### Detailed Breakdown

#### Mission Metadata
- **mission**: `audit-handler`
- **version**: `1`
- **description**: Describes the purpose of the mission.

#### Model Configuration
- **model**: `qwen2.5:32b`
- **temperature**: `0.2`

#### Context
- **files**: 
  - Path to the target handler file: `/opt/mythos/telegram_bot/handlers/finance_handler.py`
- **graph**: 
  - Cypher queries to retrieve functions, imports, and dependents.
- **postgres**: 
  - SQL query to find related database tables.

#### Phases
- **analyze**:
  - **description**: Describes the phase.
  - **max_retries**: `1`
  - **prompt**: AI prompt to generate the audit report.
  - **output_format**: `json`
  - **output_alias**: `audit`
  - **output_path**: `/tmp/mythos-mission/audit_finance_handler.json`

#### Success
- **description**: Message upon successful completion.
- **outputs**: Path to the generated audit report.
- **on_success**: Command to log the completion.

This YAML file serves as a comprehensive configuration for auditing a specific handler file within the Mythos system, integrating various components and generating a structured report.
