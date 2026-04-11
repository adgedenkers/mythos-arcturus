#!/usr/bin/env python3
"""
Conversation Engine — Chain Models
====================================
Pydantic models for tool chains: sequences of tools where
the output of one pipes into the input of the next.

Chain:       A named sequence of ChainLinks.
ChainLink:   One step — tool name + field mapping + static args.
ChainResult: What comes back after execution.
ChainTrace:  Full execution telemetry.

LOG-0018: Foundation deploy.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from ..tools.base import ToolOutput


# ─── Chain Link ──────────────────────────────────────────────────────────────

class ChainLink(BaseModel):
    """Single step in a tool chain."""

    tool_name: str = Field(description="Registered tool name")
    field_mapping: Optional[dict[str, str]] = Field(
        default=None,
        description=(
            "Maps source output fields to target input fields. "
            "None = auto-map by name. "
            "Example: {'full_name': 'name'} maps output.full_name → input.name"
        ),
    )
    static_args: Optional[dict[str, Any]] = Field(
        default=None,
        description="Static arguments that don't come from the previous link",
    )
    model_override: Optional[str] = Field(
        default=None,
        description="Use a different model for this link (LLM-based tools only)",
    )


# ─── Chain ───────────────────────────────────────────────────────────────────

class Chain(BaseModel):
    """A sequence of tools that pipe output → input.

    Can be pre-defined (loaded from chains.yaml) or composed
    dynamically by the model via the compose_chain meta-tool.
    """

    name: str
    description: str = ""
    links: list[ChainLink] = Field(min_length=1)


# ─── Execution Trace ────────────────────────────────────────────────────────

class LinkTrace(BaseModel):
    """Execution trace for one chain link."""

    tool_name: str
    input_data: dict = Field(default_factory=dict)
    output_data: dict = Field(default_factory=dict)
    elapsed_ms: int = 0
    success: bool = True
    error: Optional[str] = None


class ChainTrace(BaseModel):
    """Full execution trace for a chain."""

    chain_name: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    links: list[LinkTrace] = Field(default_factory=list)

    @property
    def total_ms(self) -> int:
        return sum(link.elapsed_ms for link in self.links)

    @property
    def tools_called(self) -> list[str]:
        return [link.tool_name for link in self.links]


# ─── Chain Result ────────────────────────────────────────────────────────────

class ChainResult(BaseModel):
    """Result of a chain execution."""

    success: bool
    output: Optional[dict] = None  # Final link's output as dict
    error: Optional[str] = None
    trace: ChainTrace = Field(default_factory=lambda: ChainTrace(chain_name=""))
