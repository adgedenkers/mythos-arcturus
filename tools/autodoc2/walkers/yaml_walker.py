"""
YAML walker using tree-sitter.

YAML isn't code, so the abstractions are different. We extract:

  - Top-level mapping keys -> ParsedClass with __yaml_key__ tag
    (e.g. for a docker-compose.yml: 'version', 'services', 'networks', 'volumes')
  - Each top-level document is also represented if the file has multiple docs

This gives demo queries like:
  "find every YAML file in this codebase that has a 'services:' key"
  "show me every workflow file's top-level structure"
  "what's the schema of all the kubernetes manifests in this repo?"

There are no functions or imports in YAML. pf.functions and pf.imports
stay empty.

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


class YamlWalker(LanguageWalker):
    language = "yaml"
    grammar_key = "yaml"

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

        # The grammar nests as: stream -> document -> block_node -> block_mapping
        # We walk to find every block_mapping that is a *top-level* mapping
        # of a document and emit its keys.
        for child in root.children:
            if child.type == 'document':
                self._handle_document(child, pf, module_name)
        return pf

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        for ext in ('.yaml', '.yml'):
            if p.endswith(ext):
                p = p[:-len(ext)]
                break
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _handle_document(self, doc_node, pf: ParsedFile, module_name: str):
        """Find the top-level block_mapping in this document and emit its keys."""
        mapping = self._find_top_mapping(doc_node)
        if mapping is None:
            return
        for child in mapping.children:
            if child.type == 'block_mapping_pair':
                self._handle_pair(child, pf, module_name)

    def _find_top_mapping(self, node):
        """Walk down through block_node wrappers until we hit block_mapping
        or flow_mapping."""
        stack = [node]
        while stack:
            n = stack.pop()
            if n.type in ('block_mapping', 'flow_mapping'):
                return n
            for ch in n.children:
                stack.append(ch)
        return None

    def _handle_pair(self, pair_node, pf: ParsedFile, module_name: str):
        key_node = pair_node.child_by_field_name('key')
        if key_node is None:
            for ch in pair_node.children:
                if ch.type in ('flow_node', 'plain_scalar', 'string_scalar'):
                    key_node = ch
                    break
        if key_node is None:
            return
        key_text = self._text(key_node).strip().strip('"').strip("'")
        if not key_text:
            return
        pf.classes.append(ParsedClass(
            name=key_text,
            qualified_name=f"{module_name}.{key_text}",
            line_start=pair_node.start_point[0] + 1,
            line_end=pair_node.end_point[0] + 1,
            bases=['__yaml_key__'],
            docstring=None,
        ))
