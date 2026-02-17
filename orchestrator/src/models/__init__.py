"""
Models Package

Model management and Ollama integration.

Phase 1.2: Ollama Integration
"""

from .ollama_client import OllamaClient
from .model_registry import ModelRegistry
from .model_manager import ModelManager

__all__ = [
    "OllamaClient",
    "ModelRegistry",
    "ModelManager"
]
