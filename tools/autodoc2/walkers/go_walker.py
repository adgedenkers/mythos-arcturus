"""
Go walker using tree-sitter.

Extracts:
  - package declaration (used as the module qualifier)
  - imports — both single (`import "fmt"`) and grouped (`import ( "fmt" "os" )`)
  - function_declaration                -> ParsedFunction
  - method_declaration                  -> ParsedFunction with parent_class = receiver type
  - type_declaration with struct_type   -> ParsedClass with __struct__ tag
  - type_declaration with interface_type-> ParsedClass with __interface__ tag
  - type_declaration with type_alias    -> ParsedClass with __type_alias__ tag
  - call expressions in function bodies

Methods are attached to their receiver type as if it were a class. So a
method `func (s *Server) Start()` becomes Function with parent_class='Server',
and Server itself shows up as a class with __struct__ in bases.

Resilient to syntax errors.
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


class GoWalker(LanguageWalker):
    language = "go"
    grammar_key = "go"

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

        # Resolve module name from package declaration if present
        package = self._find_package(root)
        if package:
            module_name = package
        else:
            module_name = self._module_name_from_path(relative_path)

        for child in root.children:
            self._walk_top_level(child, pf, module_name)
        return pf

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        if p.endswith('.go'):
            p = p[:-3]
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _find_package(self, root) -> Optional[str]:
        for child in root.children:
            if child.type == 'package_clause':
                for ch in child.children:
                    if ch.type == 'package_identifier':
                        return self._text(ch)
        return None

    def _walk_top_level(self, node, pf: ParsedFile, module_name: str):
        t = node.type

        if t == 'function_declaration':
            self._handle_function(node, pf, module_name)
        elif t == 'method_declaration':
            self._handle_method(node, pf, module_name)
        elif t == 'type_declaration':
            self._handle_type_declaration(node, pf, module_name)
        elif t == 'import_declaration':
            self._handle_import(node, pf)

    def _handle_function(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        fn_name = self._text(name_node)
        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=f"{module_name}.{fn_name}",
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=False,
            is_method=False,
            parent_class=None,
            docstring=None,
            calls=self._extract_calls(node),
        ))

    def _handle_method(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        fn_name = self._text(name_node)

        # Receiver: func (s *Server) Foo() — extract 'Server'
        receiver_type = self._extract_receiver_type(node)

        if receiver_type:
            qualified = f"{module_name}.{receiver_type}.{fn_name}"
        else:
            qualified = f"{module_name}.{fn_name}"

        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=False,
            is_method=receiver_type is not None,
            parent_class=receiver_type,
            docstring=None,
            calls=self._extract_calls(node),
        ))

    def _extract_receiver_type(self, method_node) -> Optional[str]:
        """Extract the receiver type name from a method_declaration.
        Handles: func (s Server), func (s *Server), func (Server), func (*Server)
        """
        receiver = method_node.child_by_field_name('receiver')
        if receiver is None:
            return None
        # parameter_list -> parameter_declaration -> type
        stack = [receiver]
        while stack:
            n = stack.pop()
            if n.type in ('type_identifier',):
                return self._text(n)
            if n.type == 'pointer_type':
                for ch in n.children:
                    if ch.type == 'type_identifier':
                        return self._text(ch)
            for ch in n.children:
                stack.append(ch)
        return None

    def _handle_type_declaration(self, node, pf: ParsedFile, module_name: str):
        """Handle `type X struct { ... }`, `type X interface { ... }`, `type X = Y`."""
        for child in node.children:
            if child.type == 'type_spec':
                self._handle_type_spec(child, pf, module_name)
            elif child.type == 'type_alias':
                self._handle_type_spec(child, pf, module_name, is_alias=True)

    def _handle_type_spec(self, spec, pf: ParsedFile, module_name: str, is_alias: bool = False):
        name_node = spec.child_by_field_name('name')
        if name_node is None:
            return
        type_name = self._text(name_node)
        type_node = spec.child_by_field_name('type')

        kind = 'type_alias' if is_alias else 'type'
        if type_node is not None:
            if type_node.type == 'struct_type':
                kind = 'struct'
            elif type_node.type == 'interface_type':
                kind = 'interface'

        pc = ParsedClass(
            name=type_name,
            qualified_name=f"{module_name}.{type_name}",
            line_start=spec.start_point[0] + 1,
            line_end=spec.end_point[0] + 1,
            bases=[f"__{kind}__"],
            docstring=None,
        )
        pf.classes.append(pc)

    def _handle_import(self, node, pf: ParsedFile):
        """Handle both single and grouped imports.
        Single:  import "fmt"
        Grouped: import ( "fmt" "os" m "math" )
        """
        for child in node.children:
            if child.type == 'import_spec':
                self._handle_import_spec(child, pf, node.start_point[0] + 1)
            elif child.type == 'import_spec_list':
                for sub in child.children:
                    if sub.type == 'import_spec':
                        self._handle_import_spec(sub, pf, sub.start_point[0] + 1)

    def _handle_import_spec(self, spec, pf: ParsedFile, line: int):
        path_node = spec.child_by_field_name('path')
        if path_node is None:
            for ch in spec.children:
                if ch.type == 'interpreted_string_literal':
                    path_node = ch
                    break
        if path_node is None:
            return
        module = self._text(path_node).strip("\"'`")
        pf.imports.append(ParsedImport(
            module=module,
            names=[],
            is_relative=module.startswith('.'),
            line=line,
        ))

    def _extract_calls(self, fn_node) -> List[str]:
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
                    if '\n' not in name:
                        calls.append(name)
            for ch in n.children:
                stack.append(ch)
        return calls
