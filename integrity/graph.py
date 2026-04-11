"""
Module: integrity/graph.py
Biological System: iris-immune (Immune System)
Subsystem: mythos-integrity (v0.1.0)
Purpose: Neo4j connection helper and constraint setup for integrity system.
Introduced: Patch 0171
Last Modified: Patch 0171

Dependencies:
  - neo4j Python driver
  - /opt/mythos/.env for credentials
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


def get_driver():
    """Get a Neo4j driver instance."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def ensure_constraints(driver):
    """
    Create constraints and indexes for integrity node types.
    Uses CREATE ... IF NOT EXISTS so it's safe to run repeatedly.
    """
    constraints = [
        # Unique constraints (also create indexes)
        "CREATE CONSTRAINT file_path_unique IF NOT EXISTS FOR (f:IntegrityFile) REQUIRE f.path IS UNIQUE",
        "CREATE CONSTRAINT func_id_unique IF NOT EXISTS FOR (fn:IntegrityFunction) REQUIRE fn.uid IS UNIQUE",
        "CREATE CONSTRAINT dir_path_unique IF NOT EXISTS FOR (d:IntegrityDirectory) REQUIRE d.path IS UNIQUE",
        "CREATE CONSTRAINT table_name_unique IF NOT EXISTS FOR (t:IntegrityTable) REQUIRE t.full_name IS UNIQUE",
        "CREATE CONSTRAINT column_id_unique IF NOT EXISTS FOR (c:IntegrityColumn) REQUIRE c.uid IS UNIQUE",
        # Indexes for common lookups
        "CREATE INDEX file_status_idx IF NOT EXISTS FOR (f:IntegrityFile) ON (f.status)",
        "CREATE INDEX file_extension_idx IF NOT EXISTS FOR (f:IntegrityFile) ON (f.extension)",
        "CREATE INDEX func_name_idx IF NOT EXISTS FOR (fn:IntegrityFunction) ON (fn.name)",
        "CREATE INDEX dir_path_idx IF NOT EXISTS FOR (d:IntegrityDirectory) ON (d.path)",
    ]

    with driver.session() as session:
        for cypher in constraints:
            try:
                session.run(cypher)
            except Exception as e:
                # Log but don't fail — constraint may already exist in different form
                print(f"  ⚠️  Constraint warning: {e}")


def run_query(driver, cypher, parameters=None, **kwargs):
    """Run a single Cypher query and return records. Accepts params as dict or kwargs."""
    p = parameters if parameters is not None else kwargs
    with driver.session() as session:
        result = session.run(cypher, **p)
        return [record.data() for record in result]


def run_write(driver, cypher, parameters=None, **kwargs):
    """Run a single write Cypher query. Accepts params as dict or kwargs."""
    p = parameters if parameters is not None else kwargs
    with driver.session() as session:
        session.run(cypher, **p)
