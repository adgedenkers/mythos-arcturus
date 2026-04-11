# orchestration/ORCHESTRATION.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 102

---

### Purpose
The `ORCHESTRATION.md` file provides a comprehensive overview of the Mythos Orchestration System, detailing its architecture, execution flow, pattern structure, and integration points. It serves as a reference for developers and users to understand how the system decomposes and executes complex tasks using a MapReduce-like approach.

### Architecture
The orchestration system is structured around the `orchestrator.py` core engine, which handles the loading, gathering, executing, and synthesizing of tasks based on predefined patterns. Patterns are defined in JSON files within the `patterns/` directory, and each pattern follows a specific structure outlined in `pattern_schema.json`. Execution logs are stored in the `logs/` directory, and a future cache directory (`cache/`) is planned for context gathering.

### Patterns
The orchestration system employs a factory pattern to instantiate and execute different patterns based on the input request. The system also uses a dependency injection pattern to manage the execution order of stages within each pattern.

### Dependencies
The `orchestrator.py` file relies on the following dependencies:
- `pattern_schema.json` for validating pattern definitions.
- `patterns/` directory for loading specific pattern definitions.
- `logs/` directory for storing execution logs.
- `cache/` directory (future) for caching context gathering.

### Interfaces
The `orchestrator.py` exposes a CLI interface for:
- Listing available patterns.
- Performing dry runs to show execution plans.
- Executing patterns with optional variables.

### Database
The system interacts with Neo4j to store patterns as graph nodes for traversal-based matching. No direct interaction with PostgreSQL or Redis is mentioned in this file.

### Configuration
The system uses environment variables and configuration files to manage settings such as model preferences and execution modes. The CLI usage section provides examples of how to configure and execute patterns.

### Key Logic
The core business logic involves:
- **Pattern Matching**: Identifying the appropriate pattern based on the input request.
- **Context Gathering**: Pre-fetching necessary context before any LLM calls.
- **Stage Execution**: Executing stages in the correct order based on their dependencies.
- **Synthesis**: Merging stage outputs into a final deliverable.
- **Validation**: Running checks on the final output.
- **Logging**: Recording execution metrics for pattern refinement.

### Integration Points
The orchestration system integrates with:
- **Patch System**: Outputs are formatted as Mythos patches.
- **Telegram Bot**: Future `/orchestrate` command for triggering from chat.
- **Iris**: Future integration for automated pattern matching and execution.
- **Neo4j**: Patterns are stored as graph nodes for traversal-based matching.

### Detailed Analysis

#### Pattern Structure
Each pattern is defined with the following components:
- **trigger**: Keywords, intent types, and preconditions for activation.
- **context_gathering**: Shell commands and files to pre-fetch before LLM work.
- **stages**: Ordered execution steps with a dependency graph.
- **synthesis**: Method for merging stage outputs into a final deliverable.
- **feedback_loop**: Metrics tracking and pattern refinement rules.

#### Execution Flow
The execution flow is as follows:
1. **MATCH**: Identify the appropriate pattern based on the request.
2. **GATHER**: Pre-fetch all necessary context.
3. **DISPATCH**: Execute stages respecting the dependency graph.
4. **SYNTHESIZE**: Merge stage outputs into a final deliverable.
5. **VALIDATE**: Validate the final output.
6. **LOG**: Record execution metrics for pattern refinement.

#### Stage Dependency Model
Stages are organized into waves based on their dependencies:
- **Wave 1 (parallel)**: Stages with no dependencies.
- **Wave 2 (sequential)**: Stages depending on Wave 1.
- **Wave 3 (parallel)**: Stages depending on Wave 2.
- **Wave 4 (sequential)**: Final synthesis stage depending on all previous stages.

#### Model Routing
The system uses different models based on the task type:
- **fast**: `claude-haiku-4-5` for reconnaissance, parsing, and classification.
- **balanced**: `claude-sonnet-4-5` for planning and code generation.
- **deep**: `claude-opus-4-6` for complex synthesis and review.

#### CLI Usage
The CLI provides commands for:
- Listing available patterns.
- Performing dry runs.
- Executing patterns with optional variables.

#### Current Patterns
The `crud-update` pattern is defined with 5 stages: recon → plan → build_sql + build_code + build_bot → synthesis. Outputs are deployment-ready patch zips.

#### Status
The system is currently in development with several features planned for future integration, including Anthropic API integration, asynchronous stage execution, and Telegram bot integration.
