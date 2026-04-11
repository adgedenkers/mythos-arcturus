# orchestrator/prompts/templates/discovery.yaml

**Language:** yaml
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 300

---

### File: orchestrator/prompts/templates/discovery.yaml

#### Purpose
This YAML file defines the configuration and routing logic for the DISCOVERY worker in the Mythos system. It maps PERCEPTION output to relevant data sources and provides templates for generating and validating SQL and Cypher queries.

#### Architecture
The file is structured into several sections:
- **Meta**: Contains metadata about the DISCOVERY worker, including version, model recommendations, and latency targets.
- **Routing Table**: Maps PERCEPTION needs_context flags to specific data source queries.
- **Query Builder System Prompt**: Defines the instructions for generating queries based on perception output.
- **Query Validator System Prompt**: Defines the instructions for validating generated queries.
- **Discovery Output Schema**: Describes the expected output format of the DISCOVERY worker.

#### Patterns
- **Configuration Pattern**: The file uses a configuration pattern to store metadata and routing logic.
- **Template Pattern**: Example queries and prompts are provided as templates for query generation and validation.

#### Dependencies
- **Environment**: The file relies on the existence of specific data sources (PostgreSQL, Neo4j, filesystem, and command execution).
- **Models**: The file recommends using the `qwen2.5:32b` model for query generation and validation.

#### Interfaces
- **Input**: PERCEPTION output, which includes needs_context flags.
- **Output**: Structured context package containing relevant data fetched from various sources.

#### Database
- **PostgreSQL Tables**: `transactions`, `bill_payments`, `recurring_bills`, `calendar_events`, `life_events`, `routines`, `chat_messages`, `conversation_segments`, `voice_memo_segments`, `astro_natal_charts`, `astro_natal_aspects`, `astro_chart_points`, `astro_chart_objects`, `astro_natal_house_cusps`, `astro_dignities`, `astro_retrogrades`, `astro_balance`, `astro_sect`, `astro_arabic_parts`, `astro_geometric_patterns`, `astro_fixed_star_conjunctions`, `astro_dispositors`, `astro_chart_ruler`, `harmonic_resonance`, `harmonic_values`.
- **Neo4j Labels**: `Soul`, `Incarnation`, `Person`, `GridNode`, `Exchange`, `Theme`, `Concept`, `Process`, `GenPerson`, `GenFamily`, `GenPlace`, `Lineage`, `SoulStratigraphy`, `Chart`.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: This file itself is a configuration file.

#### Key Logic
- **Routing Logic**: The routing table maps PERCEPTION needs_context flags to specific data sources and queries.
- **Query Generation**: The query builder prompt instructs the LLM to generate queries based on perception output and available data sources.
- **Query Validation**: The query validator prompt instructs the LLM to validate the generated queries for correctness and safety.

#### Integration Points
- **PERCEPTION**: Receives needs_context flags from PERCEPTION.
- **STRATEGY and IRIS**: Provides structured context to STRATEGY and IRIS for further processing.
- **LLM**: Uses LLMs for query generation and validation.
- **Data Sources**: Integrates with PostgreSQL, Neo4j, filesystem, and command execution to fetch data.

### Detailed Breakdown

#### Meta
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
- **financial**: Queries related to financial data from PostgreSQL.
- **calendar**: Queries related to calendar events from PostgreSQL.
- **life_data**: Queries related to life events and routines from PostgreSQL.
- **conversation_history**: Queries related to chat messages and voice memos from PostgreSQL and Neo4j.
- **cosmology**: Queries related to spiritual and astrological data from Neo4j and PostgreSQL.
- **technical_system**: Queries related to system architecture and live state from Neo4j, filesystem, and command execution.
- **graph_lookup**: General entity and relationship lookup from Neo4j.

#### Query Builder System Prompt
- **Instructions**: Generates queries based on perception output and available data sources.
- **Output Schema**: JSON containing queries with `source_type`, `intent`, `query`, `priority`, and `estimated_rows`.

#### Query Validator System Prompt
- **Instructions**: Validates generated queries for correctness and safety.
- **Output Schema**: JSON containing `approved`, `issues`, `corrected_query`, and `risk_level`.

#### Discovery Output Schema
- **Wha**: The file seems to be incomplete, but it would define the expected output format of the DISCOVERY worker.

This YAML file serves as a comprehensive configuration and routing guide for the DISCOVERY worker, enabling efficient data retrieval and validation based on PERCEPTION output.
