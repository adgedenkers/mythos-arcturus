#!/usr/bin/env python3
"""
Seed Neo4j with AppRegistry nodes.
Run once after patch install, or anytime to re-sync.

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/scripts/seed_app_registry.py
"""

import os
import sys

# Add mythos root to path
sys.path.insert(0, '/opt/mythos')

from neo4j import GraphDatabase
from core.app_registry import AppRegistry


def main():
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')

    print(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        # Verify connection
        with driver.session() as session:
            result = session.run("RETURN 1 AS ok")
            result.single()
        print("✓ Connected to Neo4j")

        # Seed registry
        registry = AppRegistry(neo4j_driver=driver)
        registry.seed_neo4j()
        print("✓ AppRegistry nodes seeded")

        # Run audit
        print("\n" + registry.format_audit_report(include_orphans=True))

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        driver.close()


if __name__ == '__main__':
    main()
