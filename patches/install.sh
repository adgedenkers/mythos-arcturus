#!/bin/bash
# patch_0095_astro_numerology - install.sh
# Adds Astrology & Numerology tab to Mythos Command Center
set -e

MYTHOS="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "═══ Patch 0095: Astrology & Numerology Tab ═══"

# 1. Copy template
echo "→ Installing astrology.html template..."
cp "$PATCH_DIR/opt/mythos/web/templates/astrology.html" "$MYTHOS/web/templates/astrology.html"

# 2. Copy API routes
echo "→ Installing astrology API routes..."
cp "$PATCH_DIR/opt/mythos/api/routes/astrology.py" "$MYTHOS/api/routes/astrology.py"

# 3. Add route to web.py (if not already present)
WEB_ROUTES="$MYTHOS/api/routes/web.py"
if ! grep -q "astrology" "$WEB_ROUTES" 2>/dev/null; then
    echo "→ Adding /app/astrology/ route to web.py..."
    cat >> "$WEB_ROUTES" << 'ROUTE'


# Astrology & Numerology
@router.get("/astrology/", response_class=HTMLResponse)
@router.get("/astrology", response_class=HTMLResponse)
async def astrology_page(request: Request):
    return serve('astrology.html')
ROUTE
    echo "  ✓ Route added"
else
    echo "  ⏭ Astrology route already exists in web.py"
fi

# 4. Register astrology router in main.py (if not already present)
MAIN_PY="$MYTHOS/api/main.py"
if ! grep -q "astrology" "$MAIN_PY" 2>/dev/null; then
    echo "→ Registering astrology router in main.py..."
    # Add import after the system router import
    sed -i '/from api\.routes\.system import router as system_router/a from api.routes.astrology import router as astrology_router' "$MAIN_PY"
    # Add include_router after system_router
    sed -i '/app\.include_router(system_router)/a app.include_router(astrology_router)' "$MAIN_PY"
    echo "  ✓ Router registered"
else
    echo "  ⏭ Astrology router already registered in main.py"
fi

# 5. Add Astrology nav link to all existing templates
echo "→ Updating navigation in existing templates..."
TEMPLATES=("home.html" "dashboard.html" "system.html" "sessions.html" "registry.html")
for tmpl in "${TEMPLATES[@]}"; do
    TMPL_PATH="$MYTHOS/web/templates/$tmpl"
    if [ -f "$TMPL_PATH" ]; then
        if ! grep -q "astrology" "$TMPL_PATH" 2>/dev/null; then
            # Insert astrology link after registry link in nav
            sed -i 's|<a href="/app/registry/"[^>]*>Registry</a>|&\n    <a href="/app/astrology/">Astrology</a>|' "$TMPL_PATH"
            # Handle the active variant too
            sed -i 's|<a href="/app/registry/" class="active">Registry</a>|&\n    <a href="/app/astrology/">Astrology</a>|' "$TMPL_PATH"
            echo "  ✓ Updated nav in $tmpl"
        else
            echo "  ⏭ $tmpl already has astrology link"
        fi
    fi
done

# 6. Restart API service
echo "→ Restarting mythos-api service..."
sudo systemctl restart mythos-api.service
sleep 2

# Verify
if systemctl is-active --quiet mythos-api.service; then
    echo "  ✓ mythos-api is running"
else
    echo "  ✗ mythos-api failed to start — check: journalctl -u mythos-api -n 30"
    exit 1
fi

echo ""
echo "═══ Patch 0095 Complete ═══"
echo "→ Visit /app/astrology/ in the Command Center"
echo "→ New API endpoints:"
echo "   GET /api/astrology/charts"
echo "   GET /api/astrology/charts/{id}"
echo "   GET /api/astrology/people"
echo "   GET /api/astrology/numerology/{id}"
