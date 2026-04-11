"""
PHP walker using tree-sitter.

Extracts:
  - function definitions (top-level and inside namespaces)
  - class declarations and their methods
  - interface declarations -> ParsedClass with __interface__ tag
  - trait declarations    -> ParsedClass with __trait__ tag
  - namespace use statements as imports (use Foo\\Bar; use Foo\\{A, B as C};)
  - call expressions inside method/function bodies (call graph)

Namespace handling: PHP files can declare a namespace which becomes the
qualifier prefix for all functions/classes in the file. We detect the
namespace_definition node and use its name as the module qualifier
instead of the file path.

Resilient to syntax errors: tree-sitter parses partial trees.
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


class PhpWalker(LanguageWalker):
    language = "php"
    grammar_key = "php"

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
        # Default module name from file path; overridden by namespace_definition
        # if one is present.
        module_name = self._module_name_from_path(relative_path)

        # First pass: find a namespace declaration if any
        ns = self._find_namespace(root)
        if ns:
            module_name = ns

        # Walk recursively — PHP top-level can be wrapped in a `program` node
        # which itself wraps `php_tag` and statements.
        self._walk(root, pf, module_name, parent_class=None)
        return pf

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        if p.endswith('.php'):
            p = p[:-4]
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _find_namespace(self, root) -> Optional[str]:
        """Find the first namespace_definition and return its dotted name."""
        stack = [root]
        while stack:
            n = stack.pop()
            if n.type == 'namespace_definition':
                name_node = n.child_by_field_name('name')
                if name_node is not None:
                    return self._text(name_node).replace('\\', '.')
                # Some grammars expose the name as a namespace_name child
                for ch in n.children:
                    if ch.type == 'namespace_name':
                        return self._text(ch).replace('\\', '.')
                return None
            for ch in n.children:
                stack.append(ch)
        return None

    def _walk(self, node, pf: ParsedFile, module_name: str, parent_class: Optional[str]):
        t = node.type

        if t == 'function_definition':
            self._handle_function(node, pf, module_name, parent_class)
            return

        if t == 'class_declaration':
            self._handle_class(node, pf, module_name, kind='class')
            return

        if t == 'interface_declaration':
            self._handle_class(node, pf, module_name, kind='interface')
            return

        if t == 'trait_declaration':
            self._handle_class(node, pf, module_name, kind='trait')
            return

        if t in ('namespace_use_declaration', 'use_declaration'):
            self._handle_use(node, pf)
            return

        # Recurse into wrapping nodes (program, namespace_definition body, etc.)
        for child in node.children:
            self._walk(child, pf, module_name, parent_class)

    def _handle_function(self, node, pf: ParsedFile, module_name: str,
                         parent_class: Optional[str]):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        fn_name = self._text(name_node)
        if parent_class:
            qualified = f"{module_name}.{parent_class}.{fn_name}"
        else:
            qualified = f"{module_name}.{fn_name}"
        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=False,
            is_method=parent_class is not None,
            parent_class=parent_class,
            docstring=None,
            calls=self._extract_calls(node),
        ))

    def _handle_class(self, node, pf: ParsedFile, module_name: str, kind: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        cls_name = self._text(name_node)
        qualified = f"{module_name}.{cls_name}"

        bases: List[str] = []
        # PHP: extends and implements are exposed via different fields
        for field in ('base_clause', 'class_interface_clause'):
            ch = node.child_by_field_name(field)
            if ch is not None:
                bases.append(self._text(ch).strip())
        # Tag the kind so demo queries can filter
        if kind != 'class':
            bases.append(f"__{kind}__")

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
                if child.type == 'method_declaration':
                    self._handle_method(child, pf, module_name, cls_name, pc)
        pf.classes.append(pc)

    def _handle_method(self, node, pf: ParsedFile, module_name: str,
                       class_name: str, pc: ParsedClass):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        method_name = self._text(name_node)
        qualified = f"{module_name}.{class_name}.{method_name}"
        pf.functions.append(ParsedFunction(
            name=method_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=False,
            is_method=True,
            parent_class=class_name,
            docstring=None,
            calls=self._extract_calls(node),
        ))
        pc.methods.append(method_name)

    def _handle_use(self, node, pf: ParsedFile):
        """Parse `use Foo\\Bar;` and `use Foo\\{A, B as C};` declarations."""
        # Walk for qualified_name / namespace_name children
        for child in node.children:
            t = child.type
            if t in ('qualified_name', 'namespace_name', 'name'):
                module = self._text(child).strip(';').replace('\\', '.')
                if module:
                    pf.imports.append(ParsedImport(
                        module=module,
                        names=[],
                        is_relative=False,
                        line=node.start_point[0] + 1,
                    ))
            elif t == 'namespace_use_clause':
                # use Foo\Bar [as Baz]
                inner = child.child_by_field_name('name')
                if inner is None:
                    for sub in child.children:
                        if sub.type in ('qualified_name', 'namespace_name', 'name'):
                            inner = sub
                            break
                if inner is not None:
                    module = self._text(inner).strip(';').replace('\\', '.')
                    pf.imports.append(ParsedImport(
                        module=module,
                        names=[],
                        is_relative=False,
                        line=node.start_point[0] + 1,
                    ))
            elif t == 'namespace_use_group':
                # use Foo\{A, B as C}
                # Find the prefix qualified_name first
                prefix = ""
                for sub in child.children:
                    if sub.type in ('qualified_name', 'namespace_name'):
                        prefix = self._text(sub).replace('\\', '.')
                        break
                # Then walk for inner clauses
                names: List[str] = []
                for sub in child.children:
                    if sub.type == 'namespace_use_clause':
                        n = sub.child_by_field_name('name')
                        if n is not None:
                            names.append(self._text(n))
                pf.imports.append(ParsedImport(
                    module=prefix or "use_group",
                    names=names,
                    is_relative=False,
                    line=node.start_point[0] + 1,
                ))

    def _extract_calls(self, fn_node) -> List[str]:
        calls: List[str] = []
        body = fn_node.child_by_field_name('body')
        if body is None:
            return calls
        stack = [body]
        while stack:
            n = stack.pop()
            # PHP function call types: function_call_expression, member_call_expression,
            # scoped_call_expression, object_creation_expression
            if n.type in ('function_call_expression', 'member_call_expression',
                          'scoped_call_expression'):
                func = n.child_by_field_name('function') or n.child_by_field_name('name')
                if func is not None:
                    name = self._text(func).strip()
                    if '\n' not in name:
                        calls.append(name)
            for ch in n.children:
                stack.append(ch)
        return calls
