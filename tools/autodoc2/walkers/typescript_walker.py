"""
TypeScript walker — extends JavaScriptWalker with TS-specific node handling.

The tree-sitter-typescript grammar is a strict superset of JavaScript's
grammar at the node-type level. function_declaration, class_declaration,
import_statement, lexical_declaration, etc. all behave the same. The
TypeScript walker adds handling for:

  - interface_declaration  -> ParsedType (kind='interface')
  - type_alias_declaration -> ParsedType (kind='type_alias')

Two grammar variants exist:
  - 'typescript' grammar for .ts files
  - 'tsx' grammar for .tsx files (handles JSX-in-TS)

We use a single walker class that picks the parser based on whether
the file extension is .tsx. Both grammars produce the same node types
for the constructs we extract — only the parser instance differs.
"""

from pathlib import Path
from typing import Optional

from ..walker import (
    ParsedFile,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
)
from .javascript_walker import JavaScriptWalker


# We tack interfaces and type aliases onto pf.classes with a marker prefix
# in the qualified_name. The Neo4j writer will need to know to label them
# differently — we'll handle that in a follow-up patch. For Phase 2 they
# land as AutodocClass nodes with a 'kind' field on the bases list as a
# tag. This keeps the demo queries working without a schema change.

INTERFACE_TAG = "__interface__"
TYPE_ALIAS_TAG = "__type_alias__"


class TypeScriptWalker(JavaScriptWalker):
    language = "typescript"
    grammar_key = "typescript"

    def __init__(self):
        # Skip JavaScriptWalker.__init__ — load the TS parser instead
        try:
            from tree_sitter_language_pack import get_parser
            self._parser = get_parser(self.grammar_key)
            self._available = True
            self._init_error = None
        except Exception as e:
            self._parser = None
            self._available = False
            self._init_error = str(e)

    def _walk_top_level(self, node, pf: ParsedFile, module_name: str,
                        parent_class: Optional[str]):
        t = node.type

        # TypeScript-specific
        if t == 'interface_declaration':
            self._handle_interface(node, pf, module_name)
            return
        if t == 'type_alias_declaration':
            self._handle_type_alias(node, pf, module_name)
            return

        # Fall through to JS handling for everything else
        super()._walk_top_level(node, pf, module_name, parent_class)

    def _handle_interface(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        name = self._text(name_node)
        qualified = f"{module_name}.{name}"

        # Extract extends clause if present
        bases = [INTERFACE_TAG]
        for child in node.children:
            if child.type == 'extends_type_clause' or child.type == 'extends_clause':
                for ch in child.children:
                    if ch.type in ('type_identifier', 'identifier', 'generic_type'):
                        bases.append(self._text(ch))

        pf.classes.append(ParsedClass(
            name=name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=bases,
            docstring=None,
        ))

    def _handle_type_alias(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        name = self._text(name_node)
        qualified = f"{module_name}.{name}"

        pf.classes.append(ParsedClass(
            name=name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=[TYPE_ALIAS_TAG],
            docstring=None,
        ))


class TsxWalker(TypeScriptWalker):
    """TSX walker — same as TypeScriptWalker but uses the 'tsx' grammar.

    Used for .tsx and .jsx files where JSX syntax is present. The 'tsx'
    grammar handles both TypeScript constructs and JSX expressions.
    """
    language = "tsx"
    grammar_key = "tsx"
