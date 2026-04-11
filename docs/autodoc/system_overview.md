# Mythos System Architecture

**Generated:** 2026-04-04 18:32:05
**Files Analyzed:** 1725
**Modules:** 19

---

# Mythos: Self-Hosted AI Infrastructure Platform Architecture Document

---

## 1. What is Mythos?

**Mythos** is a self-hosted, modular AI infrastructure platform operating on a Linux server named **Arcturus**. It integrates advanced AI capabilities across five distinct development streams (SYS, LOG, NEU, MNE, SEN) to create a cohesive system that combines:

- **Consciousness modeling** (self-awareness, introspection)
- **Knowledge orchestration** (LLM coordination, skill execution)
- **Memory management** (voice memo ingestion, archival)
- **Perception processing** (astrology, sensory analysis)
- **System infrastructure** (APIs, databases, background workers)

Mythos is designed to be **adaptable**, **self-aware**, and **extensible**, with a focus on maintaining a dynamic self-model of its capabilities and dependencies. The system emphasizes **modular architecture**, **event-driven processing**, and **cross-stream integration** to enable complex AI behaviors while maintaining operational clarity.

---

## 2. Overall Architecture

The Mythos architecture is organized into **five core streams**, each with distinct responsibilities and interdependencies:

```
[User Input] → [Telegram Bot] → [FastAPI Gateway] → [Orchestrator] → [Background Workers]
    ↑                 ↑                  ↑                   ↑
    ↓                 ↓                  ↓                   ↓
[SYS: Infrastructure] [LOG: Knowledge] [NEU: Consciousness] [MNE: Memory] [SEN: Perception]
```

### Stream Responsibilities

| Stream | Core Function | Key Components |
|--------|---------------|----------------|
| **SYS** | System infrastructure | FastAPI Gateway, Telegram Bot, Background Workers, Finance System, Database Migrations |
| **LOG** | Knowledge orchestration | Skill Engine, LLM Orchestrator, Triad Identity System, Prompt System |
| **NEU** | Consciousness processing | NEURO (Perception Engine), Iris Core (Introspection Engine) |
| **MNE** | Memory management | Voice Memo Pipeline |
| **SEN** | Perception processing | Astrology Engine |

### Integration Points

- **SYS** provides the foundational infrastructure for all streams.
- **LOG** coordinates knowledge execution and LLM interactions.
- **NEU** enables self-awareness and introspection.
- **MNE** manages memory ingestion and synchronization.
- **SEN** processes sensory data (e.g., astrology charts).

---

## 3. Data Flow

### Primary Data Flow Path

```
Telegram Bot → FastAPI Gateway → Orchestrator → Background Workers → Databases
```

### Stream-Specific Flows

#### **SYS Stream**
- **User Input**: Telegram messages → FastAPI Gateway → Orchestrator → Background Workers
- **Database Operations**: PostgreSQL/Neo4j for structured data and graph relationships
- **Financial Data**: Transaction tracking, bill reminders, and analytics

#### **LOG Stream**
- **Skill Execution**: User input → Skill Engine → Skill modules → Result aggregation
- **LLM Orchestration**: Prompt composition → LLM invocation → Result logging
- **Triad Analysis**: Semantic/energetic/predictive extraction → PostgreSQL/Neo4j storage

#### **NEU Stream**
- **Perception Events**: External input → NEURO Perception Engine → Arcturian Grid processing → Iris Core introspection
- **Introspection Pipeline**: Codebase scanning → LLM analysis → PostgreSQL/Neo4j storage → Task dispatching

#### **MNE Stream**
- **Voice Memo Ingestion**: Syncthing synchronization → `.rode-manifest.json` tracking → Downstream processing

#### **SEN Stream**
- **Astrology Chart Generation**: User YAML input → Astrology Engine → Planetary calculations → Chart output (JSON/React)

---

## 4. Five-Stream Development Model

### **1. SYS (SYSTEM)**
- **Purpose**: Infrastructure backbone for all operations.
- **Key Features**:
  - Telegram bot for user interaction
  - FastAPI gateway for API entry points
  - Background workers for async processing
  - Financial system for transaction tracking
  - Database migrations for schema evolution

