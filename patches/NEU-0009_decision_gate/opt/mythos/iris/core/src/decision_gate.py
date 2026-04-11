"""
Iris Decision Gate — LLM Judgment Before Action

When a trigger has both context_queries (non-empty) and decision_prompt (non-null),
the trigger engine routes through this gate instead of direct action dispatch.

Flow:
    1. Context gathered by ContextEngine (already complete when we're called)
    2. Assemble prompt: trigger's decision_prompt with {context} replaced
    3. Append structured response instruction
    4. Call Ollama (lightweight sync httpx — no LLMClient dependency)
    5. Parse structured JSON response
    6. Apply confidence thresholds → auto-execute / execute+notify / defer

Confidence thresholds:
    >= 0.8  → auto-execute (no human needed)
    0.5-0.8 → execute + notify human
    < 0.5   → defer to human (do NOT execute)

Uses sync httpx.post() directly to Ollama /api/generate.
Does NOT import LLMClient (requires Config + PromptManager, too heavy for this).
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx

log = logging.getLogger("iris.decision_gate")

# ═══════════════════════════════════════════════════
# DECISION RESULT
# ═══════════════════════════════════════════════════

@dataclass
class DecisionResult:
    """Structured result from the decision gate."""
    action: str                          # action name from LLM (e.g. "restart", "notify_human", "log_only")
    confidence: float                    # 0.0 - 1.0
    reasoning: str                       # LLM's explanation
    params: Dict[str, Any] = field(default_factory=dict)  # optional action parameters
    raw_response: str = ""               # full LLM response text
    auto_executed: bool = False          # did we auto-execute?
    notify: bool = False                 # should we notify human?
    llm_duration_ms: int = 0            # how long the LLM call took

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "params": self.params,
            "auto_executed": self.auto_executed,
            "notify": self.notify,
            "llm_duration_ms": self.llm_duration_ms,
        }


# ═══════════════════════════════════════════════════
# RESPONSE INSTRUCTION (appended to every prompt)
# ═══════════════════════════════════════════════════

_RESPONSE_INSTRUCTION = """

You MUST respond with ONLY a JSON object. No preamble, no markdown, no explanation outside the JSON.

Required format:
{
    "action": "<action_name>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation of your decision>",
    "params": {}
}

