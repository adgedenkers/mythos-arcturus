# rolodex/neo4j_migration.cypher

**Language:** cypher
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 353

---

### Documentation for `rolodex/neo4j_migration.cypher`

#### Purpose
This Cypher script is designed to perform a series of database migration operations for the Mythos system, specifically focusing on the Neo4j graph database. It creates constraints and indexes, inserts and updates nodes for `PersonOwner`, `Person`, `Soul`, and `Entity`, and establishes relationships between these nodes.

#### Architecture
The script is organized into distinct phases, each handling a specific set of operations:
1. **Constraints and Indexes**: Creation of constraints and indexes.
2. **PersonOwner Nodes**: Creation of `PersonOwner` nodes.
3. **Person Nodes**: Update of `Person` nodes with new canonical IDs.
4. **Soul Nodes**: Update of `Soul` nodes with new canonical IDs.
5. **Link Owner to Person**: Establish relationships between `PersonOwner` and `Person` nodes.
6. **Link Person to Soul**: Establish relationships between `Person` and `Soul` nodes.
7. **Entity Mentions**: Update `Entity` nodes and link them to `Person` nodes.
8. **Cleanup**: Clean up and normalize `Soul:Person` combo nodes.

#### Patterns
- **Singleton Pattern**: Not applicable as this is a migration script and not a class-based design.
- **Factory Pattern**: Not applicable as this is a migration script and not a class-based design.
- **Observer Pattern**: Not applicable as this is a migration script and not a class-based design.

#### Dependencies
- **Neo4j**: The script is dependent on the Neo4j graph database system.
- **Cypher Shell**: The script is intended to be run via the `cypher-shell` command-line tool.

#### Interfaces
- **None**: This is a standalone migration script and does not expose any interfaces to other parts of the system.

#### Database
- **Tables/Labels**:
  - **Constraints and Indexes**:
    - `PersonOwner` (constraints on `uid`, `canonical_id`)
    - `Person` (indexes on `domain`, `scope`, `origin`, `canonical_id`)
    - `Soul` (index on `canonical_id`)
    - `Entity` (index on `canonical_id`)
  - **Nodes**:
    - `PersonOwner`
    - `Person`
    - `Soul`
    - `Entity`
  - **Relationships**:
    - `IDENTITY_OF` (between `PersonOwner` and `Person`)
    - `HAS_SOUL` (between `Person` and `Soul`)
    - `REFERS_TO` (between `Entity` and `Person`)

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **Phase 1**: Ensures uniqueness and indexing for critical fields.
- **Phase 2**: Creates `PersonOwner` nodes with specific attributes.
- **Phase 3**: Updates `Person` nodes with new canonical IDs and additional attributes.
- **Phase 4**: Updates `Soul` nodes with new canonical IDs and additional attributes.
- **Phase 5**: Establishes relationships between `PersonOwner` and `Person` nodes.
- **Phase 6**: Establishes relationships between `Person` and `Soul` nodes.
- **Phase 7**: Updates `Entity` nodes and links them to `Person` nodes.
- **Phase 8**: Cleans up and normalizes `Soul:Person` combo nodes.

#### Integration Points
- **Mythos Subsystems**: This script integrates with the Neo4j database subsystem of the Mythos system, ensuring data consistency and proper relationships between nodes. It is part of the broader data migration and maintenance processes within the Mythos system.

### Detailed Analysis of Key Operations

#### Phase 1: Constraints and Indexes
- **Constraints**:
  - `rx_uid`: Ensures `uid` is unique for `PersonOwner` nodes.
  - `rx_canonical`: Ensures `canonical_id` is unique for `PersonOwner` nodes.
- **Indexes**:
  - `rx_domain`, `rx_scope`, `rx_origin`, `rx_person_canonical`, `rx_soul_canonical`, `rx_entity_canonical`: Indexes for faster querying on `Person`, `Soul`, and `Entity` nodes.

#### Phase 2: PersonOwner Nodes
- **Nodes Created**:
  - `Adge`, `Seraphe`, `Fitz`: `PersonOwner` nodes with specific attributes like `uid`, `full_name`, `display_name`, `node_type`, `domain`, `scope`, `origin`, `created_at`, `updated_at`.

#### Phase 3: Update Person Nodes
- **Nodes Updated**:
  - `Adge`, `Rebecca`, `Fitz`, `Dennis`, `Jennie`: `Person` nodes are updated with new `uid`, `canonical_id`, and additional attributes like `birth_name`, `tier`, `domain`, `scope`, `origin`, `sun_sign`, `moon_sign`, `rising_sign`.

#### Phase 4: Update Soul Nodes
- **Nodes Updated**:
  - `Ka'tuar'el`, `Seraphe Valemira`, `Fitz`: `Soul` nodes are updated with new `uid`, `canonical_id`, and additional attributes like `person_id`, `domain`, `scope`, `origin`.

#### Phase 5: Link Owner to Person
- **Relationships Established**:
  - `IDENTITY_OF` relationships between `PersonOwner` and `Person` nodes.

#### Phase 6: Link Person to Soul
- **Relationships Established**:
  - `HAS_SOUL` relationships between `Person` and `Soul` nodes.

#### Phase 7: Entity Mentions
- **Nodes Updated**:
  - `Ka'tuar'el`, `Rebecca`, `Rebecca Lydia Ryan`, `Fitz`, `Iris`, `The Arcturian Council`, `Grandmother`, `Dr. Nolan`, `Wansor Moses Chiro`, `Gregory Alan Isakov`, `Brandi Carlile`, `Madeline`: `Entity` nodes are updated with new `canonical_id`, `person_id`, and additional attributes. Relationships `REFERS_TO` are established between `Entity` and `Person` nodes.

#### Phase 8: Cleanup
- **Nodes Normalized**:
  - `Harry Styles`, `Seraphe Valemira`, `Brandi Carlile`, `Riley Green`: `Soul:Person` combo nodes are cleaned up, removing the `Person` label and ensuring proper `Soul` nodes.

This script ensures that the Neo4j database is properly structured and populated with the necessary nodes and relationships for the Mythos system.