### **2. LOG (LOGOS)**
- **Purpose**: Knowledge orchestration and execution.
- **Key Features**:
  - Skill Engine for domain-specific tasks
  - LLM Orchestrator for model routing and metrics
  - Triad Identity System for semantic/energetic analysis
  - Prompt System for behavioral rules and mode switching

### **3. NEU (NEURO)**
- **Purpose**: Consciousness modeling and introspection.
- **Key Features**:
  - Arcturian Grid for perception routing
  - Iris Core for codebase analysis and health monitoring
  - PostgreSQL/Neo4j for metadata storage

### **4. MNE (MNEMOS)**
- **Purpose**: Memory ingestion and synchronization.
- **Key Features**:
  - Voice Memo Pipeline for cross-device synchronization
  - Syncthing integration for file tracking
  - `.rode-manifest.json` for metadata versioning

### **5. SEN (SENSUS)**
- **Purpose**: Sensory and perception processing.
- **Key Features**:
  - Astrology Engine for natal chart generation
  - Modular pipeline for planetary calculations
  - Geometry validation for chart accuracy

---

## 5. Key Design Decisions and Patterns

### **Core Design Principles**
- **Modularity**: Each stream operates as an independent module with clear interfaces.
- **Event-Driven Architecture**: Task orchestration via Redis queues.
- **Self-Awareness**: Iris Core enables introspection and system modeling.
- **Extensibility**: YAML/JSON configuration for rules, templates, and metadata.

### **Design Patterns**

| Pattern | Usage | Example |
|--------|-------|---------|
| **Microservices Architecture** | Decoupled modules | Background workers for async tasks |
| **Event-Driven Processing** | Task orchestration | Redis queues for worker communication |
| **Layered Architecture** | Separation of concerns | FastAPI Gateway for API entry points |
| **Singleton Pattern** | Centralized state | `SessionManager` for user tracking |
| **Factory Pattern** | Dynamic instantiation | `_get_conn` for database connections |
| **CQRS Pattern** | Read/write separation | `ContextManager` for conversation data |
| **Idempotent Operations** | Safe updates | Versioned migration scripts |

---

## 6. Technology Stack and Infrastructure

### **Languages and Frameworks**
- **Python**: Core implementation (872 files)
- **FastAPI**: API gateway
- **Telegram Bot API**: User interface
- **Ollama/Anthropic**: LLM inference
- **Redis**: Task queues and caching
- **PostgreSQL/Neo4j**: Data storage (structured/graph)
- **Docker**: Containerization for deployment

### **Infrastructure**
- **Linux Server**: Arcturus (hosting environment)
- **Syncthing**: Cross-device synchronization for MNE
- **Qdrant**: Vector embeddings for semantic search
- **Plaid**: Financial data integration
- **YouTube API**: Media monitoring

---

## 7. Iris (AI Entity) Operation

### **Role in NEU Stream**
Iris is the **introspection engine** within the NEU stream, responsible for:
- **Codebase Analysis**: Scanning the file system to detect components, dependencies, and capabilities.
- **Self-Modeling**: Maintaining a dynamic representation of the system's state in PostgreSQL/Neo4j.
- **Health Monitoring**: Generating reports and triggering corrective actions.

### **Operation Flow**
1. **Perception Events**: External inputs (e.g., user commands) trigger NEURO processing.
2. **Arcturian Grid**: Events are routed through hierarchical templates (ANCHOR/BEACON/COMPASS).
3. **Introspection Pipeline**:
   - Codebase scanning → LLM analysis → Database storage → Task dispatching.
4. **Health Reporting**: Reports are generated and sent to monitoring systems.

### **Key Components**
- **Perception Engine**: Routes events through consciousness layers.
- **Arcturian Grid**: Hierarchical template system for processing rules.
- **Iris Core**: Introspection pipeline with LLM-driven analysis.
- **Databases**: PostgreSQL for metadata, Neo4j for relationships.

---

## Conclusion

Mythos is a sophisticated, modular AI infrastructure platform that combines consciousness modeling, knowledge orchestration, memory management, and perception processing. Its five-stream architecture ensures scalability, adaptability, and self-awareness, making it a robust foundation for advanced AI systems. By leveraging event-driven design, microservices, and self-modeling capabilities, Mythos achieves a balance between operational efficiency and intelligent behavior.