Rules:
- "action" must be one of the actions described in the prompt above
- "confidence" is how certain you are this is the right action (0.0 = no idea, 1.0 = absolutely certain)
- "reasoning" should be 1-3 sentences explaining your decision
- "params" contains any parameters needed for the chosen action (empty dict if none)
- Respond ONLY with the JSON object, nothing else
"""


# ═══════════════════════════════════════════════════
# DECISION GATE
# ═══════════════════════════════════════════════════

class DecisionGate:
    """
    LLM-based decision layer for the trigger engine.

    Evaluates gathered context against a trigger's decision prompt,
    returns a structured decision with confidence-based routing.
    """

    # Confidence thresholds
    THRESHOLD_AUTO = 0.8      # >= this: auto-execute
    THRESHOLD_NOTIFY = 0.5    # >= this but < AUTO: execute + notify human
    # < NOTIFY: defer to human entirely

    def __init__(self, db_config: dict,
                 ollama_host: str = "http://localhost:11434",
                 default_model: str = "qwen2.5:32b",
                 default_temperature: float = 0.1,
                 default_max_tokens: int = 512,
                 request_timeout: float = 30.0):
        self.db_config = db_config
        self.ollama_host = ollama_host.rstrip("/")
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.request_timeout = request_timeout

    def evaluate(self, trigger: dict, context: dict) -> DecisionResult:
        """
        Evaluate a trigger's decision prompt against gathered context.

        Args:
            trigger: scheduled_triggers row dict (must have 'decision_prompt')
            context: gathered context dict from ContextEngine.gather()

        Returns:
            DecisionResult with action, confidence, routing flags
        """
        decision_prompt = trigger.get("decision_prompt", "")
        if not decision_prompt:
            log.warning(f"Decision gate called for trigger '{trigger.get('name')}' with no decision_prompt")
            return DecisionResult(
                action="notify_human",
                confidence=0.0,
                reasoning="No decision prompt configured for this trigger",
                notify=True,
            )

        # Assemble the full prompt
        context_json = json.dumps(context, default=str, indent=2)
        assembled_prompt = decision_prompt.replace("{context}", context_json)
        assembled_prompt += _RESPONSE_INSTRUCTION

        # Determine model — trigger metadata can override
        metadata = trigger.get("metadata") or {}
        model = metadata.get("model", self.default_model)
        temperature = metadata.get("temperature", self.default_temperature)

        # Call Ollama
        log.info(f"Decision gate calling {model} for trigger '{trigger.get('name')}'")
        start = time.time()
        raw_response = self._call_ollama(assembled_prompt, model, temperature)
        llm_duration_ms = int((time.time() - start) * 1000)

        # Parse response
        result = self._parse_response(raw_response)
        result.raw_response = raw_response
        result.llm_duration_ms = llm_duration_ms

        # Apply confidence thresholds
        if result.confidence >= self.THRESHOLD_AUTO:
            result.auto_executed = True
            result.notify = False
            log.info(
                f"Decision gate: AUTO-EXECUTE '{result.action}' "
                f"(confidence={result.confidence:.2f}) for '{trigger.get('name')}'"
            )
        elif result.confidence >= self.THRESHOLD_NOTIFY:
            result.auto_executed = True
            result.notify = True
            log.info(
                f"Decision gate: EXECUTE+NOTIFY '{result.action}' "
                f"(confidence={result.confidence:.2f}) for '{trigger.get('name')}'"
            )
        else:
            result.auto_executed = False
            result.notify = True
            log.info(
                f"Decision gate: DEFER '{result.action}' "
                f"(confidence={result.confidence:.2f}) for '{trigger.get('name')}'"
            )

        return result

    def _call_ollama(self, prompt: str, model: str, temperature: float) -> str:
        """Synchronous call to Ollama /api/generate."""
        url = f"{self.ollama_host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": self.default_max_tokens,
            },
        }

        try:
            response = httpx.post(
                url, json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except httpx.TimeoutException:
            log.error(f"Ollama request timed out after {self.request_timeout}s")
            return ""
        except httpx.HTTPStatusError as e:
            log.error(f"Ollama HTTP error: {e.response.status_code} — {e.response.text[:200]}")
            return ""
        except Exception as e:
            log.error(f"Ollama call failed: {e}")
            return ""

    def _parse_response(self, raw: str) -> DecisionResult:
        """
        Parse LLM response into DecisionResult.
        Falls back to safe defaults if unparseable.
        """
        if not raw or not raw.strip():
            log.warning("Decision gate received empty LLM response")
            return DecisionResult(
                action="notify_human",
                confidence=0.0,
                reasoning="LLM returned empty response — deferring to human",
                notify=True,
            )

        # Try to extract JSON from the response
        text = raw.strip()

        # Handle markdown code fences
        if text.startswith("```"):
            # Strip opening fence (with optional language tag)
            first_newline = text.index("\n") if "\n" in text else 3
            text = text[first_newline + 1:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        # Try direct JSON parse
        try:
            data = json.loads(text)
            return self._validated_result(data)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the response
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            try:
                data = json.loads(text[brace_start:brace_end + 1])
                return self._validated_result(data)
            except json.JSONDecodeError:
                pass

        # Completely unparseable — safe default
        log.warning(f"Decision gate could not parse LLM response: {text[:200]}")
        return DecisionResult(
            action="notify_human",
            confidence=0.0,
            reasoning=f"Could not parse LLM response — deferring to human. Raw: {text[:200]}",
            notify=True,
        )

    def _validated_result(self, data: dict) -> DecisionResult:
        """Validate and build DecisionResult from parsed JSON."""
        action = str(data.get("action", "notify_human")).strip()
        if not action:
            action = "notify_human"

        try:
            confidence = float(data.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))  # clamp to [0, 1]
        except (TypeError, ValueError):
            confidence = 0.0

        reasoning = str(data.get("reasoning", "")).strip()
        params = data.get("params", {})
        if not isinstance(params, dict):
            params = {}

        return DecisionResult(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            params=params,
        )
