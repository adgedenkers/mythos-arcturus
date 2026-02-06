#!/bin/bash
# =============================================================
# Patch 0071: Web Dashboard with Google OAuth
# =============================================================
# Installs:
#   - Google OAuth2 authentication
#   - JWT session management
#   - Finance API endpoints (live data)
#   - Web dashboard (login, dashboard, report pages)
#   - web_users table with whitelist
#   - Updates FastAPI main.py to register new routes/middleware
#
# Prerequisites:
#   - Google Cloud Console: Create OAuth2 credentials
#   - Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
#
# After install, run: ./verify_0071.sh
# =============================================================
set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PIP="$MYTHOS_ROOT/.venv/bin/pip"
VENV_PY="$MYTHOS_ROOT/.venv/bin/python3"
ENV_FILE="$MYTHOS_ROOT/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==========================================="
echo "  Patch 0071: Web Dashboard + Google OAuth"
echo "==========================================="
echo ""

# ============================================================
# 1. INSTALL PYTHON DEPENDENCIES
# ============================================================
echo -e "${YELLOW}[1/8]${NC} Installing Python packages..."
$VENV_PIP install --break-system-packages \
    PyJWT>=2.8.0 \
    httpx>=0.25.0 \
    authlib>=1.3.0 \
    2>&1 | tail -3
echo -e "${GREEN}  ✓ Dependencies installed${NC}"

# ============================================================
# 2. COPY FILES
# ============================================================
echo -e "${YELLOW}[2/8]${NC} Installing files..."

# Auth module
mkdir -p "$MYTHOS_ROOT/api/auth"
cp "$PATCH_DIR/opt/mythos/api/auth/__init__.py" "$MYTHOS_ROOT/api/auth/"
cp "$PATCH_DIR/opt/mythos/api/auth/google_auth.py" "$MYTHOS_ROOT/api/auth/"
echo "  ✓ Auth module"

# Finance API routes
cp "$PATCH_DIR/opt/mythos/api/routes/finance.py" "$MYTHOS_ROOT/api/routes/"
echo "  ✓ Finance API routes"

# Web routes
cp "$PATCH_DIR/opt/mythos/api/routes/web.py" "$MYTHOS_ROOT/api/routes/"
echo "  ✓ Web routes"

# Templates
mkdir -p "$MYTHOS_ROOT/web/templates"
cp "$PATCH_DIR/opt/mythos/web/templates/login.html" "$MYTHOS_ROOT/web/templates/"
cp "$PATCH_DIR/opt/mythos/web/templates/dashboard.html" "$MYTHOS_ROOT/web/templates/"
cp "$PATCH_DIR/opt/mythos/web/templates/report_live.html" "$MYTHOS_ROOT/web/templates/"
echo "  ✓ Web templates"

# Static dir
mkdir -p "$MYTHOS_ROOT/web/static/css"
mkdir -p "$MYTHOS_ROOT/web/static/js"
echo "  ✓ Static directories"

echo -e "${GREEN}  ✓ All files installed${NC}"

# ============================================================
# 3. RUN DATABASE MIGRATION
# ============================================================
echo -e "${YELLOW}[3/8]${NC} Running database migration..."
sudo -u postgres psql -d mythos -f "$PATCH_DIR/opt/mythos/api/auth/migration.sql" 2>&1 | grep -v "^$"
echo -e "${GREEN}  ✓ web_users table created${NC}"

# ============================================================
# 4. GENERATE JWT SECRET IF NOT SET
# ============================================================
echo -e "${YELLOW}[4/8]${NC} Checking JWT secret..."
if grep -q "^JWT_SECRET=" "$ENV_FILE" 2>/dev/null; then
    echo "  ✓ JWT_SECRET already set"
else
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    echo "" >> "$ENV_FILE"
    echo "# Web Dashboard Auth" >> "$ENV_FILE"
    echo "JWT_SECRET=$JWT_SECRET" >> "$ENV_FILE"
    echo -e "${GREEN}  ✓ JWT_SECRET generated and saved${NC}"
fi

# Add JWT expiry if not set
if ! grep -q "^JWT_EXPIRY_HOURS=" "$ENV_FILE" 2>/dev/null; then
    echo "JWT_EXPIRY_HOURS=168" >> "$ENV_FILE"
fi

# Check for Google OAuth placeholders
if ! grep -q "^GOOGLE_CLIENT_ID=" "$ENV_FILE" 2>/dev/null; then
    echo "" >> "$ENV_FILE"
    echo "# Google OAuth2 - SET THESE AFTER CREATING CREDENTIALS" >> "$ENV_FILE"
    echo "GOOGLE_CLIENT_ID=" >> "$ENV_FILE"
    echo "GOOGLE_CLIENT_SECRET=" >> "$ENV_FILE"
    echo "GOOGLE_REDIRECT_URI=https://mythos-api.denkers.co/auth/google/callback" >> "$ENV_FILE"
    echo -e "${YELLOW}  ⚠ Google OAuth placeholders added - YOU MUST SET THESE${NC}"
else
    echo "  ✓ Google OAuth env vars present"
fi

# ============================================================
# 5. UPDATE FASTAPI MAIN.PY
# ============================================================
echo -e "${YELLOW}[5/8]${NC} Updating FastAPI main.py..."

MAIN_PY="$MYTHOS_ROOT/api/main.py"

# Backup
cp "$MAIN_PY" "$MAIN_PY.bak.0071"

