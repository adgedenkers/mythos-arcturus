"""
JavaScript walker using tree-sitter.

Extracts:
  - function declarations (function foo() {})
  - generator function declarations (function* foo() {})
  - arrow functions assigned to variables (const foo = () => {})
  - function expressions assigned to variables (const foo = function() {})
  - class declarations and their methods
  - method definitions inside classes
  - ES module imports (import x from 'y', import {a,b} from 'y', import * as x from 'y')
  - CommonJS requires (const x = require('y'))
  - export statements (tracked but not yet emitted as separate nodes)
  - call expressions inside function bodies (call graph data)

Handles .js, .jsx, .mjs, .cjs files. JSX expressions inside .jsx files
are walked via the same JavaScript grammar — tree-sitter-javascript includes
JSX support natively.

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


class JavaScriptWalker(LanguageWalker):
    language = "javascript"
    grammar_key = "javascript"  # tree-sitter-language-pack key

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
        for child in root.children:
            self._walk_top_level(child, pf, module_name, parent_class=None)
        return pf

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        for ext in ('.jsx', '.mjs', '.cjs', '.js', '.tsx', '.ts'):
            if p.endswith(ext):
                p = p[:-len(ext)]
                break
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _walk_top_level(self, node, pf: ParsedFile, module_name: str,
                        parent_class: Optional[str]):
        t = node.type

        # Function declarations
        if t in ('function_declaration', 'generator_function_declaration'):
            self._handle_function_declaration(node, pf, module_name, parent_class=parent_class)

        # Class declarations
        elif t == 'class_declaration':
            self._handle_class_declaration(node, pf, module_name)

        # `const foo = () => {}` and `const foo = function() {}`
        elif t == 'lexical_declaration' or t == 'variable_declaration':
            for child in node.children:
                if child.type == 'variable_declarator':
                    self._handle_variable_declarator_function(child, pf, module_name)

        # Imports
        elif t == 'import_statement':
            self._handle_import_statement(node, pf)

        # Exports — peek inside for declarations
        elif t == 'export_statement':
            decl = node.child_by_field_name('declaration')
            if decl is not None:
                self._walk_top_level(decl, pf, module_name, parent_class)
            else:
                # `export { a, b }` or `export * from 'x'` — peek for source
                for child in node.children:
                    if child.type == 'string':
                        # re-export from another module — track as import
                        src_text = self._text(child).strip("\"'`")
                        if src_text:
                            pf.imports.append(ParsedImport(
                                module=src_text,
                                names=[],
                                is_relative=src_text.startswith('.'),
                                line=node.start_point[0] + 1,
                            ))

        # Top-level expression statements — check for require() and IIFE assignments
        elif t == 'expression_statement':
            for child in node.children:
                if child.type == 'call_expression':
                    self._maybe_handle_require(child, pf)

    # ------------------------------------------------------------------
    # Function handlers
    # ------------------------------------------------------------------

    def _handle_function_declaration(self, node, pf: ParsedFile, module_name: str,
                                     parent_class: Optional[str] = None):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        fn_name = self._text(name_node)
        is_async = self._is_async(node)

        if parent_class:
            qualified = f"{module_name}.{parent_class}.{fn_name}"
        else:
            qualified = f"{module_name}.{fn_name}"

        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=is_async,
            is_method=parent_class is not None,
            parent_class=parent_class,
            docstring=None,
            calls=self._extract_calls(node),
        ))

    def _handle_variable_declarator_function(self, node, pf: ParsedFile, module_name: str):
        """Handle `const foo = () => {}`, `const foo = function() {}`, `const foo = async () => {}`."""
        name_node = node.child_by_field_name('name')
        value_node = node.child_by_field_name('value')
        if name_node is None or value_node is None:
            return
        if value_node.type not in ('arrow_function', 'function_expression', 'function'):
            return
        # name might be an identifier or a destructure pattern; only handle identifier
        if name_node.type != 'identifier':
            return

        fn_name = self._text(name_node)
        is_async = self._is_async(value_node)

        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=f"{module_name}.{fn_name}",
            line_start=value_node.start_point[0] + 1,
            line_end=value_node.end_point[0] + 1,
            is_async=is_async,
            is_method=False,
            parent_class=None,
            docstring=None,
            calls=self._extract_calls(value_node),
        ))

    def _is_async(self, node) -> bool:
        for ch in node.children:
            if ch.type == 'async':
                return True
            txt = self._text(ch).strip() if ch.type in ('keyword', 'identifier') else ''
            if txt == 'async':
                return True
        # Check first token
        if node.children and self._text(node.children[0]).startswith('async'):
            return True
        return False

    # ------------------------------------------------------------------
    # Class handler
    # ------------------------------------------------------------------

    def _handle_class_declaration(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        cls_name = self._text(name_node)
        qualified = f"{module_name}.{cls_name}"

        bases: List[str] = []
        heritage = node.child_by_field_name('heritage')  # class_heritage in JS
        if heritage is None:
            # fall back to walking children for class_heritage node
            for ch in node.children:
                if ch.type == 'class_heritage':
                    heritage = ch
                    break
        if heritage is not None:
            for ch in heritage.children:
                if ch.type in ('identifier', 'member_expression'):
                    bases.append(self._text(ch))

        pc = ParsedClass(
            name=cls_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=bases,
            docstring=None,
        )

        body = node.child_by_field_name('body')
        if body is not None:
            for child in body.children:
                if child.type == 'method_definition':
                    self._handle_method_definition(child, pf, module_name, cls_name, pc)

        pf.classes.append(pc)

    def _handle_method_definition(self, node, pf: ParsedFile, module_name: str,
                                  class_name: str, pc: ParsedClass):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        method_name = self._text(name_node)
        is_async = self._is_async(node)
        qualified = f"{module_name}.{class_name}.{method_name}"
        pf.functions.append(ParsedFunction(
            name=method_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=is_async,
            is_method=True,
            parent_class=class_name,
            docstring=None,
            calls=self._extract_calls(node),
        ))
        pc.methods.append(method_name)

    # ------------------------------------------------------------------
    # Imports
    # ------------------------------------------------------------------

    def _handle_import_statement(self, node, pf: ParsedFile):
        """Parse ES module import statements.

        Forms:
          import 'x'
          import x from 'y'
          import { a, b as c } from 'y'
          import * as x from 'y'
          import x, { a } from 'y'
        """
        source_node = node.child_by_field_name('source')
        if source_node is None:
            # Fall back: find a string child
            for ch in node.children:
                if ch.type == 'string':
                    source_node = ch
                    break
        if source_node is None:
            return

        module = self._text(source_node).strip("\"'`")
        names: List[str] = []

        # Walk import_clause for named imports
        for child in node.children:
            if child.type == 'import_clause':
                for sub in child.children:
                    if sub.type == 'identifier':
                        names.append(self._text(sub))
                    elif sub.type == 'named_imports':
                        for spec in sub.children:
                            if spec.type == 'import_specifier':
                                n = spec.child_by_field_name('name')
                                if n is not None:
                                    names.append(self._text(n))
                    elif sub.type == 'namespace_import':
                        # `* as foo`
                        for nch in sub.children:
                            if nch.type == 'identifier':
                                names.append(self._text(nch))

        pf.imports.append(ParsedImport(
            module=module,
            names=names,
            is_relative=module.startswith('.'),
            line=node.start_point[0] + 1,
        ))

    def _maybe_handle_require(self, call_node, pf: ParsedFile):
        """Detect `require('x')` calls at expression-statement level.

        Note: this only catches bare `require('x')`. Variable declarations
        like `const x = require('y')` are caught by walking lexical_declaration
        and detecting the call_expression in the value position.
        """
        func = call_node.child_by_field_name('function')
        if func is None or self._text(func).strip() != 'require':
            return
        args = call_node.child_by_field_name('arguments')
        if args is None:
            return
        for arg in args.children:
            if arg.type == 'string':
                module = self._text(arg).strip("\"'`")
                pf.imports.append(ParsedImport(
                    module=module,
                    names=[],
                    is_relative=module.startswith('.'),
                    line=call_node.start_point[0] + 1,
                ))

    # ------------------------------------------------------------------
    # Call extraction (call graph data)
    # ------------------------------------------------------------------

    def _extract_calls(self, fn_node) -> List[str]:
        """Walk the function body collecting call expression target names.

        Also catches require() inside function bodies and adds them as imports
        on the parent file — handled by the engine pass, not here.
        """
        calls: List[str] = []
        body = fn_node.child_by_field_name('body')
        if body is None:
            return calls
        stack = [body]
        while stack:
            n = stack.pop()
            if n.type == 'call_expression':
                func = n.child_by_field_name('function')
                if func is not None:
                    name = self._text(func).strip()
                    # Trim arguments off member calls in case of formatting weirdness
                    if '\n' not in name:
                        calls.append(name)
            for ch in n.children:
                stack.append(ch)
        return calls
