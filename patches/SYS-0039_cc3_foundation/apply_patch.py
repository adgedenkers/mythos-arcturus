#!/usr/bin/env python3
"""
SYS-0039: Command Center v3 Foundation
- 7 new UI components: Badge, MoneyAmount, Tabs, Modal, Toast, SearchInput, SplitPane
- Updated ui/index.js with new exports
- Pattern Matcher placeholder page + route
- Finance sidebar: add Pattern Matcher nav item
- App.jsx: add pattern-matcher route
- main.jsx: wrap App in ToastProvider
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=39,
    description='cc3_foundation',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy new UI components ───────────────────────────────
ui_dir = 'opt/mythos/web/frontend/src/components/ui'
for comp in ['Badge.jsx', 'MoneyAmount.jsx', 'Tabs.jsx', 'Modal.jsx', 'Toast.jsx', 'SearchInput.jsx', 'SplitPane.jsx']:
    patch.deploy_file(
        f'{ui_dir}/{comp}',
        f'/opt/mythos/web/frontend/src/components/ui/{comp}'
    )

# Updated index.js
patch.deploy_file(
    f'{ui_dir}/index.js',
    '/opt/mythos/web/frontend/src/components/ui/index.js'
)

# ── Deploy PatternMatcher placeholder ──────────────────────
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/PatternMatcher.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/PatternMatcher.jsx'
)

# ── Patch CommandCenter.jsx — add Pattern Matcher to finance sidebar ──
cc_path = '/opt/mythos/web/frontend/src/layouts/CommandCenter.jsx'
with open(cc_path, 'r') as f:
    cc = f.read()

# Add Pattern Matcher to the Finance group, after Bills Map
old_bills_map = '{ icon: "🗺", label: "Bills Map",    to: "/finance/bills-map" },'
new_bills_map = old_bills_map + '\n        { icon: "⟁", label: "Matcher",     to: "/finance/pattern-matcher" },'

if '⟁' not in cc:
    cc = cc.replace(old_bills_map, new_bills_map)
    with open(cc_path, 'w') as f:
        f.write(cc)
    print('  ✓ CommandCenter.jsx: added Pattern Matcher to finance sidebar')
else:
    print('  ⊘ CommandCenter.jsx: Pattern Matcher already present')

# ── Patch App.jsx — add pattern-matcher route ──────────────
app_path = '/opt/mythos/web/frontend/src/App.jsx'
with open(app_path, 'r') as f:
    app = f.read()

# Add import
if 'PatternMatcher' not in app:
    old_import = "import Transactions from './pages/finance/Transactions'"
    new_import = old_import + "\nimport PatternMatcher from './pages/finance/PatternMatcher'"
    app = app.replace(old_import, new_import)

    # Add route after bills-map
    old_route = '<Route path="/finance/bills-map" element={<BillsTimeline />} />'
    new_route = old_route + '\n        <Route path="/finance/pattern-matcher" element={<PatternMatcher />} />'
    app = app.replace(old_route, new_route)

    with open(app_path, 'w') as f:
        f.write(app)
    print('  ✓ App.jsx: added PatternMatcher import + route')
else:
    print('  ⊘ App.jsx: PatternMatcher already present')

# ── Patch main.jsx — wrap with ToastProvider ───────────────
main_path = '/opt/mythos/web/frontend/src/main.jsx'
with open(main_path, 'r') as f:
    main = f.read()

if 'ToastProvider' not in main:
    # Add import
    if "import App from './App'" in main:
        main = main.replace(
            "import App from './App'",
            "import App from './App'\nimport { ToastProvider } from './components/ui/Toast'"
        )
    elif "import App from './App.jsx'" in main:
        main = main.replace(
            "import App from './App.jsx'",
            "import App from './App.jsx'\nimport { ToastProvider } from './components/ui/Toast'"
        )

    # Wrap <App /> with <ToastProvider>
    # Handle both <App /> and <App/> patterns inside BrowserRouter or similar
    if '<App />' in main:
        main = main.replace('<App />', '<ToastProvider><App /></ToastProvider>')
    elif '<App/>' in main:
        main = main.replace('<App/>', '<ToastProvider><App /></ToastProvider>')

    with open(main_path, 'w') as f:
        f.write(main)
    print('  ✓ main.jsx: wrapped App in ToastProvider')
else:
    print('  ⊘ main.jsx: ToastProvider already present')

# ── Build frontend ─────────────────────────────────────────
import subprocess
result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True,
    text=True,
    timeout=60,
)
if result.returncode == 0:
    print('  ✓ Frontend built successfully')
else:
    print(f'  ✗ Frontend build failed:\n{result.stderr[-500:]}')
    # Don't abort — files are deployed, build can be retried

# ── Restart API to serve new dist ──────────────────────────
patch.restart_service('mythos-api.service')

patch.finish()
