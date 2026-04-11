"""
Module: integrity/__init__.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.1.0)
Purpose: Mythos Integrity System — file cataloging, function extraction,
         table introspection, and health checking against Neo4j graph.
Introduced: Patch 0171
Last Modified: Patch 0171

The integrity system is Iris's immune system. It catalogs every file,
function, service, and table as a node in Neo4j, then detects anomalies
by comparing disk reality against graph truth.

Usage:
  /opt/mythos/.venv/bin/python3 -m integrity scan          # full scan
  /opt/mythos/.venv/bin/python3 -m integrity scan --files   # files only
  /opt/mythos/.venv/bin/python3 -m integrity scan --funcs   # functions only
  /opt/mythos/.venv/bin/python3 -m integrity scan --tables  # tables only
"""
