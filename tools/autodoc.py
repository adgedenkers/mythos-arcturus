#!/usr/bin/env python3
"""
Mythos Autodoc Engine
=====================
Crawls the entire /opt/mythos codebase, analyzes every file using AST parsing
and Ollama LLM calls, builds a Neo4j knowledge graph with :Autodoc labels,
and produces comprehensive markdown documentation.

Usage:
    autodoc                     # Full run
    autodoc --resume            # Resume interrupted run
    autodoc --reindex           # Rebuild Neo4j graph only (no LLM)
    autodoc --synthesize        # Run synthesis passes only
    autodoc --clean             # Wipe autodoc graph + docs, start fresh
    autodoc --status            # Show progress stats

Models:
    - qwen2.5:32b    → per-file code analysis
    - iris-deep      → synthesis (stream/system overviews)

Output:
    /opt/mythos/docs/autodoc/
    Neo4j :Autodoc nodes
"""

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MYTHOS_ROOT = Path("/opt/mythos")
AUTODOC_DIR = MYTHOS_ROOT / "docs" / "autodoc"
STATE_FILE = AUTODOC_DIR / ".autodoc_state.json"
MODULES_DIR = AUTODOC_DIR / "modules"
STREAMS_DIR = AUTODOC_DIR / "streams"
FILES_DIR = AUTODOC_DIR / "files"

OLLAMA_URL = "http://localhost:11434"
ANALYSIS_MODEL = "qwen2.5:32b"
SYNTHESIS_MODEL = "iris-deep"

# Neo4j
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

# Load from .env if not in environment
ENV_FILE = MYTHOS_ROOT / ".env"
if ENV_FILE.exists() and not NEO4J_PASSWORD:
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("NEO4J_PASSWORD="):
                NEO4J_PASSWORD = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("NEO4J_URI=") and NEO4J_URI == "bolt://localhost:7687":
                NEO4J_URI = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("NEO4J_USER=") and NEO4J_USER == "neo4j":
                NEO4J_USER = line.split("=", 1)[1].strip().strip('"').strip("'")

# Directories / patterns to skip
SKIP_DIRS = {
    ".venv", ".git", "node_modules", "__pycache__", ".mypy_cache",
    ".pytest_cache", "patches", "archive", ".tox", ".eggs", "*.egg-info",
    "dist", "build", ".next", "coverage",
}

SKIP_FILES = {
    ".pyc", ".pyo", ".so", ".o", ".a", ".dylib",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp", ".tiff",
    ".mp3", ".mp4", ".wav", ".flac", ".ogg", ".avi", ".mkv", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".eot",
    ".db", ".sqlite", ".sqlite3",
    ".lock",
}

# File types we care about
CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".sh", ".bash",
    ".sql", ".cypher", ".cql",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".txt", ".rst",
    ".html", ".css", ".scss",
    ".service", ".timer", ".env", ".env.example",
    "Dockerfile", "Makefile", ".gitignore",
}

# Stream mapping hints (directory → stream)
STREAM_MAP = {
    "neuro": "NEU", "iris": "NEU",
    "skills": "LOG", "orchestrator": "LOG", "prompts": "LOG", "triad": "LOG",
    "voice_memos": "MNE", "memory": "MNE",
    "astrology": "SEN", "sensus": "SEN",
    "finance": "SYS", "workers": "SYS", "integrity": "SYS",
    "telegram_bot": "SYS", "patches": "SYS", "tools": "SYS",
    "docs": "SYS", "migrations": "SYS", "config": "SYS",
    "assistants": "LOG", "api": "SYS",
}

# Module grouping (directory → module name)
MODULE_MAP = {
    "telegram_bot": "Telegram Bot",
    "finance": "Finance System",
    "astrology": "Astrology Engine",
    "skills": "Skill Engine",
    "orchestrator": "LLM Orchestrator",
    "prompts": "Prompt System",
    "triad": "Triad Identity System",
    "neuro": "NEURO / Consciousness Processing",
    "iris": "Iris Core",
    "voice_memos": "Voice Memo Pipeline",
    "workers": "Background Workers",
    "integrity": "Integrity Scanner",
    "patches": "Patch System",
    "tools": "Tools",
    "docs": "Documentation",
    "migrations": "Database Migrations",
    "assistants": "Chat Assistants",
    "api": "FastAPI Gateway",
    "config": "Configuration",
}


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------

def file_hash(path: Path) -> str:
    """SHA-256 of file contents."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def relative_path(path: Path) -> str:
    """Path relative to MYTHOS_ROOT."""
    try:
        return str(path.relative_to(MYTHOS_ROOT))
    except ValueError:
        return str(path)


def should_skip_dir(dirname: str, dirpath: Path) -> bool:
    """Check if directory should be skipped."""
    if dirname in SKIP_DIRS:
        return True
    rel = relative_path(dirpath / dirname)
    for skip in SKIP_DIRS:
        if skip in rel:
            return True
    return False


def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped."""
    ext = filepath.suffix.lower()
    if ext in SKIP_FILES:
        return True
    name = filepath.name
    if name.startswith(".") and ext not in CODE_EXTENSIONS:
        return True
    # Skip very large files (> 500KB probably binary or data)
    try:
        if filepath.stat().st_size > 500_000:
            return True
    except OSError:
        return True
    return False


def is_documentable(filepath: Path) -> bool:
    """Check if file is one we should document."""
    ext = filepath.suffix.lower()
    name = filepath.name
    return ext in CODE_EXTENSIONS or name in {"Dockerfile", "Makefile", ".gitignore", "Procfile"}


def guess_stream(filepath: Path) -> str:
    """Guess which stream a file belongs to based on its path."""
    rel = relative_path(filepath)
    parts = Path(rel).parts
    if len(parts) > 0:
        top = parts[0]
        if top in STREAM_MAP:
            return STREAM_MAP[top]
    return "SYS"  # default


def guess_module(filepath: Path) -> str:
    """Guess which module a file belongs to."""
    rel = relative_path(filepath)
    parts = Path(rel).parts
    if len(parts) > 0:
        top = parts[0]
        if top in MODULE_MAP:
            return MODULE_MAP[top]
    return "Root / Miscellaneous"


