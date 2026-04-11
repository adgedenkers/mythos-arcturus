# mission/missions/system_archaeology/prompts/dead_code.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 96

---

### Purpose
The `dead_code.md` file serves as a prompt for identifying dead code, orphaned database tables, and ghost services within the Mythos codebase. It provides detailed rules and data points for classifying code and services as dead or active.

### Architecture
The file is structured as a markdown document containing sections for data, classification rules, and output format. It does not contain any classes or functions but serves as a guide for the system archaeologist to follow.

### Patterns
No design patterns are used as this is a markdown file and not a code file.

### Dependencies
This file does not import or rely on any external libraries or modules. It relies on context provided by the system archaeologist tool, which includes data from the system graph, PostgreSQL, and shell commands.

### Interfaces
The file does not expose any interfaces. It is a static document used to guide the system archaeologist tool in its analysis.

### Database
The file references data from PostgreSQL tables and Neo4j graph services, but it does not directly interact with the database. It uses placeholders like `{context.postgres.truly_empty_tables}` and `{context.graph.never_imported_py}` to indicate where the data will be inserted.

### Configuration
The file does not use any configuration files or environment variables. It relies on the context provided by the system archaeologist tool.

### Key Logic
The key logic is embedded in the classification rules and data points provided. It guides the system archaeologist tool to:
- Identify files that are not imported by anything.
- Classify files as dead code based on specific rules.
- Identify orphaned PostgreSQL tables with zero rows.
- Identify ghost services that are registered in the graph but not running.

### Integration Points
This file integrates with the following Mythos subsystems:
- **System Graph**: Provides data on never-imported Python files and services.
- **PostgreSQL**: Provides data on empty tables and live row counts.
- **Shell Commands**: Provides data on running services.
- **Mission Engine**: Uses this prompt to guide the analysis process.

### Detailed Documentation

#### Purpose
The `dead_code.md` file is a prompt for the system archaeologist tool to identify dead code, orphaned database tables, and ghost services within the Mythos codebase.

#### Architecture
The file is a markdown document structured into sections:
- **DATA**: Contains placeholders for data points such as never-imported Python files, empty PostgreSQL tables, and running services.
- **CLASSIFICATION RULES**: Provides rules for classifying code as dead or not dead.
- **OUTPUT**: Specifies the exact JSON structure for the output.

#### Patterns
No design patterns are used as this is a markdown file and not a code file.

#### Dependencies
- **System Graph**: Provides data on never-imported Python files and services.
- **PostgreSQL**: Provides data on empty tables and live row counts.
- **Shell Commands**: Provides data on running services.

#### Interfaces
The file does not expose any interfaces. It is a static document used to guide the system archaeologist tool.

#### Database
The file references data from:
- **PostgreSQL**: Tables with zero rows and live row counts.
- **Neo4j**: Graph services and never-imported Python files.

#### Configuration
No configuration files or environment variables are used.

#### Key Logic
- **Classification Rules**: Detailed rules for identifying dead code, orphaned tables, and ghost services.
- **Data Points**: Placeholder data points for analysis.

#### Integration Points
- **System Graph**: Provides data on never-imported Python files and services.
- **PostgreSQL**: Provides data on empty tables and live row counts.
- **Shell Commands**: Provides data on running services.
- **Mission Engine**: Uses this prompt to guide the analysis process.
