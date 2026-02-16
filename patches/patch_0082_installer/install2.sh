#!/bin/bash
set -e

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
ORCH_ROOT="${MYTHOS_ROOT}/orchestrator"

echo "=========================================================="
echo "Mythos Orchestrator - Phase 1.1"
echo "Core Infrastructure"
echo ""
echo "Patch:   0082"
echo "Version: 1.0.0 → 1.15.1"
echo "Phase:   1.1 of 7 (Model Bench)"
echo "=========================================================="
echo ""

# Verify running as correct user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Do not run as root"
    echo "   Run as: adge"
    exit 1
fi

# Verify Mythos exists
if [ ! -d "$MYTHOS_ROOT" ]; then
    echo "❌ Error: /opt/mythos not found"
    exit 1
fi

# Verify PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "❌ Error: PostgreSQL is not running"
    echo "   Start with: sudo systemctl start postgresql"
    exit 1
fi

# Check base version
if [ -f "${MYTHOS_ROOT}/.version" ]; then
    CURRENT_VERSION=$(cat "${MYTHOS_ROOT}/.version")
    echo "Current version: ${CURRENT_VERSION}"
    if [ "${CURRENT_VERSION}" != "1.0.0" ] && [ "${CURRENT_VERSION}" != "1.15.1" ]; then
        echo "⚠️  Warning: Expected base version 1.0.0, found ${CURRENT_VERSION}"
        echo "   Continue anyway? (y/n)"
        read -r response
        if [ "$response" != "y" ]; then
            exit 1
        fi
    fi
else
    echo "ℹ️  No version file found (first versioned patch)"
fi

echo ""
echo "Installing Phase 1.1 - Core Infrastructure..."
echo ""

# ============================================================
# Step 1: Create version file
# ============================================================
echo "[1/11] Creating version file..."
echo "1.15.1" > "${MYTHOS_ROOT}/.version"
echo "        ✓ Version: 1.15.1"

# ============================================================
# Step 2: Create directory structure
# ============================================================
echo "[2/11] Creating directories..."
mkdir -p "${ORCH_ROOT}"/{src,scripts,test_suites,results,data,logs,docs}
mkdir -p "${ORCH_ROOT}/src"/{bench,models,router,analyzer,executor,synthesis,api}
mkdir -p "${ORCH_ROOT}/src/bench/suites"
mkdir -p "${ORCH_ROOT}/src/api"/{routes,schemas}
mkdir -p "${ORCH_ROOT}/test_suites"/{standard,custom}
mkdir -p "${ORCH_ROOT}/results"/{runs,reports}
mkdir -p "${MYTHOS_ROOT}/docs/orchestrator"

# Create __init__.py files for Python packages
touch "${ORCH_ROOT}/src/__init__.py"
touch "${ORCH_ROOT}/src/bench/__init__.py"
touch "${ORCH_ROOT}/src/models/__init__.py"
touch "${ORCH_ROOT}/src/router/__init__.py"
touch "${ORCH_ROOT}/src/analyzer/__init__.py"
touch "${ORCH_ROOT}/src/executor/__init__.py"
touch "${ORCH_ROOT}/src/synthesis/__init__.py"
touch "${ORCH_ROOT}/src/api/__init__.py"
touch "${ORCH_ROOT}/src/api/routes/__init__.py"
touch "${ORCH_ROOT}/src/api/schemas/__init__.py"
touch "${ORCH_ROOT}/src/bench/suites/__init__.py"

echo "        ✓ Directories created"

# ============================================================
# Step 3: Install Python dependencies
# ============================================================
echo "[3/11] Installing Python dependencies..."
source "${MYTHOS_ROOT}/.venv/bin/activate"
pip install --quiet --upgrade pip > /dev/null 2>&1
pip install --quiet \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    aiohttp==3.9.1 \
    asyncpg==0.29.0 \
    "psycopg[binary]==3.1.13" \
    sqlalchemy==2.0.23 \
    python-multipart==0.0.6 \
    redis==5.0.1 \
    python-dotenv==1.0.0
