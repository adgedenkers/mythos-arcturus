#!/usr/bin/env python3
"""
Conversation Engine — Tool Base Classes
=========================================
Every tool is a pure function with typed Pydantic input and output.
The output of one tool can pipe into the input of the next.

ToolInput:  Base class for all tool inputs.
ToolOutput: Base class for all tool outputs.
@tool:      Decorator that registers a function as a chainable tool.

LOG-0018: Foundation deploy.
"""
import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type, get_type_hints

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ─── Base Classes ────────────────────────────────────────────────────────────

class ToolInput(BaseModel):
    """Base class for all tool inputs. Every tool declares what it needs."""

    class Config:
        extra = "forbid"  # No surprise fields


class ToolOutput(BaseModel):
    """Base class for all tool outputs. Every tool declares what it produces."""

    success: bool = True
    error: Optional[str] = None

    class Config:
        extra = "forbid"


# ─── Tool Definition ────────────────────────────────────────────────────────

class ToolDefinition(BaseModel):
    """Registration record for a single tool.

    Holds metadata, the Pydantic types, and the handler function.
    Can generate Ollama-compatible tool schemas automatically.
    """

    name: str
    description: str
    categories: list[str] = Field(default_factory=list)
    input_type_name: str = ""   # Qualified class name (for serialization)
    output_type_name: str = ""  # Qualified class name (for serialization)

    class Config:
        arbitrary_types_allowed = True

    # ── Runtime-only (not serialized) ────────────────────────────────────
    _handler: Optional[Callable] = None
    _input_cls: Optional[Type[ToolInput]] = None
    _output_cls: Optional[Type[ToolOutput]] = None

    def model_post_init(self, __context: Any) -> None:
        # Pydantic v2: private attrs need explicit init
        object.__setattr__(self, "_handler", None)
        object.__setattr__(self, "_input_cls", None)
        object.__setattr__(self, "_output_cls", None)

    def set_runtime(
        self,
        handler: Callable,
        input_cls: Type[ToolInput],
        output_cls: Type[ToolOutput],
    ) -> None:
        """Set runtime-only fields after construction."""
        object.__setattr__(self, "_handler", handler)
        object.__setattr__(self, "_input_cls", input_cls)
        object.__setattr__(self, "_output_cls", output_cls)

    @property
    def handler(self) -> Callable:
        return object.__getattribute__(self, "_handler")

    @property
    def input_cls(self) -> Type[ToolInput]:
        return object.__getattribute__(self, "_input_cls")

    @property
    def output_cls(self) -> Type[ToolOutput]:
        return object.__getattribute__(self, "_output_cls")

    def to_ollama_schema(self) -> dict:
        """Generate Ollama tool definition from the Pydantic input model."""
        schema = self.input_cls.model_json_schema()
        # Ollama wants OpenAI-style function schema
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }

    def execute(self, input_data: Any) -> "ToolOutput":
        """Run the tool with validated input, return validated output."""
        # Accept dict, ToolInput, or ToolOutput (from previous chain link)
        if isinstance(input_data, dict):
            validated = self.input_cls.model_validate(input_data)
        elif isinstance(input_data, self.input_cls):
            validated = input_data
        elif isinstance(input_data, BaseModel):
            # Cross-type mapping: try to construct input from the model's fields
            validated = self.input_cls.model_validate(input_data.model_dump())
        else:
            raise TypeError(
                f"Tool {self.name}: expected dict or {self.input_cls.__name__}, "
                f"got {type(input_data).__name__}"
            )

        result = self.handler(validated)

        if isinstance(result, self.output_cls):
            return result
        elif isinstance(result, dict):
            return self.output_cls.model_validate(result)
        else:
            raise TypeError(
                f"Tool {self.name}: handler returned {type(result).__name__}, "
                f"expected {self.output_cls.__name__} or dict"
            )


# ─── @tool Decorator ────────────────────────────────────────────────────────

def tool(
    name: str,
    description: str,
    categories: Optional[list[str]] = None,
) -> Callable:
    """Decorator that registers a function as a chainable tool.

    The function's type hints define input/output types automatically.

    Usage::

        @tool(
            name="natal_chart",
            description="Calculate natal chart from birth data",
            categories=["astrology"],
        )
        def natal_chart(input: NatalChartInput) -> NatalChart:
            # Pure computation — takes typed input, returns typed output
            ...

    The decorated function remains directly callable AND is registered
    in the global ToolRegistry.
    """

    def decorator(func: Callable) -> Callable:
        hints = get_type_hints(func)

        # Extract input type from first parameter (skip 'return')
        param_types = [v for k, v in hints.items() if k != "return"]
        if not param_types:
            raise TypeError(f"Tool '{name}': function must have a typed parameter")
        input_cls = param_types[0]
        if not (isinstance(input_cls, type) and issubclass(input_cls, ToolInput)):
            raise TypeError(
                f"Tool '{name}': first parameter must be a ToolInput subclass, "
                f"got {input_cls}"
            )

        return_type = hints.get("return")
        if not return_type or not (
            isinstance(return_type, type) and issubclass(return_type, ToolOutput)
        ):
            raise TypeError(
                f"Tool '{name}': return type must be a ToolOutput subclass, "
                f"got {return_type}"
            )

        definition = ToolDefinition(
            name=name,
            description=description,
            categories=categories or [],
            input_type_name=f"{input_cls.__module__}.{input_cls.__qualname__}",
            output_type_name=f"{return_type.__module__}.{return_type.__qualname__}",
        )
        definition.set_runtime(
            handler=func,
            input_cls=input_cls,
            output_cls=return_type,
        )

        # Lazy import to avoid circular dependency
        from .registry import ToolRegistry

        ToolRegistry.instance().register(definition)

        # Attach metadata to the function so it's inspectable
        func._tool_definition = definition
        func._tool_name = name

        return func

    return decorator
