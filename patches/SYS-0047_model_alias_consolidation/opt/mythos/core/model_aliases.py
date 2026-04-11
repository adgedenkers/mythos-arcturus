"""
Canonical model alias registry — single source of truth.

Every file that needs model aliases imports from here.
When models change, update THIS file only.

Usage:
    from core.model_aliases import resolve_alias, MODEL_ALIASES, DEFAULT_MODEL
    from core.model_aliases import get_model_descriptions, get_help_text
"""

import os

# ── The default model (env override supported) ─────────────────────────────
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "iris-deep:latest")

# ── Short aliases → actual model names ──────────────────────────────────────
MODEL_ALIASES = {
    "fast":     "iris:latest",
    "a3b":      "iris:latest",
    "deep":     "iris-deep:latest",
    "32b":      "iris-deep:latest",
    "think":    "iris-deep:latest",
    "thinking": "iris-deep:latest",
    "auto":     DEFAULT_MODEL,
}

# ── Human-readable descriptions for display ─────────────────────────────────
MODEL_DESCRIPTIONS = {
    "fast":     "iris:latest (qwen3:30b-a3b, ~10s)",
    "a3b":      "iris:latest (qwen3:30b-a3b, ~10s)",
    "deep":     "iris-deep:latest (qwen3:32b, ~30-50s)",
    "32b":      "iris-deep:latest (qwen3:32b, ~30-50s)",
    "think":    "iris-deep:latest (qwen3:32b, ~30-50s)",
    "thinking": "iris-deep:latest (qwen3:32b, ~30-50s)",
    "auto":     f"{DEFAULT_MODEL} (default)",
}


def resolve_alias(name: str) -> str:
    """Resolve a short alias to a full model name. Returns name unchanged if not an alias."""
    return MODEL_ALIASES.get(name.lower(), name)


def is_known_alias(name: str) -> bool:
    """Check if a name is a recognized short alias."""
    return name.lower() in MODEL_ALIASES


def get_model_description(alias: str) -> str:
    """Get human-readable description for an alias."""
    return MODEL_DESCRIPTIONS.get(alias.lower(), alias)


def get_help_text() -> str:
    """Generate model selection help text for /model and /help commands."""
    return (
        "`/model deep` — iris-deep:latest (qwen3:32b, deeper reasoning)\n"
        "`/model fast` — iris:latest (qwen3:30b-a3b, quick conversational)\n"
        "`/model auto` — default model"
    )


def get_help_text_extended() -> str:
    """Generate extended model help text including /setmodel."""
    return (
        "`/model deep` — iris-deep:latest (qwen3:32b, deeper reasoning)\n"
        "`/model fast` — iris:latest (qwen3:30b-a3b, quick conversational)\n"
        "`/model auto` — default model\n"
        "**Advanced:**\n"
        "`/setmodel <exact_name>` — Use any installed model\n"
        "`/models` — List all installed Ollama models"
    )
