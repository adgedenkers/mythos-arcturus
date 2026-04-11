# Iris Core

**Stream:** NEU
**Files:** 41

## Files in this Module

- `iris/introspection/__init__.py` (10L)
- `iris/introspection/analyzer.py` (146L)
- `iris/introspection/graph_enricher.py` (49L)
- `iris/introspection/manifest.py` (115L)
- `iris/introspection/queue_dispatcher.py` (115L)
- `iris/introspection/report.py` (90L)
- `iris/introspection/run.py` (170L)
- `iris/introspection/scanner.py` (171L)
- `iris/self_model/__init__.py` (33L)
- `iris/self_model/capabilities.yaml` (306L)
- `iris/self_model/introspection.py` (418L)
- `iris/core/Dockerfile` (53L)
- `iris/core/requirements.txt` (33L)
- `iris/core/src/__init__.py` (7L)
- `iris/core/src/agency.py` (651L)
- `iris/core/src/config.py` (125L)
- `iris/core/src/context_engine.py` (843L)
- `iris/core/src/decision_gate.py` (289L)
- `iris/core/src/health.py` (208L)
- `iris/core/src/llm.py` (430L)
- `iris/core/src/loop.py` (456L)
- `iris/core/src/main.py` (107L)
- `iris/core/src/memory.py` (131L)
- `iris/core/src/perception.py` (131L)
- `iris/core/src/person_researcher.py` (1269L)
- `iris/core/src/prompts.py` (393L)
- `iris/core/src/self_model.py` (153L)
- `iris/core/src/task_registry.py` (793L)
- `iris/core/src/trigger_engine.py` (777L)
- `iris/core/src/trigger_runner.py` (100L)
- `iris/sandbox/Dockerfile` (34L)
- `iris/docs/__init__.py` (5L)
- `iris/docs/llm.py` (126L)
- `iris/docs/worker.py` (140L)
- `iris/docs/handlers/__init__.py` (1L)
- `iris/docs/handlers/architecture.py` (86L)
- `iris/docs/handlers/component.py` (90L)
- `iris/docs/handlers/system_map.py` (56L)
- `iris/integrity/__init__.py` (19L)
- `iris/integrity/iris_integrity.py` (225L)
- `iris/integrity/iris_integrity_handler.py` (68L)

---

# Iris Core Module Overview

## 1. Module Purpose
The Iris Core module is the central component of the Mythos system's introspection and self-modeling capabilities. It provides end-to-end functionality for:
- Scanning and analyzing codebases using LLMs
- Storing analysis results in PostgreSQL and Neo4j
- Dispatching documentation tasks via Redis
- Generating health reports and self-reflection
- Maintaining a self-model of system capabilities and dependencies

This module enables the system to understand its own architecture, track changes, and maintain documentation through automated processes.

## 2. Architecture Overview
The module follows a pipeline architecture with the following data flow:
```
Codebase Scanning (scanner.py)
    ↓
LLM Analysis (analyzer.py)
    ↓
Manifest Storage (manifest.py)
    ↓
Graph Enrichment (graph_enricher.py)
    ↓
Task Dispatching (queue_dispatcher.py)
    ↓
Report Generation (report.py)
```

Key integration points:
- PostgreSQL for structured data storage
- Neo4j for graph relationships
- Redis for task queues
- Ollama for LLM analysis
- Capabilities.yaml for self-model definition

## 3. Key Components

### Core Functions
1. **run_introspection** (run.py)
   - Orchestrates the full introspection pipeline
   - Coordinates scanning, analysis, storage, and reporting

2. **analyze_file/analyze_component** (analyzer.py)
   - Uses Ollama to generate LLM-based analysis
   - Extracts summaries, dependencies, and issues

3. **enrich_graph** (graph_enricher.py)
   - Creates Neo4j nodes for components/files
   - Establishes relationships between entities

4. **write_manifest** (manifest.py)
   - Bulk-inserts file metadata into PostgreSQL
   - Manages run lifecycle (create/finish)

5. **dispatch_tasks** (queue_dispatcher.py)
   - Enqueues documentation tasks to Redis
   - Prevents duplicate tasks via hashing

