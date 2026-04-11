"""
Handler for architecture documentation queue tasks.
Generates docs/generated/architecture/{name}.md
"""
import os
import json
import logging
import psycopg2

from iris.docs.llm import call_llm, build_architecture_prompt

logger = logging.getLogger("iris.docs.handlers.architecture")

DOCS_DIR = "/opt/mythos/docs/generated/architecture"


def handle(task, dry_run=False):
    """
    Process an architecture_entry task.
    Returns (success: bool, output_path: str or None)
    """
    component = task.get("component", "unknown")
    logger.info(f"Generating architecture entry: {component}")

    os.makedirs(DOCS_DIR, exist_ok=True)

    files_data = _get_component_files(component)
    if not files_data:
        logger.warning(f"No manifest data for '{component}'")
        files_data = []

    component_summary = task.get("purpose", "")

    if dry_run:
        logger.info(f"[DRY RUN] Would generate architecture/{component}.md from {len(files_data)} files")
        return True, None

    prompt = build_architecture_prompt(component, files_data, component_summary)
    content = call_llm(prompt)

    if not content:
        logger.error(f"LLM returned empty for architecture '{component}'")
        return False, None

    output_path = os.path.join(DOCS_DIR, f"{component}.md")
    with open(output_path, "w") as f:
        f.write(content)
        f.write("\n")

    logger.info(f"Wrote {output_path}")
    return True, output_path


def _get_component_files(component):
    """Pull file metadata from the latest introspection run."""
    try:
        conn = psycopg2.connect(dbname="mythos")
        with conn.cursor() as cur:
            cur.execute(
                """SELECT run_id FROM introspection_runs
                   WHERE status = 'completed'
                   ORDER BY finished_at DESC LIMIT 1"""
            )
            row = cur.fetchone()
            if not row:
                return []

            run_id = row[0]
            cur.execute(
                """SELECT file_path, file_type, line_count, size_bytes,
                          llm_summary, llm_purpose, llm_dependencies, llm_issues
                   FROM system_manifest
                   WHERE run_id = %s AND component = %s
                   ORDER BY file_path""",
                (str(run_id), component),
            )
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.warning(f"Could not fetch manifest for {component}: {e}")
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass
