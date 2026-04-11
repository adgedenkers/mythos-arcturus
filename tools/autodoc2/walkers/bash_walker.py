"""
Bash walker using tree-sitter.

Extracts:
  - function_definition (function foo() { } / foo() { })
  - source/. statements as imports (source ./lib.sh / . ./lib.sh)
  - command call expressions (call graph data — every command is a 'call')

Bash has no notion of classes; pf.classes stays empty.

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


class BashWalker(LanguageWalker):
    language = "bash"
    grammar_key = "bash"

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

        # Walk the whole tree — bash function defs can be nested inside if blocks,
        # case statements, etc.
        self._walk(root, pf, module_name)
        return pf

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        for ext in ('.bash', '.sh'):
            if p.endswith(ext):
                p = p[:-len(ext)]
                break
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _walk(self, node, pf: ParsedFile, module_name: str):
        t = node.type
        if t == 'function_definition':
            self._handle_function(node, pf, module_name)
            # Recurse into the body so nested functions are caught
            for child in node.children:
                self._walk(child, pf, module_name)
            return

        if t == 'command':
            # Detect source / . commands as imports
            self._maybe_handle_source(node, pf)

        for child in node.children:
            self._walk(child, pf, module_name)

    def _handle_function(self, node, pf: ParsedFile, module_name: str):
        name_node = node.child_by_field_name('name')
        if name_node is None:
            # Some grammars expose the name as the first word child
            for ch in node.children:
                if ch.type == 'word':
                    name_node = ch
                    break
        if name_node is None:
            return
        fn_name = self._text(name_node).strip()
        if not fn_name:
            return
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

    def _maybe_handle_source(self, command_node, pf: ParsedFile):
        """Detect `source FILE` or `. FILE` and emit as import."""
        children = command_node.children
        if not children:
            return
        first = children[0]
        first_text = self._text(first).strip()
        if first_text not in ('source', '.'):
            return
        # The next argument is the file path
        for ch in children[1:]:
            if ch.type in ('word', 'string', 'raw_string', 'concatenation'):
                module = self._text(ch).strip("\"'`")
                if module:
                    pf.imports.append(ParsedImport(
                        module=module,
                        names=[],
                        is_relative=module.startswith('.') or module.startswith('/'),
                        line=command_node.start_point[0] + 1,
                    ))
                break

    def _extract_calls(self, fn_node) -> List[str]:
        """Walk the function body collecting command names invoked."""
        calls: List[str] = []
        body = fn_node.child_by_field_name('body')
        if body is None:
            return calls
        stack = [body]
        seen = set()
        while stack:
            n = stack.pop()
            if n.type == 'command':
                if n.children:
                    name_node = n.children[0]
                    name = self._text(name_node).strip()
                    if name and name not in seen and '\n' not in name and len(name) < 80:
                        calls.append(name)
                        seen.add(name)
            for ch in n.children:
                stack.append(ch)
        return calls
