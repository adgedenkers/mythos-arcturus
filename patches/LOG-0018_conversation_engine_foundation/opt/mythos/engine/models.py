#!/usr/bin/env python3
"""
Conversation Engine — Core Pydantic Models
============================================
Every boundary in the engine is a typed Pydantic model.
No raw dicts. No untyped JSON. No hoping the shape is right.

LOG-0018: Foundation deploy.
"""
import time
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


# ─── Sampling ────────────────────────────────────────────────────────────────

class SamplingConfig(BaseModel):
    """LLM sampling parameters. All settable per request."""
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    min_p: float = 0.0
    repeat_penalty: float = 1.1
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: Optional[int] = None


# ─── Conversation Config ─────────────────────────────────────────────────────

class ConversationConfig(BaseModel):
    """Complete configuration for a single LLM call.

    The engine assembles this per message. Every field is typed.
    Nothing is guessed, nothing is implicit.
    """

    # Identity
    system_prompt: str = Field(description="Assembled from mode layers + context")

    # Model
    model: str = Field(default="qwen3:30b-a3b", description="Ollama model tag")

    # Thinking
    thinking: bool = Field(default=True, description="Enable /think or /no_think")
    thinking_budget: Optional[int] = Field(default=None, description="Max thinking tokens")

    # Tools — Ollama-formatted tool definitions
    tools: Optional[list[dict]] = Field(default=None, description="Tool definitions for this call")

    # Output shape — JSON schema for structured output
    format: Optional[dict] = Field(default=None, description="Pydantic model_json_schema()")

    # Sampling
    sampling: SamplingConfig = Field(default_factory=SamplingConfig)

    # Context
    num_ctx: int = Field(default=8192, description="Context window size in tokens")
    num_predict: int = Field(default=-1, description="Max response tokens. -1 = model decides")

    # Control
    stop: Optional[list[str]] = Field(default=None, description="Stop sequences")

    # Metadata (not sent to Ollama)
    mode: str = Field(default="conversation", description="Active conversation mode name")
    requires_memory: bool = False
    requires_graph: bool = False

    def to_ollama_payload(self, messages: list[dict]) -> dict:
        """Build the exact payload for Ollama /api/chat endpoint."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.sampling.temperature,
                "top_k": self.sampling.top_k,
                "top_p": self.sampling.top_p,
                "min_p": self.sampling.min_p,
                "repeat_penalty": self.sampling.repeat_penalty,
                "presence_penalty": self.sampling.presence_penalty,
                "frequency_penalty": self.sampling.frequency_penalty,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
            },
        }
        if self.sampling.seed is not None:
            payload["options"]["seed"] = self.sampling.seed
        if self.tools:
            payload["tools"] = self.tools
        if self.format:
            payload["format"] = self.format
        if self.stop:
            payload["options"]["stop"] = self.stop
        return payload


# ─── Conversation Mode ───────────────────────────────────────────────────────

class ConversationMode(BaseModel):
    """A named configuration preset loaded from conversation_modes.yaml."""

    name: str
    description: str = ""

    # Lever defaults
    thinking: bool = True
    temperature: float = 0.7
    num_ctx: int = 8192
    num_predict: int = -1

    # Tool access: None or ["*"] = all, [] = none, ["astrology", ...] = specific
    allowed_tools: Optional[list[str]] = None

    # Output constraint
    force_format: Optional[str] = Field(
        default=None, description="Pydantic model class name to force as output schema"
    )

    # Model override
    model: Optional[str] = None

    # System prompt layers to compose in order
    system_layers: list[str] = Field(default_factory=lambda: ["base"])


# ─── Context Budget ──────────────────────────────────────────────────────────

class ContextLayer(BaseModel):
    """A block of context to load into the conversation."""

    name: str
    priority: int = Field(description="1=critical (always include), 9=nice-to-have")
    content: str
    source: str = Field(description="memory, graph, transit, life_context, etc.")

    def estimate_tokens(self) -> int:
        """Rough token estimate. ~4 chars per token for English."""
        return len(self.content) // 4

    def compress_to(self, max_tokens: int) -> Optional["ContextLayer"]:
        """Return a version that fits in max_tokens."""
        max_chars = max_tokens * 4
        if len(self.content) <= max_chars:
            return self
        return self.model_copy(
            update={"content": self.content[:max_chars] + "\n[...truncated]"}
        )


class ContextBudget(BaseModel):
    """Manages token allocation across context layers."""

    total_budget: int = 8192

    # Reserved allocations
    system_prompt_budget: int = 1500
    current_message_budget: int = 500
    response_budget: int = 2000

    @property
    def remaining(self) -> int:
        return (
            self.total_budget
            - self.system_prompt_budget
            - self.current_message_budget
            - self.response_budget
        )

    def allocate(self, layers: list[ContextLayer]) -> list[ContextLayer]:
        """Allocate remaining budget to layers by priority (lower = more important)."""
        sorted_layers = sorted(layers, key=lambda la: la.priority)
        budget_left = self.remaining
        result: list[ContextLayer] = []

        for layer in sorted_layers:
            if budget_left <= 0:
                break
            tokens = layer.estimate_tokens()
            if tokens <= budget_left:
                result.append(layer)
                budget_left -= tokens
            else:
                compressed = layer.compress_to(budget_left)
                if compressed:
                    result.append(compressed)
                    budget_left -= compressed.estimate_tokens()

        return result


# ─── Engine Observation (Proprioceptive Telemetry) ────────────────────────────

class EngineObservation(BaseModel):
    """What the engine observed about its own processing."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[int] = None

    # What happened
    mode_selected: str = ""
    model_used: str = ""
    thinking_enabled: bool = False
    tools_called: list[str] = Field(default_factory=list)
    chains_executed: list[str] = Field(default_factory=list)

    # Performance (milliseconds)
    classification_ms: int = 0
    context_load_ms: int = 0
    llm_call_ms: int = 0
    tool_execution_ms: int = 0
    total_ms: int = 0

    # Token usage
    prompt_tokens: int = 0
    thinking_tokens: int = 0
    response_tokens: int = 0

    # Confidence
    classification_confidence: float = 0.0

    # Context budget
    context_budget_total: int = 0
    context_budget_used: int = 0
    layers_loaded: list[str] = Field(default_factory=list)
    layers_dropped: list[str] = Field(default_factory=list)


# ─── Engine Response ─────────────────────────────────────────────────────────

class EngineResponse(BaseModel):
    """What the engine returns to the delivery layer."""

    content: str
    mode: str
    model: str = ""
    observation: EngineObservation = Field(default_factory=EngineObservation)
