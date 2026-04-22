import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=91,
    description='autodoc2 graph coverage gate — post-patch Neo4j verification',
    patch_type='MINOR',
)
patch.begin()

# ── Inject step_verify_graph_coverage() into post_install.py ─────────────────
# Inserts a new function before run_pipeline(), then wires it in as step 1.5
# (runs after integrity scan, before git commit).
# Uses direct neo4j driver — does NOT import integrity.graph which is crashing.
# Non-fatal: missing files are warned, not errored. Gate becomes fatal once
# the integrity.graph crash loop is resolved (tracked in REQUESTS.md).

NEW_FUNCTION = '''
def step_verify_graph_coverage(files_deployed):
    """Verify that deployed files appear as active IntegrityFile nodes in Neo4j.

    SYS-0091: Graph coverage gate. Runs after integrity scan, before git commit.
    Uses the neo4j driver directly — does NOT import integrity.graph which has
    a known crash loop (mythos-obs-graph.service). Non-fatal: warns on missing
    files but does not block the patch. Will be made fatal once the crash loop
    is resolved.

    Returns (ok, report_dict).
    """
    print("  ⟳ Graph coverage check...")
    if not files_deployed:
        print("  ✓ Graph coverage: no files deployed, skipping")
        return True, {}

    try:
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        load_dotenv('/opt/mythos/.env')
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', '')
        driver = GraphDatabase.driver(uri, auth=(user, password))

        missing = []
        found = []
        with driver.session() as session:
            for filepath in files_deployed:
                result = session.run(
                    "MATCH (f:IntegrityFile {path: $path, status: 'active'}) "
                    "RETURN f.path AS path LIMIT 1",
                    path=filepath,
                )
                record = result.single()
                if record:
                    found.append(filepath)
                else:
                    missing.append(filepath)
        driver.close()

        total = len(files_deployed)
        n_found = len(found)
        n_missing = len(missing)

        if n_missing == 0:
            print(f"  ✓ Graph coverage: {n_found}/{total} deployed files verified in Neo4j")
            return True, {'found': n_found, 'missing': 0, 'total': total}
        else:
            print(f"  ⚠ Graph coverage: {n_found}/{total} verified, {n_missing} missing from graph:")
            for m in missing[:5]:
                print(f"      ⚠ not in graph: {m}")
            if len(missing) > 5:
                print(f"      ... and {len(missing) - 5} more")
            print("    (Non-fatal — integrity.graph crash loop tracked in REQUESTS.md)")
            return False, {'found': n_found, 'missing': n_missing, 'total': total,
                           'missing_paths': missing}

    except ImportError:
        print("  ⊘ Graph coverage: neo4j driver not available")
        return False, {'error': 'neo4j driver not installed'}
    except Exception as e:
        print(f"  ⊘ Graph coverage check failed: {e}")
        return False, {'error': str(e)}

'''

# Insert the new function just before run_pipeline()
patch.str_replace(
    '/opt/mythos/patches/scripts/post_install.py',
    old='def run_pipeline(patch_id, stream, number, description, patch_type,',
    new=NEW_FUNCTION + 'def run_pipeline(patch_id, stream, number, description, patch_type,',
)

# ── Wire step_verify_graph_coverage() into run_pipeline() ─────────────────────
# Insert it between integrity scan and git commit.

patch.str_replace(
    '/opt/mythos/patches/scripts/post_install.py',
    old=(
        '    # 2. Git commit\n'
        '    git_ok = step_git_commit(patch_id, description, files_deployed)\n'
        '    results[\'git_commit\'] = git_ok'
    ),
    new=(
        '    # 1.5. Graph coverage gate\n'
        '    coverage_ok, coverage_report = step_verify_graph_coverage(files_deployed)\n'
        '    results[\'graph_coverage\'] = coverage_ok\n'
        '\n'
        '    # 2. Git commit\n'
        '    git_ok = step_git_commit(patch_id, description, files_deployed)\n'
        '    results[\'git_commit\'] = git_ok'
    ),
)

# ── Update pipeline step count (4 → 5) in the summary line ───────────────────

patch.str_replace(
    '/opt/mythos/patches/scripts/post_install.py',
    old='    print(f"── Pipeline: {passed}/{total} steps completed ──")',
    new='    print(f"── Pipeline: {passed}/{total} steps completed ──")  # SYS-0091: 5 steps',
)

# ── Smoke test: import post_install and verify the new function exists ─────────

check = subprocess.run(
    ['/opt/mythos/.venv/bin/python3', '-c',
     'import sys; sys.path.insert(0, "/opt/mythos/patches/scripts"); '
     'import post_install; '
     'assert hasattr(post_install, "step_verify_graph_coverage"), "function missing"; '
     'import inspect; '
     'sig = inspect.signature(post_install.step_verify_graph_coverage); '
     'assert "files_deployed" in sig.parameters, "wrong signature"; '
     'print("step_verify_graph_coverage: OK")'],
    capture_output=True, text=True, timeout=15,
    cwd='/opt/mythos',
)
if check.returncode != 0:
    patch.errors.append(f"smoke test failed: {check.stderr.strip()}")
    patch.logger.log(f"  ✗ smoke test: {check.stderr.strip()}")
else:
    patch.logger.log(f"  ✓ {check.stdout.strip()}")

patch.finish()
