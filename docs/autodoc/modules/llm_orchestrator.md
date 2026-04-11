# LLM Orchestrator

**Stream:** LOG
**Files:** 129

## Files in this Module

- `orchestrator/README.md` (151L)
- `orchestrator/scripts/register_models.sh` (42L)
- `orchestrator/scripts/rollback.sh` (127L)
- `orchestrator/schema/pipeline_log.sql` (139L)
- `orchestrator/schema/unified_v2.sql` (52L)
- `orchestrator/docs/UNIFIED_ARCHITECTURE.md` (368L)
- `orchestrator/src/__init__.py` (27L)
- `orchestrator/src/config.py` (191L)
- `orchestrator/src/database.py` (290L)
- `orchestrator/src/utils.py` (340L)
- `orchestrator/src/api/__init__.py` (0L)
- `orchestrator/src/api/schemas/__init__.py` (0L)
- `orchestrator/src/api/routes/__init__.py` (0L)
- `orchestrator/src/models/__init__.py` (17L)
- `orchestrator/src/models/model_manager.py` (305L)
- `orchestrator/src/models/model_registry.py` (327L)
- `orchestrator/src/models/ollama_client.py` (329L)
- `orchestrator/src/synthesis/__init__.py` (0L)
- `orchestrator/src/logging/__init__.py` (1L)
- `orchestrator/src/logging/pipeline_logger.py` (170L)
- `orchestrator/src/executor/__init__.py` (0L)
- `orchestrator/src/pipeline/__init__.py` (9L)
- `orchestrator/src/pipeline/orchestrator.py` (616L)
- `orchestrator/src/bench/__init__.py` (28L)
- `orchestrator/src/bench/grader.py` (355L)
- `orchestrator/src/bench/grading_result.py` (64L)
- `orchestrator/src/bench/test_loader.py` (302L)
- `orchestrator/src/bench/test_question.py` (133L)
- `orchestrator/src/bench/test_run.py` (182L)
- `orchestrator/src/bench/test_runner.py` (361L)
- `orchestrator/src/bench/test_suite.py` (234L)
- `orchestrator/src/bench/suites/__init__.py` (0L)
- `orchestrator/src/analyzer/__init__.py` (0L)
- `orchestrator/src/config/__init__.py` (20L)
- `orchestrator/src/config/registry.py` (174L)
- `orchestrator/src/config/settings.py` (277L)
- `orchestrator/src/router/__init__.py` (0L)
- `orchestrator/prompts/registry.yaml` (311L)
- `orchestrator/prompts/templates/discovery.yaml` (300L)
- `orchestrator/prompts/templates/perception.yaml` (579L)
- `orchestrator/voice_tuning/tune.py` (628L)
- `orchestrator/voice_tuning/runs/after-tweak-1_20260307_234317/manifest.json` (10L)
- `orchestrator/voice_tuning/runs/after-tweak-1_20260307_234317/summary.json` (84L)
- `orchestrator/voice_tuning/runs/run_20260307_234216/manifest.json` (10L)
- `orchestrator/voice_tuning/runs/baseline_20260307_234222/manifest.json` (10L)
- `orchestrator/voice_tuning/runs/baseline_20260307_234222/summary.json` (78L)
- `orchestrator/benchmark/bench_config.json` (23L)
- `orchestrator/benchmark/bench_config_round2.json` (31L)
- `orchestrator/benchmark/report.py` (239L)
- `orchestrator/benchmark/run_benchmark.py` (667L)
- `orchestrator/benchmark/run_benchmark_round2.sh` (15L)
- `orchestrator/benchmark/run_deepseek_solo.sh` (33L)
- `orchestrator/benchmark/sovereign_align_20260310_194216.json` (350L)
- `orchestrator/benchmark/sovereign_align_20260310_194437.json` (350L)
- `orchestrator/benchmark/tasks.py` (1212L)
- `orchestrator/benchmark/resonance/iris_test_config.yaml` (80L)
- `orchestrator/benchmark/resonance/resonance_config.py` (504L)
- `orchestrator/benchmark/resonance/resonance_report.py` (320L)
- `orchestrator/benchmark/resonance/run_all.py` (97L)
- `orchestrator/benchmark/resonance/run_phase1.py` (633L)
- `orchestrator/benchmark/resonance/run_phase3.py` (333L)
- `orchestrator/benchmark/resonance/run_phase4.py` (331L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_172544_quick.json` (44L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_173420_standard.json` (79L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_173538_quick.json` (44L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_174312_quick.json` (44L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_174435_quick.json` (44L)
- `orchestrator/benchmark/resonance/runs/iris_test_20260311_174520_standard.json` (79L)
- `orchestrator/benchmark/resonance/runs/20260311_110449_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_110449_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_110449_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_133055_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_133055_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_133055_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_102839_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_102839_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_102839_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_113228_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_113228_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_113228_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_110522_resonance/manifest.json` (18L)
- `orchestrator/benchmark/resonance/runs/20260311_110522_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_110522_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_110431_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_110431_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_110431_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_105455_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_105455_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_105455_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_101651_resonance/manifest.json` (17L)
- `orchestrator/benchmark/resonance/runs/20260311_101651_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_103735_resonance/manifest.json` (17L)
- `orchestrator/benchmark/resonance/runs/20260311_103735_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_103735_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_112322_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_112322_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_112322_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_104323_resonance/manifest.json` (18L)
- `orchestrator/benchmark/resonance/runs/20260311_104323_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_104323_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_110638_resonance/manifest.json` (18L)
- `orchestrator/benchmark/resonance/runs/20260311_110638_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_110638_resonance/summary.json` (7L)
- `orchestrator/benchmark/resonance/runs/20260311_120717_resonance/manifest.json` (16L)
- `orchestrator/benchmark/resonance/runs/20260311_120717_resonance/prompt_full_iris.txt` (119L)
- `orchestrator/benchmark/resonance/runs/20260311_120717_resonance/summary.json` (7L)
- `orchestrator/benchmark/calibration/calibrate_20260331_214013_emotional.json` (75L)
- `orchestrator/benchmark/calibration/calibrate_20260331_214136_emotional.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_215959_emotional.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_220018_casual.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_220041_confab_trap.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_220123_skill_data.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_220156_technical.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260331_220226_spiritual.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260401_001143_emotional.json` (177L)
- `orchestrator/benchmark/calibration/calibrate_20260402_101648_emotional.json` (177L)
- `orchestrator/benchmark/runs/20260307_182638_0ce853/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_182638_0ce853/run_summary.json` (161L)
- `orchestrator/benchmark/runs/20260307_171642_f58f87/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_171642_f58f87/run_summary.json` (161L)
- `orchestrator/benchmark/runs/20260307_173034_2b7a93/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_173016_cfdd46/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_171356_2d3c46/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_182551_86f65f/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260308_121820_38586a/run_manifest.json` (48L)
- `orchestrator/benchmark/runs/20260308_121820_38586a/run_summary.json` (461L)
- `orchestrator/benchmark/runs/20260307_232230_783b64/run_manifest.json` (34L)
- `orchestrator/benchmark/runs/20260307_232230_783b64/run_summary.json` (161L)
- `orchestrator/test_suites/perception/test_suite.py` (541L)

---

# Mythos LLM Orchestrator Module Documentation

## 1. Module Purpose
The LLM Orchestrator module is a core component of the Mythos system designed to manage, evaluate, and orchestrate multiple large language models (LLMs) across diverse tasks. It provides capabilities for:
- Model registration and synchronization with Ollama
- Performance benchmarking and test suite execution
- Role-based model assignment and configuration management
- Pipeline execution tracking and logging
- Unified configuration management across subsystems

The module enables dynamic model selection based on task requirements and maintains a comprehensive record of model performance, test results, and pipeline execution history.

## 2. Architecture Overview
The module follows a modular architecture with clear separation of concerns, featuring:

**Data Flow:**
1. Model registration via `register_models.sh` script → ModelManager syncs with Ollama → Writes to `orch_models` table
2. Test execution → Records in `orch_test_runs` and `orch_test_results` tables
3. Pipeline execution → Logs in `pipeline_runs`, `pipeline_llm_calls`, and `pipeline_queries`
4. Configuration management → Stores in `orch_config_snapshots` and `orch_role_assignments`

**Key Components:**
- Model Management Layer (ModelManager, OllamaClient)
- Database Layer (asyncpg connection pool)
- Configuration Layer (Pydantic-based settings)
- Logging Layer (Pipeline execution tracking)
- Role Assignment System (orch_role_assignments table)

## 3. Key Components

### 3.1 ModelManager
- **Role**: Central class for model lifecycle management
- **Key Methods**:
  - `sync_models()`: Synchronizes installed Ollama models with database
  - `get_available_models()`: Retrieves list of registered models
  - `evaluate_model()`: Executes benchmark tests against models
- **Dependencies**: OllamaClient, ModelRegistry, Database

### 3.2 Database
- **Role**: Manages PostgreSQL connections and operations
- **Key Features**:
  - Connection pooling via `asyncpg`
  - Transaction management
  - Query execution methods (fetch, execute, etc.)
- **Tables Managed**: 14+ tables including `orch_models`, `orch_test_results`, `pipeline_runs`

### 3.3 Configuration System
- **Role**: Manages application settings and overrides
- **Key Features**:
  - Hierarchical configuration resolution (overrides > settings > registry > defaults)
  - Pydantic-based validation
  - Environment variable loading
- **Key Classes**: `Settings` (config.py)

### 3.4 Pipeline Tracking
- **Role**: Logs execution of LLM pipelines
- **Key Tables**:
  - `pipeline_runs`: Tracks overall pipeline execution
  - `pipeline_llm_calls`: Logs individual model invocations
  - `pipeline_queries`: Records DISCOVERY phase queries
- **Views**: `pipeline_recent`, `prompt_component_usage`

## 4. Design Patterns

| Pattern | Usage |
|---------|-------|
| Singleton | `Settings` class for configuration, `Database` class for connection pooling |
| Factory | Configuration resolution through hierarchical overrides |
| Observer | (Implied) for monitoring model performance and registry changes |
| Context Manager | For managing database connections and transactions |
| Embedded Script | Python scripts within bash scripts (e.g., `register_models.sh`) |

## 5. Data Model

### Core Tables
1. **Model Management**
   - `orch_models`: Model metadata
   - `orch_model_capabilities`: Model capabilities
   - `orch_model_benchmarks`: Benchmark results

2. **Testing Framework**
   - `orch_test_suites`: Test suite definitions
   - `orch_test_questions`: Test questions
   - `orch_test_runs`: Test execution records
   - `orch_test_results`: Test outcomes

3. **Pipeline Execution**
   - `pipeline_runs`: Pipeline execution metadata
   - `pipeline_llm_calls`: Individual model invocations
   - `pipeline_queries`: DISCOVERY phase queries

4. **Configuration Management**
   - `orch_role_assignments`: Role-to-model mappings
   - `orch_config_snapshots`: Configuration history

### Indexes
- `idx_pipeline_runs_created` (pipeline_runs.created_at)
- `idx_pipeline_llm_calls_run` (pipeline_llm_calls.run_uuid)
- `idx_orch_roles_active` (orch_role_assignments.active)

### Views
- `pipeline_recent`: Recent pipeline executions
- `prompt_component_usage`: Aggregated prompt component usage
- `orch_active_roles`: Current active role assignments

## 6. API Surface

### CLI Commands
- `register_models.sh`: Synchronizes Ollama models with database
- `rollback.sh`: Reverts to previous system version (v1.0.0)
- `run_pipeline`: (Implied) Executes LLM pipeline
- `run_bench`: (Implied) Executes model benchmark tests

### Web API (Planned)
- **Endpoints**:
  - `/models`: List registered models
  - `/tests`: Run test suites
  - `/pipelines`: Execute pipelines
  - `/config`: Manage configurations
- **Authentication**: (Not specified in documentation)

## 7. Dependencies

### External Systems
- **PostgreSQL**: Primary database for all tables
- **Ollama**: Model serving and execution
- **Neo4j**: (Implied) for graph-based model relationships

### Internal Modules
- `src.utils`: Utility functions for ID generation, hashing, time formatting
- `src.database`: Database connection and query management
- `src.config`: Configuration loading and validation
- `models.model_manager`: Core model orchestration logic

### Python Packages
- `asyncpg`: Asynchronous PostgreSQL client
- `pydantic`: Configuration validation
- `uuid`: Unique ID generation
- `hashlib`: Secure hashing for model identifiers

## 8. Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OLLAMA_HOST` | Ollama API endpoint | Required |
| `DATA_DIR` | Base directory for data files | `/opt/mythos/data` |
| `ENVIRONMENT` | `production` or `development` | `development` |
| `DATABASE_POOL_SIZE` | Connection pool size | 10 |

### Configuration Files
1. **`.env` File**
   - Located at `/opt/mythos/orchestrator/.env`
   - Contains environment-specific settings

2. **`registry.yaml`**
   - Defines prompt templates and model configurations
   - Used for default model assignments

3. **Test Config Files**
   - YAML files for test suite overrides
   - Located in `test_suites/` directory

### Configuration Resolution
1. Command-line overrides
2. Environment variables
3. `registry.yaml` defaults
4. Hardcoded defaults

## Version History
- **v1.0.0**: Base Mythos system
- **v1.15.1**: Phase 1.1 - Core Infrastructure
- **v1.15.2**: Phase 1.2 - Ollama Integration
- **v1.16.0**: Phase 1 Complete (Model Bench)

## Migration Plan
1. **Phase 1.1**: Core infrastructure implementation
2. **Phase 1.2**: Ollama integration and model management
3. **Phase 2**: Web interface development
4. **Phase 3**: Advanced configuration management
5. **Phase 4**: Full pipeline orchestration

This documentation provides a comprehensive overview of the LLM Orchestrator module, covering its architecture, key components, data model, and operational aspects. The module's design emphasizes flexibility, scalability, and maintainability while providing robust model orchestration capabilities.
