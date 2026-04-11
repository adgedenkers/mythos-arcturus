"""
Filters: which directories/files to skip, which extensions map to which languages.
Carried forward from legacy autodoc.py and expanded for multi-language support.
"""
from pathlib import Path
import fnmatch
from typing import Optional, List

# Directories to skip during crawl (anywhere in the tree)
SKIP_DIRS = {
    '.git', '.hg', '.svn',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'node_modules', 'bower_components',
    '.venv', 'venv', 'env', '.env',
    'dist', 'build', '.next', '.nuxt', '.svelte-kit',
    'coverage', '.coverage', '.nyc_output',
    '.idea', '.vscode', '.vs',
    'target',  # rust/java
    '.gradle', '.mvn',
    'vendor',  # php/go
    '.cache', '.parcel-cache', '.turbo',
    '.tox',
    '.DS_Store',
}

# File patterns to skip
SKIP_FILE_PATTERNS = {
    '*.min.js', '*.min.css',
    '*.pyc', '*.pyo',
    '*.so', '*.dylib', '*.dll',
    '*.lock',
    '*.log',
    '.DS_Store',
    '*.map',  # source maps
    '*.d.ts',  # TypeScript declaration files — generated, no real structure
    'package-lock.json',  # huge generated lockfile, no useful structure
    'yarn.lock',
    'composer.lock',
    'Cargo.lock',
}

# Extension -> language identifier
# Language identifier matches the key registered in walkers/__init__.py
EXTENSION_LANGUAGE_MAP = {
    # Python
    '.py': 'python',
    '.pyi': 'python',
    # JavaScript / JSX
    '.js': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.jsx': 'javascript',  # tree-sitter-javascript grammar handles JSX natively
    # TypeScript / TSX (different grammars!)
    '.ts': 'typescript',
    '.tsx': 'tsx',          # uses the 'tsx' grammar variant for JSX-in-TS
    # SQL
    '.sql': 'sql',
    # PHP
    '.php': 'php',
    # Go
    '.go': 'go',
    # Bash
    '.sh': 'bash',
    '.bash': 'bash',
    # YAML
    '.yaml': 'yaml',
    '.yml': 'yaml',
    # JSON
    '.json': 'json',
    # Rust
    '.rs': 'rust',
}


def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS or dirname.startswith('.')


def should_skip_file(filename: str) -> bool:
    for pattern in SKIP_FILE_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def language_for_path(path: Path) -> Optional[str]:
    """Return the language identifier for a file path, or None if unsupported."""
    # Handle compound extensions like .d.ts before single extension lookup
    name_lower = path.name.lower()
    if name_lower.endswith('.d.ts'):
        return None
    return EXTENSION_LANGUAGE_MAP.get(path.suffix.lower())


def matches_any(path: Path, patterns: List[str], root: Path) -> bool:
    """Check if a path matches any of the given glob patterns (relative to root)."""
    if not patterns:
        return False
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.as_posix()
    for pat in patterns:
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(path.name, pat):
            return True
    return False


def iter_source_files(
    root: Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
):
    """Yield (path, language) tuples for every supported source file under root."""
    root = root.resolve()
    for current_dir, dirnames, filenames in __import__('os').walk(root):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        cd = Path(current_dir)
        for fname in filenames:
            if should_skip_file(fname):
                continue
            fpath = cd / fname
            lang = language_for_path(fpath)
            if lang is None:
                continue
            if exclude and matches_any(fpath, exclude, root):
                continue
            if include and not matches_any(fpath, include, root):
                continue
            yield fpath, lang
