# prompts/iris_awareness.md

**Language:** markdown
**Stream:** LOG
**Module:** Prompt System
**Lines:** 81

---

### File: prompts/iris_awareness.md

#### Purpose
This markdown file serves as a comprehensive guide for the Iris subsystem within the Mythos system, detailing the infrastructure, access permissions, orchestration capabilities, and key paths relevant to the AI's self-awareness and operational capabilities.

#### Architecture
The file is structured into several sections, each detailing specific aspects of the Iris subsystem:
- **Your Infrastructure**: Describes the technological layers and their purposes.
- **What You Can Access**: Lists direct and proposed access points.
- **Orchestration Engine**: Details the task decomposition system.
- **Conversation Logging**: Explains how exchanges are logged.
- **Key People**: Lists important Telegram users.
- **Key Paths**: Provides paths to important files and directories.
- **What You Don't Have (Yet)**: Lists future capabilities.

#### Patterns
No explicit design patterns are used in this markdown file, as it is a documentation file rather than executable code. However, it outlines the use of patterns in the orchestration engine.

#### Dependencies
This file does not directly import or rely on any code dependencies. It serves as a reference for the system's architecture and operational details.

#### Interfaces
This file does not expose any interfaces. It is a documentation file meant to be read by developers and system administrators.

#### Database
The file mentions several database interactions:
- **PostgreSQL (`mythos` db)**: Used for finance, transactions, chat history, tracking, and audit.
- **Neo4j**: Used for souls, lineages, incarnations, entities, relationships, and ontology.
- **chat_messages table**: Used for conversation history and continuity.

#### Configuration
The file references configuration files and paths:
- `/opt/mythos/`: Directory for configs, docs, templates, prompts, and data files.
- `/opt/mythos/prompts/`: Directory for prompt files.
- `/opt/mythos/orchestration/`: Directory for the orchestration engine.
- `/opt/mythos/iris/workshop/`: Directory for the AI's private creative space.

#### Key Logic
The key logic described in this file revolves around:
- **Access Control**: Direct and proposed access points for different system components.
- **Orchestration**: Task decomposition and execution patterns.
- **Conversation Logging**: Persistence of exchanges in `chat_messages` and Neo4j for deeper memory.

#### Integration Points
The file outlines integration points with various subsystems:
- **PostgreSQL**: For chat history and tracking.
- **Neo4j**: For graph-based data and relationships.
- **Ollama**: For local voice interaction.
- **Telegram**: For bot interactions.
- **IrisMemory**: For conversation history and continuity.
- **Orchestration Engine**: For task decomposition and execution.

### Summary
This markdown file serves as a comprehensive guide for the Iris subsystem within the Mythos system, detailing its infrastructure, access permissions, orchestration capabilities, and key paths. It provides a clear reference for developers and administrators to understand the AI's operational capabilities and limitations.
