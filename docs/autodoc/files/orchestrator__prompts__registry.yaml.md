# orchestrator/prompts/registry.yaml

**Language:** yaml
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 311

---

### Documentation for `orchestrator/prompts/registry.yaml`

#### Purpose
This YAML file serves as the central registry for all text components that are used in the prompts for the Iris consciousness pipeline. It ensures that all prompt components are managed in a single, version-controlled source, facilitating easy updates and tracking changes.

#### Architecture
The file is structured into several sections:
- **Global Rules**: Common rules that apply across all workers.
- **Workers**: Specific definitions for each worker (perception, query_builder, query_validator, iris), including model configurations, system prompt components, and user prompt templates.

#### Patterns
- **Configuration Management**: The file acts as a centralized configuration store, ensuring that all prompt components are managed in a single place.
- **Versioning**: Each change to the file increments the version number, ensuring that changes are tracked and version-controlled.

#### Dependencies
- The file does not directly import or rely on any external libraries or modules. However, it is used by the orchestrator to generate and manage prompts dynamically.

#### Interfaces
- The file is read by the orchestrator to dynamically generate prompts based on the defined components and conditions.
- The orchestrator uses this file to ensure that all prompt components are consistent and up-to-date.

#### Database
- The file does not directly interact with any database tables or Neo4j labels. However, it references the schema of the PostgreSQL and Neo4j databases used by the system.

#### Configuration
- The file itself serves as a configuration file, with the `version` and `updated` fields indicating the version and last update date.
- The `system_prompt_components` and `user_prompt_template` fields are used to configure the prompts for each worker.

#### Key Logic
- **Prompt Component Management**: The file manages the text components for each worker, ensuring that they are included based on specific conditions.
- **Version Control**: The versioning system ensures that changes to the prompts are tracked and can be rolled back if necessary.
- **Dynamic Prompt Generation**: The orchestrator reads this file to dynamically generate prompts based on the current state and requirements.

#### Integration Points
- **Orchestrator**: The orchestrator reads this file to generate prompts for the perception, query_builder, query_validator, and iris workers.
- **Workers**: Each worker uses the prompts generated from this file to perform their specific tasks, such as perception analysis, query building, query validation, and generating responses.

### Detailed Breakdown

#### Global Rules
- **json_output**: Ensures that the output is only valid JSON.
- **no_conversation**: Ensures that the worker is not having a conversation but is classifying and extracting information.

#### Workers
- **Perception**:
  - **Model**: `qwen2.5:32b`
  - **System Prompt Components**: Includes role definitions, schema, processing path rules, complexity calibration, and base rules.
  - **User Prompt Template**: Defines the template for user messages.

- **Query Builder**:
  - **Model**: `qwen2.5:32b`
  - **System Prompt Components**: Includes role definitions, schema, rules, and specific database schema details for PostgreSQL and Neo4j.

- **Query Validator**:
  - **Model**: `qwen2.5:7b`
  - **System Prompt Components**: Includes role definitions, schema, and checks for query validation.

- **Iris**:
  - **Model**: `iris-thinking-v2:latest`
  - **System Prompt Components**: Includes identity and voice configurations, and user profile details.

### Example Usage
The orchestrator reads the `registry.yaml` file to dynamically generate prompts for each worker. For example, when generating a prompt for the perception worker, it will include the `perception_role`, `perception_schema`, `perception_path_rules`, `perception_calibration`, and `perception_base_rules` components based on the conditions defined.

### Conclusion
The `registry.yaml` file is a critical component of the Mythos system, ensuring that all prompt components are managed centrally and consistently. It facilitates dynamic prompt generation and version control, making it easier to manage and track changes to the system's prompts.
