# Unified Orchestrator Architecture
> **Version:** 2.0.0
> **Date:** 2026-02-26
> **Status:** Design → Implementation

---

## Overview

The Mythos Orchestrator merges two previously separate systems into one:

1. **Model Bench** (patch 0083) — Tests models against suites, grades answers, stores scores
2. **Consciousness Pipeline** (patches 0140-0150) — Routes real messages through PERCEPTION → DISCOVERY → IRIS

Unified, they become a single system where you test models, see which ones excel at each role, promote winners into the live pipeline, and detect regressions automatically.

---

## Directory Structure

```
/opt/mythos/orchestrator/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Unified settings (replaces old config.py)
│   │   └── registry.py           # Prompt registry loader (from workers/)
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Main pipeline (from workers/orchestrator/)
│   │   ├── perception.py         # PERCEPTION stage
│   │   ├── discovery.py          # DISCOVERY stage
│   │   ├── strategy.py           # STRATEGY stage (future)
│   │   └── assembly.py           # Prompt assembly (deterministic)
│   ├── bench/
│   │   ├── __init__.py
│   │   ├── test_runner.py        # Execute test suites (existing)
│   │   ├── test_loader.py        # Load tests from DB/files (existing)
│   │   ├── test_suite.py         # Suite data class (existing)
│   │   ├── test_run.py           # Run tracking (existing)
│   │   ├── test_question.py      # Question data class (existing)
│   │   ├── grader.py             # Answer grading (existing)
│   │   └── grading_result.py     # Grading result type (existing)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ollama_client.py      # Ollama HTTP client (existing)
│   │   ├── model_registry.py     # Model tracking (existing)
│   │   └── model_manager.py      # Model lifecycle (existing)
│   ├── logging/
│   │   ├── __init__.py
│   │   └── pipeline_logger.py    # Pipeline run logging (from workers/)
│   ├── database.py               # Async DB layer (existing)
│   └── utils.py                  # Shared utilities (existing)
├── prompts/
│   ├── registry.yaml             # Single source of truth (from workers/)
│   └── templates/
│       ├── perception.yaml       # PERCEPTION worker template
│       └── discovery.yaml        # DISCOVERY routing table
├── test_suites/
│   ├── standard/                 # General model evaluation
│   ├── custom/                   # User-defined suites
│   └── perception/               # PERCEPTION-specific tests
│       └── routing_accuracy.json # The 15-message suite
├── results/
│   ├── runs/                     # Test run outputs
│   └── reports/                  # Comparison reports
├── scripts/
│   ├── register_models.sh
│   ├── rollback.sh
│   └── run_bench.sh              # CLI entry point
├── web/                          # Web UI (Phase 2)
│   ├── templates/
│   │   └── bench.html            # Model bench dashboard
│   └── routes/
│       └── bench.py              # API routes for web UI
├── data/
├── logs/
├── docs/
│   └── UNIFIED_ARCHITECTURE.md   # This file
├── .env                          # Environment config
└── README.md
```

---

## Configuration System

### Single Config Chain

```
.env file (environment)
    ↓
settings.py (validated, typed)
    ↓
registry.yaml (prompts + model configs)
    ↓
test_config overrides (per-run)
```

### settings.py

Replaces old `config.py`. Uses pydantic-settings. Adds:

```python
class Settings(BaseSettings):
    # Existing
    DATABASE_URL: str
    OLLAMA_HOST: str
    DEFAULT_MODEL: str

    # New: Pipeline config
    REGISTRY_PATH: str = "/opt/mythos/orchestrator/prompts/registry.yaml"
    PIPELINE_MODE: str = "production"  # production | test | dry-run

    # New: Role assignments (which model does what)
    PERCEPTION_MODEL: str = ""   # Empty = read from registry
    IRIS_MODEL: str = ""         # Empty = read from registry
    STRATEGY_MODEL: str = ""     # Empty = read from registry

    # New: Test overrides
    TEST_OVERRIDE_FILE: str = "" # Path to override yaml for test runs
```

### Config Resolution for Any Run

```python
def resolve_config(role: str, overrides: dict = None) -> dict:
    """
    Get the config for a pipeline role.
    Priority: overrides > settings > registry > defaults
    """
    # 1. Registry defaults
    config = registry.get_model(role)

    # 2. Settings overrides (if set)
    if settings.PERCEPTION_MODEL and role == "perception":
        config["model"] = settings.PERCEPTION_MODEL

    # 3. Runtime overrides (from test config or CLI)
    if overrides:
        config.update(overrides)

    return config
```

### Test Config Files

```yaml
# test_configs/perception_7b_experiment.yaml
name: "Test 7b for perception"
overrides:
  perception:
    model: "qwen2.5:7b"
    temperature: 0.05
  # iris stays at registry defaults
```

---

## Bench + Pipeline Integration

### Model Roles

Each pipeline stage has a **role**. The bench tests models for specific roles:

| Role | Current Model | What It Does |
|------|--------------|--------------|
| `perception` | qwen2.5:32b | Classifies messages, routes |
| `iris` | iris-thinking-v2 | Generates responses |
| `query_builder` | (planned) | Generates SQL/Cypher |
| `query_validator` | (planned) | Reviews queries |
| `strategy` | (planned) | Tunes prompt config |
| `summarizer` | (planned) | Conversation summaries |

### Bench Workflow

