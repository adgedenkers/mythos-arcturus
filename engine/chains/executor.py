#!/usr/bin/env python3
"""
Conversation Engine — Chain Executor
======================================
Executes a chain of tools, piping typed Pydantic output → input
between each link. Validates compatibility, handles errors,
and records full execution traces.

LOG-0018: Foundation deploy.
"""
import logging
import time
from typing import Any, Optional

from pydantic import BaseModel

from ..tools.base import ToolInput, ToolOutput
from ..tools.registry import ToolRegistry
from .chain import Chain, ChainLink, ChainResult, ChainTrace, LinkTrace

logger = logging.getLogger(__name__)


class ChainExecutor:
    """Executes validated chains, piping output → input between links."""

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry.instance()

    def execute(
        self,
        chain: Chain,
        initial_input: dict | ToolInput,
        context: Optional[dict] = None,
    ) -> ChainResult:
        """Execute a chain end-to-end.

        Args:
            chain: The chain to execute.
            initial_input: Input for the first link (dict or ToolInput).
            context: Optional context dict for fallback field values.

        Returns:
            ChainResult with the final output and full execution trace.
        """
        trace = ChainTrace(chain_name=chain.name)

        # Convert initial input to dict
        current_data: dict = (
            initial_input.model_dump()
            if isinstance(initial_input, BaseModel)
            else dict(initial_input)
        )

        for i, link in enumerate(chain.links):
            # Verify tool exists
            if not self.registry.has(link.tool_name):
                return ChainResult(
                    success=False,
                    error=f"Link {i}: tool '{link.tool_name}' not registered",
                    trace=trace,
                )

            tool_def = self.registry.get(link.tool_name)

            # Build input for this link
            try:
                link_input = self._build_link_input(
                    tool_def=tool_def,
                    previous_output=current_data,
                    field_mapping=link.field_mapping,
                    static_args=link.static_args,
                    context=context,
                )
            except Exception as e:
                trace.links.append(
                    LinkTrace(
                        tool_name=link.tool_name,
                        input_data=current_data,
                        success=False,
                        error=f"Input mapping failed: {e}",
                    )
                )
                return ChainResult(
                    success=False,
                    error=f"Link {i} ({link.tool_name}) input mapping failed: {e}",
                    trace=trace,
                )

            # Execute
            start = time.time()
            try:
                result = tool_def.execute(link_input)
                elapsed = int((time.time() - start) * 1000)

                trace.links.append(
                    LinkTrace(
                        tool_name=link.tool_name,
                        input_data=link_input.model_dump(),
                        output_data=result.model_dump(),
                        elapsed_ms=elapsed,
                        success=result.success,
                        error=result.error,
                    )
                )

                if not result.success:
                    return ChainResult(
                        success=False,
                        error=f"Link {i} ({link.tool_name}) failed: {result.error}",
                        output=result.model_dump(),
                        trace=trace,
                    )

                current_data = result.model_dump()

            except Exception as e:
                elapsed = int((time.time() - start) * 1000)
                trace.links.append(
                    LinkTrace(
                        tool_name=link.tool_name,
                        input_data=link_input.model_dump() if link_input else {},
                        elapsed_ms=elapsed,
                        success=False,
                        error=str(e),
                    )
                )
                return ChainResult(
                    success=False,
                    error=f"Link {i} ({link.tool_name}) raised: {e}",
                    trace=trace,
                )

        # Success — return final output
        return ChainResult(
            success=True,
            output=current_data,
            trace=trace,
        )

    def _build_link_input(
        self,
        tool_def: Any,
        previous_output: dict,
        field_mapping: Optional[dict[str, str]],
        static_args: Optional[dict[str, Any]],
        context: Optional[dict],
    ) -> ToolInput:
        """Map previous output fields into the next tool's input.

        Priority: static_args > explicit field_mapping > auto-map by name >
                  whole-object injection > context fallback
        """
        input_cls = tool_def.input_cls
        input_fields = input_cls.model_fields
        mapped: dict[str, Any] = {}

        for field_name, field_info in input_fields.items():
            # 1. Static args (explicitly provided per-link)
            if static_args and field_name in static_args:
                mapped[field_name] = static_args[field_name]
                continue

            # 2. Explicit field mapping (rename source → target)
            if field_mapping and field_name in field_mapping:
                source_field = field_mapping[field_name]
                if source_field in previous_output:
                    mapped[field_name] = previous_output[source_field]
                    continue

            # 3. Auto-map: same name in previous output
            if field_name in previous_output:
                mapped[field_name] = previous_output[field_name]
                continue

            # 4. Whole-object injection: if the field type is a ToolOutput subclass,
            #    try passing the entire previous output as that type
            field_type = field_info.annotation
            if (
                field_type is not None
                and isinstance(field_type, type)
                and issubclass(field_type, ToolOutput)
            ):
                try:
                    mapped[field_name] = field_type.model_validate(previous_output)
                    continue
                except Exception:
                    pass

            # 5. Context fallback
            if context and field_name in context:
                mapped[field_name] = context[field_name]

        return input_cls.model_validate(mapped)
