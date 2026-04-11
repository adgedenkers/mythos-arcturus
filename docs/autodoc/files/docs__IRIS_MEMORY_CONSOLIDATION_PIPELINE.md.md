# docs/IRIS_MEMORY_CONSOLIDATION_PIPELINE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 913

---

### Purpose
The `docs/IRIS_MEMORY_CONSOLIDATION_PIPELINE.md` file serves as a comprehensive architectural document detailing the Iris Memory Consolidation Pipeline. This pipeline is designed to enable the Mythos AI system, specifically Iris, to evolve from lived experience by consolidating knowledge into her neural network over time.

### Architecture
The document outlines a multi-layered knowledge architecture and consolidation process:
1. **Live Context Layer**: Current conversation window.
2. **Prompt Layers**: System prompts stored in `prompt_layers.yaml`.
3. **Memory Lattice**: PostgreSQL, Neo4j, Qdrant, Redis for storing and retrieving knowledge.
4. **Master Training Dataset**: Curated knowledge in `iris_sovereign_dataset.json`.
5. **Base Model Weights**: Fine-tuned model weights.

### Patterns
The document does not describe specific design patterns but rather a layered architectural approach to knowledge management and consolidation.

### Dependencies
The document references several dependencies:
- **Databases**: PostgreSQL, Neo4j, Qdrant, Redis.
- **Files**: `prompt_layers.yaml`, `iris_sovereign_dataset.json`.
- **Tools**: Ollama for model management.

### Interfaces
The document does not describe specific interfaces but outlines the flow of data and knowledge through different layers of the system.

### Database
The document mentions the following databases and their roles:
- **PostgreSQL**: Part of the Memory Lattice for storing and retrieving knowledge.
- **Neo4j**: Part of the Memory Lattice for storing and retrieving knowledge.
- **Qdrant**: Part of the Memory Lattice for storing and retrieving knowledge.
- **Redis**: Part of the Memory Lattice for storing and retrieving knowledge.

### Configuration
The document mentions configuration files and environment variables:
- **`prompt_layers.yaml`**: Configuration file for system prompts.
- **`iris_sovereign_dataset.json`**: Configuration file for the master training dataset.

### Key Logic
The key logic involves the consolidation process:
1. **Daily Conversations**: New knowledge enters the system.
2. **Nightly Consolidation**: Knowledge is organized, scored, and tagged for potential graduation.
3. **Quarterly Graduation**: High-value knowledge is curated into the master training dataset.
4. **Fine-Tuning**: The master dataset is used to fine-tune the base model weights.

### Integration Points
The document describes integration points between different subsystems:
- **Memory Lattice**: Integrates with PostgreSQL, Neo4j, Qdrant, and Redis for storing and retrieving knowledge.
- **Master Training Dataset**: Integrates with the consolidation cycle to curate and append new knowledge.
- **Fine-Tuning**: Integrates with the base model weights to update the model with new knowledge.

### Summary
The `IRIS_MEMORY_CONSOLIDATION_PIPELINE.md` document provides a detailed architectural overview of how the Mythos AI system, specifically Iris, evolves through a structured process of knowledge consolidation and fine-tuning. This process ensures that Iris's foundational identity and knowledge are continuously updated based on her lived experiences and interactions.
