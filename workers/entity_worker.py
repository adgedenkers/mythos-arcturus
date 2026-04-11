#!/usr/bin/env python3
"""
Entity Resolution Worker

Resolves entities mentioned in messages to canonical forms.
Creates/updates entities in Neo4j and tracks mentions in TimescaleDB.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.entity")

# Known aliases for entity resolution
KNOWN_ALIASES = {
    # People
    "rebecca": "seraphe",
    "becca": "seraphe",
    "seraphe": "seraphe",
    "ka": "kataurel",
    "adge": "kataurel",
    "adriaan": "kataurel",
    "fitz": "fitz",
    # Concepts
    "merovingian": "merovingian_bloodline",
    "merovingians": "merovingian_bloodline",
}


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def get_neo4j():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "")
        )
    )


def resolve_entity(name: str, entity_type: str) -> str:
    """Resolve entity name to canonical form"""
    name_lower = name.lower().strip()
    
    if name_lower in KNOWN_ALIASES:
        return KNOWN_ALIASES[name_lower]
    
    # Default: lowercase, replace spaces with underscores
    return name_lower.replace(" ", "_").replace("-", "_")


def create_or_update_entity(driver, canonical_id: str, name: str, entity_type: str) -> str:
    """Create or update entity in Neo4j"""
    
    # Map to proper Neo4j label
    label_map = {
        "person": "Person",
        "people": "Person",
        "place": "Place",
        "places": "Place",
        "concept": "Concept",
        "concepts": "Concept",
        "symbol": "Symbol",
        "symbols": "Symbol"
    }
    label = label_map.get(entity_type.lower(), "Entity")
    
    with driver.session() as session:
        result = session.run(f"""
            MERGE (e:{label} {{canonical_id: $canonical_id}})
            ON CREATE SET
                e.name = $name,
                e.created_at = datetime(),
                e.mention_count = 1
            ON MATCH SET
                e.mention_count = COALESCE(e.mention_count, 0) + 1,
                e.last_mentioned = datetime()
            RETURN e.canonical_id as id
        """, canonical_id=canonical_id, name=name)
        
        record = result.single()
        return record["id"] if record else None


def store_entity_mention(user_uuid: str, conversation_id: str, message_id: int,
                        canonical_id: str, name: str, entity_type: str) -> None:
    """Store entity mention in TimescaleDB"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO entity_mention_timeseries (
                time, user_uuid, conversation_id, message_id,
                entity_canonical_id, entity_name, entity_type
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s)
        """, (user_uuid, conversation_id, message_id, canonical_id, name, entity_type))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.warning(f"Failed to store entity mention: {e}")
    finally:
        cur.close()
        conn.close()


def process_entity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for entity resolution worker"""
    
    message_id = payload.get("message_id")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    entities = payload.get("entities", {})
    
    if not entities:
        return {"status": "skipped", "message_id": message_id, "reason": "no_entities"}
    
    logger.info(f"Resolving entities for message {message_id}")
    
    driver = get_neo4j()
    resolved_count = 0
    
    try:
        for entity_type, names in entities.items():
            if not isinstance(names, list):
                continue
                
            for name in names:
                if not name or not isinstance(name, str):
                    continue
                    
                # Resolve to canonical form
                canonical_id = resolve_entity(name, entity_type)
                
                # Create/update in Neo4j
                create_or_update_entity(driver, canonical_id, name, entity_type)
                
                # Store mention in TimescaleDB
                store_entity_mention(
                    user_uuid, conversation_id, message_id,
                    canonical_id, name, entity_type
                )
                
                resolved_count += 1
                logger.debug(f"Resolved: {name} -> {canonical_id} ({entity_type})")
        
        return {
            "status": "success",
            "message_id": message_id,
            "entities_resolved": resolved_count
        }
        
    except Exception as e:
        logger.exception(f"Entity resolution failed: {e}")
        return {"status": "failed", "message_id": message_id, "error": str(e)}
    finally:
        driver.close()
