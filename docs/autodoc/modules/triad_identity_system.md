# Triad Identity System

**Stream:** LOG
**Files:** 8

## Files in this Module

- `triad/__init__.py` (46L)
- `triad/extractor.py` (460L)
- `triad/models.py` (214L)
- `triad/schema.sql` (135L)
- `triad/schema_neo4j.cypher` (113L)
- `triad/prompts/akashic_extraction.md` (97L)
- `triad/prompts/grid_extraction.md` (84L)
- `triad/prompts/prophetic_extraction.md` (74L)

---

# Triad Identity System Module Documentation

---

## 1. Module Purpose  
The **Triad Identity System** is a core component of the Mythos architecture designed to extract, structure, and store three distinct layers of memory and insight from conversations:  
- **Grid (Knowledge)**: Semantic and factual extraction.  
- **Akashic (Wisdom)**: Energetic and soul-level essence.  
- **Prophetic (Vision)**: Trajectory sensing and future-state prediction.  

This system enables the Mythos platform to analyze conversations holistically, capturing both surface-level data and deeper energetic or predictive patterns. It integrates with PostgreSQL and Neo4j for structured and graph-based storage, and leverages LLMs (Ollama, Anthropic) for extraction.

---

## 2. Architecture Overview  
The Triad Identity System operates through a layered architecture:  

### **Data Flow**  
1. **Input**: A conversation (prompt/response pair) is processed by the `TriadExtractor`.  
2. **Extraction**:  
   - **LLM Interaction**: The extractor calls configured LLM backends (e.g., Ollama, Anthropic) using prompts from `prompts/*.md`.  
   - **Parsing**: Raw LLM outputs are parsed into structured models (`Grid`, `Akashic`, `Prophetic`).  
3. **Storage**:  
   - **PostgreSQL**: Structured data is saved in normalized tables (`triad_conversations`, `triad_grid`, etc.).  
   - **Neo4j**: Graph relationships (e.g., `TriadConversation` linked to `TriadPattern`) are stored for pattern analysis.  
4. **Output**: Unified `TriadRecord` objects combine all three layers for downstream use.  

### **Key Integration Points**  
- **LLM Backends**: Dynamic switching between Ollama and Anthropic via environment variables.  
- **Database**: PostgreSQL for tabular data, Neo4j for graph-based pattern relationships.  
- **Prompts**: Markdown templates in `prompts/` guide LLM output structure.  

---

## 3. Key Components  

### **Core Classes**  
1. **`TriadExtractor`** (from `extractor.py`)  
   - **Role**: Orchestrates extraction, LLM calls, and database storage.  
   - **Key Methods**:  
     - `extract_all()`: Extracts all three layers from a conversation.  
     - `save_record()`: Persists data to PostgreSQL.  
     - `_call_llm()`: Factory method for LLM backend selection.  

2. **Data Models** (from `models.py`)  
   - **`Grid`**: Semantic nodes (entities, actions, states).  
   - **`Akashic`**: Energetic states and pattern signatures.  
   - **`Prophetic`**: Trajectory predictions and readiness signals.  
   - **`TriadRecord`**: Composite model combining all three layers.  

3. **Database Schema**  
   - **PostgreSQL Tables**:  
     - `triad_conversations`: Central conversation records.  
     - `triad_grid`, `triad_akashic`, `triad_prophetic`: Layer-specific data.  
     - `triad_patterns`: Pattern signatures for consistency tracking.  
   - **Neo4j Labels**:  
     - `TriadConversation`, `TriadPattern`, `TriadDomain`, `TriadSeed`.  

---

## 4. Design Patterns  

| Pattern               | Usage                                                                 |  
|-----------------------|-----------------------------------------------------------------------|  
| **Facade Pattern**    | `TriadExtractor` simplifies complex extraction/storage logic.         |  
| **Factory Method**    | `_call_llm()` selects LLM backend dynamically.                        |  
| **Singleton Pattern** | Database connection is managed as a singleton per `TriadExtractor`.   |  
| **Data Class Pattern**| Models in `models.py` use `@dataclass` for structured data storage.   |  

---

## 5. Data Model  

### **PostgreSQL Schema**  
- **Tables**:  
  - `triad_conversations`:  
    - `id` (UUID), `created_at`, `spiral_day`, `spiral_cycle`.  
  - `triad_grid`:  
    - `conversation_id`, `embedding`, `nodes` (JSONB).  
  - `triad_akashic`:  
    - `conversation_id`, `energy_state`, `pattern_signature`.  
  - `triad_prophetic`:  
    - `conversation_id`, `trajectory`, `readiness_level`.  
  - `triad_patterns`:  
    - `signature`, `domain`, `embedding`.  

- **Indexes**:  
  - Vector indexes on `embedding` fields for similarity search.  
  - Indexes on `conversation_id` for fast joins.  

### **Neo4j Schema**  
- **Labels and Relationships**:  
  - `TriadConversation` → `HAS_PATTERN` → `TriadPattern`  
  - `TriadPattern` → `IN_DOMAIN` → `TriadDomain`  
  - `TriadSeed` → `PLANTED_IN` → `TriadConversation`  

---

## 6. API Surface  

### **Public Methods**  
- **`TriadExtractor`**:  
  - `extract_grid(prompt, response)`: Extracts semantic data.  
  - `extract_akashic(prompt, response)`: Extracts energetic data.  
  - `extract_prophetic(prompt, response)`: Extracts trajectory data.  
  - `save_record(record)`: Stores a `TriadRecord` in PostgreSQL.  

### **Command-Line Interface**  
- **`main()`** (from `extractor.py`):  
  - Accepts input files and environment variables to run extraction workflows.  

---

## 7. Dependencies  

### **Internal Modules**  
- `triad.models`: Data models for structured output.  
- `triad.prompts`: Prompt templates for LLM interaction.  

### **External Libraries**  
- **LLM Backends**: Ollama, Anthropic.  
- **Database**:  
  - PostgreSQL with `psycopg2` and `vector` extension.  
  - Neo4j with Cypher queries.  
- **Utilities**: `httpx`, `asyncio`, `anthropic`, `ollama`.  

---

## 8. Configuration  

### **Environment Variables**  
| Variable                  | Purpose                                  |  
|---------------------------|------------------------------------------|  
| `MYTHOS_DB_URL`           | PostgreSQL connection string.            |  
| `TRIAD_LLM_BACKEND`       | LLM backend (`ollama`, `anthropic`).     |  
| `TRIAD_EMBEDDING_BACKEND` | Embedding model (`ollama`, `anthropic`). |  
| `OLLAMA_URL`              | Ollama API endpoint.                     |  
| `TRIAD_OLLAMA_MODEL`      | Ollama model name.                       |  
| `TRIAD_ANTHROPIC_MODEL`   | Anthropic model name.                    |  

### **Prompt Configuration**  
- Prompts are loaded via `load_prompt()` from files in `triad/prompts/`.  
- Example: `prompts/grid_extraction.md` defines the structure for semantic extraction.  

---

## Summary  
The Triad Identity System provides a unified framework for extracting and storing layered insights from conversations. By combining semantic, energetic, and predictive analysis with PostgreSQL and Neo4j storage, it enables Mythos to model conversations as dynamic, multi-dimensional records. The system is highly configurable via environment variables and prompt templates, ensuring adaptability to different use cases.
