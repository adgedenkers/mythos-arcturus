# Stream: LOG

## Modules

- Chat Assistants
- Skill Engine
- Triad Identity System
- Prompt System
- LLM Orchestrator

---

# LOG Stream Architecture Overview

## 1. Stream Purpose  
The **LOG (LOGOS) stream** is the knowledge orchestration and execution core of the Mythos system, enabling dynamic, context-aware AI interactions through:  
- **Skill-based task execution** (e.g., financial queries, memory retrieval)  
- **LLM orchestration** (model routing, prompt engineering, performance tracking)  
- **Conversational memory management** (context preservation, history logging)  
- **Triadic identity modeling** (semantic, energetic, and predictive extraction)  
- **Prompt system configuration** (behavioral rules, voice profiles, mode switching)  

This stream unifies knowledge processing, skill execution, and LLM coordination to enable adaptive, rule-compliant AI interactions across domains.

---

## 2. Architecture Overview  
The LOG stream operates as a **modular pipeline** with five interdependent components:  

### **Core Layers**  
1. **Chat Assistants**  
   - Manages multi-turn conversations using Ollama/LLM models  
   - Integrates with databases (Neo4j, PostgreSQL) for query execution  
   - Coordinates with IrisMemory for persistent storage  

2. **Skill Engine**  
   - Routes user input to domain-specific skills (e.g., `finance_balance`, `web_search`)  
   - Executes skills via `SkillEngine` and aggregates results  
   - Uses `REGISTRY.yaml` for skill metadata and routing  

3. **Triad Identity System**  
   - Extracts semantic (Grid), energetic (Akashic), and predictive (Prophetic) layers from conversations  
   - Stores structured data in PostgreSQL and graph relationships in Neo4j  
   - Uses LLMs (Ollama/Anthropic) for triadic analysis  

4. **Prompt System**  
   - Defines behavioral rules via YAML/Markdown (e.g., `personality.yaml`, `modes/oracle.yaml`)  
   - Composes dynamic prompts by stacking layers (identity, memory, skill results)  
   - Controls voice profiles and operational modes  

5. **LLM Orchestrator**  
   - Registers and routes queries to LLM models (Ollama, Anthropic, etc.)  
   - Tracks execution metrics (latency, accuracy) in PostgreSQL  
   - Benchmarks models and tunes prompts for alignment  

---

## 3. Component Interactions  
### **Data Flow**  
1. **User Input** →  
2. **Chat Assistant** (context management, LLM routing) →  
3. **Skill Engine** (skill dispatch, result aggregation) →  
4. **Triad System** (semantic/energetic extraction) →  
5. **LLM Orchestrator** (model execution, logging) →  
6. **Prompt System** (context layer composition) →  
7. **Output** (structured response to user)  

### **Key Integration Points**  
- **Chat Assistants ↔ Skill Engine**: Skill routing via `SkillRouter` and result aggregation  
- **Skill Engine ↔ Triad System**: Post-processing of skill outputs for triadic analysis  
- **LLM Orchestrator ↔ Prompt System**: Dynamic prompt generation for model alignment  
- **All ↔ Databases**: PostgreSQL for tabular data, Neo4j for graph relationships  

---

## 4. Data Flow Details  
1. **Conversation Initiation**:  
   - User input is processed by `ChatAssistant`, which loads context from `IrisMemory` and routes to appropriate skill via `SkillRouter`.  

2. **Skill Execution**:  
   - `SkillEngine` loads the skill module, executes it, and returns structured results (e.g., financial data, calendar events).  

3. **Triadic Analysis**:  
   - `TriadExtractor` uses LLMs to extract Grid (semantic), Akashic (energetic), and Prophetic (predictive) layers from the conversation.  
   - Results are stored in PostgreSQL (`triad_grid`, `triad_akashic`) and Neo4j (`TriadConversation`, `TriadPattern`).  

4. **LLM Orchestration**:  
   - `Orchestrator` selects the appropriate LLM (e.g., Ollama, Anthropic) based on skill requirements and logs execution metrics.  

5. **Prompt Composition**:  
   - `PromptSystem` layers identity, memory, and skill results into a unified prompt for the LLM, applying voice profiles and mode-specific rules.  

---

## 5. Key Design Patterns  
| Pattern               | Implementation                                                                 |
|----------------------|--------------------------------------------------------------------------------|
| **Facade**           | `ChatAssistant` and `SkillEngine` abstract complex subsystem interactions.     |
| **Strategy**         | `SkillRouter` selects skills based on input context and risk tier.             |
| **Factory Method**   | `SkillEngine` dynamically loads skill modules via `REGISTRY.yaml`.             |
| **Singleton**        | `DatabaseManager` and `PromptSystem` manage shared resources as singletons.    |
| **Observer**         | Redis queues notify grid analysis workers of new conversations.                |
| **Layering**         | Prompt layers (identity, memory, skill results) are stacked for context.       |

---

## 6. Data Models  
### **PostgreSQL Tables**  
- **Chat Messages**:  
  - `chat_messages` (user context, conversation history, model metadata)  
- **Skill Data**:  
  - `skill_results` (structured outputs from skills like `finance_balance`)  
- **Triad Layers**:  
  - `triad_grid`, `triad_akashic`, `triad_prophetic` (semantic/energetic/predictive data)  

### **Neo4j Schema**  
- **Nodes**:  
  - `TriadConversation`, `TriadPattern`, `TriadDomain`  
- **Relationships**:  
  - `HAS_PATTERN`, `IN_DOMAIN`, `PLANTED_IN`  

### **Redis Usage**  
- Message queues for grid analysis workers  
- Temporary context storage for active conversations  

---

## 7. API Surface  
### **Internal Interfaces**  
- **Skill Engine**:  
  - `GET /skill/list` → List registered skills  
  - `POST /skill/execute` → Trigger skill execution  
- **LLM Orchestrator**:  
  - `POST /llm/invoke` → Route query to LLM  
  - `GET /llm/metrics` → Retrieve model performance data  
- **Prompt System**:  
  - `POST /prompt/mode` → Switch operational mode (e.g., `forge`, `hearthfire`)  

### **External Integrations**  
- **Ollama/Anthropic**: LLM inference endpoints  
- **PostgreSQL/Neo4j**: Data storage and graph analysis  
- **Telegram**: Chat interface for user input/output  

---

## 8. Integration with Other Streams  
- **NEU (Consciousness)**: Triad system feeds energetic insights to Arcturian Grid analysis  
- **MNE (Memory)**: IrisMemory stores chat history for recall in future interactions  
- **SYS (Infrastructure)**: LLM Orchestrator uses Redis queues managed by SYS workers  

---

## 9. Summary  
The LOG stream is the **knowledge orchestration engine** of Mythos, combining skill execution, LLM routing, and triadic analysis to enable adaptive, context-aware AI interactions. Its modular architecture ensures scalability, while layered patterns (Facade, Strategy) simplify complex workflows. By unifying PostgreSQL, Neo4j, and LLMs, LOG provides a robust foundation for intelligent, rule-compliant AI systems.
