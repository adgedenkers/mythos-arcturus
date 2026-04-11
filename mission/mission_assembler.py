#!/usr/bin/env python3
"""
Mission Assembler — build runnable mission YAML from modular parts.

Instead of one giant YAML, missions are assembled from:
  - A mission config (context sources, metadata, phase ordering)
  - Prompt template files (one per phase, easy to edit and iterate)

Usage:
    mythos-mission-assemble <mission_dir> [--output <path>] [--run] [--dry-run]

Mission directory structure:
    my_mission/
    ├── mission.yaml       ← metadata, context, phase order, model config
    ├── prompts/
    │   ├── phase1.md      ← prompt template for phase 1
    │   ├── phase2.md      ← prompt template for phase 2
    │   └── phase3.md      ← prompt template for phase 3
    └── README.md          ← optional documentation

The assembler reads mission.yaml, injects prompt text from the prompts/ dir,
and produces a single runnable YAML that mythos-mission can execute.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def assemble_mission(mission_dir: str) -> dict:
    """Assemble a mission from a modular directory."""
    mission_dir = Path(mission_dir)

    # Load the mission config
    config_path = mission_dir / "mission.yaml"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found")
        sys.exit(1)

    config = yaml.safe_load(config_path.read_text())

    # Load prompt templates into each phase
    prompts_dir = mission_dir / "prompts"
    for phase in config.get("phases", []):
        prompt_file = phase.get("prompt_file")
        if prompt_file:
            prompt_path = prompts_dir / prompt_file
            if prompt_path.exists():
                phase["prompt"] = prompt_path.read_text()
            else:
                print(f"WARNING: Prompt file not found: {prompt_path}")
                phase["prompt"] = f"[MISSING PROMPT: {prompt_file}]"
            # Remove the prompt_file key — not part of mission runner spec
            del phase["prompt_file"]

        # Same for retry_prompt
        retry_file = phase.get("retry_prompt_file")
        if retry_file:
            retry_path = prompts_dir / retry_file
            if retry_path.exists():
                phase["retry_prompt"] = retry_path.read_text()
            else:
                print(f"WARNING: Retry prompt file not found: {retry_path}")
            del phase["retry_prompt_file"]

    return config


def write_assembled(config: dict, output_path: str):
    """Write assembled mission YAML."""
    # Custom representer to handle multi-line strings nicely
    def str_representer(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_representer)

    Path(output_path).write_text(yaml.dump(config, default_flow_style=False, sort_keys=False, width=120))
    print(f"Assembled mission written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Assemble a modular mission into a runnable YAML",
        prog="mythos-mission-assemble",
    )
    parser.add_argument("mission_dir", help="Path to mission directory")
    parser.add_argument("--output", "-o", help="Output path (default: /tmp/mythos-mission/assembled.yaml)")
    parser.add_argument("--run", action="store_true", help="Assemble and immediately run")
    parser.add_argument("--dry-run", action="store_true", help="Assemble and dry-run")
    parser.add_argument("--validate", action="store_true", help="Assemble and validate only")

    args = parser.parse_args()
    output = args.output or "/tmp/mythos-mission/assembled.yaml"

    os.makedirs(Path(output).parent, exist_ok=True)

    config = assemble_mission(args.mission_dir)
    write_assembled(config, output)

    if args.validate:
        subprocess.run(["mythos-mission", "validate", output])
    elif args.dry_run:
        subprocess.run(["mythos-mission", "dry-run", output])
    elif args.run:
        subprocess.run(["mythos-mission", "run", output])


if __name__ == "__main__":
    main()
