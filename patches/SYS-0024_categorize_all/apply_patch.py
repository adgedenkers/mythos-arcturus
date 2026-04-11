#!/usr/bin/env python3
"""
SYS-0024: Categorize All — Apply category changes to all matching transactions
- New API endpoint: POST /api/finance/transactions/{txn_id}/apply-category
- Updates all transactions matching the same merchant/description pattern
- Upserts a category_mapping rule for future imports
- Updated Transactions.jsx with "Apply to all" prompt after category edit
"""
import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=24,
    description='Categorize All — apply category to all matching transactions + create mapping rule',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Add endpoint to finance routes ────────────────────────
finance_py = '/opt/mythos/api/routes/finance.py'
with open(finance_py, 'r') as f:
    content = f.read()

endpoint_code = '''

# ── Apply Category to All Matching ─────────────────────────
class ApplyCategoryBody(BaseModel):
    category_primary: str
    merchant_name: Optional[str] = None
    pattern: Optional[str] = None  # override auto-detected pattern

@router.post("/transactions/{txn_id}/apply-category")
async def apply_category_to_all(request: Request, txn_id: int, body: ApplyCategoryBody):
    """
    Apply a category to all transactions matching the same vendor pattern.
    Also upserts a category_mapping rule so future imports get categorized.
    
    1. Reads the target transaction's description/original_description
    2. Finds the best pattern to match on
    3. Updates all matching transactions
    4. Upserts a category_mapping rule
    """
    conn = get_db(); cur = conn.cursor()
    
    # Get the target transaction
    cur.execute("""
        SELECT id, description, original_description, merchant_name, category_primary
        FROM transactions WHERE id = %s
    """, (txn_id,))
    txn = cur.fetchone()
    if not txn:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Determine the match pattern
    if body.pattern:
        pattern = body.pattern.strip()
    elif body.merchant_name:
        pattern = body.merchant_name.strip()
    elif txn['merchant_name']:
        pattern = txn['merchant_name'].strip()
    elif txn['description']:
        # Use the description, but try to extract a clean vendor name
        # Take the first significant word(s) — skip common prefixes
        desc = txn['description'].strip()
        # Remove common prefixes
        for prefix in ['DEP:', 'EXT:', 'POS', 'ATM', 'ACH', 'PP*', 'Paypal:']:
            if desc.upper().startswith(prefix.upper()):
                desc = desc[len(prefix):].strip()
        pattern = desc.split('  ')[0].split(' #')[0].strip()  # Take before double-space or #number
        if len(pattern) < 3:
            pattern = txn['description'].strip()
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot determine match pattern")
    
    new_category = body.category_primary.strip()
    new_merchant = (body.merchant_name or '').strip() or None
    
    # Update all matching transactions
    cur.execute("""
        UPDATE transactions
        SET category_primary = %s,
            merchant_name = COALESCE(%s, merchant_name)
        WHERE (
            LOWER(description) LIKE LOWER(%s)
            OR LOWER(original_description) LIKE LOWER(%s)
        )
        AND id != %s
        RETURNING id
    """, (
        new_category,
        new_merchant,
        f'%{pattern}%',
        f'%{pattern}%',
        txn_id,
    ))
    bulk_updated = cur.rowcount
    
    # Also update the original transaction
    cur.execute("""
        UPDATE transactions
        SET category_primary = %s, merchant_name = COALESCE(%s, merchant_name)
        WHERE id = %s
    """, (new_category, new_merchant, txn_id))
    
    # Upsert category_mapping rule
    # Check if a mapping with this pattern already exists
    cur.execute("""
        SELECT id, category_primary FROM category_mappings
        WHERE LOWER(pattern) = LOWER(%s) AND is_active = true
    """, (pattern,))
    existing = cur.fetchone()
    
    if existing:
        # Update existing mapping
        cur.execute("""
            UPDATE category_mappings
            SET category_primary = %s, merchant_name = %s
            WHERE id = %s
        """, (new_category, new_merchant, existing['id']))
        mapping_action = 'updated'
    else:
        # Create new mapping
        cur.execute("""
            INSERT INTO category_mappings (pattern, pattern_type, category_primary, merchant_name, priority, is_active)
            VALUES (%s, 'contains', %s, %s, 90, true)
        """, (pattern, new_category, new_merchant))
        mapping_action = 'created'
    
    conn.commit()
    conn.close()
    
    return json_response({
        "success": True,
        "txn_id": txn_id,
        "pattern": pattern,
        "category": new_category,
        "merchant": new_merchant,
        "bulk_updated": bulk_updated,
        "mapping_action": mapping_action,
    })
'''

if 'apply-category' not in content:
    # Insert before the last route section comment or at the end of the file
    # Find a good insertion point — after the existing transaction PATCH endpoint
    marker = "# ── Categories"
    if marker in content:
        content = content.replace(marker, endpoint_code + "\n" + marker)
    else:
        # Fallback: append before the report section
        marker2 = "# ── Report"
        if marker2 in content:
            content = content.replace(marker2, endpoint_code + "\n" + marker2)
        else:
            content += endpoint_code

    with open(finance_py, 'w') as f:
        f.write(content)
    print('  ✓ Added apply-category endpoint to finance routes')
else:
    print('  ⏭ apply-category endpoint already exists')

# ── 2. Deploy updated Transactions.jsx ───────────────────────
patch.deploy_file(
    'opt/mythos/web/frontend/src/pages/finance/Transactions.jsx',
    '/opt/mythos/web/frontend/src/pages/finance/Transactions.jsx'
)

# ── 3. Rebuild React frontend ───────────────────────────────
result = subprocess.run(
    ['npm', 'run', 'build'],
    cwd='/opt/mythos/web/frontend',
    capture_output=True, text=True, timeout=120,
)
if result.returncode == 0:
    print('  ✓ React frontend rebuilt')
else:
    print(f'  ⚠ Build output: {result.stdout[-500:] if result.stdout else ""}')
    print(f'  ⚠ Build errors: {result.stderr[-500:] if result.stderr else ""}')

# ── 4. Restart API ───────────────────────────────────────────
patch.restart_service('mythos-api.service')

patch.finish()
