import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=1,
    description='chart_pipeline_birth_time_sourcing',
    patch_type='MAJOR',
)
patch.begin()

# ── Deploy new file ──────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/astrology/chart_pipeline.py',
    '/opt/mythos/astrology/chart_pipeline.py',
)

# ── Modify person_researcher.py — add chart generation to deep research ──

pr_path = '/opt/mythos/iris/core/src/person_researcher.py'

with open(pr_path, 'r') as f:
    content = f.read()

# Add chart generation step after astro computation in run_deep_research
old_astro_block = '''        # ── Layer 2: Astro (noon chart if time unknown) ──
        astro_summary = None
        if record.has_birth_data:
            astro_summary = _compute_astro(record)
            if astro_summary:
                dossier_parts.append(f"## Astrological Profile\\n{astro_summary}")'''

new_astro_block = '''        # ── Layer 1.5: Source birth time from astrotheme if missing ──
        chart_dir = None
        try:
            sys.path.insert(0, "/opt/mythos")
            from astrology.chart_pipeline import source_birth_time_and_chart
            chart_dir = source_birth_time_and_chart(
                db_config, person_id, record.first_name, record.last_name
            )
            if chart_dir:
                log.info(f"Chart generated at: {chart_dir}")
                # Reload record in case birth time was updated
                cur2 = conn.cursor()
                cur2.execute("SELECT time_of_birth FROM people WHERE id = %s", (person_id,))
                refreshed = cur2.fetchone()
                cur2.close()
                if refreshed and refreshed.get("time_of_birth"):
                    record.time_of_birth = str(refreshed["time_of_birth"])
        except Exception as e:
            log.warning(f"Chart pipeline failed (non-fatal): {e}")

        # ── Layer 2: Astro (noon chart if time unknown) ──
        astro_summary = None
        if record.has_birth_data:
            astro_summary = _compute_astro(record)
            if astro_summary:
                dossier_parts.append(f"## Astrological Profile\\n{astro_summary}")
                if chart_dir:
                    dossier_parts.append(f"Chart files: {chart_dir}")'''

assert old_astro_block in content, f"FAILED: astro block not found in {pr_path}"
content = content.replace(old_astro_block, new_astro_block, 1)

with open(pr_path, 'w') as f:
    f.write(content)

# ── Validate syntax ──────────────────────────────────────────────────

import py_compile
py_compile.compile(pr_path, doraise=True)
py_compile.compile('/opt/mythos/astrology/chart_pipeline.py', doraise=True)
print("✓ All Python files pass syntax check")

patch.finish()