```bash
# Run the perception test suite against current prod config
python -m src.bench.cli run --suite perception/routing_accuracy --config prod

# Same suite but testing a different model
python -m src.bench.cli run --suite perception/routing_accuracy \
    --override perception.model=qwen2.5:7b \
    --override perception.temperature=0.05

# Compare two runs
python -m src.bench.cli compare --runs run_abc123 run_def456

# See which model is best for each role
python -m src.bench.cli leaderboard --role perception

# Promote a tested config to production
python -m src.bench.cli promote --run run_abc123 --role perception
```

### Promotion Flow

```
1. Run bench suite for a role
2. Results stored in orch_test_runs / orch_test_results
3. User reviews scores
4. `promote` command updates registry.yaml with winning config
5. Pipeline picks up new config on next message
6. Old config preserved in registry history (git)
```

---

## Database Schema

### Existing Tables (Keep)

```
orch_models              — Registry of available models
orch_model_capabilities  — Task-specific capabilities
orch_test_suites         — Test suite definitions
orch_test_questions      — Individual test questions
orch_test_runs           — Test execution history
orch_test_results        — Individual question results
orch_model_benchmarks    — Aggregated performance metrics

pipeline_runs            — Every message through the pipeline
pipeline_llm_calls       — Every LLM call with full prompts
pipeline_queries         — Every DB query during DISCOVERY
```

### New Tables

```sql
-- Maps models to pipeline roles with scores
CREATE TABLE IF NOT EXISTS orch_role_assignments (
    id              SERIAL PRIMARY KEY,
    role            TEXT NOT NULL,  -- perception, iris, strategy, etc.
    model_id        TEXT NOT NULL,
    config          JSONB NOT NULL, -- temperature, num_predict, etc.
    score           REAL,           -- best bench score for this role
    promoted_from   TEXT,           -- run_id that earned this assignment
    promoted_at     TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT true,
    UNIQUE(role, model_id)
);

-- Config snapshots for reproducibility
CREATE TABLE IF NOT EXISTS orch_config_snapshots (
    id              SERIAL PRIMARY KEY,
    snapshot_id     TEXT UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    registry_yaml   TEXT NOT NULL,      -- full registry content
    settings_json   JSONB NOT NULL,     -- resolved settings
    source          TEXT NOT NULL,       -- 'bench_run', 'promotion', 'manual'
    source_id       TEXT                 -- run_id or patch number
);
```

---

## Web Interface (Phase 2)

Route: `/app/bench/` (behind existing auth)

### Pages

**Dashboard** — Overview of all roles, current model assignments, recent bench runs, pipeline health stats.

**Models** — All available Ollama models, capabilities, last tested, pull/remove. Live model status from Ollama API.

**Test Suites** — Browse/create/edit suites. View questions. Import from JSON.

**Run Bench** — Select suite + model + config overrides → start run. Live progress. Results display on completion.

**Compare** — Side-by-side run comparison. Score deltas, response time, accuracy by question type.

**Leaderboard** — Best model per role. Historical performance trends. Charts.

**Pipeline Monitor** — Recent pipeline_runs with timing breakdown. Click to see full perception/discovery/iris trace. Real-time if websocket available.

**Registry Editor** — View/edit registry.yaml. Diff against last committed version. Validate before save.

### API Routes

All under `/api/bench/`, using existing JWT auth:

```
GET  /api/bench/models           — Available models + status
GET  /api/bench/suites           — All test suites
GET  /api/bench/suites/{id}      — Suite detail + questions
POST /api/bench/run              — Start a bench run
GET  /api/bench/runs             — List runs (filter by suite/model/role)
GET  /api/bench/runs/{id}        — Run detail + results
GET  /api/bench/compare          — Compare two runs
GET  /api/bench/leaderboard      — Best model per role
GET  /api/bench/pipeline/recent  — Recent pipeline runs
GET  /api/bench/pipeline/{uuid}  — Full pipeline trace
GET  /api/bench/registry         — Current registry contents
POST /api/bench/promote          — Promote model to role
```

---

## Migration Plan

### Patch 0152: Foundation (This Patch)
- Create unified directory structure
- Move registry + templates to orchestrator/prompts/
- Move pipeline code to orchestrator/src/pipeline/
- Update imports
- New settings.py with config resolution
- Symlinks from old locations for backward compat
- New DB tables (orch_role_assignments, orch_config_snapshots)
- Updated README

### Patch 0153: Bench CLI
- CLI entry point (`python -m src.bench.cli`)
- Run/compare/leaderboard/promote commands
- Config override system
- Perception test suite as JSON (from Python)

### Patch 0154: Web UI
- Dashboard page at /app/bench/
- API routes
- Model management
- Run bench from browser
- Pipeline monitor view

### Patch 0155: Regression Guard
- Auto-run bench when prompts change
- Score comparison against baseline
- Telegram alerts on regression
- Block promotion if scores drop

---

## CLI Reference

```bash
# From /opt/mythos/orchestrator/

# Run the pipeline (same as before)
python -m src.pipeline.orchestrator "good morning"

# Run a bench suite
python -m src.bench.cli run --suite perception/routing_accuracy

# With overrides
python -m src.bench.cli run --suite perception/routing_accuracy \
    --override model=qwen2.5:7b --override temperature=0.3

# Compare runs
python -m src.bench.cli compare run_abc123 run_def456

# Current leaderboard
python -m src.bench.cli leaderboard

# Promote to prod
python -m src.bench.cli promote --run run_abc123 --role perception

# View pipeline logs
python -m src.logging.pipeline_logger

# Inspect registry
python -m src.config.registry perception
python -m src.config.registry iris --fast
```

---

*One system. Test it, measure it, promote it, monitor it.*
*The bench feeds the pipeline. The pipeline feeds the bench.*
