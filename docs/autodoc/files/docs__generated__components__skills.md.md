# docs/generated/components/skills.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 91

---

### Purpose
The `skills.md` file serves as a comprehensive reference document for the skills component of the Mythos system. It outlines the modular framework for defining, registering, and executing AI-powered capabilities within the Mythos platform, including details on key files, data stores, integration points, and configuration.

### Architecture
The skills component is designed around a modular framework with several key files and roles:
- **Core Skill Files**: `analytical/soul_stratigraphy.md`, `analytical/tools/ephemeris.py`, `analytical/tools/rectification.py`, `analytical/western_tropical_natal_chart.md`.
- **Skill Templates and Guides**: `builder/` directory.
- **Data Integration**: `data/astro_context.py`, `data/calendar_context.py`, `data/finance_balance.py`.
- **Skill Engine**: `engine/base.py`, `engine/engine.py`, `engine/router.py`.
- **Meta Skills**: `meta/introspection_skill.py`.
- **Registry and Configuration**: `REGISTRY.yaml`, `SKILL_DEVELOPMENT_GUIDE.md`.

### Patterns
1. **Skill Registration Pattern**: Skills are registered in `REGISTRY.yaml` with metadata and entry points.
2. **Skill Development Workflow**: Skills are developed following a standardized process documented in `SKILL_DEVELOPMENT_GUIDE.md`.
3. **Data Context Pattern**: Data access is abstracted through classes like `AstroContext` in `data/astro_context.py`.
4. **Telegram Integration Pattern**: Skills can be integrated with the Telegram bot via custom handlers.
5. **Introspection Standard**: All skills must implement `get_metadata()` to provide introspection capabilities.

### Dependencies
The skills component relies on:
- **Python Modules**: `ephemeris.py`, `rectification.py`, `astro_context.py`, `calendar_context.py`, `finance_balance.py`, `base.py`, `engine.py`, `router.py`, `introspection_skill.py`.
- **External Libraries**: FastAPI, Neo4j, PostgreSQL, Redis.
- **Configuration Files**: `.env`, `REGISTRY.yaml`.

### Interfaces
The skills component exposes:
- **API Endpoints**: `/api/skills` via FastAPI.
- **Telegram Bot Commands**: `/skills` and other custom commands.
- **Skill Execution**: Through the `execute()` method defined in `engine/base.py`.

### Database
- **PostgreSQL**: `finance_balance.py` accesses the `balance_sheet` table.
- **Neo4j**: `astro_context.py` manages nodes (`Person`, `Event`) and relationships (`BORN_AT`, `HAS_CHART`).

### Configuration
The skills component uses the following environment variables and configuration files:
- **Environment Variables**: `MYTHOS_DB_URL`, `NEO4J_URI`, `NEO4J_AUTH`, `REDIS_URL`.
- **Configuration Files**: `REGISTRY.yaml` for skill registration.

### Key Logic
- **Skill Execution**: Managed by `engine/engine.py`, which loads skills from `REGISTRY.yaml` and routes requests to the appropriate skill implementation.
- **Data Context**: `astro_context.py` and `finance_balance.py` provide data access layers for Neo4j and PostgreSQL, respectively.
- **Telegram Integration**: Custom handlers in `build_feature_telegram_tool.md` integrate skills with the Telegram bot.

### Integration Points
- **FastAPI**: Skills are exposed via the `/api/skills` endpoint.
- **Telegram Bot**: Skills can be invoked via bot commands.
- **Ollama**: Skills can invoke LLMs for natural language processing.
- **Neo4j/PostgreSQL**: Data context modules provide data access layers for skills.

### Summary
The `skills.md` file provides a detailed overview of the skills component in the Mythos system, covering its architecture, design patterns, dependencies, interfaces, database interactions, configuration, key logic, and integration points. This document serves as a reference for developers and system administrators to understand and extend the skills framework within the Mythos platform.
