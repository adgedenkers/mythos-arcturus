#!/usr/bin/env python3
"""
Prompt Registry Loader
=======================
Reads prompt_registry.yaml and assembles complete prompts
for any worker based on conditions.

Usage:
    from registry_loader import RegistryLoader
    reg = RegistryLoader()
    prompt = reg.assemble_prompt("perception")
    model = reg.get_model("perception")
"""

import os
import yaml
from typing import Optional


REGISTRY_PATH = "/opt/mythos/workers/prompt_registry.yaml"


class RegistryLoader:
    def __init__(self, path=REGISTRY_PATH):
        with open(path) as f:
            self.registry = yaml.safe_load(f)
        self.version = self.registry.get("version", "unknown")

    def get_version(self):
        return self.version

    def get_model(self, worker_name):
        """Get model config for a worker."""
        worker = self.registry.get("workers", {}).get(worker_name, {})
        return {
            "model": worker.get("model", "qwen2.5:7b"),
            "temperature": worker.get("temperature", 0.1),
            "num_predict": worker.get("num_predict", 1024),
            "timeout": worker.get("timeout", 30),
        }

    def assemble_prompt(self, worker_name, context=None, fast_path=False):
        """Assemble the full system prompt for a worker.

        Args:
            worker_name: perception, query_builder, query_validator, iris
            context: dict of template variables for substitution
            fast_path: if True, use fast_path_components for iris

        Returns:
            (prompt_text, component_ids_list)
        """
        context = context or {}
        worker = self.registry.get("workers", {}).get(worker_name, {})

        if fast_path and "fast_path_components" in worker:
            # Fast path: only include specified components
            allowed_ids = {c["id"] for c in worker["fast_path_components"]}
            components = [c for c in worker.get("system_prompt_components", [])
                         if c["id"] in allowed_ids]
        else:
            components = worker.get("system_prompt_components", [])

        # Add global rules that apply to this worker
        global_rules = self.registry.get("global_rules", [])
        applicable_globals = [
            g for g in global_rules
            if worker_name in g.get("applies_to", [])
        ]

        # Sort everything by order
        all_parts = []

        for g in applicable_globals:
            all_parts.append((0, g["id"], g["text"]))

        for c in components:
            order = c.get("order", 50)
            cid = c["id"]

            # Check condition
            condition = c.get("condition", "always")
            if not self._check_condition(condition, context):
                continue

            # Get text
            if "text" in c:
                text = c["text"]
            elif "source" in c:
                text = self._load_source(c["source"], context)
                if text is None:
                    continue
            else:
                continue

            # Substitute variables
            text = self._substitute(text, context)
            all_parts.append((order, cid, text))

        # Sort by order
        all_parts.sort(key=lambda x: x[0])

        prompt = "\n\n".join(part[2] for part in all_parts)
        component_ids = [part[1] for part in all_parts]

        return prompt, component_ids

    def assemble_user_prompt(self, worker_name, context=None):
        """Assemble the user prompt template for a worker."""
        context = context or {}
        worker = self.registry.get("workers", {}).get(worker_name, {})
        template = worker.get("user_prompt_template", "{message}")
        return self._substitute(template, context)

    def _check_condition(self, condition, context):
        """Evaluate a component condition."""
        if condition == "always":
            return True
        if condition == "context_available":
            return bool(context.get("assembled_context"))
        if condition == "speaker_file_exists":
            speaker = context.get("speaker", "")
            path = f"/opt/mythos/iris/core/users/{speaker}.yaml"
            return os.path.exists(path)
        # Unknown condition: include by default
        return True

    def _load_source(self, source, context):
        """Load content from a file source."""
        if source.startswith("file:"):
            path = source[5:]
            path = self._substitute(path, context)
            try:
                with open(path) as f:
                    return f.read()
            except FileNotFoundError:
                return None
        return None

    def _substitute(self, text, context):
        """Simple variable substitution. {key} → context[key]."""
        for key, value in context.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text


# CLI: dump assembled prompts for inspection
if __name__ == "__main__":
    import sys

    reg = RegistryLoader()
    print(f"Registry version: {reg.get_version()}\n")

    worker = sys.argv[1] if len(sys.argv) > 1 else "perception"
    fast = "--fast" in sys.argv

    ctx = {
        "speaker": "Ka'tuar'el",
        "speaker_name": "Ka'tuar'el",
        "timestamp": "2026-02-25 16:00",
        "gap_description": "5 minutes",
        "message": "test message",
        "tone": "warm",
        "depth": "moderate",
    }

    prompt, components = reg.assemble_prompt(worker, ctx, fast_path=fast)
    print(f"Worker: {worker} {'(fast path)' if fast else ''}")
    print(f"Components: {components}")
    print(f"Model: {reg.get_model(worker)}")
    print(f"\n{'='*60}")
    print(prompt)
    print(f"{'='*60}")
    print(f"\nPrompt length: {len(prompt)} chars")
