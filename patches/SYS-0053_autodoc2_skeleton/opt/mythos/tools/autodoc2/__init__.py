"""
AutoDoc2 — multi-language codebase documentation engine.

Crawls a target directory, parses every supported file via tree-sitter,
and writes structural facts to Neo4j + markdown summaries to disk.

Architecture:
  cli.py            -- argparse entry point
  config.py         -- env file + CLI arg loading
  filters.py        -- skip rules, extension -> language mapping
  walker.py         -- LanguageWalker base class + dispatch helpers
  walkers/          -- one file per language, registered in walkers/__init__.py
  engine.py         -- AutodocEngine: orchestrates crawl, dispatch, writes
  neo4j_writer.py   -- all Neo4j write logic (isolated)
  markdown_writer.py-- all markdown output logic (isolated)
  llm_client.py     -- Ollama interaction (isolated)

Phase 1 ships: skeleton + Python walker.
Phase 2 adds: javascript_walker, typescript_walker.
Phase 3 adds: sql, php, go, bash, yaml walkers.
"""

__version__ = "2.0.0-phase1"
