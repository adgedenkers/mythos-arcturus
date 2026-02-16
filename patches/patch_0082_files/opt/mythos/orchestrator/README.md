# Mythos Orchestrator

**Multi-Model AI Orchestration System**

---

## Status

**Version:** 1.15.1  
**Phase:** 1.1 - Core Infrastructure  
**Progress:** 1 of 7 phases complete

---

## Overview

Mythos Orchestrator is a sovereign AI system that intelligently routes queries through specialized local LLM models to produce superior results at zero marginal cost.

**Core Principle:** Use the best model for each specific task, orchestrate multiple models when needed, and maintain complete data sovereignty.

---

## Installation Progress

### ✅ Phase 1.1: Core Infrastructure (v1.15.1)
- Project structure
- Database schema (7 orch_* tables)
- Configuration system
- Core utilities

### ⏳ Phase 1.2: Ollama Integration (v1.15.2)
- Ollama client wrapper
- Model registry
- Model management

### ⏳ Phase 1.3-1.7: Remaining Phases
- Test Framework
- Grading System
- Test Runner
- Test Suites (1,500+ questions)
- Benchmarking & Reporting

### 🎯 Phase 1 Complete (v1.16.0)
- Full Model Bench operational
- Ready for Phase 2 (Router)

---

## Quick Start

### Current Capabilities (Phase 1.1)

```python
# Configuration
from src.config import settings
print(f"App: {settings.APP_NAME} v{settings.VERSION}")

# Utilities
from src.utils import generate_id, format_duration
run_id = generate_id("run")  # "run_abc123def456"
duration = format_duration(125.5)  # "2m 5.5s"

# Database (after Phase 1.2+)
from src.database import db
# models = await db.fetch("SELECT * FROM orch_models")
```

---

## Project Structure

```
/opt/mythos/orchestrator/
├── src/                    # Source code
│   ├── __init__.py        # Package init (✓)
│   ├── config.py          # Configuration (✓)
│   ├── database.py        # Database access (✓)
│   ├── utils.py           # Utilities (✓)
│   ├── bench/             # Testing framework (Phase 1.3+)
│   ├── models/            # Model management (Phase 1.2+)
│   └── [future modules]
├── test_suites/           # Test questions (Phase 1.6+)
├── results/               # Test results
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── logs/                  # Log files
└── .env                   # Configuration
```

---

## Database Schema

Phase 1.1 created 7 tables (all prefixed with `orch_`):

| Table | Purpose |
|-------|---------|
| `orch_models` | Registry of available models |
| `orch_model_capabilities` | Task-specific capabilities |
| `orch_test_suites` | Test suite definitions |
| `orch_test_questions` | Individual test questions |
| `orch_test_runs` | Test execution history |
| `orch_test_results` | Individual question results |
| `orch_model_benchmarks` | Aggregated performance metrics |

---

## Configuration

Edit `/opt/mythos/orchestrator/.env`:

```env
DATABASE_URL=postgresql://adge@localhost:5432/mythos
OLLAMA_HOST=http://localhost:11434
DATA_DIR=/opt/mythos/orchestrator/data
```

---

## Documentation

- **Architecture:** `docs/orchestrator/ARCHITECTURE.md`
- **Changelog:** `docs/orchestrator/CHANGELOG.md`
- **Version Control:** `docs/VERSION_CONTROL.md`

---

## Next Steps

1. **Verify installation:**
   ```bash
   python3 -c 'import sys; sys.path.insert(0, "/opt/mythos/orchestrator/src"); from config import settings; print(f"Version: {settings.VERSION}")'
   ```

2. **Install Phase 1.2:**
   - Deploy `patch_0083` (v1.15.2 - Ollama Integration)

---

## Version History

- **v1.0.0** - Base Mythos system
- **v1.15.1** - Phase 1.1: Core Infrastructure ← You are here
- **v1.15.2** - Phase 1.2: Ollama Integration (next)
- **v1.16.0** - Phase 1 Complete (Model Bench)

---

**Last Updated:** 2026-02-16  
**Maintainer:** Ka'tuar'el  
**System:** Arcturus
