import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

import yaml
from pathlib import Path

patch_dir = Path(__file__).parent
with open(patch_dir / 'patch.yaml', 'r') as f:
    config = yaml.safe_load(f)

patch_number = config['number']
if patch_number == 'DRAFT':
    print("ERROR: Patch number is still DRAFT. Run mythos-diag streams and update patch.yaml")
    sys.exit(1)

patch = PatchBase(
    stream=config['stream'],
    number=int(patch_number),
    description=config['description'],
    patch_type=config.get('patch_type', 'MINOR'),
)
patch.begin()

# 1. Deploy new API route
patch.deploy_file(
    'opt/mythos/api/routes/finance_dashboard.py',
    '/opt/mythos/api/routes/finance_dashboard.py'
)

# 2. Deploy new React pages
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/DashboardV2.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/DashboardV2.jsx'
)
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/BillsDetailV2.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/BillsDetailV2.jsx'
)

# 3. Register new API router in main.py
main_py = Path('/opt/mythos/api/main.py')
content = main_py.read_text()

if 'finance_dashboard' not in content:
    # Find existing finance import and add ours after it
    old = 'from routes.finance import router as finance_router'
    new = old + '\nfrom routes.finance_dashboard import router as finance_dashboard_router'
    content = content.replace(old, new)

    # Find where finance_router is included and add ours
    old_include = 'app.include_router(finance_router)'
    new_include = old_include + '\napp.include_router(finance_dashboard_router)'
    content = content.replace(old_include, new_include)

    main_py.write_text(content)
    print('  ✓ api/main.py updated')
else:
    print('  ⊘ api/main.py already has finance_dashboard')

# 4. Add routes to App.jsx
app_jsx = Path('/opt/mythos/web/frontend/src/App.jsx')
content = app_jsx.read_text()

if 'DashboardV2' not in content:
    # Add import
    old_import = "import Bills from './pages/finance/Bills'"
    new_import = old_import + "\nimport DashboardV2 from './pages/finance/DashboardV2'\nimport BillsDetailV2 from './pages/finance/BillsDetailV2'"
    content = content.replace(old_import, new_import)

    # Add routes — insert new finance v2 routes before the old finance block
    old_route = '{/* Finance (live) */}'
    new_route = """{/* Finance v2 (new) */}
        <Route path="/finance/dashboard" element={<DashboardV2 />} />
        <Route path="/finance/bills-detail" element={<BillsDetailV2 />} />

        """ + old_route
    content = content.replace(old_route, new_route)

    # Update the finance redirect to go to new dashboard
    content = content.replace(
        '<Route path="/finance" element={<Navigate to="/finance/overview" replace />} />',
        '<Route path="/finance" element={<Navigate to="/finance/dashboard" replace />} />'
    )

    app_jsx.write_text(content)
    print('  ✓ App.jsx updated')
else:
    print('  ⊘ App.jsx already has DashboardV2')

# 5. Add nav items to CommandCenter.jsx
cc_jsx = Path('/opt/mythos/web/frontend/src/layouts/CommandCenter.jsx')
content = cc_jsx.read_text()

if '/finance/dashboard' not in content:
    # Add new section at top of finance sidebar
    old_sidebar = """  finance: [
    {
      label: "Finance",
      items: [
        { icon: "◈", label: "Overview",     to: "/finance/overview" },"""

    new_sidebar = """  finance: [
    {
      label: "Dashboard",
      items: [
        { icon: "⬡", label: "Dashboard",    to: "/finance/dashboard" },
        { icon: "📋", label: "Bills Detail", to: "/finance/bills-detail" },
      ]
    },
    {
      label: "Finance",
      items: [
        { icon: "◈", label: "Overview",     to: "/finance/overview" },"""

    content = content.replace(old_sidebar, new_sidebar)
    cc_jsx.write_text(content)
    print('  ✓ CommandCenter.jsx updated')
else:
    print('  ⊘ CommandCenter.jsx already has dashboard nav')

# 6. Rebuild frontend
import subprocess
result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True, text=True
)
if result.returncode == 0:
    print('  ✓ Frontend rebuilt')
else:
    print(f'  ⚠ Frontend build failed: {result.stderr[:200]}')

# 7. Restart API
patch.restart_service('mythos-api.service')

patch.finish()
