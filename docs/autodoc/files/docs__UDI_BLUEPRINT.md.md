# docs/UDI_BLUEPRINT.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 370

---

### Purpose
The `UDI_BLUEPRINT.md` file serves as a comprehensive architectural blueprint for the Unified Data Interface (UDI) within the Mythos system. It outlines the design principles, data layers, search model, dossier model, and future capabilities of the UDI, emphasizing the integration of Neo4j, PostgreSQL, and document stores.

### Architecture
The document is structured into several sections, each detailing specific aspects of the UDI:
- **Executive Vision**: Describes the high-level vision and motivation for the UDI.
- **The Three Data Layers**: Breaks down the roles and current states of Neo4j, PostgreSQL, and the document store.
- **The Unified Search Model**: Explains the search flow and examples.
- **The Dossier Model**: Details how dossiers are assembled for different entity types.
- **Concept & Topic Mapping**: Describes the ontology and auto-extraction pipeline.
- **Capabilities You Haven't Built Yet (But Should)**: Lists future enhancements and capabilities.

### Patterns
- **Graph-First Architecture**: Neo4j is treated as the master index, with other data stores providing supplementary information.
- **Unified Interface**: A single search box that aggregates data from multiple sources.
- **Auto-Extraction Pipeline**: Uses local LLMs to extract named entities, concepts, and temporal markers from documents.

### Dependencies
- **Neo4j**: For storing relationships and identity.
- **PostgreSQL**: For structured records and transactional data.
- **Document Store**: For narrative content.
- **Ollama**: For local LLM-based auto-extraction.

### Interfaces
- **Unified Search Interface**: A single search box that aggregates data from Neo4j, PostgreSQL, and document stores.
- **Dossier Interface**: Provides a complete picture of an entity assembled from all data layers.

### Database
- **Neo4j**: Node labels such as `Person`, `Soul`, `OntologyTerm`, `Document`, `Event`, `Location`.
- **PostgreSQL**: Tables such as `people`, `finance_transactions`, `finance_accounts`, `astrology_data`, `documents_meta`, `events`.
- **Document Store**: Stores text documents and references them in Neo4j.

### Configuration
- **Filesystem Paths**: `/opt/mythos/documents/` for immediate storage.
- **MinIO/S3-compatible Storage**: For larger archives.
- **Full-text Search Engines**: Meilisearch or Typesense for content search.

### Key Logic
- **Graph Traversal**: Identifies connected data by following relationships in Neo4j.
- **Parallel Fetch**: Queries multiple data sources concurrently.
- **Assembly**: Merges results into a unified response object.
- **Auto-Extraction Pipeline**: Uses local LLMs to extract named entities, concepts, and temporal markers from documents.

### Integration Points
- **Neo4j**: Serves as the master index and relationship layer.
- **PostgreSQL**: Provides structured records and transactional data.
- **Document Store**: Stores narrative content and references in Neo4j.
- **Ollama**: Integrates for auto-extraction of entities and concepts from documents.

### Detailed Analysis of Sections

#### Executive Vision
- **Core Principle**: Neo4j is the master index, with other data stores providing supplementary information.

#### The Three Data Layers
- **Neo4j**: Node labels and their counts, roles in UDI.
- **PostgreSQL**: Tables and their roles in UDI.
- **Document Store**: Storage options and future enhancements.

#### The Unified Search Model
- **Search Flow**: Query classification, graph traversal, parallel fetch, assembly, and render.
- **Search Examples**: Demonstrates how different queries are classified and processed.

#### The Dossier Model
- **Person Dossier**: Sections and sources for assembling a complete picture.
- **Concept Dossier**: Definition, related concepts, associated people, documents, timeline.
- **Event Dossier**: Metadata, participants, documents, related events.
- **Document Dossier**: Content preview, metadata, extracted entities, related documents.

#### Concept & Topic Mapping
- **Knowledge Graph Extensions**: New node types and relationships for concept mapping.
- **Auto-Extraction Pipeline**: Extraction of named entities, concepts, temporal markers, sentiment, and summary.

#### Capabilities You Haven't Built Yet (But Should)
- **Temporal Graph**: Time as a first-class dimension.
- **Cross-Domain Correlation Engine**: Finding patterns across data types.
- **Prov**: (Incomplete section, likely to be expanded in future versions).

This blueprint provides a comprehensive guide for implementing the UDI, ensuring seamless integration and unified access to diverse data sources within the Mythos system.