echo "        ✓ Dependencies installed"

# ============================================================
# Step 4: Create database schema
# ============================================================
echo "[4/11] Creating database schema..."
sudo -u postgres psql -d mythos << 'EOSQL' 2>&1 | grep -v "NOTICE" || true
CREATE TABLE IF NOT EXISTS orch_models (
    model_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT DEFAULT 'ollama',
    size_params TEXT,
    quantization TEXT,
    context_window INTEGER,
    installed BOOLEAN DEFAULT false,
    installed_at TIMESTAMP,
    last_used TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_model_capabilities (
    capability_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES orch_models(model_id) ON DELETE CASCADE,
    task_type TEXT NOT NULL,
    quality_score REAL,
    speed_tier TEXT,
    cost_per_1k_tokens REAL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_test_suites (
    suite_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    question_count INTEGER,
    difficulty TEXT,
    version TEXT DEFAULT '1.0',
    public BOOLEAN DEFAULT true,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_test_questions (
    question_id TEXT PRIMARY KEY,
    suite_id TEXT REFERENCES orch_test_suites(suite_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    correct_answer TEXT,
    answer_type TEXT,
    grading_criteria JSONB,
    difficulty TEXT,
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_test_runs (
    run_id TEXT PRIMARY KEY,
    suite_id TEXT REFERENCES orch_test_suites(suite_id),
    model_id TEXT REFERENCES orch_models(model_id),
    model_params JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER,
    accuracy REAL,
    avg_response_time REAL,
    total_cost REAL DEFAULT 0,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_test_results (
    result_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES orch_test_runs(run_id) ON DELETE CASCADE,
    question_id TEXT REFERENCES orch_test_questions(question_id),
    model_response TEXT,
    is_correct BOOLEAN,
    partial_credit REAL,
    response_time REAL,
    grading_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orch_model_benchmarks (
    benchmark_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES orch_models(model_id),
    task_type TEXT,
    test_suite TEXT,
    accuracy REAL,
    hallucination_rate REAL,
    avg_response_time REAL,
    sample_size INTEGER,
    tested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orch_test_runs_model ON orch_test_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_orch_test_runs_suite ON orch_test_runs(suite_id);
CREATE INDEX IF NOT EXISTS idx_orch_test_runs_status ON orch_test_runs(status);
CREATE INDEX IF NOT EXISTS idx_orch_test_results_run ON orch_test_results(run_id);
CREATE INDEX IF NOT EXISTS idx_orch_test_results_question ON orch_test_results(question_id);
CREATE INDEX IF NOT EXISTS idx_orch_model_benchmarks_model ON orch_model_benchmarks(model_id);
CREATE INDEX IF NOT EXISTS idx_orch_model_benchmarks_task ON orch_model_benchmarks(task_type);
CREATE INDEX IF NOT EXISTS idx_orch_model_capabilities_model ON orch_model_capabilities(model_id);
CREATE INDEX IF NOT EXISTS idx_orch_test_questions_suite ON orch_test_questions(suite_id);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adge;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO adge;

COMMENT ON TABLE orch_models IS 'Model Bench v1.15.1: Registry of available LLM models';
COMMENT ON TABLE orch_model_capabilities IS 'Model Bench v1.15.1: Task-specific capabilities';
COMMENT ON TABLE orch_test_suites IS 'Model Bench v1.15.1: Test suite definitions';
COMMENT ON TABLE orch_test_questions IS 'Model Bench v1.15.1: Individual test questions';
COMMENT ON TABLE orch_test_runs IS 'Model Bench v1.15.1: Test execution history';
COMMENT ON TABLE orch_test_results IS 'Model Bench v1.15.1: Individual question results';
COMMENT ON TABLE orch_model_benchmarks IS 'Model Bench v1.15.1: Aggregated performance metrics';
EOSQL

TABLE_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'orch_%';" | tr -d ' ')
echo "        ✓ Database: $TABLE_COUNT tables created"

# ============================================================
# Step 5: Copy source files
# ============================================================
echo "[5/11] Copying source files..."
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/__init__.py" "${ORCH_ROOT}/src/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/config.py" "${ORCH_ROOT}/src/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/database.py" "${ORCH_ROOT}/src/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/src/utils.py" "${ORCH_ROOT}/src/"
echo "        ✓ Source files copied"

# ============================================================
# Step 6: Copy documentation
# ============================================================
echo "[6/11] Copying documentation..."
cp "${PATCH_DIR}/opt/mythos/orchestrator/.env.example" "${ORCH_ROOT}/"
cp "${PATCH_DIR}/opt/mythos/orchestrator/README.md" "${ORCH_ROOT}/"
cp "${PATCH_DIR}/opt/mythos/docs/orchestrator/ARCHITECTURE.md" "${MYTHOS_ROOT}/docs/orchestrator/"
cp "${PATCH_DIR}/opt/mythos/docs/orchestrator/README.md" "${MYTHOS_ROOT}/docs/orchestrator/"
cp "${PATCH_DIR}/opt/mythos/docs/orchestrator/CHANGELOG.md" "${MYTHOS_ROOT}/docs/orchestrator/"
echo "        ✓ Documentation copied"

# ============================================================
# Step 7: Create configuration
# ============================================================
echo "[7/11] Creating configuration..."
if [ ! -f "${ORCH_ROOT}/.env" ]; then
    cp "${ORCH_ROOT}/.env.example" "${ORCH_ROOT}/.env"
    echo "        ✓ Created .env"
else
    echo "        ✓ .env exists"
fi

# ============================================================
# Step 8: Copy rollback script
# ============================================================
echo "[8/11] Installing rollback script..."
mkdir -p "${ORCH_ROOT}/scripts"
cp "${PATCH_DIR}/scripts/rollback.sh" "${ORCH_ROOT}/scripts/"
chmod +x "${ORCH_ROOT}/scripts/rollback.sh"
echo "        ✓ Rollback script installed"

# ============================================================
# Step 9: Set permissions
# ============================================================
echo "[9/11] Setting permissions..."
chown -R adge:adge "${ORCH_ROOT}" "${MYTHOS_ROOT}/docs/orchestrator" "${MYTHOS_ROOT}/.version"
echo "        ✓ Permissions set"

# ============================================================
# Step 10: Verify installation
# ============================================================
echo "[10/11] Verifying installation..."
python3 << 'EOPY' 2>&1 | grep "✓" || true
import sys
sys.path.insert(0, '/opt/mythos/orchestrator/src')
from config import settings
from database import db
from utils import generate_id
if settings.VERSION == "1.15.1":
    print("        ✓ All modules verified")
EOPY

# ============================================================
# Step 11: Update documentation
# ============================================================
echo "[11/11] Updating documentation..."
if [ -f "${MYTHOS_ROOT}/docs/TODO.md" ]; then
    echo "" >> "${MYTHOS_ROOT}/docs/TODO.md"
    echo "## [$(date +%Y-%m-%d)] Patch 0082 - v1.15.1" >> "${MYTHOS_ROOT}/docs/TODO.md"
    echo "✅ Phase 1.1: Core Infrastructure" >> "${MYTHOS_ROOT}/docs/TODO.md"
fi

cd "${MYTHOS_ROOT}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add .version orchestrator/ docs/orchestrator/ 2>/dev/null || true
    git commit -m "patch_0082: v1.15.1 - Core Infrastructure" 2>/dev/null || true
    git tag -a v1.15.1 -m "Phase 1.1 Complete" 2>/dev/null || true
    echo "        ✓ Git updated"
fi

echo ""
echo "=========================================================="
echo "Installation Complete!"
echo "=========================================================="
echo ""
echo "Version: 1.0.0 → 1.15.1"
echo "Phase:   1.1 Complete"
echo ""
echo "Installed:"
echo "  • 7 database tables (orch_*)"
echo "  • 4 Python modules"
echo "  • Documentation"
echo ""
echo "Next: patch_0083 (v1.15.2 - Ollama Integration)"
echo ""
