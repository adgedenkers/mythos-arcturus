"""
Python walker using tree-sitter.

Extracts:
  - module-level functions and async functions
  - classes and their methods (including async methods)
  - imports (both `import x` and `from x import y, z`, including relative)
  - call expressions inside each function/method (the call graph autodoc1
    was weak on — tree-sitter walks the full CST so we catch every call)

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


class PythonWalker(LanguageWalker):
    language = "python"

    def __init__(self):
        # Lazy import so the module loads even if tree-sitter isn't installed
        # (the engine will fail loudly later, not at import time)
        try:
            from tree_sitter_languages import get_parser
            self._parser = get_parser('python')
            self._available = True
        except Exception as e:
            self._parser = None
            self._available = False
            self._init_error = str(e)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        # path/to/foo.py -> path.to.foo
        p = relative_path.replace('\\', '/')
        if p.endswith('.py'):
            p = p[:-3]
        elif p.endswith('.pyi'):
            p = p[:-4]
        return p.replace('/', '.')

    def _text(self, node, source: bytes) -> str:
        return source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _walk_top_level(self, node, pf: ParsedFile, module_name: str, parent_class: Optional[str]):
        t = node.type
        if t == 'function_definition':
            self._handle_function(node, pf, module_name, parent_class=None, is_async=False)
        elif t == 'decorated_definition':
            inner = node.child_by_field_name('definition')
            if inner is not None:
                self._walk_top_level(inner, pf, module_name, parent_class)
        elif t == 'class_definition':
            self._handle_class(node, pf, module_name)
        elif t == 'import_statement':
            self._handle_import(node, pf)
        elif t == 'import_from_statement':
            self._handle_import_from(node, pf)
        elif t == 'expression_statement':
            # Could contain a top-level call we don't care about; skip
            pass

    def _handle_class(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        cls_name = self._text(name_node, self._source)
        qualified = f"{module_name}.{cls_name}"

        bases: List[str] = []
        sup_node = node.child_by_field_name('superclasses')
        if sup_node is not None:
            for ch in sup_node.children:
                if ch.type in ('identifier', 'attribute', 'call'):
                    bases.append(self._text(ch, self._source))

        docstring = self._extract_docstring(node)

        pc = ParsedClass(
            name=cls_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=bases,
            docstring=docstring,
        )

        # Walk class body for methods
        body = node.child_by_field_name('body')
        if body is not None:
            for child in body.children:
                self._walk_class_body(child, pf, module_name, cls_name, pc)

        pf.classes.append(pc)

    def _walk_class_body(self, node, pf: ParsedFile, module_name: str,
                         class_name: str, pc: ParsedClass):
        t = node.type
        if t == 'function_definition':
            self._handle_function(node, pf, module_name, parent_class=class_name,
                                  is_async=False, class_obj=pc)
        elif t == 'decorated_definition':
            inner = node.child_by_field_name('definition')
            if inner is not None:
                self._walk_class_body(inner, pf, module_name, class_name, pc)

    def _handle_function(self, node, pf: ParsedFile, module_name: str,
                         parent_class: Optional[str], is_async: bool,
                         class_obj: Optional[ParsedClass] = None):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            return
        fn_name = self._text(name_node, self._source)

        # Detect async via the first child being 'async' keyword
        async_flag = is_async or any(
            ch.type == 'async' for ch in node.children
        )

        if parent_class:
            qualified = f"{module_name}.{parent_class}.{fn_name}"
        else:
            qualified = f"{module_name}.{fn_name}"

        docstring = self._extract_docstring(node)
        calls = self._extract_calls(node)

        pf_fn = ParsedFunction(
            name=fn_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=async_flag,
            is_method=parent_class is not None,
            parent_class=parent_class,
            docstring=docstring,
            calls=calls,
        )
        pf.functions.append(pf_fn)
        if class_obj is not None:
            class_obj.methods.append(fn_name)

    def _extract_docstring(self, node) -> Optional[str]:
        body = node.child_by_field_name('body')
        if body is None:
            return None
        for child in body.children:
            if child.type == 'expression_statement':
                for sub in child.children:
                    if sub.type == 'string':
                        s = self._text(sub, self._source)
                        # Strip quotes
                        for q in ('"""', "'''", '"', "'"):
                            if s.startswith(q) and s.endswith(q):
                                return s[len(q):-len(q)].strip()
                        return s.strip()
                return None
            # Only first statement counts as docstring
            if child.type not in ('comment',):
                return None
        return None

    def _extract_calls(self, fn_node) -> List[str]:
        """Walk the function body collecting call expression target names."""
        calls: List[str] = []
        body = fn_node.child_by_field_name('body')
        if body is None:
            return calls
        stack = [body]
        while stack:
            n = stack.pop()
            if n.type == 'call':
                func = n.child_by_field_name('function')
                if func is not None:
                    name = self._text(func, self._source)
                    # Trim to last segment for attribute calls (foo.bar.baz -> baz)
                    # but keep the full dotted path as the canonical form
                    calls.append(name.strip())
            for ch in n.children:
                stack.append(ch)
        return calls

    def _handle_import(self, node, pf: ParsedFile):
        # import a, b.c as d
        for child in node.children:
            if child.type == 'dotted_name':
                pf.imports.append(ParsedImport(
                    module=self._text(child, self._source),
                    names=[],
                    is_relative=False,
                    line=node.start_point[0] + 1,
                ))
            elif child.type == 'aliased_import':
                inner = child.child_by_field_name('name')
                if inner is not None:
                    pf.imports.append(ParsedImport(
                        module=self._text(inner, self._source),
                        names=[],
                        is_relative=False,
                        line=node.start_point[0] + 1,
                    ))

    def _handle_import_from(self, node, pf: ParsedFile):
        # from x.y import a, b as c
        module_node = node.child_by_field_name('module_name')
        module_text = self._text(module_node, self._source) if module_node else ""
        is_relative = module_text.startswith('.') or any(
            ch.type == 'relative_import' for ch in node.children
        )
        names: List[str] = []
        for child in node.children:
            if child.type == 'dotted_name' and child != module_node:
                names.append(self._text(child, self._source))
            elif child.type == 'aliased_import':
                inner = child.child_by_field_name('name')
                if inner is not None:
                    names.append(self._text(inner, self._source))
        pf.imports.append(ParsedImport(
            module=module_text or '.',
            names=names,
            is_relative=is_relative,
            line=node.start_point[0] + 1,
        ))

    # ------------------------------------------------------------------
    # parse_file wrapper that stashes source for helper methods
    # ------------------------------------------------------------------

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
