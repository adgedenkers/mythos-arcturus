import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=20,
    description='Bills management page — edit match patterns, test against transactions, view match status',
    patch_type='MINOR',
)
patch.begin()

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Deploy Bills.jsx component
# ═══════════════════════════════════════════════════════════════════════════════

patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/Bills.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/Bills.jsx'
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. App.jsx — replace Placeholder import with Bills component
# ═══════════════════════════════════════════════════════════════════════════════

APP_PATH = '/opt/mythos/web/frontend/src/App.jsx'

with open(APP_PATH, 'r') as f:
    app = f.read()

# Add Bills import after Calendar import
old_import = "import Calendar from './pages/finance/Calendar'"
new_import = "import Calendar from './pages/finance/Calendar'\nimport Bills from './pages/finance/Bills'"

assert old_import in app, "Calendar import not found in App.jsx"
app = app.replace(old_import, new_import, 1)

# Replace the placeholder route with the real Bills component
old_route = '<Route path="/finance/bills" element={<Placeholder title="Bills" />} />'
new_route = '<Route path="/finance/bills" element={<Bills />} />'

assert old_route in app, "Bills placeholder route not found in App.jsx"
app = app.replace(old_route, new_route)

with open(APP_PATH, 'w') as f:
    f.write(app)

patch.logger.log("App.jsx: Added Bills import, replaced Placeholder route")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Finance API — Add PATCH /bills/{id} and GET /bills/test-pattern endpoints
#    Also expand existing queries to include merchant_pattern
# ═══════════════════════════════════════════════════════════════════════════════

FIN_PATH = '/opt/mythos/api/routes/finance.py'

with open(FIN_PATH, 'r') as f:
    fin = f.read()

# ── 3a. Add BillUpdate model ──
old_model = (
    "class BillOverrideBody(BaseModel):\n"
    "    paid: bool\n"
    "    paid_amount: Optional[float] = None\n"
    "    paid_date: Optional[str] = None   # YYYY-MM-DD\n"
    "    note: Optional[str] = None"
)

new_model = (
    "class BillOverrideBody(BaseModel):\n"
    "    paid: bool\n"
    "    paid_amount: Optional[float] = None\n"
    "    paid_date: Optional[str] = None   # YYYY-MM-DD\n"
    "    note: Optional[str] = None\n"
    "\n"
    "class BillUpdate(BaseModel):\n"
    "    merchant_name: Optional[str] = None\n"
    "    merchant_pattern: Optional[str] = None\n"
    "    expected_amount: Optional[float] = None\n"
    "    amount_variance: Optional[float] = None\n"
    "    expected_day: Optional[int] = None\n"
    "    category_primary: Optional[str] = None\n"
    "    notes: Optional[str] = None"
)

assert old_model in fin, "BillOverrideBody model not found in finance.py"
fin = fin.replace(old_model, new_model)

# ── 3b. Add new endpoints before bills/tracker ──
old_tracker_decorator = '@router.get("/bills/tracker")'

