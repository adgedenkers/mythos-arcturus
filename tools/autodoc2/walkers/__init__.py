"""
Walker registry. To add a new language:
  1. Create walkers/foo_walker.py with a class FooWalker(LanguageWalker)
  2. Import it here
  3. Add an entry to WALKER_REGISTRY

That's it. The dispatch layer in engine.py picks up new languages
automatically via get_walker().
"""
from typing import Dict, Optional
from ..walker import LanguageWalker
from .python_walker import PythonWalker
from .javascript_walker import JavaScriptWalker
from .typescript_walker import TypeScriptWalker, TsxWalker
from .sql_walker import SqlWalker
from .php_walker import PhpWalker
from .go_walker import GoWalker
from .bash_walker import BashWalker
from .yaml_walker import YamlWalker
from .json_walker import JsonWalker
from .rust_walker import RustWalker

# language identifier (matches filters.EXTENSION_LANGUAGE_MAP) -> walker instance
WALKER_REGISTRY: Dict[str, LanguageWalker] = {
    'python': PythonWalker(),
    'javascript': JavaScriptWalker(),
    'typescript': TypeScriptWalker(),
    'tsx': TsxWalker(),
    'sql': SqlWalker(),
    'php': PhpWalker(),
    'go': GoWalker(),
    'bash': BashWalker(),
    'yaml': YamlWalker(),
    'json': JsonWalker(),
    'rust': RustWalker(),
}


def get_walker(language: str) -> Optional[LanguageWalker]:
    return WALKER_REGISTRY.get(language)


def supported_languages() -> list:
    return sorted(WALKER_REGISTRY.keys())
