#!/usr/bin/env python3
"""
Pipeline Logger
================
Records every pipeline run, LLM call, and query to Postgres.
Full prompt state captured so any response can be replayed.

Usage:
    from pipeline_logger import PipelineLogger
    logger = PipelineLogger()
    run_uuid = logger.start_run(speaker, message, gap, path, registry_version)
    logger.log_llm_call(run_uuid, stage, model, temp, system_prompt, user_prompt, ...)
    logger.log_query(run_uuid, source_type, intent, query_text, ...)
    logger.finish_run(run_uuid, iris_response, total_elapsed_ms, perception, discovery)
"""

import json
import uuid
import psycopg2
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger("pipeline_logger")


class PipelineLogger:
    def __init__(self, dbname="mythos", user="adge"):
        self.dbname = dbname
        self.user = user

    def _conn(self):
        return psycopg2.connect(dbname=self.dbname, user=self.user)

    def start_run(self, speaker, message, gap_description,
                  processing_path, registry_version,
                  perception_model=None, iris_model=None):
        """Create a new pipeline run. Returns run_uuid."""
        run_uuid = str(uuid.uuid4())
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pipeline_runs
                    (run_uuid, speaker, message, gap_description,
                     processing_path, registry_version,
                     perception_model, iris_model)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (run_uuid, speaker, message, gap_description,
                  processing_path, registry_version,
                  perception_model, iris_model))
            conn.commit()
            cur.close()
            conn.close()
            return run_uuid
        except Exception as e:
            log.error(f"Failed to start run: {e}")
            return run_uuid  # return uuid anyway so pipeline continues

    def log_llm_call(self, run_uuid, stage, model, temperature,
                     system_prompt, user_prompt, prompt_components,
                     raw_response, parsed_response, elapsed_ms,
                     parse_success=True):
        """Log an individual LLM call within a run."""
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pipeline_llm_calls
                    (run_uuid, stage, model, temperature,
                     system_prompt, user_prompt, prompt_components,
                     raw_response, parsed_response, elapsed_ms,
                     parse_success)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (run_uuid, stage, model, temperature,
                  system_prompt, user_prompt,
                  json.dumps(prompt_components) if prompt_components else None,
                  raw_response,
                  json.dumps(parsed_response) if parsed_response else None,
                  elapsed_ms, parse_success))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Failed to log LLM call: {e}")

    def log_query(self, run_uuid, source_type, intent, query_text,
                  validated=False, validator_approved=None,
                  corrected_query=None, risk_level=None,
                  rows_returned=None, result_summary=None,
                  elapsed_ms=None, priority=None):
        """Log a DISCOVERY query."""
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pipeline_queries
                    (run_uuid, source_type, intent, query_text,
                     validated, validator_approved, corrected_query,
                     risk_level, rows_returned, result_summary,
                     elapsed_ms, priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (run_uuid, source_type, intent, query_text,
                  validated, validator_approved, corrected_query,
                  risk_level, rows_returned, result_summary,
                  elapsed_ms, priority))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Failed to log query: {e}")

    def finish_run(self, run_uuid, iris_response, total_elapsed_ms, processing_path=None,
                   perception=None, discovery=None):
        """Update the run with final results."""
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE pipeline_runs SET
                    processing_path = %s,
                    iris_response = %s,
                    total_elapsed_ms = %s,
                    perception = %s,
                    discovery = %s
                WHERE run_uuid = %s
            """, (processing_path, iris_response, total_elapsed_ms,
                  json.dumps(perception) if perception else None,
                  json.dumps(discovery, default=str) if discovery else None,
                  run_uuid))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Failed to finish run: {e}")

    def recent_runs(self, limit=10):
        """Fetch recent pipeline runs for inspection."""
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT created_at, speaker, LEFT(message, 60),
                       processing_path, total_elapsed_ms,
                       perception->>'message_type',
                       registry_version,
                       LEFT(iris_response, 80)
                FROM pipeline_runs
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            log.error(f"Failed to fetch runs: {e}")
            return []


if __name__ == "__main__":
    logger = PipelineLogger()
    runs = logger.recent_runs(10)
    if runs:
        print(f"{'Time':<20} {'Speaker':<15} {'Message':<40} {'Path':<10} {'ms':>6}")
        print("-" * 95)
        for r in runs:
            print(f"{str(r[0]):<20} {r[1]:<15} {r[2]:<40} {r[3] or '?':<10} {r[4] or 0:>6}")
    else:
        print("No pipeline runs yet. Run the orchestrator to generate some.")
