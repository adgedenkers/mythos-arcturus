# iris/introspection/run.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 170

---

### File: `iris/introspection/run.py`

#### Purpose
This file orchestrates the full introspection pipeline for the Mythos system, including scanning, analyzing, manifesting, graph enrichment, queue dispatching, and report generation.

#### Architecture
- **Functions**: 
  - `_load_env`: Loads environment variables from a `.env` file.
  - `run_introspection`: Main entry point for the introspection process, coordinating various phases of the pipeline.
- **Data Flow**: 
  - The `_load_env` function is called at the beginning to load environment variables.
  - The `run_introspection` function orchestrates the entire pipeline, calling various modules for scanning, analysis, manifest writing, graph enrichment, queue dispatching, and report generation.

#### Patterns
- **None Explicitly Used**: The code does not explicitly follow any design patterns like factory, singleton, or observer. It is a straightforward procedural flow.

#### Dependencies
- **Imports**: 
  - `os`, `sys`, `logging`, `json`, `subprocess`, `redis`, `neo4j.GraphDatabase`
- **External Modules**: 
  - `iris.introspection.scanner`, `iris.introspection.analyzer`, `iris.introspection.manifest`, `iris.introspection.graph_enricher`, `iris.introspection.queue_dispatcher`, `iris.introspection.report`

#### Interfaces
- **Exposed Functions**: 
  - `run_introspection(base_path, target_path, quick, report_only, queue_status_only)`: Main entry point for the introspection pipeline.
- **Internal Functions**: 
  - `_load_env()`: Loads environment variables.

#### Database
- **PostgreSQL Tables**: 
  - `iris`: Used for storing manifest data.
  - `last`: Used for storing the last run's data.
- **Neo4j**: 
  - Used for graph enrichment.

#### Configuration
- **Environment Variables**: 
  - `MYTHOS_ROOT`: Root directory of the Mythos codebase.
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Configuration for Neo4j connection.
- **Config Files**: 
  - `.env` file located at `/opt/mythos/.env` is loaded to set environment variables.

#### Key Logic
- **Scanning**: 
  - Scans the filesystem for files and groups them by components.
- **Analysis**: 
  - Performs LLM analysis on files and components, skipping if in quick mode.
- **Manifest Writing**: 
  - Writes the manifest to the PostgreSQL database.
- **Graph Enrichment**: 
  - Enriches the Neo4j graph with relationships based on the manifest data.
- **Queue Dispatching**: 
  - Dispatches tasks to a Redis queue.
- **Report Generation**: 
  - Generates a report summarizing the introspection process.

#### Integration Points
- **Subsystems**:
  - **Scanner**: `iris.introspection.scanner` for scanning filesystem.
  - **Analyzer**: `iris.introspection.analyzer` for LLM analysis.
  - **Manifest**: `iris.introspection.manifest` for writing manifest to PostgreSQL.
  - **Graph Enricher**: `iris.introspection.graph_enricher` for enriching Neo4j graph.
  - **Queue Dispatcher**: `iris.introspection.queue_dispatcher` for dispatching tasks to Redis queue.
  - **Report**: `iris.introspection.report` for generating and formatting the report.

### Detailed Breakdown

#### `_load_env`
- **Purpose**: Loads environment variables from a `.env` file if it exists.
- **Implementation**: 
  - Checks if the `.env` file exists at `/opt/mythos/.env`.
  - Reads the file and sets environment variables for each line that contains a valid key-value pair.

#### `run_introspection`
- **Purpose**: Main entry point for the introspection pipeline.
- **Parameters**:
  - `base_path`: Root of the Mythos codebase.
  - `target_path`: Optional single component path to scan.
  - `quick`: Skip LLM analysis.
  - `report_only`: Only generate report from the last run.
  - `queue_status_only`: Only show queue status.
- **Implementation**:
  - Loads environment variables using `_load_env`.
  - Sets up logging.
  - Determines the introspection mode based on parameters.
  - Connects to PostgreSQL and creates a new run.
  - Scans the filesystem and groups files by components.
  - Performs LLM analysis if not in quick mode.
  - Writes the manifest to PostgreSQL.
  - Enriches the Neo4j graph.
  - Dispatches tasks to a Redis queue.
  - Generates a report and writes it to the database.
  - Outputs the report to the console.

### Summary
This file serves as the main orchestrator for the Mythos introspection pipeline, coordinating various subsystems to scan, analyze, and report on the Mythos codebase. It integrates with PostgreSQL, Neo4j, and Redis to perform its tasks and relies on environment variables for configuration.
