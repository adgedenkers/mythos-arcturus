#!/usr/bin/env python3
"""
Conversation Engine — Tool Registry
=====================================
Central registry of all tools. Singleton pattern.
Handles registration, lookup, mode-based filtering,
and execution with Pydantic validation.

LOG-0018: Foundation deploy.
"""
import json
import logging
from typing import Any, Optional

from .base import ToolDefinition, ToolInput, ToolOutput

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry of all registered tools. Singleton."""

    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, ToolDefinition]

    def __init__(self) -> None:
        self._tools = {}

    @classmethod
    def instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    # ── Registration ─────────────────────────────────────────────────────

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            logger.warning(f"ToolRegistry: overwriting existing tool '{definition.name}'")
        self._tools[definition.name] = definition
        logger.info(
            f"ToolRegistry: registered '{definition.name}' "
            f"[{', '.join(definition.categories)}]"
        )

    # ── Lookup ───────────────────────────────────────────────────────────

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered. Available: {self.list_tools()}")
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def list_tools_with_categories(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "categories": t.categories}
            for t in self._tools.values()
        ]

    # ── Mode-based filtering ─────────────────────────────────────────────

    def get_tools_for_mode(self, allowed_tools: Optional[list[str]]) -> list[dict]:
        """Return Ollama-formatted tool schemas filtered by mode.

        Args:
            allowed_tools: Tool names or categories.
                           None or ["*"] = all tools.
                           [] = no tools.
                           ["astrology", "person_lookup"] = specific names/categories.
        """
        if allowed_tools is not None and len(allowed_tools) == 0:
            return []

        if allowed_tools is None or allowed_tools == ["*"]:
            tools = list(self._tools.values())
        else:
            allowed_set = set(allowed_tools)
            tools = [
                t
                for t in self._tools.values()
                if t.name in allowed_set
                or any(c in allowed_set for c in t.categories)
            ]

        return [t.to_ollama_schema() for t in tools]

    # ── Execution ────────────────────────────────────────────────────────

    def execute(self, name: str, arguments: dict) -> ToolOutput:
        """Execute a tool with raw arguments dict. Returns typed output."""
        tool_def = self.get(name)
        return tool_def.execute(arguments)

    # ── Schema inspection ────────────────────────────────────────────────

    def get_input_schema(self, name: str) -> dict:
        return self.get(name).input_cls.model_json_schema()

    def get_output_schema(self, name: str) -> dict:
        return self.get(name).output_cls.model_json_schema()

    # ── Status ───────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "tool_count": len(self._tools),
            "tools": {
                name: {
                    "description": t.description,
                    "categories": t.categories,
                    "input_type": t.input_type_name,
                    "output_type": t.output_type_name,
                }
                for name, t in self._tools.items()
            },
        }