def guess_language(filepath: Path) -> str:
    """Determine file language/type."""
    ext = filepath.suffix.lower()
    name = filepath.name
    lang_map = {
        ".py": "python", ".js": "javascript", ".jsx": "react/jsx",
        ".ts": "typescript", ".tsx": "react/tsx",
        ".sh": "bash", ".bash": "bash",
        ".sql": "sql", ".cypher": "cypher", ".cql": "cypher",
        ".yaml": "yaml", ".yml": "yaml",
        ".json": "json", ".toml": "toml",
        ".ini": "ini", ".cfg": "ini", ".conf": "config",
        ".md": "markdown", ".txt": "text", ".rst": "rst",
        ".html": "html", ".css": "css", ".scss": "scss",
        ".service": "systemd", ".timer": "systemd",
        ".env": "env", ".env.example": "env",
    }
    if name == "Dockerfile":
        return "dockerfile"
    if name == "Makefile":
        return "makefile"
    return lang_map.get(ext, "unknown")


# ---------------------------------------------------------------------------
# AST Analysis (Python files)
# ---------------------------------------------------------------------------

class PythonAnalyzer:
    """Extract structural information from Python files via AST."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.imports = []
        self.from_imports = []
        self.classes = []
        self.functions = []
        self.decorators = []
        self.global_vars = []
        self.fastapi_routes = []
        self.db_references = []
        self.errors = []

    def analyze(self) -> dict:
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(self.filepath))
            self._walk(tree)
            self._find_db_refs(source)
            self._find_fastapi_routes(source)
        except SyntaxError as e:
            self.errors.append(f"SyntaxError: {e}")
        except Exception as e:
            self.errors.append(f"Error: {e}")

        return {
            "imports": self.imports,
            "from_imports": self.from_imports,
            "classes": self.classes,
            "functions": self.functions,
            "decorators": self.decorators,
            "global_vars": self.global_vars,
            "fastapi_routes": self.fastapi_routes,
            "db_references": self.db_references,
            "errors": self.errors,
        }

    def _walk(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    self.from_imports.append({
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                    })

            elif isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(ast.dump(base))
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)
                self.classes.append({
                    "name": node.name,
                    "bases": bases,
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or "",
                    "line": node.lineno,
                })

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip methods (already captured in classes)
                if not isinstance(getattr(node, '_parent', None), ast.ClassDef):
                    decos = []
                    for d in node.decorator_list:
                        if isinstance(d, ast.Name):
                            decos.append(d.id)
                        elif isinstance(d, ast.Attribute):
                            decos.append(f"{ast.dump(d)}")
                        elif isinstance(d, ast.Call):
                            if isinstance(d.func, ast.Attribute):
                                decos.append(f"{ast.dump(d.func)}")
                            elif isinstance(d.func, ast.Name):
                                decos.append(d.func.id)
                    self.functions.append({
                        "name": node.name,
                        "decorators": decos,
                        "args": [a.arg for a in node.args.args if a.arg != "self"],
                        "docstring": ast.get_docstring(node) or "",
                        "line": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    })

    def _find_db_refs(self, source: str):
        """Find database table references in source code."""
        # PostgreSQL patterns
        pg_patterns = [
            r'(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+["\']?(\w+)["\']?',
            r'execute\s*\(\s*["\'].*?(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+["\']?(\w+)',
            r'cursor\.execute.*?(?:FROM|JOIN|INTO|UPDATE)\s+(\w+)',
        ]
        for pat in pg_patterns:
            matches = re.findall(pat, source, re.IGNORECASE)
            for m in matches:
                if m.lower() not in ("select", "where", "set", "values", "and", "or"):
                    self.db_references.append({"table": m, "type": "postgres"})

        # Neo4j patterns
        neo_patterns = [
            r'MATCH\s*\(.*?:(\w+)',
            r'CREATE\s*\(.*?:(\w+)',
            r'MERGE\s*\(.*?:(\w+)',
        ]
        for pat in neo_patterns:
            matches = re.findall(pat, source, re.IGNORECASE)
            for m in matches:
                self.db_references.append({"label": m, "type": "neo4j"})

    def _find_fastapi_routes(self, source: str):
        """Find FastAPI route definitions."""
        route_patterns = [
            r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        ]
        for pat in route_patterns:
            matches = re.findall(pat, source, re.IGNORECASE)
            for method, path in matches:
                self.fastapi_routes.append({"method": method.upper(), "path": path})


# ---------------------------------------------------------------------------
# Config / Service Scanner
# ---------------------------------------------------------------------------

class SystemScanner:
    """Scan for systemd services, configs, and other system-level info."""

    @staticmethod
    def find_systemd_services() -> list:
        """Find mythos-related systemd service files."""
        services = []
        service_dirs = [
            Path("/etc/systemd/system"),
            Path("/usr/lib/systemd/system"),
        ]
        for d in service_dirs:
            if d.exists():
                for f in d.iterdir():
                    if f.name.startswith("mythos") and f.suffix in (".service", ".timer"):
                        try:
                            content = f.read_text()
                            exec_start = ""
                            for line in content.split("\n"):
                                if line.strip().startswith("ExecStart="):
                                    exec_start = line.split("=", 1)[1].strip()
                            services.append({
                                "name": f.stem,
                                "type": f.suffix[1:],
                                "path": str(f),
                                "exec_start": exec_start,
                            })
                        except Exception:
                            pass
        return services

    @staticmethod
    def find_postgres_tables() -> list:
        """Query postgres for mythos tables."""
        tables = []
        try:
            result = subprocess.run(
                ["sudo", "-u", "postgres", "psql", "-d", "mythos", "-t", "-A", "-c",
                 "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line:
                        tables.append(line)
        except Exception as e:
            print(f"  ⚠ Could not query postgres: {e}")
        return tables

    @staticmethod
    def find_neo4j_labels() -> list:
        """Query Neo4j for existing labels."""
        labels = []
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
                labels = [r["label"] for r in result]
            driver.close()
        except Exception as e:
            print(f"  ⚠ Could not query Neo4j labels: {e}")
        return labels


# ---------------------------------------------------------------------------
# Neo4j Graph Builder
# ---------------------------------------------------------------------------

class GraphBuilder:
    """Build the :Autodoc knowledge graph in Neo4j."""

    def __init__(self):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def clean(self):
        """Remove all :Autodoc nodes and relationships."""
        with self.driver.session() as s:
            s.run("MATCH (n:Autodoc) DETACH DELETE n")
        print("  ✓ Cleaned all :Autodoc nodes from Neo4j")

    def create_constraints(self):
        """Create uniqueness constraints for Autodoc nodes."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocFile) REQUIRE n.path IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocModule) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocStream) REQUIRE n.code IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocService) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocDBTable) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AutodocEndpoint) REQUIRE n.key IS UNIQUE",
        ]
        with self.driver.session() as s:
            for c in constraints:
                try:
                    s.run(c)
                except Exception:
                    pass  # constraint may already exist

    def create_streams(self):
        """Create the five stream nodes."""
        streams = {
            "NEU": "NEURO — Consciousness, awareness, Arcturian Grid",
            "LOG": "LOGOS — Knowledge, skills, prompts, orchestration",
            "MNE": "MNEMOS — Memory, voice memos, recall",
            "SEN": "SENSUS — Perception, astrology, sensory processing",
            "SYS": "SYSTEM — Infrastructure, finance, bot, patches",
        }
        with self.driver.session() as s:
            for code, desc in streams.items():
                s.run("""
                    MERGE (s:Autodoc:AutodocStream {code: $code})
                    SET s.description = $desc, s.source = 'autodoc',
                        s.updated_at = datetime()
                """, code=code, desc=desc)

    def create_file_node(self, file_info: dict):
        """Create a CodeFile node."""
        with self.driver.session() as s:
            s.run("""
                MERGE (f:Autodoc:AutodocFile {path: $path})
                SET f.language = $language,
                    f.stream = $stream,
                    f.module = $module,
                    f.size = $size,
                    f.hash = $hash,
                    f.lines = $lines,
                    f.source = 'autodoc',
                    f.updated_at = datetime()
            """, **file_info)

            # Link to stream
            s.run("""
                MATCH (f:AutodocFile {path: $path})
                MATCH (s:AutodocStream {code: $stream})
                MERGE (f)-[:BELONGS_TO_STREAM]->(s)
            """, path=file_info["path"], stream=file_info["stream"])

    def create_module_node(self, name: str, stream: str):
        """Create a Module node."""
        with self.driver.session() as s:
            s.run("""
                MERGE (m:Autodoc:AutodocModule {name: $name})
                SET m.stream = $stream, m.source = 'autodoc',
                    m.updated_at = datetime()
            """, name=name, stream=stream)
            s.run("""
                MATCH (m:AutodocModule {name: $name})
                MATCH (s:AutodocStream {code: $stream})
                MERGE (m)-[:OWNED_BY]->(s)
            """, name=name, stream=stream)

    def link_file_to_module(self, file_path: str, module_name: str):
        """Link a file to its module."""
        with self.driver.session() as s:
            s.run("""
                MATCH (f:AutodocFile {path: $path})
                MATCH (m:AutodocModule {name: $module})
                MERGE (f)-[:BELONGS_TO]->(m)
            """, path=file_path, module=module_name)

    def create_function_node(self, func_info: dict, file_path: str):
        """Create a Function node linked to its file."""
        key = f"{file_path}::{func_info['name']}"
        with self.driver.session() as s:
            s.run("""
                MERGE (fn:Autodoc:AutodocFunction {key: $key})
                SET fn.name = $name,
                    fn.file_path = $file_path,
                    fn.line = $line,
                    fn.is_async = $is_async,
                    fn.docstring = $docstring,
                    fn.source = 'autodoc',
                    fn.updated_at = datetime()
            """, key=key, name=func_info["name"], file_path=file_path,
                line=func_info.get("line", 0), is_async=func_info.get("is_async", False),
                docstring=func_info.get("docstring", "")[:500])
            s.run("""
                MATCH (fn:AutodocFunction {key: $key})
                MATCH (f:AutodocFile {path: $file_path})
                MERGE (fn)-[:DEFINED_IN]->(f)
            """, key=key, file_path=file_path)

    def create_class_node(self, class_info: dict, file_path: str):
        """Create a Class node linked to its file."""
        key = f"{file_path}::{class_info['name']}"
        with self.driver.session() as s:
            s.run("""
                MERGE (c:Autodoc:AutodocClass {key: $key})
                SET c.name = $name,
                    c.file_path = $file_path,
                    c.line = $line,
                    c.bases = $bases,
                    c.methods = $methods,
                    c.docstring = $docstring,
                    c.source = 'autodoc',
                    c.updated_at = datetime()
            """, key=key, name=class_info["name"], file_path=file_path,
                line=class_info.get("line", 0),
                bases=class_info.get("bases", []),
                methods=class_info.get("methods", []),
                docstring=class_info.get("docstring", "")[:500])
            s.run("""
                MATCH (c:AutodocClass {key: $key})
                MATCH (f:AutodocFile {path: $file_path})
                MERGE (c)-[:DEFINED_IN]->(f)
            """, key=key, file_path=file_path)

    def create_import_relationship(self, from_path: str, to_module: str):
        """Create an IMPORTS relationship between files."""
        # Try to resolve the module to a file path
        possible_paths = self._resolve_module_path(to_module)
        with self.driver.session() as s:
            for target_path in possible_paths:
                s.run("""
                    MATCH (a:AutodocFile {path: $from_path})
                    MATCH (b:AutodocFile {path: $to_path})
                    MERGE (a)-[:IMPORTS]->(b)
                """, from_path=from_path, to_path=target_path)

    def _resolve_module_path(self, module: str) -> list:
        """Try to resolve a Python module name to file paths."""
        # Convert module.path.name to module/path/name.py
        parts = module.split(".")
        candidates = []
        # Try as direct path
        path_base = "/".join(parts)
        candidates.append(f"{path_base}.py")
        candidates.append(f"{path_base}/__init__.py")
        return candidates

    def create_endpoint_node(self, route_info: dict, file_path: str):
        """Create an API Endpoint node."""
        key = f"{route_info['method']}:{route_info['path']}"
        with self.driver.session() as s:
            s.run("""
                MERGE (e:Autodoc:AutodocEndpoint {key: $key})
                SET e.method = $method,
                    e.path = $path,
                    e.file_path = $file_path,
                    e.source = 'autodoc',
                    e.updated_at = datetime()
            """, key=key, method=route_info["method"], path=route_info["path"],
                file_path=file_path)
            s.run("""
                MATCH (e:AutodocEndpoint {key: $key})
                MATCH (f:AutodocFile {path: $file_path})
                MERGE (e)-[:HANDLED_BY]->(f)
            """, key=key, file_path=file_path)

    def create_service_node(self, svc: dict):
        """Create a Service node."""
        with self.driver.session() as s:
            s.run("""
                MERGE (sv:Autodoc:AutodocService {name: $name})
                SET sv.type = $type,
                    sv.system_path = $path,
                    sv.exec_start = $exec_start,
                    sv.source = 'autodoc',
                    sv.updated_at = datetime()
            """, **svc)

    def create_db_table_node(self, table_name: str, database: str = "postgres"):
        """Create a DBTable node."""
        with self.driver.session() as s:
            s.run("""
                MERGE (t:Autodoc:AutodocDBTable {name: $name})
                SET t.database = $database,
                    t.source = 'autodoc',
                    t.updated_at = datetime()
            """, name=table_name, database=database)

    def link_file_to_table(self, file_path: str, table_name: str, rel_type: str = "REFERENCES"):
        """Link a file to a database table."""
        with self.driver.session() as s:
            s.run(f"""
                MATCH (f:AutodocFile {{path: $path}})
                MATCH (t:AutodocDBTable {{name: $table}})
                MERGE (f)-[:{rel_type}]->(t)
            """, path=file_path, table=table_name)

    def create_config_node(self, path: str, format_type: str):
        """Create a Config node."""
        with self.driver.session() as s:
            s.run("""
                MERGE (c:Autodoc:AutodocConfig {path: $path})
                SET c.format = $format,
                    c.source = 'autodoc',
                    c.updated_at = datetime()
            """, path=path, format=format_type)

    def get_stats(self) -> dict:
        """Get counts of all Autodoc nodes by label."""
        with self.driver.session() as s:
            result = s.run("""
                MATCH (n:Autodoc)
                WITH labels(n) AS lbls
                UNWIND lbls AS lbl
                WITH lbl WHERE lbl <> 'Autodoc'
                RETURN lbl AS label, count(*) AS count
                ORDER BY count DESC
            """)
            return {r["label"]: r["count"] for r in result}


