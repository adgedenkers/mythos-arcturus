"""
SQL walker using tree-sitter.

The tree-sitter-sql grammar (sqlite-flavored, but accepts most postgres/mysql
DDL) gives us a full CST. We extract structural definitions:

  CREATE TABLE x      -> ParsedClass (kind tag in bases: '__table__')
  CREATE VIEW x       -> ParsedClass (kind tag: '__view__')
  CREATE INDEX x      -> ParsedClass (kind tag: '__index__')
  CREATE FUNCTION x   -> ParsedFunction
  CREATE PROCEDURE x  -> ParsedFunction
  CREATE TRIGGER x    -> ParsedFunction (kind tag: '__trigger__' on docstring)

Mapping CREATE TABLE/VIEW to ParsedClass keeps existing Cypher demo queries
portable — "show me all the structures defined in this codebase" works the
same way whether the language is Python, TypeScript, or SQL.

There's no notion of imports in SQL, so pf.imports stays empty.

Resilient to syntax errors: tree-sitter parses partial trees and marks
ERROR nodes rather than throwing.
"""
from pathlib import Path
from typing import List, Optional
from ..walker import (
    LanguageWalker,
    ParsedFile,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
)


class SqlWalker(LanguageWalker):
    language = "sql"
    grammar_key = "sql"

    def __init__(self):
        try:
            from tree_sitter_language_pack import get_parser
            self._parser = get_parser(self.grammar_key)
            self._available = True
            self._init_error = None
        except Exception as e:
            self._parser = None
            self._available = False
            self._init_error = str(e)

    def parse_file(self, path: Path, relative_path: str, source: bytes) -> ParsedFile:
        self._source = source
        pf = ParsedFile(
            path=path,
            relative_path=relative_path,
            language=self.language,
            line_count=source.count(b'\n') + 1,
        )
        if not self._available:
            pf.parse_errors.append(f"tree-sitter not available: {self._init_error}")
            return pf
        try:
            tree = self._parser.parse(source)
        except Exception as e:
            pf.parse_errors.append(f"parse failed: {e}")
            return pf

        root = tree.root_node
        module_name = self._module_name_from_path(relative_path)

        # SQL parses as a sequence of statements at the top level.
        # We walk the entire tree because CREATE statements can be nested
        # inside DO blocks, BEGIN/END, etc.
        self._walk(root, pf, module_name)
        return pf

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        for ext in ('.sql',):
            if p.endswith(ext):
                p = p[:-len(ext)]
                break
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _walk(self, node, pf: ParsedFile, module_name: str):
        """Recursively walk the CST looking for CREATE statements."""
        t = node.type

        # The tree-sitter-sql grammar uses these node types for DDL.
        # Different sql grammars name these slightly differently — we accept
        # the common variants.
        if t in (
            'create_table_statement', 'create_table',
            'create_view_statement', 'create_view',
            'create_materialized_view_statement',
            'create_index_statement', 'create_index',
        ):
            self._handle_create_structural(node, pf, module_name)
            return  # don't recurse into table/view bodies

        if t in (
            'create_function_statement', 'create_function',
            'create_procedure_statement', 'create_procedure',
            'create_trigger_statement', 'create_trigger',
        ):
            self._handle_create_callable(node, pf, module_name)
            return

        for child in node.children:
            self._walk(child, pf, module_name)

    def _extract_object_name(self, node) -> Optional[str]:
        """SQL grammars vary on how they expose the created object name.
        Strategy: walk the immediate children, the first identifier or
        object_reference / table_reference / dotted_name we see is it.
        Skip keyword children (CREATE, TABLE, IF, NOT, EXISTS, etc.).
        """
        for child in node.children:
            t = child.type
            if t in ('object_reference', 'table_reference', 'dotted_name',
                     'qualified_name', 'identifier'):
                txt = self._text(child).strip().strip('`"[]')
                if txt and txt.lower() not in (
                    'if', 'not', 'exists', 'or', 'replace', 'temp', 'temporary',
                    'unique', 'materialized'
                ):
                    return txt
        return None

    def _kind_from_node_type(self, node_type: str) -> str:
        if 'table' in node_type:
            return 'table'
        if 'materialized_view' in node_type:
            return 'materialized_view'
        if 'view' in node_type:
            return 'view'
        if 'index' in node_type:
            return 'index'
        if 'function' in node_type:
            return 'function'
        if 'procedure' in node_type:
            return 'procedure'
        if 'trigger' in node_type:
            return 'trigger'
        return 'unknown'

    def _handle_create_structural(self, node, pf: ParsedFile, module_name: str):
        name = self._extract_object_name(node)
        if not name:
            return
        kind = self._kind_from_node_type(node.type)
        qualified = f"{module_name}.{name}"
        pf.classes.append(ParsedClass(
            name=name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=[f"__{kind}__"],
            docstring=f"SQL {kind}",
        ))

    def _handle_create_callable(self, node, pf: ParsedFile, module_name: str):
        name = self._extract_object_name(node)
        if not name:
            return
        kind = self._kind_from_node_type(node.type)
        qualified = f"{module_name}.{name}"
        pf.functions.append(ParsedFunction(
            name=name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=False,
            is_method=False,
            parent_class=None,
            docstring=f"SQL {kind}",
            calls=[],
        ))
