#!/usr/bin/env python3
"""
SYS-0025: Bills Timeline — visual monthly map of bills and income by day
- New React page: BillsTimeline.jsx
- Route: /finance/bills-map
- Sidebar entry under Finance
"""
import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=25,
    description='Bills Timeline — visual monthly map of bills and income by day',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Deploy page ──────────────────────────────────────────
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/BillsTimeline.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/BillsTimeline.jsx'
)

# ── 2. Add route to App.jsx ─────────────────────────────────
app_jsx = '/opt/mythos/web/frontend/src/App.jsx'
with open(app_jsx, 'r') as f:
    content = f.read()

if 'BillsTimeline' not in content:
    # Add import
    old_import = "import Bills from './pages/finance/Bills'"
    new_import = """import Bills from './pages/finance/Bills'
import BillsTimeline from './pages/finance/BillsTimeline'"""
    content = content.replace(old_import, new_import)

    # Add route after bills route
    old_route = '<Route path="/finance/bills" element={<Bills />} />'
    new_route = """<Route path="/finance/bills" element={<Bills />} />
        <Route path="/finance/bills-map" element={<BillsTimeline />} />"""
    content = content.replace(old_route, new_route)

    with open(app_jsx, 'w') as f:
        f.write(content)
    print('  ✓ Added BillsTimeline route to App.jsx')
else:
    print('  ⏭ BillsTimeline route already exists')

# ── 3. Add sidebar entry to CommandCenter.jsx ────────────────
layout_jsx = '/opt/mythos/web/frontend/src/layouts/CommandCenter.jsx'
with open(layout_jsx, 'r') as f:
    content = f.read()

if '/finance/bills-map' not in content:
    old_sidebar = '{ icon: "📅", label: "Bills",        to: "/finance/bills" },'
    new_sidebar = """{ icon: "📅", label: "Bills",        to: "/finance/bills" },
        { icon: "🗺", label: "Bills Map",    to: "/finance/bills-map" },"""
    content = content.replace(old_sidebar, new_sidebar)

    with open(layout_jsx, 'w') as f:
        f.write(content)
    print('  ✓ Added Bills Map to sidebar')
else:
    print('  ⏭ Bills Map already in sidebar')

# ── 4. Rebuild frontend ─────────────────────────────────────
# Clean dist first to avoid permission issues
subprocess.run(['sudo', 'rm', '-rf', '/opt/mythos/web/frontend/dist'], capture_output=True)
result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True, text=True, timeout=120,
)
if result.returncode == 0:
    print('  ✓ React frontend rebuilt')
else:
    print(f'  ⚠ Build: {result.stderr[-300:] if result.stderr else result.stdout[-300:]}')

patch.finish()
