#!/usr/bin/env python3
"""
Mythos Graph Bridge — Neo4j query helpers for the mission executor.

Provides high-level functions for querying the Integrity graph
and other Neo4j labels. Used by mission files and by the executor
to gather structural context about the Mythos codebase.

Usage as CLI:
    graph-bridge functions /opt/mythos/assistants/chat_assistant.py
    graph-bridge deps /opt/mythos/assistants/chat_assistant.py
    graph-bridge search-func query
    graph-bridge tables
    graph-bridge snapshot [output_path]

Usage in Python:
    from graph_bridge import GraphBridge
    gb = GraphBridge()
    funcs = gb.functions_in_file('/opt/mythos/assistants/chat_assistant.py')
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional


def _load_credentials() -> tuple[str, str, str]:
    """Load Neo4j credentials from /opt/mythos/.env"""
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = None

    env_path = Path("/opt/mythos/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            if line.startswith("NEO4J_URI="):
                uri = line.split("=", 1)[1]
            elif line.startswith("NEO4J_USER="):
                user = line.split("=", 1)[1]
            elif line.startswith("NEO4J_PASSWORD="):
                password = line.split("=", 1)[1]

    if not password:
        raise RuntimeError("NEO4J_PASSWORD not found in /opt/mythos/.env")

    return uri, user, password


class GraphBridge:
    """High-level Neo4j query interface for the Mythos codebase graph."""

    def __init__(self):
        from neo4j import GraphDatabase
        uri, user, password = _load_credentials()
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def query(self, cypher: str, **params) -> list[dict]:
        """Run a Cypher query and return results as list of dicts."""
        with self._driver.session() as session:
            result = session.run(cypher, **params)
            return [dict(record) for record in result]

    # ------------------------------------------------------------------
    # File queries
    # ------------------------------------------------------------------

    def functions_in_file(self, path: str) -> list[str]:
        """Get all function names defined in a file."""
        rows = self.query(
            "MATCH (f:IntegrityFile {path: $path})-[:CONTAINS]->(fn:IntegrityFunction) "
            "RETURN fn.name as name ORDER BY fn.name",
            path=path,
        )
        return [r["name"] for r in rows]

    def file_dependencies(self, path: str) -> list[str]:
        """Get all files that a file imports."""
        rows = self.query(
            "MATCH (f:IntegrityFile {path: $path})-[:IMPORTS]->(dep:IntegrityFile) "
            "RETURN dep.path as path ORDER BY dep.path",
            path=path,
        )
        return [r["path"] for r in rows]

    def file_dependents(self, path: str) -> list[str]:
        """Get all files that import this file."""
        rows = self.query(
            "MATCH (dep:IntegrityFile)-[:IMPORTS]->(f:IntegrityFile {path: $path}) "
            "RETURN dep.path as path ORDER BY dep.path",
            path=path,
        )
        return [r["path"] for r in rows]

    def files_in_directory(self, directory: str, extension: str = None) -> list[dict]:
        """Get all files in a directory with their metadata."""
        cypher = (
            "MATCH (f:IntegrityFile) "
            "WHERE f.directory = $directory "
        )
        if extension:
            cypher += "AND f.extension = $extension "
        cypher += "RETURN f.path as path, f.filename as filename, f.size_bytes as size ORDER BY f.filename"
        return self.query(cypher, directory=directory, extension=extension)

    def file_info(self, path: str) -> Optional[dict]:
        """Get full metadata for a file."""
        rows = self.query(
            "MATCH (f:IntegrityFile {path: $path}) "
            "RETURN f.path as path, f.filename as filename, f.directory as directory, "
            "f.extension as extension, f.size_bytes as size, f.sha256 as sha256, "
            "f.last_modified as last_modified, f.status as status",
            path=path,
        )
        return rows[0] if rows else None

    def files_calling_function(self, function_name: str) -> list[str]:
        """Find files that contain a specific function."""
        rows = self.query(
            "MATCH (f:IntegrityFile)-[:CONTAINS]->(fn:IntegrityFunction {name: $name}) "
            "RETURN f.path as path ORDER BY f.path",
            name=function_name,
        )
        return [r["path"] for r in rows]

    def recently_modified_files(self, limit: int = 20) -> list[dict]:
        """Get the most recently modified files."""
        return self.query(
            "MATCH (f:IntegrityFile) WHERE f.hash_changed = true "
            "RETURN f.path as path, f.last_modified as modified, f.size_bytes as size "
            "ORDER BY f.last_modified DESC LIMIT $limit",
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Table / Schema queries
    # ------------------------------------------------------------------

    def table_columns(self, table_name: str) -> list[dict]:
        """Get columns for a Postgres table from the graph."""
        return self.query(
            "MATCH (t:IntegrityTable {name: $name})-[:HAS_COLUMN]->(c:IntegrityColumn) "
            "RETURN c.name as column, c.data_type as type ORDER BY c.name",
            name=table_name,
        )

    def all_tables(self) -> list[str]:
        """Get all table names."""
        rows = self.query(
            "MATCH (t:IntegrityTable) RETURN t.name as name ORDER BY t.name"
        )
        return [r["name"] for r in rows]

    def tables_for_service(self, service_name: str) -> list[str]:
        """Find which tables a service touches (via file relationships)."""
        rows = self.query(
            "MATCH (s:IntegrityService {name: $name})-[:RUNS]->(f:IntegrityFile)"
            "-[:REFERENCES]->(t:IntegrityTable) "
            "RETURN DISTINCT t.name as name ORDER BY t.name",
            name=service_name,
        )
        return [r["name"] for r in rows]

    # ------------------------------------------------------------------
    # Service queries
    # ------------------------------------------------------------------

    def all_services(self) -> list[dict]:
        """Get all registered services."""
        return self.query(
            "MATCH (s:IntegrityService) "
            "RETURN s.name as name ORDER BY s.name"
        )

    def service_files(self, service_name: str) -> list[str]:
        """Get files associated with a service."""
        rows = self.query(
            "MATCH (s:IntegrityService {name: $name})-[:RUNS]->(f:IntegrityFile) "
            "RETURN f.path as path ORDER BY f.path",
            name=service_name,
        )
        return [r["path"] for r in rows]

    # ------------------------------------------------------------------
    # Cross-reference queries
    # ------------------------------------------------------------------

    def search_functions(self, pattern: str) -> list[dict]:
        """Search for functions by name pattern."""
        return self.query(
            "MATCH (f:IntegrityFile)-[:CONTAINS]->(fn:IntegrityFunction) "
            "WHERE fn.name CONTAINS $pattern "
            "RETURN fn.name as function, f.path as file "
            "ORDER BY fn.name LIMIT 50",
            pattern=pattern,
        )

    def search_files(self, pattern: str) -> list[dict]:
        """Search for files by path pattern."""
        return self.query(
            "MATCH (f:IntegrityFile) "
            "WHERE f.path CONTAINS $pattern "
            "RETURN f.path as path, f.size_bytes as size "
            "ORDER BY f.path LIMIT 50",
            pattern=pattern,
        )

    def directory_tree(self, root: str, depth: int = 2) -> list[str]:
        """Get directory tree starting from a root."""
        rows = self.query(
            "MATCH (d:IntegrityDirectory) "
            "WHERE d.path STARTS WITH $root "
            "RETURN d.path as path ORDER BY d.path",
            root=root,
        )
        # Filter by depth
        root_depth = root.rstrip("/").count("/")
        return [r["path"] for r in rows if r["path"].rstrip("/").count("/") <= root_depth + depth]

    # ------------------------------------------------------------------
    # Graph snapshot (for Claude refresh)
    # ------------------------------------------------------------------

    def export_snapshot(self, output_path: str = "/tmp/mythos-graph-snapshot.json"):
        """Export a structural snapshot for Claude to consume.

        Produces a complete JSON summary of the Mythos codebase:
        - Node counts per label
        - All directories with file and function counts
        - All tables with column counts
        - All services
        - Hub files (most imported)
        - Key files with their function lists
        - Recently changed files
        - Stream patch counters
        """
        from datetime import datetime

        snapshot = {
            "generated": datetime.now().isoformat(),
            "stats": {},
            "directories": [],
            "tables": [],
            "services": [],
            "hub_files": [],
            "key_files": [],
            "recent_changes": [],
            "stream_status": {},
        }

        # Stats — node counts
        for label in ["IntegrityFile", "IntegrityFunction", "IntegrityDirectory",
                       "IntegrityTable", "IntegrityColumn", "IntegrityService"]:
            rows = self.query(f"MATCH (n:{label}) RETURN count(n) as c")
            snapshot["stats"][label] = rows[0]["c"] if rows else 0

        # Directories with file and function counts
        dirs = self.query(
            "MATCH (f:IntegrityFile) "
            "OPTIONAL MATCH (f)-[:CONTAINS]->(fn:IntegrityFunction) "
            "WITH f.directory as dir, count(DISTINCT f) as files, count(fn) as functions "
            "RETURN dir, files, functions "
            "ORDER BY files DESC"
        )
        snapshot["directories"] = dirs

        # All tables with column counts
        tables = self.query(
            "MATCH (t:IntegrityTable) "
            "OPTIONAL MATCH (t)-[:HAS_COLUMN]->(c:IntegrityColumn) "
            "RETURN t.name as table_name, count(c) as columns "
            "ORDER BY t.name"
        )
        snapshot["tables"] = tables

        # Services
        services = self.query(
            "MATCH (s:IntegrityService) "
            "OPTIONAL MATCH (s)-[:RUNS]->(f:IntegrityFile) "
            "RETURN s.name as service, collect(f.path) as files "
            "ORDER BY s.name"
        )
        snapshot["services"] = services

        # Hub files — most imported (top 30)
        hubs = self.query(
            "MATCH (dep:IntegrityFile)-[:IMPORTS]->(f:IntegrityFile) "
            "WITH f.path as path, count(dep) as imported_by "
            "RETURN path, imported_by "
            "ORDER BY imported_by DESC LIMIT 30"
        )
        snapshot["hub_files"] = hubs

        # Key files with function lists (files with most functions, top 40)
        key_files = self.query(
            "MATCH (f:IntegrityFile)-[:CONTAINS]->(fn:IntegrityFunction) "
            "WITH f.path as path, collect(fn.name) as functions, count(fn) as func_count "
            "RETURN path, functions, func_count "
            "ORDER BY func_count DESC LIMIT 40"
        )
        snapshot["key_files"] = key_files

        # Recently changed files
        snapshot["recent_changes"] = self.recently_modified_files(30)

        # Stream counters from STREAMS.json
        streams_path = Path("/opt/mythos/docs/STREAMS.json")
        if streams_path.exists():
            try:
                streams_data = json.loads(streams_path.read_text())
                for name, info in streams_data.get("streams", {}).items():
                    snapshot["stream_status"][name] = {
                        "next_patch": info.get("next_patch"),
                        "domain": info.get("domain", ""),
                    }
            except Exception:
                snapshot["stream_status"] = {"error": "could not parse STREAMS.json"}

        Path(output_path).write_text(json.dumps(snapshot, indent=2, default=str))
        return output_path


# ---------------------------------------------------------------------------
# CLI interface for quick queries
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  graph-bridge functions <file_path>    # List functions in a file")
        print("  graph-bridge deps <file_path>         # Files this file imports")
        print("  graph-bridge dependents <file_path>   # Files that import this file")
        print("  graph-bridge search-func <pattern>    # Search functions by name")
        print("  graph-bridge search-file <pattern>    # Search files by path")
        print("  graph-bridge tables                   # List all tables")
        print("  graph-bridge columns <table_name>     # List columns for a table")
        print("  graph-bridge services                 # List all services")
        print("  graph-bridge snapshot [output_path]   # Export full snapshot for Claude")
        sys.exit(1)

    cmd = sys.argv[1]

    with GraphBridge() as gb:
        if cmd == "functions" and len(sys.argv) > 2:
            for f in gb.functions_in_file(sys.argv[2]):
                print(f)

        elif cmd == "deps" and len(sys.argv) > 2:
            for d in gb.file_dependencies(sys.argv[2]):
                print(d)

        elif cmd == "dependents" and len(sys.argv) > 2:
            for d in gb.file_dependents(sys.argv[2]):
                print(d)

        elif cmd == "search-func" and len(sys.argv) > 2:
            for r in gb.search_functions(sys.argv[2]):
                print(f"  {r['function']:40s}  {r['file']}")

        elif cmd == "search-file" and len(sys.argv) > 2:
            for r in gb.search_files(sys.argv[2]):
                print(f"  {r['path']}")

        elif cmd == "tables":
            for t in gb.all_tables():
                print(t)

        elif cmd == "columns" and len(sys.argv) > 2:
            for c in gb.table_columns(sys.argv[2]):
                print(f"  {c['column']:30s}  {c.get('type', '?')}")

        elif cmd == "services":
            for s in gb.all_services():
                print(s["name"])

        elif cmd == "snapshot":
            out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/mythos-graph-snapshot.json"
            path = gb.export_snapshot(out)
            stats = json.loads(Path(path).read_text())["stats"]
            print(f"Snapshot written to {path}")
            print(f"  {stats.get('IntegrityFile', 0)} files, "
                  f"{stats.get('IntegrityFunction', 0)} functions, "
                  f"{stats.get('IntegrityTable', 0)} tables, "
                  f"{stats.get('IntegrityService', 0)} services")

        else:
            print(f"Unknown command: {cmd}")
            print("Run 'graph-bridge' with no arguments for usage.")
            sys.exit(1)