# ---------------------------------------------------------------------------
# Ollama LLM Interface
# ---------------------------------------------------------------------------

class OllamaClient:
    """Interface to Ollama for code analysis."""

    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def generate(self, model: str, prompt: str, system: str = "",
                 temperature: float = 0.3, timeout: int = 120) -> str:
        """Generate a response from Ollama."""
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 4096,
            },
        }
        try:
            resp = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except requests.exceptions.Timeout:
            return "[TIMEOUT - file may be too large for analysis]"
        except Exception as e:
            return f"[ERROR: {e}]"

    def analyze_file(self, filepath: Path, content: str, ast_info: dict = None,
                     language: str = "unknown") -> str:
        """Analyze a single file using qwen2.5:32b."""
        system_prompt = """You are a senior software architect documenting the Mythos system — a self-hosted AI infrastructure platform built on PostgreSQL, Neo4j, Redis, FastAPI, and Ollama, running on a Linux server called Arcturus.

Your job is to analyze source code files and produce clear, thorough documentation. For each file, explain:

1. **Purpose**: What this file does in 1-2 sentences
2. **Architecture**: How it's designed — classes, functions, data flow
3. **Patterns**: Design patterns used (factory, singleton, observer, etc.)
4. **Dependencies**: What it imports and relies on
5. **Interfaces**: What it exposes to other parts of the system
6. **Database**: Any database tables or Neo4j labels it reads/writes
7. **Configuration**: Any config files or environment variables it uses
8. **Key Logic**: The most important business logic or algorithms
9. **Integration Points**: How it connects to other Mythos subsystems

Be specific and technical. Use actual function/class names from the code. Do not be vague or generic."""

        ast_context = ""
        if ast_info:
            if ast_info.get("classes"):
                ast_context += f"\nClasses found: {json.dumps(ast_info['classes'], indent=2)}"
            if ast_info.get("functions"):
                ast_context += f"\nTop-level functions: {json.dumps(ast_info['functions'], indent=2)}"
            if ast_info.get("imports"):
                ast_context += f"\nImports: {ast_info['imports']}"
            if ast_info.get("fastapi_routes"):
                ast_context += f"\nFastAPI routes: {json.dumps(ast_info['fastapi_routes'], indent=2)}"
            if ast_info.get("db_references"):
                ast_context += f"\nDB references: {json.dumps(ast_info['db_references'], indent=2)}"

        prompt = f"""Analyze this {language} file from the Mythos system.

File: {relative_path(filepath)}
{ast_context}

--- FILE CONTENT ---
{content[:12000]}
--- END ---

Provide thorough documentation following the structure in your instructions."""

        return self.generate(ANALYSIS_MODEL, prompt, system_prompt, timeout=180)

    def synthesize_module(self, module_name: str, file_summaries: list) -> str:
        """Synthesize a module-level overview from individual file analyses."""
        system_prompt = """You are documenting the Mythos system architecture. Given summaries of individual files within a module/subsystem, synthesize a comprehensive module overview that covers:

1. **Module Purpose**: What this module does overall
2. **Architecture Overview**: How the pieces fit together, data flow through the module
3. **Key Components**: The most important classes/functions and their roles
4. **Design Patterns**: Patterns used across the module
5. **Data Model**: Tables, graphs, or data structures this module owns
6. **API Surface**: Endpoints, commands, or interfaces exposed
7. **Dependencies**: What this module depends on from other modules
8. **Configuration**: How to configure this module

Write a clear, well-structured technical document. Be specific."""

        summaries_text = "\n\n---\n\n".join([
            f"### {s['path']}\n{s['analysis']}" for s in file_summaries
        ])

        prompt = f"""Synthesize a module overview for: {module_name}

The following are analyses of individual files in this module:

{summaries_text[:30000]}

Write a comprehensive module documentation."""

        return self.generate(SYNTHESIS_MODEL, prompt, system_prompt, timeout=300)

    def synthesize_stream(self, stream_code: str, module_summaries: list) -> str:
        """Synthesize a stream-level overview from module summaries."""
        system_prompt = """You are documenting the Mythos system's development streams. Given module summaries within a stream, write a stream-level architectural overview covering the stream's overall purpose, how its modules interact, data flows, and key patterns.

Mythos has five streams:
- NEU (NEURO): Consciousness processing, awareness, Arcturian Grid, Iris core
- LOG (LOGOS): Knowledge, skills, prompts, orchestration, LLM routing
- MNE (MNEMOS): Memory, voice memos, recall systems
- SEN (SENSUS): Perception, astrology, sensory processing
- SYS (SYSTEM): Infrastructure, finance, bot, patches, workers

Write a thorough architectural document for this stream."""

        summaries_text = "\n\n---\n\n".join([
            f"### {s['name']}\n{s['summary']}" for s in module_summaries
        ])

        prompt = f"""Write a stream architecture overview for: {stream_code}

Module summaries in this stream:

{summaries_text[:30000]}"""

        return self.generate(SYNTHESIS_MODEL, prompt, system_prompt, timeout=300)

    def synthesize_system(self, stream_summaries: list, stats: dict) -> str:
        """Synthesize the top-level system overview."""
        system_prompt = """You are writing the definitive architectural overview of Mythos — a self-hosted AI infrastructure platform running on a Linux server called Arcturus. Given summaries of all five development streams, write a comprehensive system-level document that explains:

1. What Mythos is and what it does
2. The overall architecture — how all the pieces fit together
3. Data flow — how information moves through the system
4. The five-stream development model
5. Key design decisions and patterns
6. Technology stack and infrastructure
7. How Iris (the AI entity) operates within this architecture

This is the master reference document for understanding the entire system. Be thorough, precise, and clear."""

        summaries_text = "\n\n---\n\n".join([
            f"## Stream: {s['code']}\n{s['summary']}" for s in stream_summaries
        ])

        prompt = f"""Write the master system architecture document for Mythos.

System Statistics:
{json.dumps(stats, indent=2)}

Stream Summaries:

{summaries_text[:40000]}"""

        return self.generate(SYNTHESIS_MODEL, prompt, system_prompt, timeout=600)


