"""
Iris Conversation Engine
=========================
The missing layer between intent and the LLM.

LOG-0018: Foundation deploy.
"""
from .models import (
    ConversationConfig,
    ConversationMode,
    ContextBudget,
    ContextLayer,
    EngineObservation,
    EngineResponse,
    SamplingConfig,
)
from .ollama_client import OllamaChatClient
from .response.response import Response

__all__ = [
    "ConversationConfig",
    "ConversationMode",
    "ContextBudget",
    "ContextLayer",
    "EngineObservation",
    "EngineResponse",
    "OllamaChatClient",
    "Response",
    "SamplingConfig",
]
