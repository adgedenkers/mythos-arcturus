# workers/templates/discovery_template.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Background Workers
**Lines:** 300

---

### File: workers/templates/discovery_template.yaml

#### Purpose
This YAML file defines the configuration and routing table for the DISCOVERY worker in the Mythos system. The DISCOVERY worker is responsible for fetching relevant data from various sources based on the output from the PERCEPTION subsystem, assembling context for further processing by the STRATEGY and IRIS subsystems.

#### Architecture
The file is structured into several sections:
1. **Meta**: Contains metadata about the worker, including node name, layer, version, and recommended model parameters.
2. **Routing Table**: Maps PERCEPTION needs_context flags to specific data source queries.
3. **Query Builder System Prompt**: Defines the prompt for the LLM to generate queries based on perception output.
4. **Query Validator System Prompt**: Defines the prompt for the LLM to validate generated queries before execution.
5. **Discovery Output Schema**: Describes the expected output structure of the DISCOVERY worker.

#### Patterns
- **Template Pattern**: The file serves as a template for configuring the DISCOVERY worker.
- **Routing Table Pattern**: The routing table maps specific flags to data source queries, facilitating dynamic query generation.

#### Dependencies
- **LLM Models**: The file references the `qwen2.5:32b` model for generating and validating queries.
- **Data Sources**: The file depends on PostgreSQL and Neo4j databases, as well as filesystem and command execution capabilities.

#### Interfaces
- **Routing Table**: Exposes a mapping of needs_context flags to specific queries.
- **Query Builder Prompt**: Exposes a structured prompt for generating queries.
- **Query Validator Prompt**: Exposes a structured prompt for validating queries.
- **Output Schema**: Defines the expected output structure for the DISCOVERY worker.

#### Database
- **PostgreSQL Tables**: Various tables such as `transactions`, `bill_payments`, `calendar_events`, `life_events`, `chat_messages`, `astro_natal_charts`, etc.
- **Neo4j Labels**: Various labels such as `Soul`, `Incarnation`, `Person`, `GridNode`, `Exchange`, `Theme`, `Concept`, `GenPerson`, `GenFamily`, `GenPlace`, `Lineage`, `SoulStratigraphy`, `Chart`.

#### Configuration
- **Meta Section**: Contains configuration parameters such as `recommended_model`, `temperature`, `num_predict`, `target_latency_ms`, and `max_latency_ms`.
- **Routing Table**: Configures the data sources and example queries for different contexts.
- **Query Builder and Validator Prompts**: Define the prompts for the LLM to generate and validate queries.

#### Key Logic
- **Query Generation**: The query builder LLM generates queries based on perception output and the routing table.
- **Query Validation**: The query validator LLM ensures the generated queries are safe and correct before execution.
- **Data Fetching**: The worker fetches data from PostgreSQL, Neo4j, filesystem, and command execution based on the generated queries.

#### Integration Points
- **PERCEPTION Subsystem**: Receives needs_context flags from PERCEPTION.
- **STRATEGY and IRIS Subsystems**: Provides assembled context data to STRATEGY and IRIS for further processing.
- **LLM Models**: Integrates with LLM models for query generation and validation.
- **Data Sources**: Integrates with PostgreSQL, Neo4j, filesystem, and command execution for data retrieval.

### Detailed Analysis

#### Meta Section
- **node**: `DISCOVERY`
- **layer**: `2`
- **version**: `1.0.0`
- **created**: `2026-02-25`
- **recommended_model**: `qwen2.5:32b`
- **temperature**: `0.1`
- **num_predict**: `2048`
- **target_latency_ms**: `3000`
- **max_latency_ms**: `8000`

#### Routing Table
The routing table maps needs_context flags to specific data source queries. Each context (e.g., `financial`, `calendar`, `life_data`, `conversation_history`, `cosmology`, `technical_system`, `graph_lookup`) has its own set of sources and example queries.

#### Query Builder System Prompt
The prompt instructs the LLM to generate queries based on perception output and available data sources. The output is expected to be in JSON format, containing a list of queries with details such as `source_type`, `intent`, `query`, `priority`, and `estimated_rows`.

#### Query Validator System Prompt
The prompt instructs the LLM to validate the generated queries for correctness and safety. The output is expected to be in JSON format, containing `approved`, `issues`, `corrected_query`, and `risk_level`.

#### Discovery Output Schema
The output schema defines the structure of the data returned by the DISCOVERY worker, which includes the results of the fetched queries.

### Example Queries
- **PostgreSQL**: Example queries include fetching transaction history, calendar events, life events, chat messages, and astrological chart data.
- **Neo4j**: Example queries include fetching relationships between souls, incarnations, persons, and other entities, as well as general entity and relationship lookups.

### Conclusion
The `discovery_template.yaml` file provides a comprehensive configuration for the DISCOVERY worker, detailing how it integrates with various data sources and LLM models to fetch and validate queries based on PERCEPTION output. This ensures that the STRATEGY and IRIS subsystems receive accurate and relevant context data for further processing.