new_endpoints_block = (
    '@router.patch("/bills/{bill_id}")\n'
    'async def update_bill(request: Request, bill_id: int, update: BillUpdate):\n'
    '    """Update a recurring bill\'s match pattern, amount, or other fields."""\n'
    '    conn = get_db(); cur = conn.cursor()\n'
    '    fields, params = [], []\n'
    '    if update.merchant_name is not None:\n'
    '        fields.append("merchant_name = %s"); params.append(update.merchant_name.strip())\n'
    '    if update.merchant_pattern is not None:\n'
    '        fields.append("merchant_pattern = %s"); params.append(update.merchant_pattern.strip() or None)\n'
    '    if update.expected_amount is not None:\n'
    '        fields.append("expected_amount = %s"); params.append(update.expected_amount)\n'
    '    if update.amount_variance is not None:\n'
    '        fields.append("amount_variance = %s"); params.append(update.amount_variance)\n'
    '    if update.expected_day is not None:\n'
    '        fields.append("expected_day = %s"); params.append(update.expected_day if update.expected_day > 0 else None)\n'
    '    if update.category_primary is not None:\n'
    '        fields.append("category_primary = %s"); params.append(update.category_primary.strip() or None)\n'
    '    if update.notes is not None:\n'
    '        fields.append("notes = %s"); params.append(update.notes.strip() or None)\n'
    '    if not fields:\n'
    '        conn.close(); raise HTTPException(status_code=400, detail="No fields to update")\n'
    '    params.append(bill_id)\n'
    '    cur.execute(f"UPDATE recurring_bills SET {\', \'.join(fields)} WHERE id = %s RETURNING id, merchant_name", params)\n'
    '    result = cur.fetchone(); conn.commit(); conn.close()\n'
    '    if not result: raise HTTPException(status_code=404, detail="Bill not found")\n'
    '    return json_response({"success": True, "id": bill_id, "merchant_name": result[\'merchant_name\']})\n'
    '\n'
    '@router.get("/bills/test-pattern")\n'
    'async def test_bill_pattern(\n'
    '    request: Request,\n'
    '    pattern: str = Query(..., description="Pattern to test against transaction descriptions"),\n'
    '    limit: int = Query(default=20, ge=1, le=50),\n'
    '):\n'
    '    """Test a match pattern against recent transactions."""\n'
    '    conn = get_db(); cur = conn.cursor()\n'
    '    cur.execute(\n'
    '        "SELECT t.id, t.transaction_date, t.description, t.original_description, "\n'
    '        "t.amount, a.abbreviation as account "\n'
    '        "FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id "\n'
    '        "WHERE t.amount < 0 AND (t.description ILIKE %s OR t.original_description ILIKE %s) "\n'
    '        "ORDER BY t.transaction_date DESC LIMIT %s",\n'
    "        (f'%{pattern}%', f'%{pattern}%', limit)\n"
    '    )\n'
    '    matches = [dict(r) for r in cur.fetchall()]\n'
    '    conn.close()\n'
    '    return json_response({"pattern": pattern, "matches": matches, "count": len(matches)})\n'
    '\n'
    '@router.get("/bills/tracker")'
)

assert old_tracker_decorator in fin, "bills/tracker decorator not found in finance.py"
fin = fin.replace(old_tracker_decorator, new_endpoints_block, 1)

# ── 3c. Expand bills list query to include merchant_pattern and amount_variance ──
old_bills_q = (
    "        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,\n"
    "               rb.frequency, rb.category_primary, rb.notes, a.abbreviation as account\n"
    "        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id\n"
    "        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST"
)

new_bills_q = (
    "        SELECT rb.id, rb.merchant_name, rb.merchant_pattern, rb.expected_amount,\n"
    "               rb.expected_day, rb.amount_variance, rb.frequency, rb.category_primary,\n"
    "               rb.notes, a.abbreviation as account\n"
    "        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id\n"
    "        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST"
)

assert old_bills_q in fin, "Bills list query not found in finance.py"
fin = fin.replace(old_bills_q, new_bills_q)

# ── 3d. Expand tracker query to include merchant_pattern ──
old_tracker_q = (
    "        SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day,\n"
    "               rb.frequency, rb.category_primary, rb.amount_variance, rb.notes,\n"
    "               a.abbreviation as account\n"
    "        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id\n"
    "        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST, rb.merchant_name"
)

new_tracker_q = (
    "        SELECT rb.id, rb.merchant_name, rb.merchant_pattern, rb.expected_amount,\n"
    "               rb.expected_day, rb.frequency, rb.category_primary, rb.amount_variance,\n"
    "               rb.notes, a.abbreviation as account\n"
    "        FROM recurring_bills rb LEFT JOIN accounts a ON rb.account_id = a.id\n"
    "        WHERE rb.is_active = true ORDER BY rb.expected_day NULLS LAST, rb.merchant_name"
)

assert old_tracker_q in fin, "Tracker query not found in finance.py"
fin = fin.replace(old_tracker_q, new_tracker_q)

with open(FIN_PATH, 'w') as f:
    f.write(fin)

patch.logger.log("finance.py: Added PATCH /bills/{id}, GET /bills/test-pattern, expanded queries")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Verify Python compiles
# ═══════════════════════════════════════════════════════════════════════════════

import py_compile
py_compile.compile(FIN_PATH, doraise=True)
patch.logger.log("finance.py compiles OK")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Rebuild frontend
# ═══════════════════════════════════════════════════════════════════════════════

import subprocess

result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True, text=True, timeout=120,
)
if result.returncode != 0:
    patch.logger.log("Frontend build FAILED: " + result.stderr[-500:])
    patch.errors.append("Frontend build failed: " + result.stderr[-200:])
else:
    patch.logger.log("Frontend rebuilt OK")

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Restart API
# ═══════════════════════════════════════════════════════════════════════════════

patch.restart_service('mythos-api.service')

patch.finish()
