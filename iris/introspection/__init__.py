"""
Iris Introspection Scanner - Patch 0187
Self-analysis system: scans codebase, LLM-analyzes components,
stores manifest in Postgres, enriches Neo4j graph, dispatches
documentation tasks to Redis queues.
"""

from iris.introspection.run import run_introspection

__all__ = ["run_introspection"]
