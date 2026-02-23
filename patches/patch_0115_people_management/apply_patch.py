#!/usr/bin/env python3
"""
Patch 0115: People Management
Adds /app/people/ route, /api/people/* API, nav links, home card.
"""

import os
import sys
import shutil
import py_compile

MYTHOS = '/opt/mythos'
PATCH_DIR = os.path.dirname(os.path.abspath(__file__))


def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def backup(path):
    if os.path.exists(path):
        bak = path + '.bak_0115'
        shutil.copy2(path, bak)
        print(f"  📦 Backed up {path}")
        return bak
    return None


def safe_replace(filepath, old, new, label=""):
    with open(filepath, 'r') as f:
        content = f.read()
    if old not in content:
        fail(f"Expected string not found in {filepath}: {label or old[:60]}")
    if content.count(old) > 1:
        print(f"  ⚠️  Multiple matches for '{label}' in {filepath}, replacing first only")
        content = content.replace(old, new, 1)
    else:
        content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"  ✏️  Updated {filepath}: {label}")


def copy_file(src_rel, dest):
    src = os.path.join(PATCH_DIR, src_rel)
    if not os.path.exists(src):
        fail(f"Patch file not found: {src}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    print(f"  📄 Installed {dest}")


def main():
    print("=" * 60)
    print("Patch 0115: People Management")
    print("=" * 60)

    # ── 1. Copy new files ──
    print("\n[1/5] Installing new files...")
    copy_file('opt/mythos/api/routes/people.py', f'{MYTHOS}/api/routes/people.py')
    copy_file('opt/mythos/web/templates/people.html', f'{MYTHOS}/web/templates/people.html')

    # ── 2. Register people router in main.py ──
    print("\n[2/5] Registering API routes...")
    main_py = f'{MYTHOS}/api/main.py'
    backup(main_py)

    with open(main_py, 'r') as f:
        content = f.read()

    # Add import
    if 'from api.routes.people import' not in content:
        safe_replace(main_py,
            'from api.routes.ontology import router as ontology_router',
            'from api.routes.ontology import router as ontology_router\nfrom api.routes.people import router as people_router',
            'add people import')
    else:
        print("  ℹ️  People import already exists")

    # Add router include
    with open(main_py, 'r') as f:
        content = f.read()
    if 'app.include_router(people_router)' not in content:
        safe_replace(main_py,
            'app.include_router(ontology_router)',
            'app.include_router(ontology_router)\napp.include_router(people_router)',
            'add people router')
    else:
        print("  ℹ️  People router already registered")

    # ── 3. Register web route ──
    print("\n[3/5] Adding web route...")
    web_py = f'{MYTHOS}/api/routes/web.py'
    backup(web_py)

    with open(web_py, 'r') as f:
        content = f.read()

    if '/app/people/' not in content:
        # Add route after ontology route
        route_block = '''
# People
@router.get("/people/", response_class=HTMLResponse)
@router.get("/people", response_class=HTMLResponse)
async def people_page(request: Request):
    return serve('people.html')
'''
        if '# Ontology' in content:
            safe_replace(web_py,
                '# Registry',
                route_block + '\n# Registry',
                'add people web route')
        elif '# Registry' in content:
            safe_replace(web_py,
                '# Registry',
                route_block + '\n# Registry',
                'add people web route (fallback)')
        else:
            # Append before last line
            with open(web_py, 'a') as f:
                f.write(route_block)
            print("  ✏️  Appended people route to web.py")
    else:
        print("  ℹ️  People web route already exists")

    # ── 4. Update navigation across templates ──
    print("\n[4/5] Updating navigation bars...")

    # Templates that need nav updates - add People between Finance and Ontology
    nav_templates = {
        'home.html': {
            'old': '<a href="/app/ontology/">Ontology</a>',
            'new': '<a href="/app/people/">People</a>\n    <a href="/app/ontology/">Ontology</a>',
        },
        'dashboard.html': {
            'old': '<a href="/app/ontology/">Ontology</a>',
            'new': '<a href="/app/people/">People</a>\n      <a href="/app/ontology/">Ontology</a>',
        },
        'system.html': {
            'old': '<a href="/app/system/" class="active">System</a>',
            'new': '<a href="/app/people/">People</a>\n    <a href="/app/ontology/">Ontology</a>\n    <a href="/app/system/" class="active">System</a>',
            'check': '<a href="/app/people/">People</a>',  # skip if already present
        },
        'sessions.html': {
            'old': '<a href="/app/sessions/" class="active">Sessions</a>',
            'new': '<a href="/app/people/">People</a><a href="/app/ontology/">Ontology</a><a href="/app/system/">System</a>\n    <a href="/app/sessions/" class="active">Sessions</a>',
            'check': '<a href="/app/people/">People</a>',
        },
        'registry.html': {
            'old': '<a href="/app/registry/" class="active">Registry</a>',
            'new': '<a href="/app/people/">People</a><a href="/app/ontology/">Ontology</a><a href="/app/system/">System</a>\n    <a href="/app/sessions/">Sessions</a><a href="/app/registry/" class="active">Registry</a>',
            'check': '<a href="/app/people/">People</a>',
        },
    }

    for tpl_name, spec in nav_templates.items():
        tpl_path = f'{MYTHOS}/web/templates/{tpl_name}'
        if not os.path.exists(tpl_path):
            print(f"  ⚠️  Template not found: {tpl_name}, skipping")
            continue

        backup(tpl_path)

        with open(tpl_path, 'r') as f:
            content = f.read()

        # Skip if already has People link
        check_str = spec.get('check', '<a href="/app/people/">People</a>')
        if check_str in content:
            print(f"  ℹ️  {tpl_name} already has People nav")
            continue

        if spec['old'] not in content:
            print(f"  ⚠️  Nav anchor not found in {tpl_name}, skipping nav update")
            continue

        safe_replace(tpl_path, spec['old'], spec['new'], f'{tpl_name} nav')

    # Handle ontology.html separately (might have different nav structure)
    ontology_path = f'{MYTHOS}/web/templates/ontology.html'
    if os.path.exists(ontology_path):
        backup(ontology_path)
        with open(ontology_path, 'r') as f:
            content = f.read()
        if '<a href="/app/people/">People</a>' not in content:
            if '<a href="/app/ontology/"' in content:
                # Insert People before Ontology
                safe_replace(ontology_path,
                    '<a href="/app/ontology/"',
                    '<a href="/app/people/">People</a>\n    <a href="/app/ontology/"',
                    'ontology.html nav')
            else:
                print("  ⚠️  Could not find nav anchor in ontology.html")
        else:
            print("  ℹ️  ontology.html already has People nav")

    # ── 5. Add People card to home page ──
    print("\n[5/5] Adding People card to home page...")
    home_path = f'{MYTHOS}/web/templates/home.html'

    with open(home_path, 'r') as f:
        content = f.read()

    if 'section-card people' not in content:
        # Add people card before the sessions card (which has class "sessions")
        people_card = '''    <a href="/app/people/" class="section-card people">
      <span class="card-icon">👤</span>
      <div class="card-head"><h2 class="card-title">People</h2><span class="card-tag tag-live">live</span></div>
      <p class="card-desc">Contact directory — identities, birth data, lineage notes, and spiritual connections for everyone in the Mythos field.</p>
      <div class="card-stats">
        <div class="card-stat"><div class="stat-label">People</div><div class="stat-value" id="ppl-total">—</div></div>
        <div class="card-stat"><div class="stat-label">With DOB</div><div class="stat-value" id="ppl-dob">—</div></div>
        <div class="card-stat"><div class="stat-label">Status</div><div class="stat-value" style="color:var(--green)">Active</div></div>
      </div>
    </a>
'''
        if 'section-card sessions' in content:
            safe_replace(home_path,
                '    <a href="/app/sessions/" class="section-card sessions">',
                people_card + '    <a href="/app/sessions/" class="section-card sessions">',
                'home page people card')
        else:
            print("  ⚠️  Could not find sessions card anchor in home.html")

        # Add CSS for people card color
        if '.section-card.people' not in content:
            with open(home_path, 'r') as f:
                content = f.read()
            safe_replace(home_path,
                ".section-card.registry::before { background: linear-gradient(90deg, var(--gold), transparent); }",
                ".section-card.registry::before { background: linear-gradient(90deg, var(--gold), transparent); }\n.section-card.people::before { background: linear-gradient(90deg, #f43f5e, transparent); }\n.section-card.people .card-title { color: #f43f5e; }",
                'people card CSS')

        # Add JS to fetch people stats
        with open(home_path, 'r') as f:
            content = f.read()
        if "ppl-total" in content and "/api/people/stats" not in content:
            safe_replace(home_path,
                "fetch('/api/finance/bills')",
                "fetch('/api/people/stats').then(r=>r.json()).then(d=>{document.getElementById('ppl-total').textContent=d.total;document.getElementById('ppl-dob').textContent=d.with_dob;}).catch(()=>{});\nfetch('/api/finance/bills')",
                'people stats fetch')
    else:
        print("  ℹ️  People card already exists on home page")

    # ── Verify ──
    print("\n[Verify] Syntax checking Python files...")
    for pyfile in [
        f'{MYTHOS}/api/routes/people.py',
        f'{MYTHOS}/api/main.py',
        f'{MYTHOS}/api/routes/web.py',
    ]:
        try:
            py_compile.compile(pyfile, doraise=True)
            print(f"  ✅ {pyfile}")
        except py_compile.PyCompileError as e:
            fail(f"Syntax error in {pyfile}: {e}")

    # ── Restart services ──
    print("\n[Restart] Restarting API service...")
    os.system('sudo systemctl restart mythos-api.service')

    import time
    time.sleep(2)
    ret = os.system('systemctl is-active --quiet mythos-api.service')
    if ret != 0:
        print("  ❌ API service failed to start! Check logs:")
        os.system('journalctl -u mythos-api.service -n 20 --no-pager')
        fail("Service restart failed")
    else:
        print("  ✅ mythos-api.service is active")

    print("\n" + "=" * 60)
    print("✅ Patch 0115 applied successfully!")
    print("   → /app/people/ — People directory")
    print("   → /api/people/* — People API (list, get, create, update, delete)")
    print("   → Nav updated across all templates")
    print("   → Home page card added")
    print("=" * 60)


if __name__ == '__main__':
    main()
