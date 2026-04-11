#!/usr/bin/env python3
"""
SYS-0021: Finance Projection Page
- New API endpoint: /api/finance/projection
- New React page: Projection.jsx
- Route added to App.jsx
- Sidebar entry added to CommandCenter.jsx
- API router registered in main.py
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=21,
    description='Finance Projection Page — per-account daily balance projection with timeline + calendar views',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy API endpoint ──────────────────────────────────
patch.deploy_file(
    'opt/mythos/api/routes/projection.py',
    '/opt/mythos/api/routes/projection.py'
)

# ── 2. Deploy React page ────────────────────────────────────
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/Projection.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/Projection.jsx'
)

# ── 3. Register projection router in main.py ────────────────
main_py = '/opt/mythos/api/main.py'
with open(main_py, 'r') as f:
    content = f.read()

# Add import
old_import = 'from api.routes.finance import router as finance_router'
new_import = '''from api.routes.finance import router as finance_router
from api.routes.projection import router as projection_router'''

if 'projection_router' not in content:
    content = content.replace(old_import, new_import)

    # Add router inclusion after finance_router
    old_include = 'app.include_router(finance_router)'
    new_include = '''app.include_router(finance_router)
app.include_router(projection_router)'''
    content = content.replace(old_include, new_include)

    with open(main_py, 'w') as f:
        f.write(content)
    print('  ✓ Registered projection_router in main.py')
else:
    print('  ⏭ projection_router already registered in main.py')

# ── 4. Add route to App.jsx ─────────────────────────────────
app_jsx = '/opt/mythos/web/frontend/src/App.jsx'
with open(app_jsx, 'r') as f:
    content = f.read()

if 'Projection' not in content:
    # Add import
    old_cal_import = "import Calendar from './pages/finance/Calendar'"
    new_cal_import = """import Calendar from './pages/finance/Calendar'
import Projection from './pages/finance/Projection'"""
    content = content.replace(old_cal_import, new_cal_import)

    # Add route after calendar route
    old_cal_route = '<Route path="/finance/calendar" element={<Calendar />} />'
    new_cal_route = """<Route path="/finance/calendar" element={<Calendar />} />
        <Route path="/finance/projection" element={<Projection />} />"""
    content = content.replace(old_cal_route, new_cal_route)

    with open(app_jsx, 'w') as f:
        f.write(content)
    print('  ✓ Added Projection route to App.jsx')
else:
    print('  ⏭ Projection route already in App.jsx')

# ── 5. Add sidebar entry to CommandCenter.jsx ────────────────
layout_jsx = '/opt/mythos/web/frontend/src/layouts/CommandCenter.jsx'
with open(layout_jsx, 'r') as f:
    content = f.read()

if '/finance/projection' not in content:
    # Add after calendar sidebar entry
    old_sidebar = '{ icon: "🗓", label: "Calendar",     to: "/finance/calendar" },'
    new_sidebar = """{ icon: "🗓", label: "Calendar",     to: "/finance/calendar" },
        { icon: "📆", label: "Projection",   to: "/finance/projection" },"""
    content = content.replace(old_sidebar, new_sidebar)

    with open(layout_jsx, 'w') as f:
        f.write(content)
    print('  ✓ Added Projection to sidebar in CommandCenter.jsx')
else:
    print('  ⏭ Projection already in CommandCenter sidebar')

# ── 6. Rebuild React frontend ───────────────────────────────
import subprocess
result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True,
    text=True,
    timeout=120,
)
if result.returncode == 0:
    print('  ✓ React frontend rebuilt')
else:
    print(f'  ⚠ Frontend build output: {result.stdout}')
    print(f'  ⚠ Frontend build errors: {result.stderr}')
    # Don't fail the patch — API endpoint still works
    print('  ℹ Frontend build issue — may need manual rebuild')

# ── 7. Restart API service ───────────────────────────────────
patch.restart_service('mythos-api.service')

patch.finish()
