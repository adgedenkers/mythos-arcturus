#!/usr/bin/env python3
"""
Knowledge Writer — Extracted Knowledge Persistence
===================================================
Writes Fact, Preference, Observation, Directive nodes to both
Postgres (knowledge_extractions) and Neo4j with full provenance.

Handles:
  - New knowledge creation
  - Dedup detection (same fact from different nodes = confirmation)
  - Supersession (corrected facts mark old ones as superseded)
  - Neo4j sync (Postgres is source of truth, Neo4j is projection)

Usage:
    writer = KnowledgeWriter()
    extraction_id = writer.write(
        exchange_id="exchange-abc123",
        manifest_id=42,
        node="beacon",
        layer=1,
        version="1.0",
        knowledge_type="fact",
        subject="electric bill",
        content="Electric bill paid for March 2026",
        domain="finance",
        significance=4,
        confidence=0.95,
    )
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger('grid.knowledge_writer')

# Neo4j — optional, degrades gracefully
try:
    from neo4j import GraphDatabase
    _neo4j_available = True
except ImportError:
    _neo4j_available = False

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


class KnowledgeWriter:
    """Writes extracted knowledge to Postgres and Neo4j."""

    def __init__(self):
        self._neo4j_driver = None
        if _neo4j_available:
            try:
                self._neo4j_driver = GraphDatabase.driver(
                    NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
                )
                self._neo4j_driver.verify_connectivity()
                logger.info("KnowledgeWriter: Neo4j connected")
            except Exception as e:
                logger.warning(f"KnowledgeWriter: Neo4j not available: {e}")
                self._neo4j_driver = None

    def write(
        self,
        exchange_id: str,
        manifest_id: int,
        node: str,
        layer: int,
        version: str,
        knowledge_type: str,
        content: str,
        subject: str = None,
        domain: str = None,
        significance: int = 1,
        confidence: float = 1.0,
    ) -> Optional[str]:
        """
        Write a single knowledge extraction to Postgres and Neo4j.
        Returns the extraction_id (UUID) if successful.

        Before creating a new node, checks for existing similar extractions
        to either confirm (bump confidence) or create new.
        """
        # Check for dedup / confirmation opportunity
        existing = self._find_similar(content, subject, knowledge_type)

        if existing:
            # Same knowledge already extracted — confirm it
            return self._confirm_existing(
                existing_id=existing['extraction_id'],
                node=node,
                version=version,
                exchange_id=exchange_id,
            )

        # New knowledge — create it
        return self._create_new(
            exchange_id=exchange_id,
            manifest_id=manifest_id,
            node=node,
            layer=layer,
            version=version,
            knowledge_type=knowledge_type,
            content=content,
            subject=subject,
            domain=domain,
            significance=significance,
            confidence=confidence,
        )

    def write_batch(self, extractions: List[Dict]) -> List[str]:
        """Write multiple extractions. Returns list of extraction_ids."""
        ids = []
        for ext in extractions:
            eid = self.write(**ext)
            if eid:
                ids.append(eid)
        return ids

    def supersede(self, old_extraction_id: str, new_extraction_id: str) -> bool:
        """
        Mark an old extraction as superseded by a new one.
        The old node stays in the graph with status='superseded'.
        """
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE knowledge_extractions
                SET status = 'superseded', superseded_by = %s, updated_at = NOW()
                WHERE extraction_id = %s AND status = 'active'
            """, (new_extraction_id, old_extraction_id))
            conn.commit()
            cur.close()
            conn.close()

            # Update Neo4j
            if self._neo4j_driver:
                try:
                    with self._neo4j_driver.session() as session:
                        session.run("""
                            MATCH (old {extraction_id: $old_id})
                            MATCH (new {extraction_id: $new_id})
                            SET old.status = 'superseded'
                            MERGE (old)-[:SUPERSEDED_BY]->(new)
                        """, old_id=old_extraction_id, new_id=new_extraction_id)
                except Exception as e:
                    logger.warning(f"Neo4j supersede failed (non-fatal): {e}")

            logger.info(f"Knowledge superseded: {old_extraction_id[:16]} → {new_extraction_id[:16]}")
            return True
        except Exception as e:
            logger.error(f"Supersede failed: {e}")
            return False

    def get_unsynced(self, limit: int = 50) -> List[Dict]:
        """Get extractions not yet synced to Neo4j."""
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM knowledge_extractions
                WHERE neo4j_synced = false AND status = 'active'
                ORDER BY created_at
                LIMIT %s
            """, (limit,))
            results = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Unsynced query failed: {e}")
            return []

    def get_pending_notifications(self, limit: int = 10) -> List[Dict]:
        """Get significant extractions that haven't been confirmed via Telegram."""
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT extraction_id, knowledge_type, subject, content,
                       domain, significance, node, created_at
                FROM knowledge_extractions
                WHERE notification_sent = false
                  AND significance >= 4
                  AND status = 'active'
                ORDER BY significance DESC, created_at
                LIMIT %s
            """, (limit,))
            results = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Pending notifications query failed: {e}")
            return []

    def mark_notified(self, extraction_id: str) -> bool:
        """Mark an extraction as notified via Telegram."""
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE knowledge_extractions
                SET notification_sent = true, notification_sent_at = NOW()
                WHERE extraction_id = %s
            """, (extraction_id,))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Mark notified failed: {e}")
            return False

    # ── Internal Methods ─────────────────────────────────────────────

    def _find_similar(self, content: str, subject: str, knowledge_type: str) -> Optional[Dict]:
        """
        Check if we already have this knowledge (dedup).
        Uses content similarity + subject match.
        Only matches active extractions.
        """
        try:
            conn = _get_conn()
            cur = conn.cursor()
            # Simple dedup: exact content match + same type + same subject
            cur.execute("""
                SELECT extraction_id, content, confirmed_count, confidence
                FROM knowledge_extractions
                WHERE knowledge_type = %s
                  AND status = 'active'
                  AND LOWER(content) = LOWER(%s)
                  AND (subject IS NULL AND %s IS NULL OR LOWER(subject) = LOWER(%s))
                LIMIT 1
            """, (knowledge_type, content, subject, subject))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Dedup check failed: {e}")
            return None

    def _confirm_existing(self, existing_id: str, node: str,
                           version: str, exchange_id: str) -> str:
        """Bump confirmed_count on an existing extraction."""
        try:
            conn = _get_conn()
            cur = conn.cursor()

            # Add confirmation source
            cur.execute("""
                UPDATE knowledge_extractions
                SET confirmed_count = confirmed_count + 1,
                    confidence = LEAST(1.0, confidence + 0.1),
                    confirmation_sources = confirmation_sources || %s::jsonb,
                    status = 'confirmed',
                    updated_at = NOW()
                WHERE extraction_id = %s
                RETURNING extraction_id
            """, (
                Json([{'node': node, 'version': version, 'exchange_id': exchange_id}]),
                existing_id,
            ))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            if row:
                logger.debug(f"Knowledge confirmed: {existing_id[:16]} (+1 from {node})")
                return str(row['extraction_id'])
            return existing_id
        except Exception as e:
            logger.error(f"Confirm existing failed: {e}")
            return existing_id

    def _create_new(
        self,
        exchange_id: str,
        manifest_id: int,
        node: str,
        layer: int,
        version: str,
        knowledge_type: str,
        content: str,
        subject: str = None,
        domain: str = None,
        significance: int = 1,
        confidence: float = 1.0,
    ) -> Optional[str]:
        """Create a new knowledge extraction in Postgres + Neo4j."""
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO knowledge_extractions (
                    exchange_id, manifest_id, node, layer, version,
                    knowledge_type, subject, content, domain,
                    confidence, significance,
                    confirmation_sources
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s::jsonb
                ) RETURNING extraction_id
            """, (
                exchange_id, manifest_id, node, layer, version,
                knowledge_type, subject, content, domain,
                confidence, significance,
                Json([{'node': node, 'version': version, 'exchange_id': exchange_id}]),
            ))
            row = cur.fetchone()
            conn.commit()
            extraction_id = str(row['extraction_id'])

            # Write to Neo4j
            neo4j_id = self._write_neo4j(
                extraction_id=extraction_id,
                exchange_id=exchange_id,
                knowledge_type=knowledge_type,
                content=content,
                subject=subject,
                domain=domain,
                significance=significance,
                confidence=confidence,
                node=node,
                layer=layer,
                version=version,
            )

            if neo4j_id:
                cur2 = conn.cursor()
                cur2.execute("""
                    UPDATE knowledge_extractions
                    SET neo4j_synced = true, neo4j_synced_at = NOW(), neo4j_node_id = %s
                    WHERE extraction_id = %s
                """, (neo4j_id, extraction_id))
                conn.commit()
                cur2.close()

            cur.close()
            conn.close()

            logger.info(
                f"Knowledge created: [{knowledge_type}] {content[:60]}... "
                f"(sig={significance}, node={node}, neo4j={'✓' if neo4j_id else '✗'})"
            )
            return extraction_id
        except Exception as e:
            logger.error(f"Create knowledge failed: {e}")
            return None

    def _write_neo4j(
        self,
        extraction_id: str,
        exchange_id: str,
        knowledge_type: str,
        content: str,
        subject: str,
        domain: str,
        significance: int,
        confidence: float,
        node: str,
        layer: int,
        version: str,
    ) -> Optional[str]:
        """Write a knowledge node to Neo4j. Returns element ID."""
        if not self._neo4j_driver:
            return None

        # Map knowledge_type to Neo4j label
        label_map = {
            'fact': 'Fact',
            'preference': 'Preference',
            'observation': 'Observation',
            'directive': 'Directive',
        }
        label = label_map.get(knowledge_type, 'Fact')

        try:
            with self._neo4j_driver.session() as session:
                # Create the knowledge node
                result = session.run(f"""
                    CREATE (k:{label} {{
                        extraction_id: $extraction_id,
                        content: $content,
                        subject: $subject,
                        domain: $domain,
                        significance: $significance,
                        confidence: $confidence,
                        extracted_by_node: $node,
                        extracted_by_layer: $layer,
                        extracted_by_version: $version,
                        status: 'active',
                        created_at: datetime()
                    }})
                    RETURN elementId(k) as eid
                """, extraction_id=extraction_id, content=content,
                     subject=subject or '', domain=domain or '',
                     significance=significance, confidence=confidence,
                     node=node, layer=layer, version=version)
                record = result.single()
                neo4j_id = record['eid'] if record else None

                # Link to the Exchange that produced it
                if neo4j_id:
                    session.run("""
                        MATCH (k {extraction_id: $extraction_id})
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (k)-[:EXTRACTED_FROM]->(e)
                    """, extraction_id=extraction_id, exchange_id=exchange_id)

                    # Link to Person/Entity if subject matches known people
                    if subject:
                        subject_lower = subject.lower()
                        person_map = {
                            'adge': 'PE-KaTuarEl', "ka'tuar'el": 'PE-KaTuarEl',
                            'adriaan': 'PE-KaTuarEl',
                            'seraphe': 'PE-Seraphe', 'rebecca': 'PE-Seraphe',
                            'becky': 'PE-Seraphe',
                            'fitz': 'PE-Fitz',
                        }
                        canonical_id = person_map.get(subject_lower)
                        if canonical_id:
                            session.run("""
                                MATCH (k {extraction_id: $extraction_id})
                                MATCH (p {canonical_id: $cid})
                                MERGE (k)-[:ABOUT]->(p)
                            """, extraction_id=extraction_id, cid=canonical_id)

                return neo4j_id
        except Exception as e:
            logger.warning(f"Neo4j knowledge write failed (non-fatal): {e}")
            return None

    def close(self):
        """Close Neo4j driver."""
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
