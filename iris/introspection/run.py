"""
Orchestrator - runs the full introspection pipeline:
scan -> analyze -> manifest -> graph -> queue -> report
"""
import os
import sys
import logging
import json
from neo4j import GraphDatabase

logger = logging.getLogger("iris.introspection.run")

def _load_env():
    """Load /opt/mythos/.env if present."""
    env_file = os.path.join(os.environ.get("MYTHOS_ROOT", "/opt/mythos"), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

def run_introspection(
    base_path="/opt/mythos",
    target_path=None,
    quick=False,
    report_only=False,
    queue_status_only=False,
):
    """
    Main entry point for Iris introspection.

    Args:
        base_path: Root of the Mythos codebase
        target_path: Optional single component path to scan
        quick: Skip LLM analysis
        report_only: Only generate report from last run
        queue_status_only: Only show queue status
    """
    _load_env()

    from iris.introspection.scanner import scan_directory, group_by_component
    from iris.introspection.analyzer import analyze_file, analyze_component
    from iris.introspection.manifest import get_connection, create_run, finish_run, write_manifest
    from iris.introspection.graph_enricher import enrich_graph
    from iris.introspection.queue_dispatcher import dispatch_tasks, get_queue_status
    from iris.introspection.report import generate_report, format_report_text

    # Handle queue-status-only mode
    if queue_status_only:
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            status = get_queue_status(r)
            print(json.dumps(status, indent=2))
        except Exception as e:
            print(f"Error getting queue status: {e}")
        return

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    mode = "quick" if quick else ("single_component" if target_path else "full")
    logger.info(f"Starting introspection: mode={mode}, target={target_path or 'all'}")

    # Connect to Postgres
    conn = get_connection()
    run_id = create_run(conn, mode=mode, target_path=target_path)

    stats = {"files_scanned": 0, "components_found": 0, "llm_analyses": 0, "queue_tasks": 0}

    try:
        # Phase 1: Scan
        logger.info("Phase 1: Scanning filesystem...")
        file_list = scan_directory(base_path=base_path, target_path=target_path)
        component_groups = group_by_component(file_list)
        stats["files_scanned"] = len(file_list)
        stats["components_found"] = len(component_groups)
        logger.info(f"Found {len(file_list)} files in {len(component_groups)} components")

        # Check git tracking
        try:
            import subprocess
            git_files = set(
                subprocess.check_output(
                    ["git", "-C", base_path, "ls-files"],
                    text=True
                ).strip().split("\n")
            )
            for f in file_list:
                rel = f["file_path"].replace(base_path + "/", "")
                f["git_tracked"] = rel in git_files
        except Exception:
            logger.warning("Could not check git tracking status")

        # Phase 2: LLM Analysis (skip if --quick)
        component_analyses = {}
        if not quick:
            logger.info("Phase 2: LLM analysis...")
            analyzed = 0
            for f in file_list:
                if f.get("file_type") in ("py", "sh", "sql", "yaml", "yml"):
                    result = analyze_file(f)
                    f.update(result)
                    if result.get("llm_summary"):
                        analyzed += 1
            stats["llm_analyses"] = analyzed
            logger.info(f"LLM analyzed {analyzed} files")

            # Component-level analysis
            for comp_name, comp_files in component_groups.items():
                component_analyses[comp_name] = analyze_component(comp_name, comp_files)
        else:
            logger.info("Phase 2: Skipped (quick mode)")

        # Phase 3: Write manifest to Postgres
        logger.info("Phase 3: Writing manifest to Postgres...")
        write_manifest(conn, run_id, file_list)

        # Phase 4: Enrich Neo4j graph
        neo4j_rels = 0
        try:
            neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
            neo4j_pass = os.environ.get("NEO4J_PASSWORD", "")
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
            logger.info("Phase 4: Enriching Neo4j graph...")
            neo4j_rels = enrich_graph(driver, run_id, file_list, component_groups)
            driver.close()
        except ImportError:
            logger.warning("Phase 4: neo4j driver not installed, skipping")
        except Exception as e:
            logger.warning(f"Phase 4: Neo4j enrichment failed: {e}")

        # Phase 5: Dispatch Redis queue tasks
        queue_tasks = 0
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            logger.info("Phase 5: Dispatching queue tasks...")
            queue_tasks = dispatch_tasks(r, component_groups, file_list, component_analyses)
            stats["queue_tasks"] = queue_tasks
        except ImportError:
            logger.warning("Phase 5: redis not installed, skipping")
        except Exception as e:
            logger.warning(f"Phase 5: Redis dispatch failed: {e}")

        # Phase 6: Generate report
        logger.info("Phase 6: Generating report...")
        report = generate_report(
            run_id, file_list, component_groups,
            component_analyses, queue_tasks, neo4j_rels
        )
        finish_run(conn, run_id, stats, status="completed", report=report)

        # Output
        print(format_report_text(report))
        logger.info(f"Introspection complete: run_id={run_id}")
        return report

    except Exception as e:
        logger.error(f"Introspection failed: {e}")
        finish_run(conn, run_id, stats, status="failed", error_message=str(e))
        raise
    finally:
        conn.close()
