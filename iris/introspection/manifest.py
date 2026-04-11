"""
Manifest writer - stores scan results in Postgres system_manifest table.
"""

import json
import logging
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger("iris.introspection.manifest")

DB_NAME = "mythos"


def get_connection():
    """Connect to the mythos Postgres database."""
    return psycopg2.connect(dbname=DB_NAME)


def create_run(conn, mode: str = "full", target_path: str = None) -> str:
    """Create an introspection_runs record and return the run_id."""
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO introspection_runs (mode, target_path)
               VALUES (%s, %s)
               RETURNING run_id""",
            (mode, target_path),
        )
        run_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Created introspection run: {run_id}")
        return str(run_id)


def finish_run(conn, run_id: str, stats: dict, status: str = "completed",
               error_message: str = None, report: dict = None):
    """Update the run record with final stats."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE introspection_runs
               SET finished_at = now(),
                   files_scanned = %s,
                   components_found = %s,
                   llm_analyses = %s,
                   queue_tasks = %s,
                   status = %s,
                   error_message = %s,
                   report_json = %s
               WHERE run_id = %s::uuid""",
            (
                stats.get("files_scanned", 0),
                stats.get("components_found", 0),
                stats.get("llm_analyses", 0),
                stats.get("queue_tasks", 0),
                status,
                error_message,
                json.dumps(report) if report else None,
                run_id,
            ),
        )
        conn.commit()


def write_manifest(conn, run_id: str, file_list: list[dict]):
    """Bulk-insert all scanned file metadata into system_manifest."""
    if not file_list:
        return

    columns = [
        "run_id", "file_path", "component", "file_type", "size_bytes",
        "line_count", "last_modified", "git_tracked", "functions", "classes",
        "imports", "tables_referenced", "llm_summary", "llm_purpose",
        "llm_dependencies", "llm_issues", "content_hash",
    ]

    rows = []
    for f in file_list:
        rows.append((
            run_id,
            f.get("file_path", ""),
            f.get("component"),
            f.get("file_type"),
            f.get("size_bytes"),
            f.get("line_count"),
            f.get("last_modified"),
            f.get("git_tracked", False),
            json.dumps(f.get("functions", [])),
            json.dumps(f.get("classes", [])),
            json.dumps(f.get("imports", [])),
            json.dumps(f.get("tables_referenced", [])),
            f.get("llm_summary"),
            f.get("llm_purpose"),
            json.dumps(f.get("llm_dependencies", [])),
            json.dumps(f.get("llm_issues", [])),
            f.get("content_hash"),
        ))

    with conn.cursor() as cur:
        insert_sql = f"""
            INSERT INTO system_manifest ({', '.join(columns)})
            VALUES %s
            ON CONFLICT (run_id, file_path) DO UPDATE SET
                component = EXCLUDED.component,
                llm_summary = EXCLUDED.llm_summary,
                llm_purpose = EXCLUDED.llm_purpose,
                llm_dependencies = EXCLUDED.llm_dependencies,
                llm_issues = EXCLUDED.llm_issues,
                content_hash = EXCLUDED.content_hash,
                updated_at = now()
        """
        template = "(" + ", ".join(["%s"] * len(columns)) + ")"
        execute_values(cur, insert_sql, rows, template=template)
        conn.commit()

    logger.info(f"Wrote {len(rows)} manifest entries for run {run_id}")
