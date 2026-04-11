#!/usr/bin/env python3
"""
Manifest Writer — Grid Processing Provenance
=============================================
Records every node-layer activation (or skip) for every exchange
processed by the Arcturian Grid. This is the audit trail.

Usage:
    writer = ManifestWriter()

    # Record an activation
    manifest_id = writer.record_activation(
        exchange_id="exchange-abc123",
        conversation_id="chat-xyz",
        user_uuid="d01f9f28-...",
        node="beacon",
        layer=1,
        version="1.0",
        activation_score=85,
        output_summary="Extracted: electric bill paid, USAA balance update",
        extracted_count=2,
        processing_ms=340,
        model_used="qwen3:30b-a3b",
    )

    # Record a skip (node didn't fire)
    writer.record_skip(
        exchange_id="exchange-abc123",
        node="glyph",
        layer=1,
        version="1.0",
        activation_score=12,
        skipped_reason="score below threshold (12/30)",
    )
"""

import os
import hashlib
import logging
from typing import Optional, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger('grid.manifest_writer')


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


class ManifestWriter:
    """Records grid processing manifest entries to Postgres."""

    def record_activation(
        self,
        exchange_id: str,
        node: str,
        layer: int,
        version: str,
        conversation_id: str = None,
        user_uuid: str = None,
        prompt_hash: str = None,
        activation_score: int = None,
        depth_gate: int = None,
        input_content: str = None,
        output_summary: str = None,
        extracted_count: int = 0,
        output_json: Dict = None,
        processing_ms: int = None,
        model_used: str = None,
    ) -> Optional[int]:
        """
        Record that a node-layer activated and processed an exchange.
        Returns the manifest row ID.
        """
        input_hash = None
        input_chars = None
        if input_content:
            input_hash = hashlib.sha256(input_content.encode()).hexdigest()[:16]
            input_chars = len(input_content)

        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO grid_processing_manifest (
                    exchange_id, conversation_id, user_uuid,
                    node, layer, version, prompt_hash,
                    activated, activation_score, depth_gate,
                    input_hash, input_chars,
                    output_summary, extracted_count, output_json,
                    processing_ms, model_used
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    true, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s
                ) RETURNING id
            """, (
                exchange_id, conversation_id, user_uuid,
                node, layer, version, prompt_hash,
                activation_score, depth_gate,
                input_hash, input_chars,
                output_summary, extracted_count,
                Json(output_json) if output_json else None,
                processing_ms, model_used,
            ))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            manifest_id = row['id'] if row else None
            logger.debug(
                f"Manifest: recorded {node} L{layer} v{version} for {exchange_id[:16]}... "
                f"({extracted_count} extractions, {processing_ms}ms)"
            )
            return manifest_id
        except Exception as e:
            logger.error(f"Manifest write failed: {e}")
            return None

    def record_skip(
        self,
        exchange_id: str,
        node: str,
        layer: int,
        version: str,
        conversation_id: str = None,
        user_uuid: str = None,
        activation_score: int = None,
        skipped_reason: str = None,
    ) -> Optional[int]:
        """
        Record that a node-layer was considered but did NOT activate.
        Preserves the routing decision for audit.
        """
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO grid_processing_manifest (
                    exchange_id, conversation_id, user_uuid,
                    node, layer, version,
                    activated, activation_score, skipped_reason
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    false, %s, %s
                ) RETURNING id
            """, (
                exchange_id, conversation_id, user_uuid,
                node, layer, version,
                activation_score, skipped_reason,
            ))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return row['id'] if row else None
        except Exception as e:
            logger.error(f"Manifest skip-write failed: {e}")
            return None

    def record_legacy_activation(
        self,
        exchange_id: str,
        grid_scores: Dict[str, int],
        conversation_id: str = None,
        user_uuid: str = None,
        processing_ms: int = None,
        model_used: str = None,
    ) -> int:
        """
        Record the existing flat grid analysis as a Layer 0 (legacy) manifest entry.
        This bridges the old grid worker output into the manifest system.
        One row per node, layer=0 (pre-layered analysis).
        Returns count of rows written.
        """
        count = 0
        for node in ['anchor', 'echo', 'beacon', 'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway']:
            score = grid_scores.get(node, 0)
            try:
                conn = _get_conn()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO grid_processing_manifest (
                        exchange_id, conversation_id, user_uuid,
                        node, layer, version,
                        activated, activation_score,
                        processing_ms, model_used,
                        output_summary
                    ) VALUES (
                        %s, %s, %s,
                        %s, 0, 'legacy',
                        %s, %s,
                        %s, %s,
                        %s
                    )
                """, (
                    exchange_id, conversation_id, user_uuid,
                    node,
                    score > 0, score,
                    processing_ms, model_used,
                    f"Legacy flat analysis: score={score}",
                ))
                conn.commit()
                cur.close()
                conn.close()
                count += 1
            except Exception as e:
                logger.error(f"Legacy manifest write failed for {node}: {e}")
        return count

    def get_exchange_manifest(self, exchange_id: str) -> list:
        """
        Get the full processing manifest for an exchange.
        Returns all node-layer activations and skips, ordered by node then layer.
        """
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT node, layer, version, activated, skipped_reason,
                       activation_score, depth_gate, extracted_count,
                       output_summary, processing_ms, model_used, processed_at
                FROM grid_processing_manifest
                WHERE exchange_id = %s
                ORDER BY node, layer
            """, (exchange_id,))
            results = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Manifest query failed: {e}")
            return []

    def get_processing_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get processing statistics for the last N hours."""
        try:
            conn = _get_conn()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    COUNT(*) as total_activations,
                    COUNT(DISTINCT exchange_id) as unique_exchanges,
                    COUNT(*) FILTER (WHERE activated = true) as fired,
                    COUNT(*) FILTER (WHERE activated = false) as skipped,
                    SUM(extracted_count) FILTER (WHERE activated = true) as total_extractions,
                    AVG(processing_ms) FILTER (WHERE activated = true) as avg_ms,
                    MAX(processed_at) as last_processed
                FROM grid_processing_manifest
                WHERE processed_at > NOW() - INTERVAL '%s hours'
            """, (hours,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Stats query failed: {e}")
            return {}
