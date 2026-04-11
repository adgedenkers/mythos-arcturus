# Skill Engine

**Stream:** LOG
**Files:** 58

## Files in this Module

- `skills/README.md` (129L)
- `skills/REGISTRY.yaml` (157L)
- `skills/SKILL_DEVELOPMENT_GUIDE.md` (371L)
- `skills/engine/__init__.py` (10L)
- `skills/engine/base.py` (175L)
- `skills/engine/engine.py` (227L)
- `skills/engine/router.py` (111L)
- `skills/templates/SKILL_TEMPLATE.md` (77L)
- `skills/data/__init__.py` (1L)
- `skills/data/add_idea.py` (156L)
- `skills/data/astro_context.py` (177L)
- `skills/data/calendar_context.py` (186L)
- `skills/data/complete_routine.py` (134L)
- `skills/data/daily_briefing.py` (71L)
- `skills/data/daily_task_planner.py` (91L)
- `skills/data/extract_date_range.py` (130L)
- `skills/data/extract_search_terms.py` (120L)
- `skills/data/finance_balance.py` (166L)
- `skills/data/financial_overview.py` (63L)
- `skills/data/format_financial_summary.py` (113L)
- `skills/data/format_person_summary.py` (107L)
- `skills/data/grocery_skill.py` (441L)
- `skills/data/idea_backlog_manager.py` (80L)
- `skills/data/log_checkin.py` (121L)
- `skills/data/log_life_event.py` (124L)
- `skills/data/lunar_calendar_skill.py` (173L)
- `skills/data/memory_router.py` (149L)
- `skills/data/memory_search_composite.py` (147L)
- `skills/data/neo4j_graph_search.py` (100L)
- `skills/data/people_lookup.py` (187L)
- `skills/data/person_deep_dive.py` (71L)
- `skills/data/person_research.py` (209L)
- `skills/data/query_bills_due.py` (175L)
- `skills/data/query_calendar.py` (165L)
- `skills/data/query_natal_chart.py` (120L)
- `skills/data/query_routines.py` (136L)
- `skills/data/query_shopping_lists.py` (161L)
- `skills/data/query_transactions.py` (207L)
- `skills/data/rank_by_recency.py` (91L)
- `skills/data/rank_by_relevance.py` (134L)
- `skills/data/search_conversations.py` (197L)
- `skills/data/search_documents.py` (216L)
- `skills/data/search_ideas.py` (221L)
- `skills/data/search_life_events.py` (224L)
- `skills/data/search_voice_memos.py` (204L)
- `skills/data/spending_analysis.py` (116L)
- `skills/data/spiral_time.py` (85L)
- `skills/data/spiral_walker.py` (129L)
- `skills/data/web_browser.py` (298L)
- `skills/data/web_search.py` (389L)
- `skills/data/youtube_channel.py` (296L)
- `skills/data/youtube_intake.py` (220L)
- `skills/analytical/soul_stratigraphy.md` (294L)
- `skills/analytical/western_tropical_natal_chart.md` (147L)
- `skills/analytical/tools/ephemeris.py` (647L)
- `skills/analytical/tools/rectification.py` (463L)
- `skills/meta/humandoc_to_skill.md` (198L)
- `skills/meta/introspection_skill.py` (57L)

---

# Mythos Skill Engine Module Documentation

## 1. Module Purpose
The **Skill Engine** is the core execution framework of the Mythos system, enabling dynamic, context-aware skill invocation and orchestration. It manages skill discovery, routing, execution, and result aggregation to transform user inputs into structured outputs. The module supports:
- **Skill categorization** (analytical, builder, data, etc.)
- **Risk-tiered execution** (autonomous, semi-autonomous, manual approval)
- **Cross-subsystem integration** (PostgreSQL, Neo4j, Redis, FastAPI)
- **Caching and error handling** for performance and reliability

---

## 2. Architecture Overview
The Skill Engine operates as a layered pipeline:
1. **Registry Layer**:  
   - Reads `REGISTRY.yaml` to discover skills, tools, and triggers.
   - Maps skill metadata (name, version, dependencies, risk tier).
2. **Routing Layer**:  
   - Uses `SkillRouter`/`AlwaysOnRouter` to match user input to skills via keyword triggers.
   - Applies relevance scoring and risk-tier filtering.
3. **Execution Layer**:  
   - `SkillEngine` loads skill modules, executes them, and composes results.
   - Manages caching (`_cache_key`, `_set_cache`) and error propagation.
4. **Integration Layer**:  
   - Exposes skill results as prompt-ready context blocks.
   - Integrates with databases (PostgreSQL, Neo4j) and external APIs (FastAPI, Ollama).

**Data Flow**:
```
User Input → SkillRouter (Trigger Matching) → SkillEngine (Execution) → SkillResponse → Context Block
```

---

## 3. Key Components

### Core Classes
- **`SkillBase`** (Abstract Base Class):  
  - Defines `execute()`, `relevance()`, and caching methods.
  - Enforces metadata attributes (`name`, `version`, `triggers`, `risk_tier`).
- **`SkillRequest`**:  
  - Encapsulates user input, context, and parameters.
- **`SkillResponse`**:  
  - Structured output with `data`, `summary`, `confidence`, and `sources`.
