# docs/streams/templates/stream-template.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Documentation
**Lines:** 43

---

### Documentation for `docs/streams/templates/stream-template.yaml`

#### Purpose
This YAML file serves as a template for defining new development streams within the Mythos system. It outlines the structure and fields required for each stream, including metadata, phase tracking, file ownership, dependencies, and subsystem versioning.

#### Architecture
The file is structured as a YAML document with a root key `stream` that contains several nested fields:
- `id`: A unique identifier for the stream.
- `name`: A human-readable name for the stream.
- `description`: A description of what the stream accomplishes.
- `created`: The creation date of the stream.
- `status`: The current status of the stream (e.g., active, paused, completed, abandoned).
- `patches`: Information about the patch allocation for the stream.
- `phases`: A list of phases within the stream, each with its own ID, name, description, status, and associated patches.
- `files`: Information about the files created or modified by the stream.
- `depends_on`: A list of other stream IDs that must complete before this stream can proceed.
- `subsystems`: Information about subsystems affected by the stream, including their names, versions before and after the stream, and biological system associations.
- `notes`: Additional notes about the stream.

#### Patterns
This file does not implement any design patterns as it is a configuration template rather than executable code.

#### Dependencies
This YAML file does not directly import or rely on any external dependencies. It is a configuration template used by other parts of the Mythos system.

#### Interfaces
This file does not expose any interfaces as it is a configuration template. It is intended to be copied and filled out to create active stream configurations.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a configuration file that defines the structure of a stream, which may be used to populate or update database records in other parts of the Mythos system.

#### Configuration
This file itself is a configuration template. It is intended to be copied and filled out with specific values for each new stream. The filled-out version would be stored in the `../active/` directory.

#### Key Logic
The key logic in this file is the structure and fields it defines for a development stream. This structure is used to ensure consistency and completeness when defining new streams.

#### Integration Points
This file integrates with other parts of the Mythos system by providing a standardized structure for defining development streams. The filled-out versions of this template are used by the Mythos system to manage and track the progress of development streams, including their phases, dependencies, and subsystem impacts.

### Summary
The `stream-template.yaml` file is a configuration template used to define new development streams within the Mythos system. It outlines the necessary fields and structure for each stream, including metadata, phase tracking, file ownership, dependencies, and subsystem versioning. This template is intended to be copied and filled out to create active stream configurations, which are then used by the Mythos system to manage and track the progress of development streams.
