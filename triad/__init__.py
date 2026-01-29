"""
Triad Memory System
===================

Three-layer conversation memory extraction:
- Grid (Knowledge): What is known - 9-node semantic structure
- Akashic (Wisdom): What it means - energetic imprint and patterns  
- Prophetic (Vision): What's emerging - trajectory and attractor sensing

Usage:
    from triad import TriadExtractor
    
    extractor = TriadExtractor()
    record = await extractor.extract_all(prompt, response)
    extractor.save_record(record)
"""

from .models import (
    Grid, GridContext, Entity, Action, State, Relationship,
    Timestamp, Artifact, OpenThread, Declaration,
    Akashic, EnergyState, ArcType, Domain,
    Prophetic, Readiness, ReadinessLevel, Seed,
    TriadRecord
)
from .extractor import TriadExtractor, load_prompt

__all__ = [
    # Main extractor
    "TriadExtractor",
    "load_prompt",
    
    # Grid models
    "Grid", "GridContext", "Entity", "Action", "State",
    "Relationship", "Timestamp", "Artifact", "OpenThread", "Declaration",
    
    # Akashic models
    "Akashic", "EnergyState", "ArcType", "Domain",
    
    # Prophetic models
    "Prophetic", "Readiness", "ReadinessLevel", "Seed",
    
    # Unified record
    "TriadRecord"
]

__version__ = "0.1.0"