- **`SkillEngine`**:  
  - Orchestrates skill discovery, execution, and result aggregation.
  - Methods: `load_skills()`, `process()`, `_assemble_context()`.
- **`SkillRouter` / `AlwaysOnRouter`**:  
  - Routes messages to skills via keyword matching and relevance scoring.

### Critical Files
- **`REGISTRY.yaml`**:  
  - Central registry for skill metadata, tools, and triggers.
- **`SKILL_TEMPLATE.md`**:  
  - Template for defining new skills with metadata and process steps.
- **`add_idea.py` / `astro_context.py`**:  
  - Example skills interacting with PostgreSQL (e.g., `idea_inbox`, `astro_natal_charts`).

---

## 4. Design Patterns
- **Factory Pattern**:  
  - `SkillEngine.load_skills()` dynamically loads skill modules.
- **Observer Pattern**:  
  - `SkillRouter` observes user input to activate relevant skills.
- **Registry Pattern**:  
  - `REGISTRY.yaml` acts as a centralized skill registry.
- **Decorator Pattern**:  
  - `AlwaysOnRouter` extends `SkillRouter` to enforce always-on skills.

---

## 5. Data Model
### Databases
- **PostgreSQL**:  
  - Tables: `idea_inbox`, `astro_natal_charts`, `astro_chart_objects`.
  - Used for structured data storage and retrieval.
- **Neo4j**:  
  - Labels: `User`, `Idea`, `Domain`.
  - For graph-based relationships (e.g., idea-to-domain links).
- **Redis**:  
  - Keys: `skill_cache:{skill_name}:{hash}`.
  - Caches skill results for performance.

### Example Schema (PostgreSQL)
```sql
CREATE TABLE idea_inbox (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    domain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. API Surface
### Internal Interfaces
- **Skill Engine API**:
  - `SkillEngine.load_skills()`: Loads skill modules from `SKILLS_DATA_DIR`.
  - `SkillEngine.process(message: str)`: Asynchronously routes and executes skills.
  - `SkillEngine.register_skill(skill: SkillBase)`: Manually registers a skill.
- **Skill Router API**:
  - `SkillRouter.route(message: str)`: Returns list of activated skills.

### External Endpoints (via FastAPI)
- **POST `/skills/execute`**:  
  - Triggers skill execution with user input.
- **GET `/skills/status`**:  
  - Returns engine diagnostics (e.g., loaded skills, cache stats).

---

## 7. Dependencies
### Internal
- **Modules**:  
  - `engine.base` (SkillBase, SkillRequest)
  - `engine.router` (SkillRouter)
  - `engine.engine` (SkillEngine)
- **Tools**:  
  - `ephemeris_engine` (astrological calculations)
  - `data_skills` (PostgreSQL/Neo4j adapters)

### External
- **Databases**:  
  - PostgreSQL, Neo4j, Redis
- **Libraries**:  
  - `psycopg2`, `neo4j`, `asyncio`, `pydantic`

---

## 8. Configuration
### Environment Variables
```env
POSTGRES_HOST=localhost
POSTGRES_DB=mythos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_PORT=5432
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j
SKILLS_DATA_DIR=/opt/mythos/skills/data
```

### Configuration Files
- **`REGISTRY.yaml`**:  
  - Defines skill metadata, tools, and triggers.
- **`.env`**:  
  - Stores database connection details and runtime settings.

---

## 9. Example Skill Integration
### Skill: `AddIdeaSkill`
- **Purpose**: Captures user ideas and inserts them into `idea_inbox`.
- **Process**:
  1. Extract idea text from user message.
  2. Detect domain via keyword matching.
  3. Insert into PostgreSQL with `created_at` timestamp.
- **Code Snippet**:
  ```python
  def _insert_idea(self, text: str, domain: str):
      with _get_conn() as conn:
          with conn.cursor() as cur:
              cur.execute(
                  "INSERT INTO idea_inbox (text, domain) VALUES (%s, %s) RETURNING id",
                  (text, domain)
              )
              idea_id = cur.fetchone()[0]
              conn.commit()
              return idea_id
  ```

---

## 10. Risk Tier Execution Model
| Risk Tier | Behavior | Approval Required |
|-----------|----------|-------------------|
| **T1-autonomous** | Full autonomy | No |
| **T2-semi-autonomous** | Requires confirmation | Yes (user) |
| **T3-manual** | Manual execution only | Yes (admin) |

---

## 11. Testing and Development
- **Skill Development Guide**:  
  - Follow `SKILL_TEMPLATE.md` for metadata and process steps.
  - Use `SKILL_DEVELOPMENT_GUIDE.md` for best practices.
- **Testing**:  
  - Run `python -m skills.data.add_idea` for standalone testing.
  - Use `pytest` for unit tests with mocked databases.

---

## 12. Future Enhancements
- **Dynamic Skill Loading**: Auto-reload skills on `REGISTRY.yaml` changes.
- **Graph-Based Routing**: Use Neo4j to map skill dependencies.
- **AI-Driven Triggers**: Replace keyword matching with NLP models.

---

This documentation provides a comprehensive overview of the Mythos Skill Engine, covering its architecture, components, and integration points. Developers should reference `REGISTRY.yaml` and `SKILL_TEMPLATE.md` when adding new skills, and use the `SkillEngine` API for orchestration.