# ---------------------------------------------------------------------------
# State Manager (Resumability)
# ---------------------------------------------------------------------------

class StateManager:
    """Track autodoc progress for resumability."""

    def __init__(self):
        self.state = {
            "version": 2,
            "started_at": None,
            "last_run": None,
            "files": {},  # path -> {hash, status, analyzed_at}
            "modules_synthesized": [],
            "streams_synthesized": [],
            "system_synthesized": False,
            "stats": {},
        }
        self._load()

    def _load(self):
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    saved = json.load(f)
                if saved.get("version", 1) == self.state["version"]:
                    self.state = saved
            except Exception:
                pass

    def save(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def needs_analysis(self, path: str, current_hash: str) -> bool:
        """Check if a file needs (re)analysis."""
        entry = self.state["files"].get(path)
        if not entry:
            return True
        if entry.get("hash") != current_hash:
            return True
        if entry.get("status") != "done":
            return True
        return False

    def mark_done(self, path: str, file_hash: str):
        self.state["files"][path] = {
            "hash": file_hash,
            "status": "done",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def mark_failed(self, path: str, file_hash: str, error: str):
        self.state["files"][path] = {
            "hash": file_hash,
            "status": "failed",
            "error": error,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_progress(self) -> dict:
        files = self.state["files"]
        total = len(files)
        done = sum(1 for f in files.values() if f.get("status") == "done")
        failed = sum(1 for f in files.values() if f.get("status") == "failed")
        pending = total - done - failed
        return {
            "total": total,
            "done": done,
            "failed": failed,
            "pending": pending,
            "modules_synthesized": len(self.state.get("modules_synthesized", [])),
            "streams_synthesized": len(self.state.get("streams_synthesized", [])),
            "system_synthesized": self.state.get("system_synthesized", False),
        }


# ---------------------------------------------------------------------------
# Main Autodoc Engine
# ---------------------------------------------------------------------------

class AutodocEngine:
    """Main engine orchestrating the autodoc process."""

    def __init__(self, resume: bool = False):
        self.state = StateManager()
        self.ollama = OllamaClient()
        self.graph = None  # lazy init
        self.resume = resume
        self.file_inventory = []
        self.module_groups = {}
        self.stream_groups = {}

    def _init_graph(self):
        if self.graph is None:
            try:
                self.graph = GraphBuilder()
                print("  ✓ Connected to Neo4j")
            except Exception as e:
                print(f"  ✗ Neo4j connection failed: {e}")
                print("    Graph building will be skipped.")
                self.graph = None

    def _ensure_dirs(self):
        for d in [AUTODOC_DIR, MODULES_DIR, STREAMS_DIR, FILES_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    # ---- Phase 1: Inventory ----

    def inventory(self):
        """Walk the codebase and build file inventory."""
        print("\n━━━ Phase 1: Inventory ━━━")
        self.file_inventory = []

        for dirpath, dirnames, filenames in os.walk(MYTHOS_ROOT):
            dirpath = Path(dirpath)

            # Filter out skip dirs in-place
            dirnames[:] = [
                d for d in dirnames
                if not should_skip_dir(d, dirpath)
            ]

            for fname in sorted(filenames):
                filepath = dirpath / fname
                if should_skip_file(filepath):
                    continue
                if not is_documentable(filepath):
                    continue

                try:
                    stat = filepath.stat()
                    rel = relative_path(filepath)
                    line_count = 0
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                            line_count = sum(1 for _ in f)
                    except Exception:
                        pass

                    self.file_inventory.append({
                        "path": rel,
                        "abs_path": str(filepath),
                        "language": guess_language(filepath),
                        "stream": guess_stream(filepath),
                        "module": guess_module(filepath),
                        "size": stat.st_size,
                        "lines": line_count,
                        "hash": file_hash(filepath),
                    })
                except Exception:
                    continue

        # Group by module and stream
        self.module_groups = {}
        self.stream_groups = {}
        for fi in self.file_inventory:
            mod = fi["module"]
            stream = fi["stream"]
            self.module_groups.setdefault(mod, []).append(fi)
            self.stream_groups.setdefault(stream, []).append(fi)

        print(f"  Found {len(self.file_inventory)} documentable files")
        print(f"  {len(self.module_groups)} modules across {len(self.stream_groups)} streams")
        for stream, files in sorted(self.stream_groups.items()):
            print(f"    {stream}: {len(files)} files")

    # ---- Phase 2: Structural Analysis + Neo4j ----

    def build_graph(self):
        """AST-parse files and build Neo4j graph."""
        print("\n━━━ Phase 2: Structural Analysis + Neo4j Graph ━━━")
        self._init_graph()

        if self.graph:
            self.graph.create_constraints()
            self.graph.create_streams()

        # Create module nodes
        for mod_name, files in self.module_groups.items():
            stream = files[0]["stream"] if files else "SYS"
            if self.graph:
                self.graph.create_module_node(mod_name, stream)

        # Scan system-level info
        print("  Scanning systemd services...")
        services = SystemScanner.find_systemd_services()
        for svc in services:
            if self.graph:
                self.graph.create_service_node(svc)
        print(f"    Found {len(services)} mythos services")

        print("  Scanning Postgres tables...")
        tables = SystemScanner.find_postgres_tables()
        for t in tables:
            if self.graph:
                self.graph.create_db_table_node(t, "postgres")
        print(f"    Found {len(tables)} tables")

        print("  Scanning Neo4j labels...")
        labels = SystemScanner.find_neo4j_labels()
        for lbl in labels:
            if lbl.startswith("Autodoc"):
                continue  # don't index ourselves
            if self.graph:
                self.graph.create_db_table_node(lbl, "neo4j")
        print(f"    Found {len(labels)} labels")

        # Process each file
        total = len(self.file_inventory)
        print(f"\n  Processing {total} files for structural analysis...")

        for i, fi in enumerate(self.file_inventory):
            filepath = Path(fi["abs_path"])
            rel = fi["path"]

            # Create file node in graph
            if self.graph:
                self.graph.create_file_node({
                    "path": rel,
                    "language": fi["language"],
                    "stream": fi["stream"],
                    "module": fi["module"],
                    "size": fi["size"],
                    "lines": fi["lines"],
                    "hash": fi["hash"],
                })
                self.graph.link_file_to_module(rel, fi["module"])

            # AST analysis for Python files
            if fi["language"] == "python":
                analyzer = PythonAnalyzer(filepath)
                ast_info = analyzer.analyze()
                fi["ast_info"] = ast_info

                if self.graph:
                    # Create function nodes
                    for func in ast_info.get("functions", []):
                        self.graph.create_function_node(func, rel)

                    # Create class nodes
                    for cls in ast_info.get("classes", []):
                        self.graph.create_class_node(cls, rel)

                    # Create endpoint nodes
                    for route in ast_info.get("fastapi_routes", []):
                        self.graph.create_endpoint_node(route, rel)

                    # Create import relationships
                    for imp in ast_info.get("imports", []):
                        self.graph.create_import_relationship(rel, imp)
                    for imp in ast_info.get("from_imports", []):
                        self.graph.create_import_relationship(rel, imp["module"])

                    # Link to DB tables
                    for ref in ast_info.get("db_references", []):
                        if ref["type"] == "postgres" and ref.get("table"):
                            self.graph.link_file_to_table(rel, ref["table"])
                        elif ref["type"] == "neo4j" and ref.get("label"):
                            self.graph.link_file_to_table(rel, ref["label"])

            # Config files
            if fi["language"] in ("yaml", "json", "toml", "ini", "env", "config"):
                if self.graph:
                    self.graph.create_config_node(rel, fi["language"])

            if (i + 1) % 50 == 0:
                print(f"    [{i+1}/{total}] structural analysis...")

        if self.graph:
            stats = self.graph.get_stats()
            print(f"\n  Neo4j Autodoc graph stats:")
            for label, count in stats.items():
                print(f"    {label}: {count}")

        print("  ✓ Structural analysis complete")

    # ---- Phase 3: LLM Analysis ----

    def analyze_files(self):
        """Send each file to Ollama for semantic analysis."""
        print("\n━━━ Phase 3: LLM File Analysis ━━━")

        # Filter to files needing analysis
        to_analyze = []
        for fi in self.file_inventory:
            if self.state.needs_analysis(fi["path"], fi["hash"]):
                to_analyze.append(fi)

        total = len(to_analyze)
        skipped = len(self.file_inventory) - total
        if skipped > 0:
            print(f"  Skipping {skipped} already-analyzed files (unchanged)")
        print(f"  Analyzing {total} files with {ANALYSIS_MODEL}...")

        if total == 0:
            print("  ✓ Nothing to analyze")
            return

        start_time = time.time()

        for i, fi in enumerate(to_analyze):
            filepath = Path(fi["abs_path"])
            rel = fi["path"]

            # Read file content
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                self.state.mark_failed(rel, fi["hash"], str(e))
                continue

            # Skip near-empty files
            if len(content.strip()) < 10:
                # Write a minimal doc
                doc_path = FILES_DIR / f"{rel.replace('/', '__')}.md"
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                doc_path.write_text(f"# {rel}\n\nEmpty or near-empty file.\n")
                self.state.mark_done(rel, fi["hash"])
                continue

            # Progress
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (total - i - 1) / rate if rate > 0 else 0
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta)) if eta > 0 else "—"
            print(f"  [{i+1}/{total}] {rel} ({fi['lines']}L) [ETA: {eta_str}]")

            # Get AST info if available
            ast_info = fi.get("ast_info")

            # Call Ollama
            analysis = self.ollama.analyze_file(filepath, content, ast_info, fi["language"])

            if analysis.startswith("[ERROR") or analysis.startswith("[TIMEOUT"):
                print(f"    ⚠ {analysis}")
                self.state.mark_failed(rel, fi["hash"], analysis)
                continue

            # Write per-file doc
            doc_filename = rel.replace("/", "__") + ".md"
            doc_path = FILES_DIR / doc_filename
            doc_content = f"""# {rel}

**Language:** {fi['language']}
**Stream:** {fi['stream']}
**Module:** {fi['module']}
**Lines:** {fi['lines']}

---

{analysis}
"""
            doc_path.write_text(doc_content)
            self.state.mark_done(rel, fi["hash"])

            # Save state periodically
            if (i + 1) % 10 == 0:
                self.state.save()

        self.state.save()
        elapsed = time.time() - start_time
        print(f"\n  ✓ File analysis complete in {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")

    # ---- Phase 4: Module Synthesis ----

    def synthesize_modules(self):
        """Synthesize module-level overview docs."""
        print("\n━━━ Phase 4: Module Synthesis ━━━")

        already_done = set(self.state.state.get("modules_synthesized", []))
        modules_to_do = [m for m in self.module_groups.keys() if m not in already_done]

        print(f"  {len(modules_to_do)} modules to synthesize ({len(already_done)} already done)")

        for mod_name in modules_to_do:
            files = self.module_groups[mod_name]
            print(f"  Synthesizing: {mod_name} ({len(files)} files)")

            # Gather file analyses
            file_summaries = []
            for fi in files:
                doc_filename = fi["path"].replace("/", "__") + ".md"
                doc_path = FILES_DIR / doc_filename
                if doc_path.exists():
                    analysis = doc_path.read_text()
                    # Strip header
                    lines = analysis.split("\n")
                    body_start = 0
                    for j, line in enumerate(lines):
                        if line.strip() == "---":
                            body_start = j + 1
                            break
                    analysis_body = "\n".join(lines[body_start:]).strip()
                    file_summaries.append({
                        "path": fi["path"],
                        "analysis": analysis_body[:3000],  # truncate for context window
                    })

            if not file_summaries:
                continue

            # Call synthesis model
            synthesis = self.ollama.synthesize_module(mod_name, file_summaries)

            # Write module doc
            safe_name = mod_name.lower().replace(" ", "_").replace("/", "_")
            mod_doc_path = MODULES_DIR / f"{safe_name}.md"
            stream = files[0]["stream"] if files else "SYS"
            file_list = "\n".join([f"- `{fi['path']}` ({fi['lines']}L)" for fi in files])

            mod_doc_path.write_text(f"""# {mod_name}

**Stream:** {stream}
**Files:** {len(files)}

## Files in this Module

{file_list}

---

{synthesis}
""")
            self.state.state.setdefault("modules_synthesized", []).append(mod_name)
            self.state.save()

        print("  ✓ Module synthesis complete")

    # ---- Phase 5: Stream Synthesis ----

    def synthesize_streams(self):
        """Synthesize stream-level overview docs."""
        print("\n━━━ Phase 5: Stream Synthesis ━━━")

        already_done = set(self.state.state.get("streams_synthesized", []))
        streams_to_do = [s for s in self.stream_groups.keys() if s not in already_done]

        print(f"  {len(streams_to_do)} streams to synthesize")

        for stream_code in streams_to_do:
            # Gather module summaries for this stream
            module_summaries = []
            for mod_name, files in self.module_groups.items():
                if files and files[0]["stream"] == stream_code:
                    safe_name = mod_name.lower().replace(" ", "_").replace("/", "_")
                    mod_doc_path = MODULES_DIR / f"{safe_name}.md"
                    if mod_doc_path.exists():
                        content = mod_doc_path.read_text()
                        module_summaries.append({
                            "name": mod_name,
                            "summary": content[:5000],
                        })

            if not module_summaries:
                continue

            print(f"  Synthesizing stream: {stream_code} ({len(module_summaries)} modules)")
            synthesis = self.ollama.synthesize_stream(stream_code, module_summaries)

            stream_doc_path = STREAMS_DIR / f"{stream_code}_overview.md"
            mod_list = "\n".join([f"- {s['name']}" for s in module_summaries])
            stream_doc_path.write_text(f"""# Stream: {stream_code}

## Modules

{mod_list}

---

{synthesis}
""")
            self.state.state.setdefault("streams_synthesized", []).append(stream_code)
            self.state.save()

        print("  ✓ Stream synthesis complete")

    # ---- Phase 6: System Synthesis ----

    def synthesize_system(self):
        """Produce the master system overview."""
        print("\n━━━ Phase 6: System Overview Synthesis ━━━")

        if self.state.state.get("system_synthesized") and self.resume:
            print("  Already done, skipping")
            return

        stream_summaries = []
        for stream_code in ["NEU", "LOG", "MNE", "SEN", "SYS"]:
            stream_doc = STREAMS_DIR / f"{stream_code}_overview.md"
            if stream_doc.exists():
                stream_summaries.append({
                    "code": stream_code,
                    "summary": stream_doc.read_text()[:8000],
                })

        stats = {
            "total_files": len(self.file_inventory),
            "modules": list(self.module_groups.keys()),
            "streams": list(self.stream_groups.keys()),
            "files_by_language": {},
            "files_by_stream": {},
        }
        for fi in self.file_inventory:
            lang = fi["language"]
            stream = fi["stream"]
            stats["files_by_language"][lang] = stats["files_by_language"].get(lang, 0) + 1
            stats["files_by_stream"][stream] = stats["files_by_stream"].get(stream, 0) + 1

        if self.graph:
            stats["neo4j_nodes"] = self.graph.get_stats()

        print("  Generating master system overview with iris-deep...")
        synthesis = self.ollama.synthesize_system(stream_summaries, stats)

        overview_path = AUTODOC_DIR / "system_overview.md"
        overview_path.write_text(f"""# Mythos System Architecture

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Files Analyzed:** {len(self.file_inventory)}
**Modules:** {len(self.module_groups)}

---

{synthesis}
""")

        self.state.state["system_synthesized"] = True
        self.state.save()
        print("  ✓ System overview complete")

    # ---- Phase 7: Index Generation ----

    def generate_index(self):
        """Generate master index files."""
        print("\n━━━ Phase 7: Index Generation ━━━")

        # JSON index
        index = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_files": len(self.file_inventory),
            "modules": {},
            "streams": {},
            "files": [],
        }

        for fi in self.file_inventory:
            index["files"].append({
                "path": fi["path"],
                "language": fi["language"],
                "stream": fi["stream"],
                "module": fi["module"],
                "lines": fi["lines"],
                "size": fi["size"],
            })

        for mod, files in self.module_groups.items():
            index["modules"][mod] = {
                "stream": files[0]["stream"] if files else "SYS",
                "file_count": len(files),
                "total_lines": sum(f["lines"] for f in files),
            }

        for stream, files in self.stream_groups.items():
            index["streams"][stream] = {
                "file_count": len(files),
                "total_lines": sum(f["lines"] for f in files),
                "modules": list(set(f["module"] for f in files)),
            }

        index_json_path = AUTODOC_DIR / "index.json"
        with open(index_json_path, "w") as f:
            json.dump(index, f, indent=2)

        # Markdown index
        md_lines = [
            "# Mythos Autodoc Index",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Files:** {len(self.file_inventory)}",
            f"**Modules:** {len(self.module_groups)}",
            "",
            "## System Overview",
            "",
            "- [System Architecture Overview](system_overview.md)",
            "",
            "## Streams",
            "",
        ]

        for stream in ["NEU", "LOG", "MNE", "SEN", "SYS"]:
            stream_doc = f"streams/{stream}_overview.md"
            file_count = len(self.stream_groups.get(stream, []))
            md_lines.append(f"- [{stream}]({stream_doc}) ({file_count} files)")

        md_lines.extend(["", "## Modules", ""])

        for mod_name in sorted(self.module_groups.keys()):
            safe_name = mod_name.lower().replace(" ", "_").replace("/", "_")
            files = self.module_groups[mod_name]
            stream = files[0]["stream"] if files else "SYS"
            md_lines.append(
                f"- [{mod_name}](modules/{safe_name}.md) "
                f"[{stream}] ({len(files)} files, "
                f"{sum(f['lines'] for f in files)} lines)"
            )

        md_lines.extend(["", "## All Files", ""])

        for fi in sorted(self.file_inventory, key=lambda x: x["path"]):
            doc_filename = fi["path"].replace("/", "__") + ".md"
            md_lines.append(
                f"- [`{fi['path']}`](files/{doc_filename}) "
                f"({fi['language']}, {fi['lines']}L, {fi['stream']})"
            )

        index_md_path = AUTODOC_DIR / "INDEX.md"
        index_md_path.write_text("\n".join(md_lines) + "\n")

        print(f"  ✓ Index written: {len(self.file_inventory)} files cataloged")

    # ---- Main Run ----

    def run(self):
        """Execute the full autodoc pipeline."""
        print("╔══════════════════════════════════════════╗")
        print("║     Mythos Autodoc Engine v1.0           ║")
        print("║     Iris-Powered Codebase Documentation  ║")
        print("╚══════════════════════════════════════════╝")

        self.state.state["last_run"] = datetime.now(timezone.utc).isoformat()
        if not self.state.state.get("started_at"):
            self.state.state["started_at"] = self.state.state["last_run"]

        self._ensure_dirs()

        start_time = time.time()

        self.inventory()
        self.build_graph()
        self.analyze_files()
        self.synthesize_modules()
        self.synthesize_streams()
        self.synthesize_system()
        self.generate_index()

        elapsed = time.time() - start_time

        print(f"\n{'━' * 44}")
        print(f"  Autodoc complete in {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
        progress = self.state.get_progress()
        print(f"  Files: {progress['done']} analyzed, {progress['failed']} failed")
        print(f"  Modules: {progress['modules_synthesized']} synthesized")
        print(f"  Streams: {progress['streams_synthesized']} synthesized")
        print(f"  System overview: {'✓' if progress['system_synthesized'] else '✗'}")
        print(f"  Output: {AUTODOC_DIR}")

        if self.graph:
            stats = self.graph.get_stats()
            print(f"  Neo4j nodes: {sum(stats.values())}")
            self.graph.close()

        self.state.save()

    def run_reindex(self):
        """Rebuild Neo4j graph only (no LLM calls)."""
        print("Autodoc: Rebuilding Neo4j graph (no LLM)...")
        self._ensure_dirs()
        self.inventory()
        self.build_graph()
        if self.graph:
            self.graph.close()
        print("✓ Graph rebuild complete")

    def run_synthesize(self):
        """Run synthesis passes only."""
        print("Autodoc: Running synthesis passes only...")
        self._ensure_dirs()
        self.inventory()
        self.synthesize_modules()
        self.synthesize_streams()
        self.synthesize_system()
        self.generate_index()
        print("✓ Synthesis complete")

    def run_clean(self):
        """Wipe everything and start fresh."""
        print("Autodoc: Cleaning...")
        self._init_graph()
        if self.graph:
            self.graph.clean()
            self.graph.close()

        import shutil
        if AUTODOC_DIR.exists():
            shutil.rmtree(AUTODOC_DIR)
            print(f"  ✓ Removed {AUTODOC_DIR}")

        print("✓ Clean complete")

    def run_status(self):
        """Show progress stats."""
        progress = self.state.get_progress()
        print("Autodoc Status:")
        print(f"  Started: {self.state.state.get('started_at', 'never')}")
        print(f"  Last run: {self.state.state.get('last_run', 'never')}")
        print(f"  Files tracked: {progress['total']}")
        print(f"    Analyzed: {progress['done']}")
        print(f"    Failed: {progress['failed']}")
        print(f"    Pending: {progress['pending']}")
        print(f"  Modules synthesized: {progress['modules_synthesized']}")
        print(f"  Streams synthesized: {progress['streams_synthesized']}")
        print(f"  System overview: {'✓' if progress['system_synthesized'] else '✗'}")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mythos Autodoc Engine")
    parser.add_argument("--resume", action="store_true",
                        help="Resume interrupted run (skip completed files)")
    parser.add_argument("--reindex", action="store_true",
                        help="Rebuild Neo4j graph only (no LLM calls)")
    parser.add_argument("--synthesize", action="store_true",
                        help="Run synthesis passes only")
    parser.add_argument("--clean", action="store_true",
                        help="Wipe all autodoc data and start fresh")
    parser.add_argument("--status", action="store_true",
                        help="Show progress stats")

    args = parser.parse_args()

    engine = AutodocEngine(resume=args.resume)

    if args.clean:
        engine.run_clean()
    elif args.status:
        engine.run_status()
    elif args.reindex:
        engine.run_reindex()
    elif args.synthesize:
        engine.run_synthesize()
    else:
        engine.run()


if __name__ == "__main__":
    main()