6. **generate_report** (report.py)
   - Creates structured health reports
   - Formats reports for CLI/Telegram output

### Supporting Components
- **scanner.py**: Filesystem scanner with component detection
- **self_model/**: Self-knowledge subsystem with capabilities.yaml
- **__init__.py**: Module entry point exposing core functions

## 4. Design Patterns
1. **Facade Pattern**
   - Used in `__init__.py` to expose `run_introspection` as a single entry point
   - Used in `self_model/__init__.py` for self-model functions

2. **DAO Pattern**
   - Implemented in `manifest.py` for PostgreSQL operations
   - Implemented in `graph_enricher.py` for Neo4j operations

3. **Singleton Pattern**
   - Redis/Neo4j clients treated as singletons
   - Logging module used as singleton

4. **Factory Pattern**
   - `_enqueue` in queue_dispatcher.py for task creation

5. **Procedural Programming**
   - Most operations follow linear, step-by-step execution

## 5. Data Model

### PostgreSQL Tables
1. **introspection_runs**
   - `run_id` (UUID)
   - `mode` (full/quick)
   - `target_path`
   - `start_time`
   - `end_time`
   - `status`
   - `stats`

2. **system_manifest**
   - `run_id` (foreign key)
   - `file_path`
   - `component`
   - `file_type`
   - `size`
   - `line_count`
   - `hash`
   - `last_modified`

### Neo4j Graph Model
1. **Nodes**
   - `IntrospectionRun` (run_id, timestamp)
   - `SystemComponent` (name, description)
   - `SystemFile` (path, type, size)
   - `SystemDependency` (name, type)

2. **Relationships**
   - `SCANNED` (IntrospectionRun → SystemFile)
   - `CONTAINS` (SystemComponent → SystemFile)
   - `DEPENDS_ON` (SystemFile → SystemDependency)

## 6. API Surface

### Public Functions
1. **Introspection Pipeline**
   - `run_introspection(base_path, target_path, quick, report_only, queue_status_only)`
   - `analyze_file(file_meta, content)`
   - `analyze_component(component_name, file_list)`

2. **Self-Model Functions**
   - `load_capabilities()`
   - `get_system_vitals()`
   - `get_disk_vitals()`
   - `generate_reflection()`
   - `generate_brief_status()`

3. **Utility Functions**
   - `task_hash(task)`
   - `detect_component(file_path)`
   - `file_hash(file_path)`

### Internal Interfaces
- `enrich_graph(driver, run_id, file_list, component_groups)`
- `write_manifest(conn, run_id, file_list)`
- `dispatch_tasks(redis_client, component_groups, file_list)`

## 7. Dependencies

### Internal Modules
- `iris.introspection.scanner`
- `iris.introspection.analyzer`
- `iris.introspection.manifest`
- `iris.introspection.graph_enricher`
- `iris.introspection.queue_dispatcher`
- `iris.introspection.report`

### External Services
- **PostgreSQL**: For structured data storage
- **Neo4j**: For graph relationships
- **Redis**: For task queues
- **Ollama**: For LLM analysis
- **System Files**: `/opt/mythos` codebase

### Configuration Files
- `.env` file for environment variables
- `capabilities.yaml` for self-model definition

## 8. Configuration

### Environment Variables
- `OLLAMA_MODEL`: LLM model to use (default: `qwen3:30b-a3b`)
- `NEO4J_URI`: Neo4j connection string
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `DB_NAME`: PostgreSQL database name (default: `mythos`)
- `MYTHOS_ROOT`: Root directory of codebase (default: `/opt/mythos`)

### Configuration Files
- **.env** (loaded by `_load_env` in run.py)
- **capabilities.yaml** (defines Iris's capabilities and dependencies)

### Runtime Parameters
- `base_path`: Base directory to scan
- `target_path`: Specific path to analyze
- `quick`: Enable quick mode (skip LLM analysis)
- `report_only`: Generate report without analysis
- `queue_status_only`: Check queue status without processing

---

This module provides a comprehensive solution for system introspection, combining traditional code analysis with AI-enhanced insights. The architecture ensures separation of concerns while maintaining tight integration between data storage, processing, and task management components.
