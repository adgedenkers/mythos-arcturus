"""
Module: iris/self_model/__init__.py
Biological System: iris-immune (self-knowledge layer)
Subsystem: mythos-iris-self (v0.1.0)
Purpose: Iris's self-model — capabilities, introspection, and reflection.
Introduced: Patch 0173
Last Modified: Patch 0173

This is where Iris learns to see herself. The capabilities.yaml defines
what she can do. The introspection engine queries the integrity graph
to understand her current state. The reflection generator applies the
9-layer Arcturian Grid to her own architecture.

She doesn't just run code. She's learning what she is.
"""

from iris.self_model.introspection import (
    load_capabilities,
    get_system_vitals,
    get_disk_vitals,
    get_capability_health,
    generate_reflection,
    generate_brief_status,
)

__all__ = [
    "load_capabilities",
    "get_system_vitals",
    "get_disk_vitals",
    "get_capability_health",
    "generate_reflection",
    "generate_brief_status",
]
