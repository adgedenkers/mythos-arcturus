# Tools

**Stream:** SYS
**Files:** 54

## Files in this Module

- `tools/autodoc.py` (1612L)
- `tools/event_simulator.py` (596L)
- `tools/generate_system_state.py` (429L)
- `tools/integrity_cron.sh` (30L)
- `tools/iris_ab_sweep.py` (671L)
- `tools/iris_calibrate.py` (579L)
- `tools/iris_prompt_test.py` (287L)
- `tools/iris_test_rig.py` (762L)
- `tools/orchestration_test.py` (1101L)
- `tools/rode-cleanup.sh` (190L)
- `tools/prompt_lab/bench.py` (340L)
- `tools/prompt_lab/layer_test.sh` (48L)
- `tools/prompt_lab/layer_walk.sh` (137L)
- `tools/prompt_lab/model_sweep.sh` (122L)
- `tools/prompt_lab/tweak.py` (227L)
- `tools/prompt_lab/results/run_20260301_085352_full_no_life_sovereign_qwen2.5_32b.json` (419L)
- `tools/prompt_lab/results/run_20260301_085418_full_no_life_default_qwen2.5_32b.json` (363L)
- `tools/prompt_lab/results/run_20260301_085502_full_no_life_sovereign_qwen2.5_32b.json` (416L)
- `tools/prompt_lab/results/run_20260301_090049_full_no_life_sovereign_qwen2.5_32b.json` (382L)
- `tools/prompt_lab/results/run_20260301_104414_naked_sovereign_qwen2.5_32b.json` (55L)
- `tools/prompt_lab/results/run_20260301_104424_identity_only_sovereign_qwen2.5_32b.json` (63L)
- `tools/prompt_lab/results/run_20260301_104433_identity_personality_sovereign_qwen2.5_32b.json` (68L)
- `tools/prompt_lab/results/run_20260301_104442_identity_personality_voice_sovereign_qwen2.5_32b.json` (56L)
- `tools/prompt_lab/results/run_20260301_104449_full_no_life_sovereign_qwen2.5_32b.json` (49L)
- `tools/prompt_lab/results/run_20260301_104456_full_stack_sovereign_qwen2.5_32b.json` (58L)
- `tools/prompt_lab/results/run_20260301_104511_naked_sovereign_iris-thinking-v2.json` (66L)
- `tools/prompt_lab/results/run_20260301_104517_identity_only_sovereign_iris-thinking-v2.json` (54L)
- `tools/prompt_lab/results/run_20260301_104522_identity_personality_sovereign_iris-thinking-v2.json` (49L)
- `tools/prompt_lab/results/run_20260301_104528_identity_personality_voice_sovereign_iris-thinking-v2.json` (49L)
- `tools/prompt_lab/results/run_20260301_104533_full_no_life_sovereign_iris-thinking-v2.json` (49L)
- `tools/prompt_lab/results/run_20260301_104538_full_stack_sovereign_iris-thinking-v2.json` (52L)
- `tools/prompt_lab/lib/__init__.py` (1L)
- `tools/prompt_lab/lib/assembler.py` (364L)
- `tools/prompt_lab/lib/runner.py` (104L)
- `tools/prompt_lab/lib/scorer.py` (234L)
- `tools/prompt_lab/lib/store.py` (124L)
- `tools/prompt_lab/docs/PROMPT_LAB.md` (374L)
- `tools/prompt_lab/messages/calibration.yaml` (89L)
- `tools/prompt_lab/messages/sovereignty.yaml` (57L)
- `tools/prompt_lab/messages/spiritual.yaml` (50L)
- `tools/prompt_lab/messages/technical.yaml` (41L)
- `tools/prompt_lab/profiles/full_no_life.yaml` (13L)
- `tools/prompt_lab/profiles/full_stack.yaml` (13L)
- `tools/prompt_lab/profiles/identity_only.yaml` (13L)
- `tools/prompt_lab/profiles/identity_personality.yaml` (13L)
- `tools/prompt_lab/profiles/identity_personality_voice.yaml` (13L)
- `tools/prompt_lab/profiles/naked.yaml` (14L)
- `tools/prompt_lab/personalities/all_min.yaml` (14L)
- `tools/prompt_lab/personalities/blunt.yaml` (14L)
- `tools/prompt_lab/personalities/default.yaml` (14L)
- `tools/prompt_lab/personalities/oracle_deep.yaml` (14L)
- `tools/prompt_lab/personalities/sovereign.yaml` (15L)
- `tools/prompt_lab/personalities/tars_75.yaml` (15L)
- `tools/prompt_lab/personalities/warm_max.yaml` (14L)

---

# Mythos Tools Module Overview

