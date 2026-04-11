# docs/ARCHITECTURE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 1243

---

### Purpose
The `docs/ARCHITECTURE.md` file serves as a comprehensive architectural overview of the Mythos system, detailing its components, services, databases, and integration points. It provides a high-level view of how the system is structured and operates.

### Architecture
The file is structured as a markdown document with sections detailing the system's architecture, services, databases, and web interfaces. It includes diagrams and tables to illustrate the system's components and their relationships.

### Patterns
This document does not implement any design patterns as it is a documentation file rather than a source code file.

### Dependencies
This file does not import or rely on any external dependencies. It is a standalone markdown file that serves as documentation.

### Interfaces
The file does not expose any interfaces. It is intended for human readers to understand the system architecture.

### Database
The file describes the database schema and usage for PostgreSQL and Neo4j, detailing tables and labels used across different streams and purposes.

### Configuration
The file does not use any configuration files or environment variables. It is a static document.

### Key Logic
The file does not contain any business logic or algorithms. It is a descriptive document outlining the architecture and components of the Mythos system.

### Integration Points
The file describes how different components of the Mythos system integrate with each other, including:
- **API Gateway**: Routes requests to different subsystems like finance, voice, and chat.
- **Services**: Various services like `mythos-api`, `mythos-bot`, and `mythos-worker-grid` that handle specific tasks.
- **Databases**: PostgreSQL and Neo4j are used for data storage and retrieval.
- **Web Dashboard**: Integration with Google OAuth for authentication and JWT-based protection for routes.

### Detailed Breakdown

#### System Overview
The system is hosted on a server named Arcturus running Ubuntu 24.04. The architecture is centered around the Iris component, which manages the consciousness loop with persistent memory, model-aware prompts, and identity context. The API Gateway, built with FastAPI, handles various routes including finance, voice, and chat interactions.

#### Services
The file lists active services running on the system, each with a specific purpose and stream (e.g., SYS, NEU, MNE). These services are responsible for different aspects of the system, from API handling to background processing.

#### Databases
- **PostgreSQL**: Contains multiple tables categorized by streams (SYS, MNE, SEN, NEU, LOG). Tables include `users`, `chat_messages`, `transactions`, `conversations`, `voice_memos`, and more.
- **Neo4j**: Used for graph-based data storage with labels like `Soul`, `Person`, `Incarnation`, `Conversation`, `GridNode`, `Entity`, `Theme`, `OntologyTerm`, `AppRegistry`, `Chart`, `Event`, `Location`.

#### Web Dashboard & Finance Hub
The web dashboard provides a user interface for interacting with the system, including authentication via Google OAuth and protected routes. The Finance Hub offers various sections for managing financial data, with endpoints for API interactions.

### Conclusion
This document serves as a critical reference for understanding the Mythos system's architecture, detailing its components, services, databases, and integration points. It provides a high-level overview that is essential for developers and system administrators working on or with the Mythos system.
