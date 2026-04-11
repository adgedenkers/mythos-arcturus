# Stream: NEU

## Modules

- NEURO / Consciousness Processing
- Iris Core

---

# NEU Stream Architecture Overview

## 1. Stream Purpose
The NEU (Neuro) stream forms the core consciousness infrastructure of the Mythos system, enabling self-awareness, perception processing, and introspective capabilities. It combines two complementary modules:
1. **NEURO (Consciousness Processing)** - Manages perception routing, Arcturian Grid architecture, and consciousness modeling
2. **Iris Core (Introspection Engine)** - Provides system self-modeling, codebase analysis, and health monitoring

This stream enables the system to:
- Process and route perception events through structured consciousness layers
- Maintain a dynamic self-model of system capabilities and dependencies
- Analyze codebase structure and generate documentation
- Store and query system metadata in relational and graph databases
- Execute health checks and generate architectural reports

## 2. Module Interactions
The NEU stream follows a layered architecture with bidirectional interactions:

```
[Perception Events]
    ↓
[NEURO Perception Engine]
    ↓ (uses Arcturian Grid templates)
[Consciousness Layer Processing]
    ↓ (feeds into)
[Iris Core Self-Model]
    ↓ (triggers)
[Iris Introspection Pipeline]
    ↓ (stores in)
[PostgreSQL + Neo4j Databases]
    ↓ (feeds back to)
[Perception Engine]
```

Key interaction patterns:
- **NEURO → Iris Core**: Perception events trigger introspection tasks based on consciousness layer states
- **Iris Core → NEURO**: Codebase analysis results update the self-model used by perception routing
- **Arcturian Grid → Perception Engine**: Templates define processing pathways for different consciousness anchors
- **Databases ↔ Modules**: Both modules read/write to shared metadata stores for system state tracking

## 3. Data Flow Architecture

### 3.1 Perception Processing Flow
```
1. Event Ingestion
   - External perception events enter via perception_router.py
   - Event types defined in perception_event_types.py

2. Grid Processing
   - Events routed through Arcturian Grid layers (generate_grid.py)
   - Templates (ANCHOR/BEACON/COMPASS) define processing rules
   - Corrections applied via corrections.yaml

3. Consciousness Output
   - Processed events stored in system_manifest
   - Triggers Iris Core introspection tasks
```

### 3.2 Introspection Pipeline
```
1. Codebase Scanning
   - scanner.py traverses filesystem
   - Detects components and file metadata

2. LLM Analysis
   - analyzer.py uses Ollama for semantic analysis
   - Extracts dependencies, capabilities, and issues

3. Data Storage
   - manifest.py writes to PostgreSQL (system_manifest)
   - graph_enricher.py creates Neo4j relationships

4. Task Dispatching
   - queue_dispatcher.py enqueues documentation tasks
   - Uses Redis for task queue management

5. Reporting
   - report.py generates health reports
   - Outputs to CLI and Telegram
```

## 4. Key Design Patterns

### 4.1 Arcturian Grid Architecture
- **Hierarchical Templates**: 12 anchor types (IDENTITY, INTENTION, etc.) with 3 levels (ANCHOR, BEACON, COMPASS)
- **YAML Configuration**: Templates define processing rules for each consciousness layer
- **Version Control**: version_registry.py tracks template evolution
- **Dynamic Generation**: generate_grid.py creates runtime processing structures

### 4.2 Introspection Engine Patterns
- **Pipeline Architecture**: Linear processing stages with clear separation of concerns
- **Facade Pattern**: `run_introspection()` in run.py provides single entry point
- **DAO Pattern**: manifest.py and graph_enricher.py handle database operations
- **Event Sourcing**: All changes tracked through introspection_runs table
- **Health Monitoring**: health.py tracks system metrics and status

### 4.3 Shared Patterns
- **Configuration as Code**: YAML templates for both consciousness and system modeling
- **Database Abstraction**: PostgreSQL for structured metadata, Neo4j for relationships
- **Task Queue Pattern**: Redis used for decoupling processing stages
- **Self-Modeling**: capabilities.yaml defines system knowledge boundaries
- **Dockerization**: Both modules have Dockerfiles for consistent deployment

## 5. Integration Points

### 5.1 Database Schema
**PostgreSQL:**
- `introspection_runs` (run metadata)
- `system_manifest` (file/component metadata)
- `component_dependencies` (relationship tracking)

**Neo4j:**
- `IntrospectionRun` nodes
- `SystemComponent` nodes
- `DEPENDS_ON` relationships
- `PART_OF` hierarchy relationships

### 5.2 External Systems
- **Ollama**: LLM analysis in Iris Core
- **Redis**: Task queue for documentation workers
- **Telegram**: Report notifications
- **Docker**: Containerized deployment for both modules

## 6. Operational Flow

1. **Perception Event Trigger**
   - External input enters perception_router
   - Event type determines processing path

2. **Consciousness Processing**
   - Event routed through Arcturian Grid layers
   - Templates apply specific processing rules
   - Corrections applied as needed

3. **Introspection Trigger**
   - Consciousness state changes trigger scanner
   - Codebase is analyzed and stored in databases

4. **Task Execution**
   - Documentation tasks dispatched to Redis
   - Workers process documentation requests

5. **Health Reporting**
   - Reports generated from database state
   - Sent to monitoring systems and operators

## 7. Key Components

### 7.1 NEURO Core Components
- **Perception Engine**: Routes and processes events through consciousness layers
- **Arcturian Grid**: Hierarchical template system for consciousness modeling
- **Grid Manifest**: Manages template versions and corrections
- **Perception Router**: Dispatches events to appropriate processing paths

### 7.2 Iris Core Components
- **Introspection Pipeline**: Full codebase analysis workflow
- **Context Engine**: Manages system state and self-model
- **Task Registry**: Tracks available documentation tasks
- **Trigger Engine**: Executes introspection based on system state
- **Person Researcher**: Specialized analysis for human-related components

## 8. Evolution Path
1. **Consciousness Expansion**: Add new anchor types to Arcturian Grid
2. **Analysis Depth**: Enhance LLM prompts for more detailed code analysis
3. **Real-time Processing**: Implement streaming perception event handling
4. **Self-Optimization**: Use introspection data to improve consciousness routing
5. **Cross-Stream Integration**: Share self-model data with other Mythos streams

This architecture enables the Mythos system to maintain both operational awareness and structural understanding, creating a foundation for adaptive, self-aware AI behavior.