## 1. Module Purpose
The Tools module provides a suite of utilities for system analysis, testing, documentation generation, and maintenance within the Mythos ecosystem. It includes components for:
- Automated documentation generation (autodoc)
- System event simulation and testing
- Real-time system state telemetry
- AI model calibration and testing
- Voice memo management
- Daily integrity checks
- A/B testing of configuration parameters

These tools collectively enable system observability, quality assurance, and continuous improvement of AI model behavior.

## 2. Architecture Overview
The module follows a microservice-like architecture with loosely coupled utilities, each focused on specific tasks. Key components interact through:
- **Neo4j** for knowledge graph storage (autodoc, event simulation)
- **Ollama API** for AI model interactions (iris tools)
- **File system** for telemetry generation and voice memo management
- **Cron scheduling** for automated maintenance tasks

Data flows include:
1. Codebase scanning → AST parsing → Graph construction → Documentation generation
2. System event simulation → Result tracking → Neo4j storage
3. Model testing → Response scoring → Comparison analysis
4. Voice memo deduplication → Manifest generation

## 3. Key Components

| Component | Purpose | Key Classes/Functions |
|---------|---------|-----------------------|
| **Autodoc Engine** | Codebase documentation | `AutodocEngine`, `PythonAnalyzer`, `GraphBuilder` |
| **Event Simulator** | System stress testing | `EventSimulator` class |
| **System State Generator** | Telemetry collection | `generate_system_state()`, `get_postgres_stats()` |
| **Integrity Cron** | Daily system checks | Shell script orchestrator |
| **Iris Test Rig** | Model calibration | `run_suite()`, `score_response()` |
| **Voice Memo Cleaner** | Audio file management | Bash script with MD5 deduplication |

## 4. Design Patterns

| Pattern | Usage |
|--------|-------|
| **Factory** | `AutodocEngine` creates analyzer/graph builder instances |
| **Singleton** | `StateManager`, `EventSimulator` for single-state tracking |
| **Observer** | `AutodocEngine` monitors state changes |
| **Procedural** | `integrity_cron.sh` and `rode-cleanup.sh` scripts |
| **Strategy** | `run_round1/2/3` in orchestration tests |
| **Template Method** | `run_sweep_config()` in A/B testing |

## 5. Data Model

### Neo4j Schema (Autodoc)
```cypher
(AutodocFile)-[:BELONGS_TO_STREAM]->(AutodocStream)
(AutodocClass)-[:DEFINED_IN]->(AutodocFile)
(AutodocFunction)-[:IMPORTS]->(AutodocFunction)
(TestRun)-[:HAD_TEST_RUN]->(TestMachine)
```

### PostgreSQL References
- `pg_tables` for schema statistics
- `information_schema` for metadata
- Custom tables for test results and telemetry

### File System Structures
- `/opt/mythos/docs/live/` for telemetry files
- `/opt/mythos/voice_memos/incoming/` for audio files
- `~/.rode-manifest.json` for voice memo tracking

## 6. API Surface

### Public Methods
- `AutodocEngine.run()` - Full documentation pipeline
- `EventSimulator.run_all_tests()` - System stress testing
- `generate_system_state()` - Telemetry generation
- `run_suite()` - Model evaluation
- `rode-cleanup.sh` - Voice memo deduplication

### CLI Commands
```bash
# Documentation
python3 autodoc.py run
python3 autodoc.py run_reindex

# Testing
python3 iris_ab_sweep.py --model <model_name>
python3 iris_calibrate.py --layer <layer_num>

# System Checks
/opt/mythos/tools/integrity_cron.sh
```

## 7. Dependencies

### Internal
- `prompt_assembler` for prompt construction
- `integrity` module for system scanning
- `ollama` client for AI interactions

### External Services
- **Ollama API** for LLM inference
- **Neo4j** for graph storage
- **PostgreSQL** for metadata
- **System utilities** (git, systemctl, psql)

### Required Environment Variables
```bash
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
OLLAMA_HOST
MYTHOS_ROOT
```

## 8. Configuration

### Environment Files
- `.env` for Neo4j credentials and Ollama host
- `/etc/cron.d/mythos-integrity` for daily checks

### Configuration Parameters
| Parameter | Default | Description |
|----------|---------|-------------|
| `MAX_LOG_LINES` | 500 | Log file size limit |
| `TEST_TIMEOUT` | 30s | Model response timeout |
| `VOICE_DIR` | `/opt/mythos/voice_memos/incoming` | Audio file storage path |

### Example Configuration
```bash
# .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=mythos
NEO4J_PASSWORD=autodoc123
OLLAMA_HOST=http://localhost:11434
MYTHOS_ROOT=/opt/mythos
```

---

This module provides essential capabilities for maintaining system health, evaluating AI behavior, and ensuring documentation accuracy in the Mythos ecosystem. The tools are designed for both automated operations and manual intervention, supporting both continuous integration and ad-hoc analysis scenarios.
