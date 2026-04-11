# workers/templates/perception_template.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Background Workers
**Lines:** 579

---

### File: workers/templates/perception_template.yaml

#### Purpose
This YAML file defines the configuration and behavior of the `PERCEPTION` worker in the Mythos system. It specifies the model configuration, performance targets, system prompt, user prompt template, and example inputs and outputs for training and validation.

#### Architecture
The file is structured into several sections:
- **Meta**: Contains metadata about the worker, including the node name, layer, grid functions, version, creation date, model configuration, and performance targets.
- **System Prompt**: A detailed prompt that guides the language model (LLM) on how to process and classify messages.
- **User Prompt Template**: A template for formatting user messages before sending them to the LLM.
- **Examples**: Sample inputs and expected outputs used for few-shot prompting and validation.

#### Patterns
- **Configuration Pattern**: The file uses a configuration pattern to store and manage settings and behavior of the `PERCEPTION` worker.
- **Template Pattern**: The user prompt template and system prompt use a template pattern to ensure consistent formatting and structure.

#### Dependencies
- **Environment**: This file does not directly import any code or libraries but relies on the Mythos system's infrastructure to interpret and use the configuration.
- **Models**: It references specific models like `qwen2.5:7b` and fallback models.

#### Interfaces
- **External Systems**: This template is used by the `PERCEPTION` worker to configure and interact with the LLM. It provides the system prompt and user prompt template to the LLM.
- **Data Flow**: The `PERCEPTION` worker receives raw messages, processes them according to the system prompt, and outputs structured JSON.

#### Database
- **Neo4j**: The `grid_hints` section in the output JSON suggests that this worker might interact with Neo4j for entity and relationship lookups.
- **PostgreSQL**: No direct interaction is specified, but the `technical_system` context might involve PostgreSQL queries.

#### Configuration
- **Environment Variables**: The file does not explicitly use environment variables but relies on the Mythos system's configuration to interpret the metadata and prompts.
- **Config Files**: This file itself is a configuration file used by the `PERCEPTION` worker.

#### Key Logic
- **Classification Logic**: The system prompt defines the logic for classifying messages into types like `greeting`, `life_event`, `question_technical`, etc.
- **Complexity Calibration**: The system prompt includes rules for determining the complexity and processing path of messages.
- **Grid Hints**: The system prompt guides the LLM on how to estimate the relevance of different grid nodes.

#### Integration Points
- **Downstream Workers**: The `PERCEPTION` worker outputs structured JSON that is used by downstream workers in the Mythos system.
- **Iris**: The `processing_path` in the output JSON directs the message to the appropriate stage in the processing pipeline, ultimately leading to the `Iris` worker.
- **Data Discovery**: The `needs_context` field in the output JSON drives data discovery stages in the pipeline, potentially involving queries to Neo4j and PostgreSQL.

### Summary
The `perception_template.yaml` file is a critical configuration file for the `PERCEPTION` worker in the Mythos system. It defines the behavior, model configuration, and expected output format for classifying and processing messages. The file integrates with downstream workers and data discovery stages, ensuring that messages are appropriately routed and processed based on their content and complexity.
