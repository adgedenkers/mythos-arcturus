#!/opt/mythos/.venv/bin/python3
"""
/opt/mythos/tools/patchbase_register.py

Reads patch_base.py via AST, extracts public PatchBase method signatures
and docstrings, and writes MythosTool nodes to Neo4j.

Also supports --dump mode: prints the API to stdout as a compact reference
for use in Claude diagnostic bundles (patchbase-methods CLI).

SYS-0092: AutoDoc2 Letter D — PatchBase microtool registration.

Usage:
    patchbase-methods              # dump API to stdout
    patchbase-methods --register   # write to Neo4j (also runs on patch install)
    patchbase-methods --json       # dump as JSON
"""
import ast
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Optional

PATCH_BASE_PATH = Path('/opt/mythos/patches/scripts/patch_base.py')
MYTHOS = Path('/opt/mythos')

# Methods prefixed with _ are private — skip them
# Also skip __init__, begin, finish (infrastructure, not microtool API)
SKIP_METHODS = {'__init__', 'begin', 'finish', 'log', 'write_logs',
                '_bump_streams_json', '_write_patch_history', '_write_file_tx'}


def extract_methods(source_path: Path) -> list[dict]:
    """Parse patch_base.py via AST and extract PatchBase method metadata."""
    source = source_path.read_text(encoding='utf-8')
    tree = ast.parse(source)

    methods = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != 'PatchBase':
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = item.name
            if name in SKIP_METHODS or name.startswith('_'):
                continue

            # Signature
            args = item.args
            params = []
            # skip 'self'
            for arg in args.args[1:]:
                annotation = ''
                if arg.annotation:
                    annotation = ast.unparse(arg.annotation)
                params.append(f"{arg.arg}: {annotation}" if annotation else arg.arg)
            # defaults
            defaults = args.defaults
            n_defaults = len(defaults)
            n_params = len(params)
            if n_defaults:
                for i, default in enumerate(defaults):
                    param_idx = n_params - n_defaults + i
                    if param_idx < len(params):
                        params[param_idx] += f' = {ast.unparse(default)}'

            # Return annotation
            returns = ''
            if item.returns:
                returns = ast.unparse(item.returns)

            sig = f"patch.{name}({', '.join(params)})"
            if returns:
                sig += f' -> {returns}'

            # Docstring
            docstring = ast.get_docstring(item) or ''
            # First line only for compact display
            doc_first = docstring.split('\n')[0].strip() if docstring else ''

            methods.append({
                'name': name,
                'signature': sig,
                'docstring': docstring,
                'doc_first': doc_first,
                'returns': returns,
                'params': params,
                'lineno': item.lineno,
            })
        break  # found PatchBase, done

    return sorted(methods, key=lambda m: m['lineno'])


def dump_text(methods: list[dict]) -> str:
    """Format API for human/Claude consumption in diagnostic bundles."""
    lines = ['PatchBase API — /opt/mythos/patches/scripts/patch_base.py',
             '=' * 60]
    for m in methods:
        lines.append(f"\n{m['signature']}")
        if m['doc_first']:
            lines.append(f"    # {m['doc_first']}")
    lines.append('\n' + '=' * 60)
    lines.append(f"{len(methods)} public methods")
    return '\n'.join(lines)


def register_to_neo4j(methods: list[dict]) -> tuple[int, int]:
    """Write MythosTool nodes to Neo4j. Returns (created, updated)."""
    try:
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        load_dotenv(MYTHOS / '.env')
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', '')
        driver = GraphDatabase.driver(uri, auth=(user, password))
    except Exception as e:
        print(f"[patchbase_register] Neo4j connection failed: {e}", file=sys.stderr)
        return 0, 0

    created = 0
    updated = 0

    with driver.session() as session:
        # Ensure constraint
        try:
            session.run(
                "CREATE CONSTRAINT mythos_tool_unique IF NOT EXISTS "
                "FOR (t:MythosTool) REQUIRE (t.tool_class, t.name) IS UNIQUE"
            )
        except Exception:
            pass  # constraint may already exist

        # Upsert PatchBase node
        session.run(
            """
            MERGE (pb:MythosToolClass {name: 'PatchBase'})
            SET pb.source_path = $path,
                pb.description = 'Standard base class for all Mythos apply_patch.py scripts',
                pb.registered_at = datetime()
            """,
            path=str(PATCH_BASE_PATH),
        )

        for m in methods:
            result = session.run(
                """
                MERGE (t:MythosTool {tool_class: 'PatchBase', name: $name})
                ON CREATE SET t.created = true
                ON MATCH SET t.created = false
                SET t.signature    = $signature,
                    t.docstring    = $docstring,
                    t.doc_first    = $doc_first,
                    t.returns      = $returns,
                    t.lineno       = $lineno,
                    t.updated_at   = datetime()
                WITH t
                MATCH (pb:MythosToolClass {name: 'PatchBase'})
                MERGE (pb)-[:HAS_METHOD]->(t)
                RETURN t.created AS was_created
                """,
                name=m['name'],
                signature=m['signature'],
                docstring=m['docstring'][:500],
                doc_first=m['doc_first'],
                returns=m['returns'],
                lineno=m['lineno'],
            )
            record = result.single()
            if record and record['was_created']:
                created += 1
            else:
                updated += 1

    driver.close()
    return created, updated


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='patchbase-methods',
        description='Dump or register PatchBase microtool API',
    )
    parser.add_argument('--register', action='store_true',
                        help='Write MythosTool nodes to Neo4j')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of text')
    parser.add_argument('--source', default=str(PATCH_BASE_PATH),
                        help=f'Path to patch_base.py (default: {PATCH_BASE_PATH})')
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"[patchbase-methods] ERROR: {source_path} not found", file=sys.stderr)
        sys.exit(1)

    methods = extract_methods(source_path)

    if args.register:
        created, updated = register_to_neo4j(methods)
        print(f"[patchbase-methods] Neo4j: {created} created, {updated} updated")
        return

    if args.json:
        print(json.dumps(methods, indent=2))
        return

    # Default: text dump for diagnostic bundles / Claude context
    print(dump_text(methods))


if __name__ == '__main__':
    main()
