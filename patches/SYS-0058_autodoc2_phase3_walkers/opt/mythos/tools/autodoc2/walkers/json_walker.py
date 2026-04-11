"""
JSON walker using tree-sitter.

JSON is everywhere in modern codebases: package.json, tsconfig.json,
composer.json, .eslintrc.json, kubernetes manifests, OpenAPI specs,
GitHub Actions event payloads, every config file in modern web stacks.

We extract:
  - Top-level object keys -> ParsedClass with __json_key__ tag
    (e.g. for a package.json: 'name', 'version', 'dependencies', 'scripts')
  - For arrays at the root, we emit a single __json_array__ marker

This enables demo queries like:
  "show me every package.json in this monorepo and what scripts they define"
  "find every config file with a 'devDependencies' key"
  "show me all the tsconfig files and their compilerOptions structure"

There are no functions or imports in JSON. pf.functions and pf.imports
stay empty.

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


class JsonWalker(LanguageWalker):
    language = "json"
    grammar_key = "json"

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

        # The grammar wraps content in 'document' which contains a single value.
        # We find the top-level object and emit its keys.
        top = self._find_top_value(root)
        if top is None:
            return pf

        if top.type == 'object':
            self._emit_object_keys(top, pf, module_name)
        elif top.type == 'array':
            pf.classes.append(ParsedClass(
                name='__root_array__',
                qualified_name=f"{module_name}.__root_array__",
                line_start=top.start_point[0] + 1,
                line_end=top.end_point[0] + 1,
                bases=['__json_array__'],
                docstring=None,
            ))
        return pf

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        if p.endswith('.json'):
            p = p[:-5]
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _find_top_value(self, root):
        """Walk down from the document root to find the first object/array."""
        stack = [root]
        while stack:
            n = stack.pop()
            if n.type in ('object', 'array'):
                return n
            for ch in n.children:
                stack.append(ch)
        return None

    def _emit_object_keys(self, obj_node, pf: ParsedFile, module_name: str):
        for child in obj_node.children:
            if child.type == 'pair':
                self._emit_pair(child, pf, module_name)

    def _emit_pair(self, pair_node, pf: ParsedFile, module_name: str):
        # Pair: key : value
        key_node = pair_node.child_by_field_name('key')
        if key_node is None:
            for ch in pair_node.children:
                if ch.type == 'string':
                    key_node = ch
                    break
        if key_node is None:
            return
        # JSON keys are quoted strings — strip quotes
        key_text = self._text(key_node).strip().strip('"').strip("'")
        if not key_text:
            return
        pf.classes.append(ParsedClass(
            name=key_text,
            qualified_name=f"{module_name}.{key_text}",
            line_start=pair_node.start_point[0] + 1,
            line_end=pair_node.end_point[0] + 1,
            bases=['__json_key__'],
            docstring=None,
        ))