# Add imports if not already present
if ! grep -q "google_auth" "$MAIN_PY"; then
    # Find the line with 'from api.routes.sales import' and add after it
    sed -i '/^from api.routes.sales import/a\from api.routes.finance import router as finance_router\nfrom api.routes.web import router as web_router\nfrom api.auth.google_auth import router as auth_router, AuthMiddleware' "$MAIN_PY"
    echo "  ✓ Imports added"
else
    echo "  ✓ Imports already present"
fi

# Add routers if not already present
if ! grep -q "finance_router" "$MAIN_PY"; then
    # Find 'app.include_router(sales_router)' and add after it
    sed -i '/app.include_router(sales_router)/a\app.include_router(finance_router)\napp.include_router(web_router)\napp.include_router(auth_router)' "$MAIN_PY"
    echo "  ✓ Routers registered"
else
    echo "  ✓ Routers already registered"
fi

# Add middleware if not already present
if ! grep -q "AuthMiddleware" "$MAIN_PY"; then
    # Add after the CORS middleware block - find the closing paren of add_middleware
    sed -i '/^)$/!b;:a;N;/allow_headers.*\n)/!ba;a\# Auth middleware for web dashboard\napp.add_middleware(AuthMiddleware)' "$MAIN_PY"
    
    # If that didn't work (sed pattern matching is fragile), try simpler approach
    if ! grep -q "AuthMiddleware" "$MAIN_PY"; then
        # Add right after the CORS allow_headers line
        sed -i '/allow_headers=\["\*"\]/,/^)/{ /^)/a\# Auth middleware for web dashboard\napp.add_middleware(AuthMiddleware)
        }' "$MAIN_PY"
    fi
    
    # Final fallback - just add it after the sales_router include
    if ! grep -q "AuthMiddleware" "$MAIN_PY"; then
        sed -i '/app.include_router(auth_router)/a\\n# Auth middleware for web dashboard\napp.add_middleware(AuthMiddleware)' "$MAIN_PY"
    fi
    
    echo "  ✓ Auth middleware added"
else
    echo "  ✓ Auth middleware already present"
fi

# Add report-html endpoint to serve template with injected data
if ! grep -q "report-html" "$MAIN_PY"; then
    cat >> "$MAIN_PY" << 'PYEOF'

# Serve live report HTML (report template with API data injection)
from fastapi.responses import HTMLResponse as _HTMLResponse
from pathlib import Path as _Path
import json as _json

@app.get("/api/finance/report-html", response_class=_HTMLResponse)
async def report_html():
    """Serve the report template with live data injected"""
    import sys
    sys.path.insert(0, '/opt/mythos/finance')
    from report_generator import generate_report
    
    # Generate fresh report to temp path
    from datetime import date
    from pathlib import Path
    
    output = Path('/tmp/mythos_live_report.html')
    generate_report(num_months=6, output_path=str(output))
    
    if output.exists():
        return _HTMLResponse(content=output.read_text())
    return _HTMLResponse(content="<h1>Report generation failed</h1>", status_code=500)
PYEOF
    echo "  ✓ Report HTML endpoint added"
fi

echo -e "${GREEN}  ✓ FastAPI main.py updated${NC}"

# ============================================================
# 6. VERIFY SYNTAX
# ============================================================
echo -e "${YELLOW}[6/8]${NC} Checking Python syntax..."
$VENV_PY -c "import py_compile; py_compile.compile('$MAIN_PY', doraise=True)" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Syntax OK${NC}"
else
    echo -e "${RED}  ✗ Syntax error in main.py!${NC}"
    echo "  Restoring backup..."
    cp "$MAIN_PY.bak.0071" "$MAIN_PY"
    echo "  Original restored. Check the error and fix manually."
    exit 1
fi

# ============================================================
# 7. RESTART API SERVICE
# ============================================================
echo -e "${YELLOW}[7/8]${NC} Restarting API service..."
sudo systemctl restart mythos-api.service
sleep 3

if systemctl is-active --quiet mythos-api.service; then
    echo -e "${GREEN}  ✓ API running${NC}"
else
    echo -e "${RED}  ✗ API failed to start!${NC}"
    sudo journalctl -u mythos-api.service --no-pager -n 15
    echo ""
    echo "  Restoring backup..."
    cp "$MAIN_PY.bak.0071" "$MAIN_PY"
    sudo systemctl restart mythos-api.service
    exit 1
fi

# ============================================================
# 8. SUMMARY
# ============================================================
echo ""
echo "==========================================="
echo -e "${GREEN}  Patch 0071 Installed Successfully${NC}"
echo "==========================================="
echo ""
echo "Files installed:"
echo "  /opt/mythos/api/auth/google_auth.py"
echo "  /opt/mythos/api/routes/finance.py"
echo "  /opt/mythos/api/routes/web.py"
echo "  /opt/mythos/web/templates/login.html"
echo "  /opt/mythos/web/templates/dashboard.html"
echo "  /opt/mythos/web/templates/report_live.html"
echo ""
echo "Database:"
echo "  ✓ web_users table created with 2 whitelisted accounts"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Create Google OAuth2 credentials:"
echo "   → https://console.cloud.google.com/apis/credentials"
echo "   → Create OAuth 2.0 Client ID (Web application)"
echo "   → Authorized redirect URI: https://mythos-api.denkers.co/auth/google/callback"
echo ""
echo "2. Set credentials in /opt/mythos/.env:"
echo "   GOOGLE_CLIENT_ID=your-client-id-here"
echo "   GOOGLE_CLIENT_SECRET=your-client-secret-here"
echo ""
echo "3. Restart API: sudo systemctl restart mythos-api.service"
echo ""
echo "4. Visit: https://mythos-api.denkers.co/app/login"
echo ""
echo "5. Run verify script: ./verify_0071.sh"
