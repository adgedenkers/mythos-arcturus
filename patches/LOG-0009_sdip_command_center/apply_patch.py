import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=9,
    description='SDIP Command Center dashboard - React page with 6 sub-tabs',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy the SDIP dashboard component ───────────────────
os.makedirs('/opt/mythos/web/frontend/src/pages/sdip', exist_ok=True)
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/sdip/SDIPDashboard.jsx',
    '/opt/mythos/web/frontend/src/pages/sdip/SDIPDashboard.jsx'
)

# ── Wire into App.jsx (routing) ───────────────────────────
app_path = '/opt/mythos/web/frontend/src/App.jsx'
with open(app_path, 'r') as f:
    content = f.read()

if 'SDIPDashboard' not in content:
    # Add import
    content = content.replace(
        "import IrisSystems from './pages/iris/IrisSystems'",
        "import IrisSystems from './pages/iris/IrisSystems'\nimport SDIPDashboard from './pages/sdip/SDIPDashboard'"
    )

    # Add route — before the Research stub
    content = content.replace(
        '        {/* Research (stub) */}',
        '        {/* SDIP */}\n'
        '        <Route path="/sdip" element={<SDIPDashboard />} />\n\n'
        '        {/* Research (stub) */}'
    )

    with open(app_path, 'w') as f:
        f.write(content)
    print("  ✓ Wired SDIP route into App.jsx")
else:
    print("  ℹ SDIP route already in App.jsx")

# ── Wire into CommandCenter.jsx (top nav) ─────────────────
layout_path = '/opt/mythos/web/frontend/src/layouts/CommandCenter.jsx'
with open(layout_path, 'r') as f:
    content = f.read()

if '"SDIP"' not in content and "'SDIP'" not in content:
    # Add SDIP nav item after Iris
    content = content.replace(
        '  { label: "Iris",     to: "/iris" },',
        '  { label: "Iris",     to: "/iris" },\n'
        '  { label: "SDIP",     to: "/sdip" },'
    )

    with open(layout_path, 'w') as f:
        f.write(content)
    print("  ✓ Added SDIP to top nav in CommandCenter.jsx")
else:
    print("  ℹ SDIP already in top nav")

# ── Build the frontend ────────────────────────────────────
print("  Building frontend...")
os.system('cd /opt/mythos/web/frontend && npm run build 2>&1')
print("  ✓ Frontend built")

patch.finish()
