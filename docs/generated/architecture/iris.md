## iris
The **iris** component serves as Mythos's core operational layer, managing the agent's self-model, perception, memory, and LLM interactions to enable coherent environmental understanding and context-aware responses. It maintains the agent's persistent identity and operational state while processing inputs and generating outputs through a structured data flow.

**Key Files & Structure**  
- *Identity/Config*: `IDENTITY.md` (agent role), `MODEL_CONFIG.md` (LLM parameters), `OPERATIONAL.md` (constraints)  
- *Core Logic*: `agency.py` (decision flow), `self_model.py` (internal representation), `memory.py` (state storage), `perception.py` (input processing)  
- *Integration Points*: `llm.py` (LLM API), `prompts.py` (template management), `loop.py` (event cycle), `config.py` (component settings)  
- *Entry Points*: `main.py` (startup), `__init__.py` (module initialization), `health.py` (monitoring)

**Data Flow**  
Environmental inputs → `perception.py` (raw data processing) → `memory.py` (state update) + `self_model.py` (identity alignment) → `prompts.py` (contextual template assembly) → `llm.py` (LLM call) → `memory.py` (response storage) → `agency.py` (action routing) → `loop.py` (cycle iteration).

**Dependencies & Integration**  
- *Internal*: Relies on `memory.py` for state persistence and `self_model.py` for identity consistency.  
- *External*: Integrates with `llm` module (via `llm.py`), consumes `MODEL_CONFIG.md` for LLM parameters, and exposes `main.py` as the primary interface to higher-level components.  
- *Critical Path*: `loop.py` orchestrates all data flow; `agency.py` handles state transitions.

**Known Issues**  
- **Technical Debt**: `self_model.py` tightly couples identity logic with `memory.py`, complicating memory system replacement.  
- **Edge Cases**: `loop.py` lacks robust error handling for LLM timeouts (tracked in `health.py` monitoring gaps).  
- **Documentation Gap**: `OPERATIONAL.md` requires updates to reflect current constraint handling in `agency.py`.
