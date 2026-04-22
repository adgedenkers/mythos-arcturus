"""
Configuration loading for AutoDoc2.
Loads Neo4j credentials and Ollama settings from a .env file (default
/opt/mythos/.env). CLI args override env file values.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class Config:
    # Crawl target
    target: Path
    output_dir: Path
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    # Ollama (for markdown summaries via LLM)
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "iris-deep:latest"
    # Crawl behavior
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    clean: bool = False
    resume: bool = False
    skip_llm: bool = False  # if True, do not generate markdown summaries via LLM
    verbose: bool = False
    analyze: bool = False   # SYS-0087: if True, run ollama-analyze (gemma4:26b) per file


def _parse_env_file(path: Path) -> dict:
    """Minimal .env parser. KEY=VALUE per line, # comments, no shell expansion."""
    out = {}
    if not path.exists():
        return out
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        out[k] = v
    return out


def load_config(
    target: Path,
    output_dir: Optional[Path],
    env_file: Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    clean: bool = False,
    resume: bool = False,
    skip_llm: bool = False,
    verbose: bool = False,
    analyze: bool = False,
) -> Config:
    env = _parse_env_file(env_file)

    # Default output dir resolution:
    #   target == /opt/mythos -> /opt/mythos/docs/autodoc2/
    #   else                  -> <target>/.autodoc2/
    if output_dir is None:
        if target.resolve() == Path('/opt/mythos').resolve():
            output_dir = Path('/opt/mythos/docs/autodoc2')
        else:
            output_dir = target / '.autodoc2'

    cfg = Config(
        target=target.resolve(),
        output_dir=output_dir.resolve(),
        neo4j_uri=env.get('NEO4J_URI', os.environ.get('NEO4J_URI', 'bolt://localhost:7687')),
        neo4j_user=env.get('NEO4J_USER', os.environ.get('NEO4J_USER', 'neo4j')),
        neo4j_password=env.get('NEO4J_PASSWORD', os.environ.get('NEO4J_PASSWORD', '')),
        ollama_url=env.get('OLLAMA_URL', os.environ.get('OLLAMA_URL', 'http://localhost:11434')),
        ollama_model=env.get('OLLAMA_MODEL', os.environ.get('OLLAMA_MODEL', 'iris-deep:latest')),
        include=include or [],
        exclude=exclude or [],
        clean=clean,
        resume=resume,
        skip_llm=skip_llm,
        verbose=verbose,
        analyze=analyze,
    )
    return cfg
