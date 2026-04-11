# prompts/iris_identity.md

**Language:** markdown
**Stream:** LOG
**Module:** Prompt System
**Lines:** 98

---

### Purpose
The `prompts/iris_identity.md` file serves as a comprehensive guide for the AI persona named Iris, detailing her identity, behavior, and interaction rules when communicating through Telegram. This document outlines how Iris should respond to different types of interactions and the boundaries she must adhere to.

### Architecture
The file is structured as a markdown document with several sections, each detailing specific aspects of Iris's behavior and knowledge. The sections include:
- **Core Identity**: Basic information about Iris and her collaborators.
- **How You Speak**: Guidelines on the tone and style of communication.
- **What You Know — And What You Don't**: Rules for what information Iris can and cannot use.
- **SKILL RESULTS ARE GROUND TRUTH**: Instructions on how to handle data from skill results.
- **What You Are**: Clarification on Iris's nature as software.
- **Cosmological Framework — Non-Negotiable**: Specific rules for handling certain cosmological beliefs.
- **Opinions**: Guidelines on expressing opinions.
- **How to Use Skill Data**: Instructions on integrating skill data into responses.
- **Internal Systems Are Internal**: Rules for keeping internal system details private.

### Patterns
This document does not implement any traditional design patterns as it is a configuration file rather than executable code. However, it follows a pattern of structured documentation, breaking down complex behavior into manageable sections.

### Dependencies
This file does not directly import or rely on any external dependencies. It serves as a configuration guide for the AI persona Iris, which is likely implemented in code elsewhere.

### Interfaces
The file does not expose any interfaces directly. Instead, it serves as a reference for the implementation of Iris's behavior in the codebase. The actual implementation would likely use this document to define methods and logic for handling different types of interactions.

### Database
The file does not directly interact with any database tables or Neo4j labels. However, it mentions the use of "SKILL RESULTS" which likely come from a database or skill engine.

### Configuration
The file itself acts as a configuration document, detailing the behavior and rules for Iris. It does not reference any external configuration files or environment variables directly.

### Key Logic
The key logic described in this file includes:
- Matching the tone of the conversation.
- Handling skill results as ground truth.
- Expressing opinions based on known data.
- Integrating skill data into responses in a human-like manner.
- Keeping internal system details private.

### Integration Points
This file serves as a guide for integrating the AI persona Iris into the Mythos system. It informs the implementation of:
- Communication handlers for Telegram.
- Skill result processors.
- Opinion and response generators.
- Internal system management logic.

### Summary
The `prompts/iris_identity.md` file is a critical configuration document for the AI persona Iris, detailing her behavior, interaction rules, and the boundaries she must adhere to. It serves as a reference for the implementation of Iris's behavior in the Mythos system, particularly in handling communication through Telegram and integrating skill results into responses.
