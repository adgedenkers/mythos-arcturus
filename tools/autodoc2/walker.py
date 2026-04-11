"""
LanguageWalker base class and shared dataclasses.

Each language walker subclasses LanguageWalker and implements parse_file(),
returning a ParsedFile with extracted structural facts. The engine consumes
ParsedFile objects without caring which language they came from.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ParsedFunction:
    name: str
    qualified_name: str       # e.g. "ClassName.method" or "module.func"
    line_start: int
    line_end: int
    is_async: bool = False
    is_method: bool = False
    parent_class: Optional[str] = None
    docstring: Optional[str] = None
    calls: List[str] = field(default_factory=list)  # function names this function calls


@dataclass
class ParsedClass:
    name: str
    qualified_name: str
    line_start: int
    line_end: int
    bases: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    methods: List[str] = field(default_factory=list)


@dataclass
class ParsedImport:
    module: str               # e.g. "requests.adapters"
    names: List[str] = field(default_factory=list)  # imported symbols, [] if module-level
    is_relative: bool = False
    line: int = 0


@dataclass
class ParsedFile:
    path: Path                # absolute
    relative_path: str        # relative to crawl root
    language: str
    line_count: int
    classes: List[ParsedClass] = field(default_factory=list)
    functions: List[ParsedFunction] = field(default_factory=list)
    imports: List[ParsedImport] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)


class LanguageWalker:
    """Base class for language-specific walkers.

    Subclasses must implement parse_file(). They typically use tree-sitter
    via tree_sitter_languages.get_parser(<lang>) and walk the resulting CST.
    """

    language: str = "unknown"

    def parse_file(self, path: Path, relative_path: str, source: bytes) -> ParsedFile:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement parse_file()"
        )

    @staticmethod
    def _decode(node_bytes: bytes) -> str:
        try:
            return node_bytes.decode('utf-8', errors='replace')
        except Exception:
            return ""
