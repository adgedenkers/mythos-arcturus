#!/usr/bin/env python3
"""
Skills Context Builder
======================
Reads the Mythos skills registry and produces a compact context block
for injection into Iris's system prompt.

This is what makes Iris aware of her available skills — she can then
reason about which skill to invoke when a task matches trigger conditions.

Target: under 300 tokens for the skills context block.
"""

import logging
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

SKILLS_DIR = Path("/opt/mythos/skills")
REGISTRY_FILE = SKILLS_DIR / "REGISTRY.yaml"


def build_skills_context() -> str:
    """
    Build a compact skills awareness block for Iris.
    Returns a string to append to the system prompt.
    
    Reads REGISTRY.yaml and formats available skills as a concise
    reference Iris can use to decide when to invoke a skill.
    """
    if not REGISTRY_FILE.exists():
        logger.debug("No skills registry found at %s", REGISTRY_FILE)
        return ""
    
    try:
        with open(REGISTRY_FILE) as f:
            registry = yaml.safe_load(f)
        
        if not registry or 'skills' not in registry:
            return ""
        
        skills = registry['skills']
        if not skills:
            return ""
        
        # Group by category
        by_category = {}
        for skill in skills:
            cat = skill.get('category', 'other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)
        
        lines = []
        lines.append("\n\nYOUR SKILLS — Capabilities you can invoke:")
        lines.append("When a task matches these, read the skill file at /opt/mythos/skills/{path} and follow its process.")
        
        category_labels = {
            'analytical': '🔍 Analytical',
            'builder': '🔧 Builder',
            'meta': '⚙️ Meta',
        }
        
        for cat in ['analytical', 'builder', 'meta']:
            if cat not in by_category:
                continue
            lines.append(f"\n{category_labels.get(cat, cat)}:")
            for skill in by_category[cat]:
                name = skill.get('name', '?')
                summary = skill.get('summary', '').strip()
                tier = skill.get('risk_tier', '?')
                path = skill.get('path', '?')
                
                # Compact: one line per skill
                tier_label = {'T1-autonomous': 'T1', 'T2-patch': 'T2', 'T3-propose': 'T3'}.get(tier, tier)
                lines.append(f"  [{tier_label}] {name}: {summary} → {path}")
        
        lines.append("")
        lines.append("Risk tiers: T1=execute freely, T2=build patch and deploy, T3=propose plan and wait for approval.")
        lines.append("To use a skill: read the full skill file, follow its pre-flight checks and process steps.")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Skills context build failed: {e}", exc_info=True)
        return ""


def get_skill_content(skill_path: str) -> Optional[str]:
    """
    Read a specific skill file content.
    
    Args:
        skill_path: Relative path from skills dir (e.g., 'builder/build_patch.md')
    
    Returns:
        Skill file content as string, or None if not found.
    """
    full_path = SKILLS_DIR / skill_path
    if not full_path.exists():
        logger.warning(f"Skill file not found: {full_path}")
        return None
    
    try:
        return full_path.read_text()
    except Exception as e:
        logger.error(f"Failed to read skill file {full_path}: {e}")
        return None


if __name__ == "__main__":
    print(build_skills_context())
