# docs/PERSON_NODE_SPEC.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 432

---

### Purpose
This document defines the various types of person-representing nodes in the Mythos Neo4j graph, detailing their properties, creation methods, and relationships. It serves as a comprehensive specification for managing different types of person nodes, ensuring consistency and clarity in the system.

### Architecture
The document is structured into sections that define each node type (`CorePerson`, `Person`, `GenPerson`, `Soul`, `Incarnation`, `Entity`), their properties, creation methods, and relationships. Each section provides a clear definition, required and optional properties, and ownership details.

### Patterns
- **Singleton Pattern**: Not applicable in this document.
- **Factory Pattern**: Not applicable in this document.
- **Observer Pattern**: Not applicable in this document.

### Dependencies
This document does not import or rely on any specific code files or libraries. It is a specification document that guides the implementation of person nodes in the Neo4j graph.

### Interfaces
This document does not expose any interfaces directly. Instead, it serves as a reference for developers and system administrators to understand and implement the person node types in the Neo4j graph.

### Database
The document specifies the Neo4j graph schema and the properties for each node type. It also defines the relationships between these nodes.

### Configuration
The document does not reference any specific configuration files or environment variables. However, it implies the need for configuration in the form of manual creation instructions and automated entity detection settings.

### Key Logic
The key logic revolves around defining and managing different types of person nodes, ensuring that each node type has the correct properties and relationships. The document also outlines the process for transitioning nodes from one type to another as understanding deepens.

### Integration Points
- **SYS Stream**: Responsible for creating and managing `CorePerson`, `Person`, `GenPerson`, and `Entity` nodes.
- **NEU Stream**: Responsible for creating and reading `Soul` and `Incarnation` nodes, as well as handling entity detection.
- **LOG Stream**: Responsible for reading and querying `Person`, `GenPerson`, `Soul`, and `Incarnation` nodes for ontology and graph queries.

### Detailed Node Definitions

#### CorePerson
- **Purpose**: Represents a living, named, fully-known individual central to the Mythos system.
- **Properties**:
  - Required: `name`, `preferred_name`, `also_known_as`, `role`, `telegram_id`, `birth_date`, `birth_location`, `canonical`, `node_version`
  - Optional: `spiritual_role`, `lineage_codes`, `soul_id`, `notes`
- **Creation**: Manual only.
- **Relationships**: `IS_SOUL`, `HAS_INCARNATION`, `SAME_PERSON_AS`, `RESOLVES_TO`

#### Person
- **Purpose**: Represents named individuals in Iris's awareness, including historical figures and public figures.
- **Properties**:
  - Required: `name`, `also_known_as`, `birth_year`, `death_year`, `birth_location`, `category`, `canonical`, `node_version`
  - Optional: `lineage`, `spiritual_significance`, `soul_id`, `notes`
- **Creation**: Manual or Iris on explicit instruction.
- **Relationships**: `IS_SOUL`, `HAS_INCARNATION`, `SAME_PERSON_AS`, `RESOLVES_TO`

#### GenPerson
- **Purpose**: Represents individuals in a genealogical lineage.
- **Properties**:
  - Required: `name`, `maiden_name`, `birth_year`, `birth_location`, `death_year`, `lineage_family`, `tree`, `generation`, `canonical`, `node_version`
  - Optional: `also_known_as`, `marriage_year`, `spouse_name`, `occupation`, `immigration_year`, `immigration_origin`, `notes`, `ancestry_id`, `person_id`
- **Creation**: Genealogy import patches or manual Cypher.
- **Relationships**: `CHILD_OF`, `SPOUSE_OF`, `SIBLING_OF`, `SAME_PERSON_AS`

#### Soul
- **Purpose**: Represents a persistent spiritual identity transcending individual incarnations.
- **Properties**:
  - Required: `soul_name`, `also_known_as`, `soul_type`, `active_incarnation`, `lineage_codes`, `canonical`, `node_version`
  - Optional: `spiritual_titles`, `soul_mission`, `activation_status`, `notes`
- **Creation**: Manual only.
- **Relationships**: `HAS_INCARNATION`, `PARTNERED_WITH`, `RELATED_TO`

#### Incarnation
- **Purpose**: Represents a specific lifetime of a Soul.
- **Properties**:
  - Required: `name`, `soul_id`, `time_period`, `location`, `role`, `certainty`, `canonical`, `node_version`
  - Optional: `birth_year`, `death_year`, `death_circumstance`, `lineage_active`, `notes`
- **Creation**: Manual during soul stratigraphy or past life research.
- **Relationships**: `KNEW`, `WITNESSED`

#### Entity
- **Purpose**: Represents auto-generated nodes created by Iris's entity detection.
- **Properties**:
  - Required: `name`, `detected_in`, `detection_confidence`, `detection_method`, `resolved`, `canonical`, `node_version`
  - Optional: `resolved_to_type`, `resolved_to_id`, `resolved_by`, `notes`
- **Creation**: Automated by the `mythos-worker-entity.service`.
- **Relationships**: `MENTIONED_IN`, `RESOLVES_TO`

### Transition Paths
- **Entity → Person**: When an auto-detected entity is identified as a real named individual.
- **Entity → CorePerson**: When an entity is detected as a central individual in the Mythos system.

This document ensures that the Mythos system maintains a consistent and well-defined schema for managing person nodes in the Neo4j graph.
