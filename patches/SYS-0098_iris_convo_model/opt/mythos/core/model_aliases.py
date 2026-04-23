"""
Canonical model alias registry — single source of truth.
Every file that needs model aliases imports from here.
When models change, update THIS file only.

SYS-0098: iris:convo is now the default model.
  - iris:convo     — clean technical partner (FROM qwen3:32b)
  - iris:cosmos    — full spiritual framework (FROM qwen3:30b-a3b)
  - iris:cosmos-deep — deep spiritual framework (FROM qwen3:32b)
  - iris:latest    — alias for iris:cosmos (backward compat)
  - iris-deep:latest — alias for iris:cosmos-deep (backward compat)

Usage:
    from core.model_aliases import resolve_alias, MODEL_ALIASES, DEFAULT_MODEL
    from core.model_aliases import get_model_descriptions, get_help_text
"""
import os

# ── The default model (env override supported) ─────────────────────────────
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "iris:convo")

# ── Short aliases → actual model names ──────────────────────────────────────
MODEL_ALIASES = {
    # New names
    "convo":    "iris:convo",
    "cosmos":   "iris:cosmos-deep",
    "standard": "iris:convo",

    # Legacy aliases — still work
    "fast":     "iris:cosmos",
    "a3b":      "iris:cosmos",
    "deep":     "iris:cosmos-deep",
    "32b":      "iris:cosmos-deep",
    "think":    "iris:cosmos-deep",
    "thinking": "iris:cosmos-deep",

    "auto":     DEFAULT_MODEL,
}

# ── Human-readable descriptions for display ─────────────────────────────────
MODEL_DESCRIPTIONS = {
    "convo":    "iris:convo (qwen3:32b, technical partner — default)",
    "cosmos":   "iris:cosmos-deep (qwen3:32b, full spiritual framework)",
    "standard": "iris:convo (qwen3:32b, technical partner — default)",
    "fast":     "iris:cosmos (qwen3:30b-a3b, ~10s, spiritual)",
    "a3b":      "iris:cosmos (qwen3:30b-a3b, ~10s, spiritual)",
    "deep":     "iris:cosmos-deep (qwen3:32b, ~30-50s, spiritual)",
    "32b":      "iris:cosmos-deep (qwen3:32b, ~30-50s, spiritual)",
    "think":    "iris:cosmos-deep (qwen3:32b, ~30-50s, spiritual)",
    "thinking": "iris:cosmos-deep (qwen3:32b, ~30-50s, spiritual)",
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
        "`/model convo` — iris:convo (qwen3:32b, technical partner — default)\n"
        "`/model cosmos` — iris:cosmos-deep (qwen3:32b, full spiritual framework)\n"
        "`/model fast` — iris:cosmos (qwen3:30b-a3b, quick spiritual)\n"
        "`/model auto` — default model"
    )


def get_help_text_extended() -> str:
    """Generate extended model help text including /setmodel."""
    return (
        "`/model convo` — iris:convo (qwen3:32b, technical partner — default)\n"
        "`/model cosmos` — iris:cosmos-deep (qwen3:32b, full spiritual framework)\n"
        "`/model fast` — iris:cosmos (qwen3:30b-a3b, quick spiritual)\n"
        "`/model auto` — default model\n"
        "**Shortcuts:**\n"
        "`/cosmos` — switch to full spiritual framework\n"
        "`/standard` — switch back to technical partner\n"
        "**Advanced:**\n"
        "`/setmodel <exact_name>` — Use any installed model\n"
        "`/models` — List all installed Ollama models"
    )
