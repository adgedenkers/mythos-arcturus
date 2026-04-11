# skills/README.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 129

---

### Purpose
The `skills/README.md` file serves as a comprehensive guide to the Mythos Skills System, detailing the structure, inventory, and conventions of the skills and tools used within the system. It provides an overview of how skills are organized, categorized, and executed.

### Architecture
The file is structured into several sections, each detailing different aspects of the skills system:
- **Overview**: Describes the concept of skills and their role in the Mythos system.
- **Directory Structure**: Outlines the layout of the skills directory.
- **Skills Inventory**: Lists and categorizes the skills available, detailing their versions, files, engines, and functionalities.
- **Shared Tools**: Describes computation engines that are shared among skills.
- **Skill File Format**: Explains the format of skill files.
- **Risk Tiers**: Describes the execution models for different risk tiers.
- **Adding New Skills**: Provides a step-by-step guide for adding new skills.
- **Conventions**: Lists the naming and file conventions for skills and tools.

### Patterns
The file does not implement any design patterns as it is a documentation file. However, it follows a structured documentation pattern, breaking down information into logical sections for easy reference.

### Dependencies
The file does not import or rely on any external dependencies. It serves as a reference document and does not execute any code.

### Interfaces
The file does not expose any interfaces as it is a documentation file. It serves as a reference for developers and system administrators.

### Database
The file does not interact with any databases directly. However, it references the `REGISTRY.yaml` file, which is used by the system to discover and manage skills.

### Configuration
The file references the `REGISTRY.yaml` configuration file, which is essential for the system to discover and manage skills. It also mentions the use of environment variables and paths specific to the Arcturus server.

### Key Logic
The key logic described in the file is the process of discovering, loading, and executing skills. This involves:
- Reading the `REGISTRY.yaml` file to discover available skills.
- Matching trigger conditions against the current task.
- Loading the relevant skill file and following its instructions.

### Integration Points
The file integrates with several subsystems of the Mythos system:
- **Iris**: The system component that reads the `REGISTRY.yaml` file and matches trigger conditions.
- **Skills**: The individual skill files that are loaded and executed.
- **Tools**: Shared computation engines that are used by multiple skills.
- **REGISTRY.yaml**: The master index file that Iris reads to discover available skills.
- **Builder Skills**: Skills that create and deploy infrastructure, which are executed via patches.

### Summary
The `skills/README.md` file is a comprehensive guide to the Mythos Skills System, detailing the structure, inventory, and conventions of the skills and tools used within the system. It provides essential information for developers and system administrators to understand and manage the skills effectively.
