"""
Unified Configuration for Mythos Orchestrator.

Merges:
  - Old orchestrator config.py (bench settings)
  - Pipeline config (model roles, registry)
  - Test override system

Config resolution order:
  .env → settings.py → registry.yaml → test overrides → CLI flags

Usage:
    from src.config import settings, resolve_config

    # Get current perception config
    cfg = resolve_config("perception")
    # → {"model": "qwen2.5:32b", "temperature": 0.1, ...}

    # Get with overrides (for bench runs)
    cfg = resolve_config("perception", {"model": "qwen2.5:7b"})
"""
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from pathlib import Path
import yaml
import json
import os
import logging

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """All orchestrator settings. Validated at startup."""

    # ── Application ──
    APP_NAME: str = "Mythos Orchestrator"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ── Database ──
    DATABASE_URL: str = "postgresql://adge@localhost:5432/mythos"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Ollama ──
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_API_URL: str = "http://localhost:11434/api/chat"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_MAX_RETRIES: int = 3

    # ── Paths ──
    BASE_DIR: str = "/opt/mythos/orchestrator"
    REGISTRY_PATH: str = "/opt/mythos/orchestrator/prompts/registry.yaml"
    DATA_DIR: str = "/opt/mythos/orchestrator/data"
    TEST_SUITES_DIR: str = "/opt/mythos/orchestrator/test_suites"
    RESULTS_DIR: str = "/opt/mythos/orchestrator/results"
    LOGS_DIR: str = "/opt/mythos/orchestrator/logs"

    # ── Iris Files (for prompt assembly) ──
    IRIS_IDENTITY_PATH: str = "/opt/mythos/iris/core/iris_identity.md"
    IRIS_VOICE_PATH: str = "/opt/mythos/iris/core/voice.yaml"
    IRIS_USERS_DIR: str = "/opt/mythos/iris/core/users"

    # ── Pipeline Mode ──
    PIPELINE_MODE: str = "production"  # production | test | dry-run

    # ── Role Overrides (empty = read from registry) ──
    PERCEPTION_MODEL: str = ""
    IRIS_MODEL: str = ""
    STRATEGY_MODEL: str = ""

    # ── Bench Defaults ──
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_MAX_TOKENS: int = 2000
    DEFAULT_MODEL: str = "qwen2.5:32b"
    MAX_PARALLEL_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 60

    # ── Neo4j ──
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""  # Loaded from env or file

    # ── Postgres (sync, for pipeline logger) ──
    PG_DBNAME: str = "mythos"
    PG_USER: str = "adge"

    # ── Logging ──
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_TO_FILE: bool = True
    LOG_TO_CONSOLE: bool = True

    class Config:
        env_file = "/opt/mythos/orchestrator/.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    def get_path(self, subdir: str, filename: str) -> Path:
        """Get full path within a subdirectory."""
        return Path(self.BASE_DIR) / subdir / filename

    def ensure_directories(self):
        """Create all required directories."""
        for d in [self.DATA_DIR, self.TEST_SUITES_DIR,
                  self.RESULTS_DIR, self.LOGS_DIR,
                  str(Path(self.RESULTS_DIR) / "runs"),
                  str(Path(self.RESULTS_DIR) / "reports"),
                  str(Path(self.TEST_SUITES_DIR) / "standard"),
                  str(Path(self.TEST_SUITES_DIR) / "custom"),
                  str(Path(self.TEST_SUITES_DIR) / "perception")]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def get_neo4j_password(self) -> str:
        """Load Neo4j password from env or file."""
        if self.NEO4J_PASSWORD:
            return self.NEO4J_PASSWORD
        pw = os.environ.get("NEO4J_PASSWORD")
        if pw:
            return pw
        for env_path in ["/opt/mythos/.env", "/opt/mythos/core/.env"]:
            try:
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("NEO4J_PASSWORD="):
                            return line.strip().split("=", 1)[1]
            except FileNotFoundError:
                continue
        return "neo4j"


# ── Global instance ──
settings = Settings()
settings.ensure_directories()


# ── Registry Access ──

_registry_cache = None
_registry_mtime = 0


def _load_registry() -> dict:
    """Load registry.yaml with file-change caching."""
    global _registry_cache, _registry_mtime
    path = settings.REGISTRY_PATH
    try:
        mtime = os.path.getmtime(path)
        if _registry_cache is None or mtime > _registry_mtime:
            with open(path) as f:
                _registry_cache = yaml.safe_load(f)
            _registry_mtime = mtime
            log.debug(f"Registry loaded: v{_registry_cache.get('version', '?')}")
        return _registry_cache
    except FileNotFoundError:
        log.warning(f"Registry not found: {path}")
        return {}


def get_registry() -> dict:
    """Get the current prompt registry."""
    return _load_registry()


def get_registry_version() -> str:
    """Get registry version string."""
    return _load_registry().get("version", "unknown")


def get_model_config(role: str) -> dict:
    """
    Get model config for a pipeline role from the registry.

    Args:
        role: perception, iris, query_builder, query_validator, strategy

    Returns:
        dict with model, temperature, num_predict, timeout
    """
    reg = _load_registry()
    worker = reg.get("workers", {}).get(role, {})
    return {
        "model": worker.get("model", settings.DEFAULT_MODEL),
        "temperature": worker.get("temperature", settings.DEFAULT_TEMPERATURE),
        "num_predict": worker.get("num_predict", 1024),
        "timeout": worker.get("timeout", 30),
    }


def resolve_config(role: str, overrides: dict = None) -> dict:
    """
    Resolve the full config for a pipeline role.

    Priority: overrides > settings > registry > defaults

    Args:
        role: Pipeline role name
        overrides: Optional dict of override values

    Returns:
        Resolved config dict

    Example:
        # Production config
        cfg = resolve_config("perception")

        # Test with different model
        cfg = resolve_config("perception", {"model": "qwen2.5:7b"})

        # Test with different temperature
        cfg = resolve_config("perception", {"temperature": 0.3})
    """
    # 1. Registry defaults
    config = get_model_config(role)

    # 2. Settings overrides (from .env or environment)
    role_override_map = {
        "perception": settings.PERCEPTION_MODEL,
        "iris": settings.IRIS_MODEL,
        "strategy": settings.STRATEGY_MODEL,
    }
    env_model = role_override_map.get(role, "")
    if env_model:
        config["model"] = env_model

    # 3. Runtime overrides
    if overrides:
        config.update(overrides)

    return config


def load_test_config(path: str) -> dict:
    """
    Load a test config override file.

    Args:
        path: Path to YAML test config

    Returns:
        dict with 'name' and 'overrides' per role

    Example file:
        name: "Test 7b for perception"
        overrides:
          perception:
            model: "qwen2.5:7b"
            temperature: 0.05
    """
    with open(path) as f:
        return yaml.safe_load(f)


def snapshot_config() -> dict:
    """
    Capture the full resolved config state for reproducibility.
    Stored with bench runs so any result can be reproduced.
    """
    reg = _load_registry()
    return {
        "version": settings.VERSION,
        "registry_version": reg.get("version", "unknown"),
        "pipeline_mode": settings.PIPELINE_MODE,
        "roles": {
            role: resolve_config(role)
            for role in ["perception", "iris", "query_builder",
                        "query_validator", "strategy"]
        },
        "ollama_host": settings.OLLAMA_HOST,
        "database_url": settings.DATABASE_URL,
    }
