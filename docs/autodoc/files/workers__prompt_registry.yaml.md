# workers/prompt_registry.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Background Workers
**Lines:** 311

---

### Documentation for `workers/prompt_registry.yaml`

#### Purpose
This YAML file serves as the central registry for all text components that form part of the prompts used in the Mythos system's LLM (Large Language Model) pipeline. It ensures that all prompt components are managed centrally, version-controlled, and applied consistently across different workers (e.g., perception, query_builder, query_validator, iris).

#### Architecture
The file is structured into several sections:
- **Global Rules**: Common rules that apply across all workers.
- **Workers**: Specific configurations for each worker, including their system prompt components and user prompt templates.
- **Versioning**: Tracks changes and updates to the registry.

#### Patterns
- **Configuration Management**: The file acts as a centralized configuration store, ensuring all prompt components are managed in one place.
- **Version Control**: Each change to the registry increments the version number, allowing for tracking and auditing.

#### Dependencies
- **Environment**: The file is read by the Mythos system's orchestrator and other components.
- **Files**: Some components reference external files (e.g., `iris_identity.md`, `voice.yaml`).

#### Interfaces
- **Orchestrator**: The orchestrator reads this file to construct prompts dynamically.
- **Workers**: Each worker uses the relevant sections of this file to configure their prompts.

#### Database
- **No Direct Database Interaction**: This file does not directly interact with databases. However, it contains information about database schemas and query structures that are used by workers.

#### Configuration
- **Versioning**: The `version` and `updated` fields track changes.
- **Worker Configurations**: Each worker has its own configuration, including model settings and prompt components.

#### Key Logic
- **Prompt Component Management**: Ensures that all prompt components are defined, version-controlled, and applied consistently.
- **Condition-Based Inclusion**: Components are included based on conditions (e.g., `always`).

#### Integration Points
- **Orchestrator**: The orchestrator reads this file to construct prompts.
- **Workers**: Each worker uses the relevant sections of this file to configure their prompts.
- **External Files**: References to external files (e.g., `iris_identity.md`, `voice.yaml`) are used to inject additional content into prompts.

### Detailed Breakdown

#### Global Rules
- **json_output**: Ensures that all outputs are in valid JSON format.
- **no_conversation**: Ensures that workers are not in a conversational mode but are focused on specific tasks.

#### Workers
- **Perception**:
  - **Model**: `qwen2.5:32b`
  - **System Prompt Components**: Defines roles, schemas, and rules for processing messages.
  - **User Prompt Template**: Template for user messages.

- **Query Builder**:
  - **Model**: `qwen2.5:32b`
  - **System Prompt Components**: Defines roles, schemas, and rules for generating queries.
  - **Postgres Schema**: Details of key tables in the PostgreSQL database.
  - **Neo4j Schema**: Details of key node types and relationships in the Neo4j graph database.

- **Query Validator**:
  - **Model**: `qwen2.5:7b`
  - **System Prompt Components**: Defines roles, schemas, and checks for validating queries.

- **Iris**:
  - **Model**: `iris-thinking-v2:latest`
  - **System Prompt Components**: References external files for identity and voice configuration.

### Example Components
- **Perception**:
  ```yaml
  system_prompt_components:
    - id: "perception_role"
      order: 1
      text: "You are a perception processor. Your ONLY job is to analyze a raw message and output structured JSON describing what is present in the message."
      condition: always
  ```

- **Query Builder**:
  ```yaml
  system_prompt_components:
    - id: "qb_role"
      order: 1
      text: "You are a query builder. Given a user's message, perception analysis, and available data sources, generate the exact queries needed to fetch relevant context."
      condition: always
  ```

- **Query Validator**:
  ```yaml
  system_prompt_components:
    - id: "qv_role"
      order: 1
      text: "You are a query validator. Review the following query for correctness and safety before execution."
      condition: always
  ```

- **Iris**:
  ```yaml
  system_prompt_components:
    - id: "iris_identity"
      order: 1
      source: "file:/opt/mythos/iris/core/iris_identity.md"
      condition: always
  ```

This YAML file ensures that all prompt components are managed centrally, version-controlled, and applied consistently across different workers, thereby maintaining the integrity and consistency of the Mythos system's LLM pipeline.
