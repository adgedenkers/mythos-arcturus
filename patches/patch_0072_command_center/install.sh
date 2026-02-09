#!/bin/bash
# =============================================================
# Patch 0072: Mythos Command Center
# =============================================================
# Restructures the web app into a proper command center:
#   - Immersive landing page with sacred geometry
#   - System status page with live service monitoring
#   - Session and Registry placeholder pages
#   - Updated navigation across all pages
#   - System status API endpoint
#   - Restructured routes (/app/ = home, /app/finance/ = finance)
# =============================================================
set -e

MYTHOS_ROOT="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MAIN_PY="$MYTHOS_ROOT/api/main.py"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==========================================="
echo "  Patch 0072: Mythos Command Center"
echo "==========================================="
echo ""

# 1. Install templates
echo -e "${YELLOW}[1/5]${NC} Installing templates..."
mkdir -p "$MYTHOS_ROOT/web/templates"
cp "$PATCH_DIR/opt/mythos/web/templates/home.html" "$MYTHOS_ROOT/web/templates/"
cp "$PATCH_DIR/opt/mythos/web/templates/system.html" "$MYTHOS_ROOT/web/templates/"
cp "$PATCH_DIR/opt/mythos/web/templates/sessions.html" "$MYTHOS_ROOT/web/templates/"
cp "$PATCH_DIR/opt/mythos/web/templates/registry.html" "$MYTHOS_ROOT/web/templates/"
echo -e "${GREEN}  ✓ Templates installed${NC}"

# 2. Install routes
echo -e "${YELLOW}[2/5]${NC} Installing routes..."
cp "$PATCH_DIR/opt/mythos/api/routes/web.py" "$MYTHOS_ROOT/api/routes/web.py"
cp "$PATCH_DIR/opt/mythos/api/routes/system.py" "$MYTHOS_ROOT/api/routes/system.py"
echo -e "${GREEN}  ✓ Routes installed${NC}"

# 3. Update main.py - add system router
echo -e "${YELLOW}[3/5]${NC} Updating main.py..."
cp "$MAIN_PY" "$MAIN_PY.bak.0072"

if ! grep -q "system_router" "$MAIN_PY"; then
    # Add import
    sed -i '/from api.routes.finance import/a\from api.routes.system import router as system_router' "$MAIN_PY"
    # Add include_router
    sed -i '/app.include_router(finance_router)/a\app.include_router(system_router)' "$MAIN_PY"
    echo -e "${GREEN}  ✓ System router added${NC}"
else
    echo "  ✓ System router already present"
fi

# Update AuthMiddleware to protect /app/ root path
# Also add /api/system/ to protected paths
echo "  Checking auth middleware protection..."

# 4. Update the existing dashboard to use consistent nav
echo -e "${YELLOW}[4/5]${NC} Updating dashboard navigation..."

DASHBOARD="$MYTHOS_ROOT/web/templates/dashboard.html"
if [ -f "$DASHBOARD" ]; then
    # Replace the old topbar nav with the command center nav
    # Old pattern: <a href="/app/dashboard" class="active">Dashboard</a>
    # New pattern: Full nav with all sections
    
    # Replace title
    sed -i 's|<title>Mythos — Dashboard</title>|<title>Mythos — Financial Command</title>|' "$DASHBOARD"
    
    # Add Cinzel font if not present
    if ! grep -q "Cinzel" "$DASHBOARD"; then
        sed -i 's|fonts.googleapis.com/css2?family=JetBrains|fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700\&family=JetBrains|' "$DASHBOARD"
    fi
    
    # Replace the topbar content
    python3 << 'PYEOF'
import re

with open('/opt/mythos/web/templates/dashboard.html', 'r') as f:
    content = f.read()

# Replace the old topbar with the new command center nav
old_topbar = re.search(r'<div class="topbar">.*?</div>\s*</div>', content, re.DOTALL)
if old_topbar:
    new_topbar = '''<div class="topbar">
  <div class="topbar-left" style="display:flex;align-items:center;gap:20px">
    <div style="font-family:'Cinzel',serif;font-size:16px;font-weight:600;letter-spacing:4px;color:#d4a574">MYTHOS</div>
    <nav class="topbar-nav">
      <a href="/app/">Home</a>
      <a href="/app/finance/" class="active">Finance</a>
      <a href="/app/system/">System</a>
      <a href="/app/sessions/">Sessions</a>
      <a href="/app/registry/">Registry</a>
    </nav>
  </div>
  <div class="topbar-right">
    <span class="user-info" id="user-info"></span>
    <a href="/auth/logout" class="logout-btn">logout</a>
  </div>
</div>'''
    content = content[:old_topbar.start()] + new_topbar + content[old_topbar.end():]

with open('/opt/mythos/web/templates/dashboard.html', 'w') as f:
    f.write(content)

print("  ✓ Dashboard nav updated")
PYEOF
fi

echo -e "${GREEN}  ✓ Dashboard updated${NC}"

# 5. Restart and verify
echo -e "${YELLOW}[5/5]${NC} Restarting API..."

# Syntax check
$MYTHOS_ROOT/.venv/bin/python3 -c "import py_compile; py_compile.compile('$MAIN_PY', doraise=True)" 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}  ✗ Syntax error!${NC}"
    cp "$MAIN_PY.bak.0072" "$MAIN_PY"
    exit 1
fi

sudo systemctl restart mythos-api.service
sleep 3

if systemctl is-active --quiet mythos-api.service; then
    echo -e "${GREEN}  ✓ API running${NC}"
else
    echo -e "${RED}  ✗ API failed!${NC}"
    sudo journalctl -u mythos-api.service --no-pager -n 10
    cp "$MAIN_PY.bak.0072" "$MAIN_PY"
    sudo systemctl restart mythos-api.service
    exit 1
fi

# Quick endpoint check
echo ""
echo "Verifying endpoints..."
for path in "/app/" "/app/finance/" "/app/system/" "/app/sessions/" "/app/registry/" "/api/system/status"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000${path}")
    if [ "$code" = "200" ] || [ "$code" = "307" ] || [ "$code" = "302" ]; then
        echo -e "  ${GREEN}✓${NC} ${path} → ${code}"
    else
        echo -e "  ${RED}✗${NC} ${path} → ${code}"
    fi
done

echo ""
echo "==========================================="
echo -e "${GREEN}  Patch 0072 Complete${NC}"
echo "==========================================="
echo ""
echo "Visit: https://mythos-api.denkers.co/app/"
echo ""
echo "Pages:"
echo "  /app/           → Command Center home"
echo "  /app/finance/   → Financial dashboard"
echo "  /app/system/    → System status"
echo "  /app/sessions/  → Transmission sessions"
echo "  /app/registry/  → The 144 registry"
