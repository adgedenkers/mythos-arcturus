"""
Module: integrity/function_extractor.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.1.0)
Purpose: Parse Python files using the ast module to extract function
         definitions, imports, and call relationships. MERGE Function
         nodes into Neo4j with CONTAINS and IMPORTS relationships.
Introduced: Patch 0171
Last Modified: Patch 0171

Dependencies:
  - ast (Python standard library)
  - neo4j (graph database)

Part of: Integrity Scanner
"""

import ast
import logging
from datetime import datetime

from integrity.graph import get_driver, run_write, run_query

logger = logging.getLogger("mythos.integrity.function_extractor")


def extract_functions(driver=None) -> dict:
    """
    For each .py IntegrityFile node in Neo4j, parse with ast and extract
    function definitions, imports, and (best-effort) call relationships.

    Returns:
        dict with extraction stats: files_parsed, functions_found,
        imports_found, parse_errors
    """
    own_driver = driver is None
    if own_driver:
        driver = get_driver()

    scan_timestamp = datetime.now().isoformat()
    stats = {
        "files_parsed": 0,
        "functions_found": 0,
        "imports_found": 0,
        "parse_errors": 0,
        "scan_start": scan_timestamp,
    }

    try:
        # Get all active .py files from the graph
        cypher = """
        MATCH (f:IntegrityFile)
        WHERE f.extension = '.py' AND f.status = 'active'
          AND NOT f.path STARTS WITH '/opt/mythos/eval/'
          AND NOT f.path STARTS WITH '/opt/mythos/updates/'
          AND NOT f.path ENDS WITH '_example.py'
        RETURN f.path AS path
        ORDER BY f.path
        """
        files = run_query(driver, cypher)

        for record in files:
            filepath = record["path"]
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                    source = fh.read()

                tree = ast.parse(source, filename=filepath)
                file_stats = _process_file_ast(driver, filepath, tree, scan_timestamp)

                stats["files_parsed"] += 1
                stats["functions_found"] += file_stats["functions"]
                stats["imports_found"] += file_stats["imports"]

            except SyntaxError as e:
                logger.warning(f"Syntax error in {filepath}: {e}")
                stats["parse_errors"] += 1
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot read {filepath}: {e}")
                stats["parse_errors"] += 1

    finally:
        if own_driver:
            driver.close()

    stats["scan_end"] = datetime.now().isoformat()
    return stats


def _process_file_ast(driver, filepath: str, tree: ast.AST,
                      scan_timestamp: str) -> dict:
    """Process the AST of a single file. Returns local stats."""
    stats = {"functions": 0, "imports": 0}

    # Extract function definitions
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _merge_function(driver, filepath, node, scan_timestamp)
            stats["functions"] += 1

    # Extract imports
    imports = _extract_imports(tree)
    for imp in imports:
        _merge_import(driver, filepath, imp, scan_timestamp)
        stats["imports"] += 1

    return stats


def _merge_function(driver, filepath: str, node, scan_timestamp: str):
    """MERGE a function node and link to its file."""
    # Build unique ID: filepath::function_name::line
    uid = f"{filepath}::{node.name}::{node.lineno}"

    # Extract docstring
    docstring = ast.get_docstring(node) or ""
    if len(docstring) > 2000:
        docstring = docstring[:2000] + "..."

    # Extract parameter names
    params = []
    for arg in node.args.args:
        params.append(arg.arg)
    for arg in node.args.posonlyargs:
        params.append(arg.arg)
    for arg in node.args.kwonlyargs:
        params.append(arg.arg)
    if node.args.vararg:
        params.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        params.append(f"**{node.args.kwarg.arg}")

    # Extract return annotation if present
    returns = ""
    if node.returns:
        try:
            returns = ast.unparse(node.returns)
        except Exception:
            returns = ""

    is_async = isinstance(node, ast.AsyncFunctionDef)

    # Get end line
    end_line = getattr(node, "end_lineno", node.lineno)

    # Extract decorators
    decorators = []
    for dec in node.decorator_list:
        try:
            decorators.append(ast.unparse(dec))
        except Exception:
            pass

    cypher = """
    MERGE (fn:IntegrityFunction {uid: $uid})
    SET fn.name = $name,
        fn.file_path = $filepath,
        fn.line_start = $line_start,
        fn.line_end = $line_end,
        fn.docstring = $docstring,
        fn.parameters = $params,
        fn.returns = $returns,
        fn.is_async = $is_async,
        fn.decorators = $decorators,
        fn.last_scanned = $scan_timestamp
    """
    run_write(driver, cypher, uid=uid, name=node.name, filepath=filepath,
              line_start=node.lineno, line_end=end_line,
              docstring=docstring, params=params, returns=returns,
              is_async=is_async, decorators=decorators,
              scan_timestamp=scan_timestamp)

    # Link function to file
    link_cypher = """
    MATCH (fn:IntegrityFunction {uid: $uid})
    MATCH (f:IntegrityFile {path: $filepath})
    MERGE (f)-[:CONTAINS]->(fn)
    """
    run_write(driver, link_cypher, uid=uid, filepath=filepath)


def _extract_imports(tree: ast.AST) -> list:
    """Extract import statements from an AST."""
    imports = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": alias.name,
                    "name": alias.asname or alias.name,
                    "line": node.lineno,
                })
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append({
                    "type": "from_import",
                    "module": module,
                    "name": alias.name,
                    "alias": alias.asname,
                    "line": node.lineno,
                })

    return imports


def _merge_import(driver, filepath: str, imp: dict, scan_timestamp: str):
    """
    Record an import relationship. We try to resolve the import to an
    actual IntegrityFile if it's a local Mythos import.
    """
    module = imp["module"]

    # Try to resolve to a local file path
    # e.g., "integrity.graph" → "/opt/mythos/integrity/graph.py"
    # e.g., "finance.importer" → "/opt/mythos/finance/importer.py"
    possible_paths = _resolve_import_path(module)

    for target_path in possible_paths:
        # Check if this file exists in the graph
        check = run_query(
            driver,
            "MATCH (f:IntegrityFile {path: $path}) RETURN f.path AS path",
            path=target_path
        )
        if check:
            # Create IMPORTS relationship
            cypher = """
            MATCH (src:IntegrityFile {path: $src_path})
            MATCH (tgt:IntegrityFile {path: $tgt_path})
            MERGE (src)-[:IMPORTS {module: $module, line: $line}]->(tgt)
            """
            run_write(driver, cypher, src_path=filepath, tgt_path=target_path,
                      module=module, line=imp["line"])
            break  # Found it, stop looking


def _resolve_import_path(module: str) -> list:
    """
    Convert a Python module path to possible file paths.
    Returns a list of candidate absolute paths.
    """
    if not module:
        return []

    import os
    mythos_root = os.getenv("MYTHOS_ROOT", "/opt/mythos")

    parts = module.split(".")
    candidates = []

    # Try as a direct module file: integrity.graph → /opt/mythos/integrity/graph.py
    file_path = os.path.join(mythos_root, *parts) + ".py"
    candidates.append(file_path)

    # Try as a package: integrity → /opt/mythos/integrity/__init__.py
    pkg_path = os.path.join(mythos_root, *parts, "__init__.py")
    candidates.append(pkg_path)

    return candidates
