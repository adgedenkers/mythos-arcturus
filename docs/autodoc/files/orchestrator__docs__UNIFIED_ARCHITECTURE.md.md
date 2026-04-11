# orchestrator/docs/UNIFIED_ARCHITECTURE.md

**Language:** markdown
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 368

---

### Purpose
The `UNIFIED_ARCHITECTURE.md` file provides a comprehensive overview of the Mythos Orchestrator's unified architecture, detailing how the Model Bench and Consciousness Pipeline subsystems are integrated into a single system. It outlines the directory structure, configuration system, database schema, web interface, migration plan, and CLI reference.

### Architecture
The file is structured into several sections, each detailing a specific aspect of the system:
- **Overview**: Describes the integration of Model Bench and Consciousness Pipeline.
- **Directory Structure**: Outlines the file and directory layout of the orchestrator.
- **Configuration System**: Explains the configuration hierarchy and settings.
- **Bench + Pipeline Integration**: Details how models are tested and promoted.
- **Database Schema**: Lists existing and new database tables.
- **Web Interface (Phase 2)**: Describes planned web pages and API routes.
- **Migration Plan**: Outlines the steps for integrating and updating the system.
- **CLI Reference**: Provides commands for running the pipeline and bench tests.

### Patterns
The file does not explicitly describe design patterns, but it implies the use of:
- **Singleton**: Configuration settings are likely singletons.
- **Factory**: Config resolution might use factory methods to create configurations.
- **Observer**: The system might observe changes in the registry or model performance.

### Dependencies
The file does not list specific dependencies but mentions:
- **pydantic-settings**: For configuration validation.
- **Ollama HTTP client**: For model interactions.
- **Neo4j and PostgreSQL**: For database operations.

### Interfaces
The file describes several interfaces:
- **CLI**: Commands for running and managing the orchestrator.
- **Web API**: Routes for the web interface.
- **Database**: Tables and operations for storing and retrieving data.

### Database
The file lists several tables:
- **Existing Tables**: `orch_models`, `orch_model_capabilities`, `orch_test_suites`, `orch_test_questions`, `orch_test_runs`, `orch_test_results`, `orch_model_benchmarks`, `pipeline_runs`, `pipeline_llm_calls`, `pipeline_queries`.
- **New Tables**: `orch_role_assignments`, `orch_config_snapshots`.

### Configuration
The file describes the configuration system:
- **Environment Variables**: `.env` file.
- **Settings**: `settings.py` with pydantic settings.
- **Registry**: `registry.yaml` for prompts and model configurations.
- **Test Config Files**: YAML files for test overrides.

### Key Logic
The file highlights several key pieces of logic:
- **Config Resolution**: Prioritizes overrides, settings, registry, and defaults.
- **Bench Workflow**: Running, comparing, and promoting models.
- **Promotion Flow**: Updating the registry with winning configurations.

### Integration Points
The file describes integration points:
- **Model Bench**: Tests models against suites and grades answers.
- **Consciousness Pipeline**: Routes messages through PERCEPTION, DISCOVERY, and IRIS stages.
- **Web Interface**: Provides a dashboard and API routes for managing the orchestrator.
- **Database**: Stores test results, model assignments, and configuration snapshots.

### Detailed Analysis

#### Overview
The Mythos Orchestrator integrates two subsystems:
1. **Model Bench**: Tests models against suites, grades answers, and stores scores.
2. **Consciousness Pipeline**: Routes messages through PERCEPTION, DISCOVERY, and IRIS stages.

#### Directory Structure
The orchestrator directory structure includes:
- **src/**: Contains configuration, pipeline, bench, models, logging, database, and utilities.
- **prompts/**: Stores prompt registry and templates.
- **test_suites/**: Contains test suites for model evaluation.
- **results/**: Stores test run outputs and reports.
- **scripts/**: CLI entry points and scripts.
- **web/**: Web UI components.
- **data/**: Data storage.
- **logs/**: Log files.
- **docs/**: Documentation.

#### Configuration System
The configuration system uses a chain of:
- **Environment Variables**: `.env`.
- **Settings**: `settings.py` with pydantic settings.
- **Registry**: `registry.yaml` for prompts and model configurations.
- **Test Config Files**: YAML files for test overrides.

#### Bench + Pipeline Integration
Models are tested for specific roles:
- **Roles**: `perception`, `iris`, `query_builder`, `query_validator`, `strategy`, `summarizer`.
- **Bench Workflow**: Commands for running, comparing, and promoting models.

#### Database Schema
The database schema includes:
- **Existing Tables**: `orch_models`, `orch_model_capabilities`, `orch_test_suites`, `orch_test_questions`, `orch_test_runs`, `orch_test_results`, `orch_model_benchmarks`, `pipeline_runs`, `pipeline_llm_calls`, `pipeline_queries`.
- **New Tables**: `orch_role_assignments`, `orch_config_snapshots`.

#### Web Interface (Phase 2)
The web interface includes:
- **Pages**: Dashboard, Models, Test Suites, Run Bench, Compare, Leaderboard, Pipeline Monitor, Registry Editor.
- **API Routes**: `/api/bench/models`, `/api/bench/suites`, `/api/bench/run`, `/api/bench/runs`, `/api/bench/compare`, `/api/bench/leaderboard`, `/api/bench/pipeline/recent`, `/api/bench/pipeline/{uuid}`, `/api/bench/registry`, `/api/bench/promote`.

#### Migration Plan
The migration plan includes:
- **Patch 0152**: Foundation.
- **Patch 0153**: Bench CLI.
- **Patch 0154**: Web UI.
- **Patch 0155**: Regression Guard.

#### CLI Reference
The CLI reference includes commands for:
- Running the pipeline.
- Running and managing bench tests.
- Comparing runs.
- Promoting models.
- Logging and inspecting the registry.

### Conclusion
The `UNIFIED_ARCHITECTURE.md` file provides a detailed overview of the Mythos Orchestrator's unified architecture, covering its directory structure, configuration system, database schema, web interface, migration plan, and CLI reference. This documentation serves as a comprehensive guide for developers and administrators to understand and manage the system effectively.
