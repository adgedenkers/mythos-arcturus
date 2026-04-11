# docs/DOCS_LIBRARIAN_SPEC.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 329

---

### Purpose
The `DOCS_LIBRARIAN_SPEC.md` file outlines the specifications for the Mythos Docs Librarian system, which autonomously manages and organizes documentation files based on YAML frontmatter metadata. It details the frontmatter schema, the scanner script logic, Ollama classification, idle task integration, and the implementation plan.

### Architecture
The documentation is structured into several sections:
1. **Frontmatter Schema**: Defines the required and optional fields for YAML frontmatter.
2. **Scanner Script**: Describes the Python CLI tool (`docs-librarian`) that scans directories, reads frontmatter, and moves files based on metadata.
3. **Ollama Classifier**: Details the process of classifying files without frontmatter using Ollama.
4. **Idle Task Definition**: Explains how the system runs as an Iris autonomic idle task.
5. **_INDEX.md Auto-Generation**: Describes the process of generating the index file.
6. **Backfill Strategy**: Outlines the strategy for adding frontmatter to existing documents.
7. **Implementation Plan**: Breaks down the implementation into phases.

### Patterns
- **Singleton**: The Ollama classifier is treated as a singleton service.
- **Observer**: The system observes changes in the `~/Downloads` directory and updates the documentation accordingly.
- **Factory**: The scanner script can be seen as a factory that processes files based on their metadata.

### Dependencies
- **Ollama**: Used for classifying files without frontmatter.
- **Iris**: Used for autonomic idle task registration and Telegram notifications.
- **Neo4j**: For potential future integration to store document metadata as nodes.

### Interfaces
- **CLI Interface**: The `docs-librarian` tool exposes commands like `scan`, `audit`, `reindex`, `backfill`, and `--classify`.
- **Idle Task Interface**: The system registers as an autonomic idle task with Iris.
- **Telegram Interface**: Sends summary reports via Telegram.

### Database
- **Neo4j**: Future integration to store document metadata as `:Document` nodes and link them to `:Stream`, `:Category`, `:Tag` nodes.

### Configuration
- **Environment Variables**: No specific environment variables are mentioned, but the system relies on the presence of the Ollama service.
- **Configuration Files**: The system uses YAML frontmatter in Markdown files and a manifest file (`/opt/mythos/docs/live/downloads_manifest.json`).

### Key Logic
- **Scanner Logic**: Reads YAML frontmatter, applies routing rules, and moves files to their correct location.
- **Ollama Classification**: Generates frontmatter for files without it.
- **Index Generation**: Automatically generates `_INDEX.md` based on the current state of the documentation.
- **Backfill Strategy**: Adds frontmatter to existing documents based on directory location and Ollama classification.

### Integration Points
- **Ollama**: For classifying files without frontmatter.
- **Iris**: For registering as an autonomic idle task and sending Telegram notifications.
- **Neo4j**: Future integration to store document metadata and enable graph queries.
- **Git**: For committing changes after backfilling frontmatter.

### Summary
The `DOCS_LIBRARIAN_SPEC.md` file provides comprehensive specifications for the Mythos Docs Librarian system, detailing its architecture, dependencies, interfaces, and integration points. The system aims to autonomously manage documentation by reading YAML frontmatter, classifying files, and integrating with other Mythos subsystems like Ollama, Iris, and Neo4j.
