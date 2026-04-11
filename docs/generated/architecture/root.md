## root
The root component serves as the central orchestration layer for the Mythos platform, unifying core services, authentication, data management, and external integrations into a cohesive system. It provides the foundational structure for all sub-components while managing cross-cutting concerns like context handling and metadata indexing.

**Key Files & Structure**  
Critical root-level files include:  
- `main.py`: Primary entry point for application startup.  
- `orchestrator.py`: Coordinates high-level workflows (e.g., media processing, financial operations).  
- `context_manager.py`: Manages global application state and session context.  
- `ontology.py`/`doc_registry.py`: Define semantic metadata structure and document indexing.  
- `google_auth.py`: Handles OAuth2 authentication flows.  
- `iris_systems.py`: Integrates with external Iris data systems.  
- `media_routes.py`/`finance.py`: Domain-specific service endpoints.  
The structure groups functionality by domain (e.g., `finance`, `media`) with minimal top-level complexity.

**Data Flow**  
User authentication (`google_auth.py`) → Context initialization (`context_manager.py`) → Workflow orchestration (`orchestrator.py`) → Domain-specific processing (e.g., media via `media_routes.py`, financial data via `finance.py`) → Metadata indexing (`doc_registry.py`/`ontology.py`) → Frontend rendering (`frontend.py`). Data persists via SQL databases and external systems (e.g., Iris).

**Dependencies & Integration Points**  
- **External**: Google OAuth2, Iris Systems API, SQL databases.  
- **Internal**: `orchestrator.py` depends on `ontology.py` (metadata), `media_routes.py` (media ops), and `iris_systems.py` (external data).  
- **Key Integration**: `frontend.py` consumes metadata from `doc_registry.py` and `ontology.py`; `finance.py` feeds into `orchestrator.py` for transaction workflows.

**Known Issues & Technical Debt**  
- **Over-engineered context management**: `context_manager.py` and redundant `__init__.py` files (3 instances) increase cognitive load without clear benefit.  
- **Placeholder code**: `integration_example.py` is unused and untested, representing unaddressed technical debt.  
- **Scalability risk**: High file count (433) and line density (81,836) suggest potential for refactoring to reduce complexity in core workflows.
