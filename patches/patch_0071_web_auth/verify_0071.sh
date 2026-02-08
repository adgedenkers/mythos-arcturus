#!/bin/bash
# =============================================================
# Verify Patch 0071: Web Dashboard + Google OAuth
# =============================================================
# Run after install to confirm everything is working
# =============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
PASS=0
FAIL=0

check() {
    local desc="$1"
    local result="$2"
    if [ "$result" = "0" ]; then
        echo -e "  ${GREEN}✓${NC} $desc"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} $desc"
        ((FAIL++))
    fi
}

echo ""
echo "==========================================="
echo "  Verifying Patch 0071"
echo "==========================================="
echo ""

# 1. API Service
echo "Service Status:"
systemctl is-active --quiet mythos-api.service
check "mythos-api.service running" $?

# 2. Files exist
echo ""
echo "Files:"
test -f /opt/mythos/api/auth/google_auth.py
check "google_auth.py exists" $?

test -f /opt/mythos/api/routes/finance.py
check "finance.py routes exist" $?

test -f /opt/mythos/api/routes/web.py
check "web.py routes exist" $?

test -f /opt/mythos/web/templates/login.html
check "login.html exists" $?

test -f /opt/mythos/web/templates/dashboard.html
check "dashboard.html exists" $?

# 3. Database
echo ""
echo "Database:"
USERS=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM web_users WHERE is_active = true;" 2>/dev/null | tr -d ' ')
[ "$USERS" = "2" ]
check "web_users table has 2 active users" $?

sudo -u postgres psql -d mythos -t -c "SELECT email FROM web_users WHERE is_active = true;" 2>/dev/null | grep -q "adge.denkers"
check "Ka'tuar'el whitelisted" $?

sudo -u postgres psql -d mythos -t -c "SELECT email FROM web_users WHERE is_active = true;" 2>/dev/null | grep -q "rebecca.denkers"
check "Seraphe whitelisted" $?

# 4. Python imports
echo ""
echo "Python:"
/opt/mythos/.venv/bin/python3 -c "import jwt" 2>/dev/null
check "PyJWT installed" $?

/opt/mythos/.venv/bin/python3 -c "import httpx" 2>/dev/null
check "httpx installed" $?

/opt/mythos/.venv/bin/python3 -c "
import sys; sys.path.insert(0, '/opt/mythos')
from api.auth.google_auth import create_jwt, verify_jwt
" 2>/dev/null
check "Auth module importable" $?

# 5. API endpoints
echo ""
echo "API Endpoints:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null)
[ "$HTTP_CODE" = "200" ]
check "GET /health → 200" $?

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/app/login 2>/dev/null)
[ "$HTTP_CODE" = "200" ]
check "GET /app/login → 200 (public)" $?

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/app/dashboard 2>/dev/null)
[ "$HTTP_CODE" = "307" ] || [ "$HTTP_CODE" = "302" ]
check "GET /app/dashboard → redirect (protected)" $?

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/finance/summary 2>/dev/null)
[ "$HTTP_CODE" = "401" ]
check "GET /api/finance/summary → 401 (protected)" $?

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/auth/google/login 2>/dev/null)
# Should be 302 redirect to Google, or 500 if credentials not set
[ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "500" ]
check "GET /auth/google/login → redirect or config error" $?

# 6. Environment
echo ""
echo "Configuration:"
grep -q "^JWT_SECRET=" /opt/mythos/.env 2>/dev/null
check "JWT_SECRET in .env" $?

grep -q "^GOOGLE_CLIENT_ID=" /opt/mythos/.env 2>/dev/null
check "GOOGLE_CLIENT_ID in .env" $?

GOOGLE_ID=$(grep "^GOOGLE_CLIENT_ID=" /opt/mythos/.env 2>/dev/null | cut -d= -f2)
if [ -n "$GOOGLE_ID" ] && [ "$GOOGLE_ID" != "" ]; then
    check "GOOGLE_CLIENT_ID has value" 0
else
    echo -e "  ${YELLOW}⚠${NC} GOOGLE_CLIENT_ID is empty - set it after creating credentials"
fi

grep -q "^GOOGLE_REDIRECT_URI=" /opt/mythos/.env 2>/dev/null
check "GOOGLE_REDIRECT_URI in .env" $?

# 7. Cloudflare
echo ""
echo "Cloudflare:"
systemctl is-active --quiet cloudflared
check "cloudflared tunnel running" $?

grep -q "mythos-api.denkers.co" /etc/cloudflared/config.yml 2>/dev/null
check "mythos-api.denkers.co in tunnel config" $?

# Summary
echo ""
echo "==========================================="
echo -e "  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "==========================================="
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${YELLOW}Issues found. Check the failures above.${NC}"
    echo ""
fi

if [ -z "$GOOGLE_ID" ] || [ "$GOOGLE_ID" = "" ]; then
    echo -e "${YELLOW}REMINDER: Set up Google OAuth credentials:${NC}"
    echo "  1. Go to https://console.cloud.google.com/apis/credentials"
    echo "  2. Create OAuth 2.0 Client ID (Web application)"
    echo "  3. Add redirect URI: https://mythos-api.denkers.co/auth/google/callback"
    echo "  4. Copy Client ID and Secret to /opt/mythos/.env"
    echo "  5. Restart: sudo systemctl restart mythos-api.service"
    echo "  6. Visit: https://mythos-api.denkers.co/app/login"
fi
