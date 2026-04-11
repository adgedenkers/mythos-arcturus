# orchestrator/prompts/templates/perception.yaml

**Language:** yaml
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 579

---

### File: orchestrator/prompts/templates/perception.yaml

#### Purpose
This YAML file defines the configuration and templates for the PERCEPTION worker in the Mythos system. It specifies the system prompt, user prompt template, and example inputs and outputs to guide the LLM in processing raw messages and generating structured JSON responses.

#### Architecture
The file is structured into several sections:
- **Meta**: Contains metadata about the node, including the recommended model, performance targets, and grid functions.
- **System Prompt**: Defines the instructions and output schema for the LLM.
- **User Prompt Template**: Provides a template for wrapping user messages.
- **Examples**: Includes sample inputs and expected outputs for few-shot prompting and validation.

#### Patterns
- **Configuration Pattern**: The file uses a configuration pattern to define settings and templates for the PERCEPTION worker.
- **Template Pattern**: The user prompt template and system prompt use a template pattern to ensure consistent formatting.

#### Dependencies
- **Environment**: The file relies on the LLM (e.g., qwen2.5:7b) to process the messages.
- **Configuration Files**: The file is part of a larger configuration system and may be referenced by other parts of the Mythos infrastructure.

#### Interfaces
- **Input**: The PERCEPTION worker receives raw messages from users.
- **Output**: The worker outputs structured JSON responses according to the defined schema.

#### Database
- **Neo4j**: The `grid_hints` and `needs_context` fields may require Neo4j queries for entity and relationship lookups.
- **PostgreSQL**: The `needs_context` field may require queries to the PostgreSQL database for various data lookups.

#### Configuration
- **Environment Variables**: The file does not directly use environment variables but relies on the system configuration for model selection and performance targets.
- **Config Files**: The file itself is a configuration file used by the PERCEPTION worker.

#### Key Logic
- **Message Classification**: The system prompt guides the LLM to classify messages into specific types (e.g., greeting, question_technical) and determine their complexity.
- **Grid Hints Calculation**: The LLM calculates grid hints based on the message content to guide downstream processing.
- **Context Needs Determination**: The LLM determines which external data sources are needed to improve the response.

#### Integration Points
- **Upstream**: The PERCEPTION worker receives raw messages from the user interface or other upstream components.
- **Downstream**: The structured JSON output is passed to other components (e.g., Stages 2-3 of the pipeline) for further processing.
- **LLM**: The PERCEPTION worker interacts with the LLM to process messages and generate responses.
- **Database**: The worker may trigger database queries based on the `needs_context` field in the output JSON.

### Detailed Breakdown

#### Meta Section
- **node**: "PERCEPTION"
- **layer**: 1
- **grid_functions**: List of grid functions the PERCEPTION worker interacts with.
- **version**: "1.0.0"
- **created**: "2026-02-25"
- **recommended_model**: "qwen2.5:7b"
- **temperature**: 0.1
- **num_predict**: 1024
- **target_latency_ms**: 1500
- **max_latency_ms**: 3000

#### System Prompt
- **Instructions**: The LLM is instructed to analyze raw messages and output structured JSON.
- **Output Schema**: Defines the structure of the JSON output, including fields like `message_type`, `complexity`, `processing_path`, `entities`, `grid_hints`, `emotion`, `energy`, `topics`, `references_past`, `needs_context`, and `response_guidance`.
- **Field Definitions**: Provides detailed explanations for each field in the output schema.

#### User Prompt Template
- **Template**: Wraps user messages with metadata like speaker name, timestamp, and gap since the last message.

#### Examples
- **Inputs and Outputs**: Provides sample inputs and expected outputs to guide the LLM in generating consistent and accurate responses.

### Summary
The `perception.yaml` file serves as a comprehensive configuration and template guide for the PERCEPTION worker in the Mythos system. It ensures that raw messages are processed consistently and that the output is structured in a way that can be easily consumed by downstream components. The file integrates with the LLM and potentially with the Neo4j and PostgreSQL databases for context lookups.
